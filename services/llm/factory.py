from typing import Optional
from .base import BaseLLMProvider
from .config import LLMConfig, LLMProvider
from .providers.deepseek import DeepSeekProvider
from .providers.gemini import GeminiProvider
from .providers.openai import OpenAIProvider


class ProviderFactory:
    _providers = {
        LLMProvider.DEEPSEEK: DeepSeekProvider,
        LLMProvider.GEMINI: GeminiProvider,
        LLMProvider.OPENAI: OpenAIProvider
    }
    
    @classmethod
    def create_provider(cls, config: LLMConfig) -> Optional[BaseLLMProvider]:
        provider_class = cls._providers.get(config.provider)
        
        if provider_class is None:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        provider = provider_class(config)
        
        if not provider.validate_config():
            raise ValueError(f"Invalid configuration for provider: {config.provider}")
        
        return provider
    
    @classmethod
    def register_provider(cls, provider: LLMProvider, provider_class: type):
        cls._providers[provider] = provider_class
    
    @classmethod
    def get_supported_providers(cls) -> list[LLMProvider]:
        return list(cls._providers.keys())
