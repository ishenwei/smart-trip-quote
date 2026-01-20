import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class LLMProvider(Enum):
    DEEPSEEK = 'deepseek'
    GEMINI = 'gemini'
    OPENAI = 'openai'


@dataclass
class LLMConfig:
    provider: LLMProvider
    api_key: str
    api_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_cache: bool = True
    cache_ttl: int = 3600
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'provider': self.provider.value,
            'api_url': self.api_url,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'enable_cache': self.enable_cache,
            'cache_ttl': self.cache_ttl
        }


@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10
    enabled: bool = True


@dataclass
class LoggingConfig:
    level: str = 'INFO'
    log_file: Optional[str] = None
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    enable_request_logging: bool = True
    enable_response_logging: bool = True


class ConfigManager:
    _instance = None
    _configs: Dict[LLMProvider, LLMConfig] = {}
    _rate_limit_config: RateLimitConfig = RateLimitConfig()
    _logging_config: LoggingConfig = LoggingConfig()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_configs()
        return cls._instance
    
    def _load_configs(self):
        config_file = Path(os.getenv('LLM_CONFIG_FILE', 'config/llm_config.json'))
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self._parse_configs(config_data)
        else:
            self._load_env_configs()
    
    def _parse_configs(self, config_data: Dict[str, Any]):
        providers_config = config_data.get('providers', {})
        
        for provider_name, provider_config in providers_config.items():
            try:
                provider = LLMProvider(provider_name)
                self._configs[provider] = LLMConfig(
                    provider=provider,
                    api_key=provider_config['api_key'],
                    api_url=provider_config['api_url'],
                    model=provider_config['model'],
                    temperature=provider_config.get('temperature', 0.7),
                    max_tokens=provider_config.get('max_tokens', 2000),
                    timeout=provider_config.get('timeout', 30),
                    max_retries=provider_config.get('max_retries', 3),
                    retry_delay=provider_config.get('retry_delay', 1.0),
                    enable_cache=provider_config.get('enable_cache', True),
                    cache_ttl=provider_config.get('cache_ttl', 3600)
                )
            except (ValueError, KeyError) as e:
                print(f"Failed to load config for provider {provider_name}: {e}")
        
        rate_limit_data = config_data.get('rate_limit', {})
        self._rate_limit_config = RateLimitConfig(
            requests_per_minute=rate_limit_data.get('requests_per_minute', 60),
            requests_per_hour=rate_limit_data.get('requests_per_hour', 1000),
            burst_size=rate_limit_data.get('burst_size', 10),
            enabled=rate_limit_data.get('enabled', True)
        )
        
        logging_data = config_data.get('logging', {})
        self._logging_config = LoggingConfig(
            level=logging_data.get('level', 'INFO'),
            log_file=logging_data.get('log_file'),
            log_format=logging_data.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            enable_request_logging=logging_data.get('enable_request_logging', True),
            enable_response_logging=logging_data.get('enable_response_logging', True)
        )
    
    def _load_env_configs(self):
        deepseek_config = LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            api_key=os.getenv('DEEPSEEK_API_KEY', ''),
            api_url=os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions'),
            model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
        )
        
        gemini_config = LLMConfig(
            provider=LLMProvider.GEMINI,
            api_key=os.getenv('GEMINI_API_KEY', ''),
            api_url=os.getenv('GEMINI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'),
            model=os.getenv('GEMINI_MODEL', 'gemini-pro')
        )
        
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key=os.getenv('OPENAI_API_KEY', ''),
            api_url=os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4')
        )
        
        self._configs = {
            LLMProvider.DEEPSEEK: deepseek_config,
            LLMProvider.GEMINI: gemini_config,
            LLMProvider.OPENAI: openai_config
        }
    
    def get_config(self, provider: LLMProvider) -> Optional[LLMConfig]:
        return self._configs.get(provider)
    
    def set_config(self, config: LLMConfig):
        self._configs[config.provider] = config
    
    def get_rate_limit_config(self) -> RateLimitConfig:
        return self._rate_limit_config
    
    def set_rate_limit_config(self, config: RateLimitConfig):
        self._rate_limit_config = config
    
    def get_logging_config(self) -> LoggingConfig:
        return self._logging_config
    
    def set_logging_config(self, config: LoggingConfig):
        self._logging_config = config
    
    def get_available_providers(self) -> list[LLMProvider]:
        return [p for p, config in self._configs.items() if config.api_key]
    
    def get_default_provider(self) -> Optional[LLMProvider]:
        providers = self.get_available_providers()
        return providers[0] if providers else None
    
    def reload_configs(self):
        self._load_configs()
