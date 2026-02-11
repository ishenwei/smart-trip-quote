import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .config import ConfigManager, LLMProvider, LLMConfig
from .factory import ProviderFactory
from .base import BaseLLMProvider, LLMRequest, LLMResponse
from .extractor import RequirementExtractor, ValidationResult
from .persistence import RequirementService
from .rate_limiter import RateLimiter
from .security import SecurityManager
from .cache import CacheManager
from .logger import LLMLogger
from .location_exception_handler import LocationExceptionHandler, LocationExceptionHandlerResult


@dataclass
class ProcessResult:
    success: bool
    requirement_id: Optional[str] = None
    raw_response: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    validation_result: Optional[ValidationResult] = None
    llm_response: Optional[LLMResponse] = None
    error: Optional[str] = None
    warnings: list = None
    conversation_id: Optional[str] = None
    retry_count: int = 0
    suggestions: Optional[list] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class LLMRequirementService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config_manager = ConfigManager()
        self.security_manager = SecurityManager()
        self.cache_manager = CacheManager()
        self.logger = LLMLogger()
        self.location_exception_handler = LocationExceptionHandler()
        
        rate_limit_config = self.config_manager.get_rate_limit_config()
        self.rate_limiter = RateLimiter(rate_limit_config)
        
        self._providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self._current_provider: Optional[LLMProvider] = None
    
    def _get_provider(self, provider: Optional[LLMProvider] = None) -> BaseLLMProvider:
        if provider is None:
            provider = self.config_manager.get_default_provider()
        
        if provider is None:
            raise ValueError("No available LLM provider configured")
        
        if provider not in self._providers:
            config = self.config_manager.get_config(provider)
            if config is None:
                raise ValueError(f"No configuration found for provider: {provider}")
            
            self._providers[provider] = ProviderFactory.create_provider(config)
        
        return self._providers[provider]
    
    def _check_rate_limit(self, client_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        return self.rate_limiter.is_allowed(client_id)
    
    def _record_request(self, client_id: Optional[str] = None):
        self.rate_limiter.record_request(client_id)
    
    def process_requirement_sync(
        self,
        user_input: str,
        provider: Optional[LLMProvider] = None,
        client_id: Optional[str] = None,
        save_to_db: bool = True
    ) -> ProcessResult:
        try:
            allowed, reason = self._check_rate_limit(client_id)
            if not allowed:
                self.logger.log_rate_limit(client_id, False, reason)
                return ProcessResult(
                    success=False,
                    error=f"Rate limit exceeded: {reason}"
                )
            
            self._record_request(client_id)
            self.logger.log_rate_limit(client_id, True)
            
            llm_provider = self._get_provider(provider)
            provider_info = llm_provider.get_model_info()
            
            self.logger.log_request(
                provider_info['provider'],
                provider_info['model'],
                user_input,
                client_id
            )
            
            cached_data = self.cache_manager.get(
                user_input,
                provider_info['provider'],
                provider_info['model']
            )
            
            if cached_data:
                self.logger.log_cache_hit(provider_info['provider'], provider_info['model'], len(user_input))
                llm_response = LLMResponse(
                    content=cached_data['content'],
                    model=provider_info['model'],
                    provider=provider_info['provider'],
                    tokens_used=cached_data.get('tokens_used'),
                    response_time=cached_data.get('response_time', 0)
                )
            else:
                self.logger.log_cache_miss(provider_info['provider'], provider_info['model'], len(user_input))
                
                request = LLMRequest(
                    prompt=user_input,
                    system_prompt=RequirementExtractor.SYSTEM_PROMPT
                )
                
                llm_response = llm_provider.generate_sync(request)
                
                if not llm_response.is_success():
                    self.logger.log_response(
                        provider_info['provider'],
                        provider_info['model'],
                        llm_response.response_time or 0,
                        llm_response.tokens_used,
                        False,
                        llm_response.error,
                        client_id
                    )
                    return ProcessResult(
                        success=False,
                        error=f"LLM API error: {llm_response.error}",
                        llm_response=llm_response
                    )
                
                if llm_provider.config.enable_cache:
                    self.cache_manager.set(
                        user_input,
                        provider_info['provider'],
                        provider_info['model'],
                        {
                            'content': llm_response.content,
                            'tokens_used': llm_response.tokens_used,
                            'response_time': llm_response.response_time
                        },
                        ttl=llm_provider.config.cache_ttl
                    )
            
            self.logger.log_response(
                provider_info['provider'],
                provider_info['model'],
                llm_response.response_time or 0,
                llm_response.tokens_used,
                True,
                None,
                client_id
            )
            
            extracted_data = RequirementExtractor.extract_json_from_response(llm_response.content)
            
            if extracted_data is None:
                self.logger.log_extraction(False, ["Failed to extract JSON from LLM response"], [])
                return ProcessResult(
                    success=False,
                    error="Failed to extract JSON from LLM response",
                    raw_response=llm_response.content,
                    llm_response=llm_response
                )
            
            normalized_data = RequirementExtractor.normalize_data(extracted_data)
            validation_result = RequirementExtractor.validate_requirement_data(normalized_data)
            
            self.logger.log_extraction(
                validation_result.is_valid,
                validation_result.errors,
                validation_result.warnings
            )
            
            if not validation_result.is_valid:
                return ProcessResult(
                    success=False,
                    error=f"Validation failed: {', '.join(validation_result.errors)}",
                    raw_response=llm_response.content,
                    structured_data=normalized_data,
                    validation_result=validation_result,
                    llm_response=llm_response,
                    warnings=validation_result.warnings
                )
            
            location_handler_result = self.location_exception_handler.handle_location_validation(
                user_input=user_input,
                llm_response_data=normalized_data,
                conversation_id=client_id,
                user_id=client_id
            )
            
            if not location_handler_result.success:
                if location_handler_result.should_continue:
                    return ProcessResult(
                        success=False,
                        error=location_handler_result.user_message,
                        raw_response=llm_response.content,
                        structured_data=normalized_data,
                        validation_result=validation_result,
                        llm_response=llm_response,
                        warnings=validation_result.warnings,
                        conversation_id=location_handler_result.conversation_id,
                        retry_count=location_handler_result.retry_count,
                        suggestions=location_handler_result.suggestions
                    )
                else:
                    return ProcessResult(
                        success=False,
                        error=location_handler_result.user_message,
                        raw_response=llm_response.content,
                        structured_data=None,
                        validation_result=None,
                        llm_response=llm_response,
                        warnings=None,
                        conversation_id=location_handler_result.conversation_id,
                        retry_count=location_handler_result.retry_count
                    )
            
            requirement_id = None
            
            if save_to_db:
                try:
                    # 将原始用户输入添加到normalized_data中，以便保存到origin_input字段
                    normalized_data['origin_input'] = user_input
                    requirement = RequirementService.create_requirement_from_json(normalized_data)
                    requirement_id = requirement.requirement_id
                    
                    self.logger.log_persistence('create', requirement_id, True)
                except Exception as e:
                    self.logger.log_persistence('create', normalized_data.get('requirement_id'), False, str(e))
                    return ProcessResult(
                        success=False,
                        error=f"Failed to save to database: {str(e)}",
                        raw_response=llm_response.content,
                        structured_data=normalized_data,
                        validation_result=validation_result,
                        llm_response=llm_response,
                        warnings=validation_result.warnings
                    )
            
            return ProcessResult(
                success=True,
                requirement_id=requirement_id,
                raw_response=llm_response.content,
                structured_data=normalized_data,
                validation_result=validation_result,
                llm_response=llm_response,
                warnings=validation_result.warnings
            )
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logger.log_error('processing_error', str(e), {'user_input': user_input[:100]})
            return ProcessResult(
                success=False,
                error=f"Processing error: {str(e)}"
            )
    
    async def process_requirement_async(
        self,
        user_input: str,
        provider: Optional[LLMProvider] = None,
        client_id: Optional[str] = None,
        save_to_db: bool = True
    ) -> ProcessResult:
        try:
            allowed, reason = self._check_rate_limit(client_id)
            if not allowed:
                self.logger.log_rate_limit(client_id, False, reason)
                return ProcessResult(
                    success=False,
                    error=f"Rate limit exceeded: {reason}"
                )
            
            self._record_request(client_id)
            self.logger.log_rate_limit(client_id, True)
            
            llm_provider = self._get_provider(provider)
            provider_info = llm_provider.get_model_info()
            
            self.logger.log_request(
                provider_info['provider'],
                provider_info['model'],
                user_input,
                client_id
            )
            
            cached_data = self.cache_manager.get(
                user_input,
                provider_info['provider'],
                provider_info['model']
            )
            
            if cached_data:
                self.logger.log_cache_hit(provider_info['provider'], provider_info['model'], len(user_input))
                llm_response = LLMResponse(
                    content=cached_data['content'],
                    model=provider_info['model'],
                    provider=provider_info['provider'],
                    tokens_used=cached_data.get('tokens_used'),
                    response_time=cached_data.get('response_time', 0)
                )
            else:
                self.logger.log_cache_miss(provider_info['provider'], provider_info['model'], len(user_input))
                
                request = LLMRequest(
                    prompt=user_input,
                    system_prompt=RequirementExtractor.SYSTEM_PROMPT
                )
                
                llm_response = await llm_provider.generate(request)
                
                if not llm_response.is_success():
                    self.logger.log_response(
                        provider_info['provider'],
                        provider_info['model'],
                        llm_response.response_time or 0,
                        llm_response.tokens_used,
                        False,
                        llm_response.error,
                        client_id
                    )
                    return ProcessResult(
                        success=False,
                        error=f"LLM API error: {llm_response.error}",
                        llm_response=llm_response
                    )
                
                if llm_provider.config.enable_cache:
                    self.cache_manager.set(
                        user_input,
                        provider_info['provider'],
                        provider_info['model'],
                        {
                            'content': llm_response.content,
                            'tokens_used': llm_response.tokens_used,
                            'response_time': llm_response.response_time
                        },
                        ttl=llm_provider.config.cache_ttl
                    )
            
            self.logger.log_response(
                provider_info['provider'],
                provider_info['model'],
                llm_response.response_time or 0,
                llm_response.tokens_used,
                True,
                None,
                client_id
            )
            
            extracted_data = RequirementExtractor.extract_json_from_response(llm_response.content)
            
            if extracted_data is None:
                self.logger.log_extraction(False, ["Failed to extract JSON from LLM response"], [])
                return ProcessResult(
                    success=False,
                    error="Failed to extract JSON from LLM response",
                    raw_response=llm_response.content,
                    llm_response=llm_response
                )
            
            normalized_data = RequirementExtractor.normalize_data(extracted_data)
            validation_result = RequirementExtractor.validate_requirement_data(normalized_data)
            
            self.logger.log_extraction(
                validation_result.is_valid,
                validation_result.errors,
                validation_result.warnings
            )
            
            if not validation_result.is_valid:
                return ProcessResult(
                    success=False,
                    error=f"Validation failed: {', '.join(validation_result.errors)}",
                    raw_response=llm_response.content,
                    structured_data=normalized_data,
                    validation_result=validation_result,
                    llm_response=llm_response,
                    warnings=validation_result.warnings
                )
            
            requirement_id = None
            
            if save_to_db:
                try:
                    # 将原始用户输入添加到normalized_data中，以便保存到origin_input字段
                    normalized_data['origin_input'] = user_input
                    requirement = RequirementService.create_requirement_from_json(normalized_data)
                    requirement_id = requirement.requirement_id
                    
                    self.logger.log_persistence('create', requirement_id, True)
                except Exception as e:
                    self.logger.log_persistence('create', normalized_data.get('requirement_id'), False, str(e))
                    return ProcessResult(
                        success=False,
                        error=f"Failed to save to database: {str(e)}",
                        raw_response=llm_response.content,
                        structured_data=normalized_data,
                        validation_result=validation_result,
                        llm_response=llm_response,
                        warnings=validation_result.warnings
                    )
            
            return ProcessResult(
                success=True,
                requirement_id=requirement_id,
                raw_response=llm_response.content,
                structured_data=normalized_data,
                validation_result=validation_result,
                llm_response=llm_response,
                warnings=validation_result.warnings
            )
            
        except Exception as e:
            self.logger.log_error('processing_error', str(e), {'user_input': user_input[:100]})
            return ProcessResult(
                success=False,
                error=f"Processing error: {str(e)}"
            )
    
    def get_provider_info(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        llm_provider = self._get_provider(provider)
        return llm_provider.get_model_info()
    
    def get_rate_limit_stats(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        return self.rate_limiter.get_stats(client_id)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        return self.cache_manager.get_stats()
    
    def clear_cache(self):
        self.cache_manager.clear()
    
    def reload_configs(self):
        self.config_manager.reload_configs()
        self._providers.clear()
        
        rate_limit_config = self.config_manager.get_rate_limit_config()
        self.rate_limiter = RateLimiter(rate_limit_config)
