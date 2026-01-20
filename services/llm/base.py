from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def is_success(self) -> bool:
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'model': self.model,
            'provider': self.provider,
            'tokens_used': self.tokens_used,
            'response_time': self.response_time,
            'raw_response': self.raw_response,
            'error': self.error
        }


@dataclass
class LLMRequest:
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    additional_params: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'prompt': self.prompt,
            'system_prompt': self.system_prompt
        }
        
        if self.temperature is not None:
            result['temperature'] = self.temperature
        if self.max_tokens is not None:
            result['max_tokens'] = self.max_tokens
        if self.additional_params:
            result.update(self.additional_params)
        
        return result


class BaseLLMProvider(ABC):
    def __init__(self, config):
        self.config = config
        self.provider_name = config.provider.value
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            'provider': self.provider_name,
            'model': self.config.model,
            'api_url': self.config.api_url
        }
    
    def _prepare_messages(self, request: LLMRequest) -> list:
        messages = []
        
        if request.system_prompt:
            messages.append({
                'role': 'system',
                'content': request.system_prompt
            })
        
        messages.append({
            'role': 'user',
            'content': request.prompt
        })
        
        return messages
