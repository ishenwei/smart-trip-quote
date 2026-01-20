import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from services.llm.config import LLMConfig, LLMProvider
from services.llm.base import LLMRequest
from services.llm.providers.deepseek import DeepSeekProvider
from services.llm.providers.gemini import GeminiProvider
from services.llm.providers.openai import OpenAIProvider
from services.llm.factory import ProviderFactory


class TestDeepSeekProvider:
    @pytest.fixture
    def config(self):
        return LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            api_key='test_api_key',
            api_url='https://api.deepseek.com/v1/chat/completions',
            model='deepseek-chat'
        )
    
    @pytest.fixture
    def provider(self, config):
        return DeepSeekProvider(config)
    
    def test_validate_config(self, provider):
        assert provider.validate_config() is True
    
    def test_validate_config_missing_api_key(self):
        config = LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            api_key='',
            api_url='https://api.deepseek.com/v1/chat/completions',
            model='deepseek-chat'
        )
        provider = DeepSeekProvider(config)
        assert provider.validate_config() is False
    
    @patch('services.llm.providers.deepseek.requests.post')
    def test_generate_sync_success(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Test response'
                }
            }],
            'usage': {
                'total_tokens': 100
            }
        }
        mock_post.return_value = mock_response
        
        request = LLMRequest(prompt='Test prompt')
        response = provider.generate_sync(request)
        
        assert response.is_success() is True
        assert response.content == 'Test response'
        assert response.tokens_used == 100
        assert response.provider == 'deepseek'
    
    @patch('services.llm.providers.deepseek.requests.post')
    def test_generate_sync_error(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'
        mock_post.return_value = mock_response
        
        request = LLMRequest(prompt='Test prompt')
        response = provider.generate_sync(request)
        
        assert response.is_success() is False
        assert 'HTTP 500' in response.error
    
    @patch('services.llm.providers.deepseek.requests.post')
    def test_generate_sync_timeout(self, mock_post, provider):
        mock_post.side_effect = Exception('Timeout')
        
        request = LLMRequest(prompt='Test prompt')
        response = provider.generate_sync(request)
        
        assert response.is_success() is False
        assert 'Timeout' in response.error


class TestGeminiProvider:
    @pytest.fixture
    def config(self):
        return LLMConfig(
            provider=LLMProvider.GEMINI,
            api_key='test_api_key',
            api_url='https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            model='gemini-pro'
        )
    
    @pytest.fixture
    def provider(self, config):
        return GeminiProvider(config)
    
    def test_validate_config(self, provider):
        assert provider.validate_config() is True
    
    @patch('services.llm.providers.gemini.requests.post')
    def test_generate_sync_success(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Test response'
                    }]
                }
            }],
            'usageMetadata': {
                'totalTokenCount': 100
            }
        }
        mock_post.return_value = mock_response
        
        request = LLMRequest(prompt='Test prompt')
        response = provider.generate_sync(request)
        
        assert response.is_success() is True
        assert response.content == 'Test response'
        assert response.tokens_used == 100
        assert response.provider == 'gemini'


class TestOpenAIProvider:
    @pytest.fixture
    def config(self):
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key='test_api_key',
            api_url='https://api.openai.com/v1/chat/completions',
            model='gpt-4'
        )
    
    @pytest.fixture
    def provider(self, config):
        return OpenAIProvider(config)
    
    def test_validate_config(self, provider):
        assert provider.validate_config() is True
    
    @patch('services.llm.providers.openai.requests.post')
    def test_generate_sync_success(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Test response'
                }
            }],
            'usage': {
                'total_tokens': 100
            }
        }
        mock_post.return_value = mock_response
        
        request = LLMRequest(prompt='Test prompt')
        response = provider.generate_sync(request)
        
        assert response.is_success() is True
        assert response.content == 'Test response'
        assert response.tokens_used == 100
        assert response.provider == 'openai'


class TestProviderFactory:
    def test_create_deepseek_provider(self):
        config = LLMConfig(
            provider=LLMProvider.DEEPSEEK,
            api_key='test_key',
            api_url='https://api.deepseek.com/v1/chat/completions',
            model='deepseek-chat'
        )
        provider = ProviderFactory.create_provider(config)
        
        assert isinstance(provider, DeepSeekProvider)
        assert provider.provider_name == 'deepseek'
    
    def test_create_gemini_provider(self):
        config = LLMConfig(
            provider=LLMProvider.GEMINI,
            api_key='test_key',
            api_url='https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            model='gemini-pro'
        )
        provider = ProviderFactory.create_provider(config)
        
        assert isinstance(provider, GeminiProvider)
        assert provider.provider_name == 'gemini'
    
    def test_create_openai_provider(self):
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            api_key='test_key',
            api_url='https://api.openai.com/v1/chat/completions',
            model='gpt-4'
        )
        provider = ProviderFactory.create_provider(config)
        
        assert isinstance(provider, OpenAIProvider)
        assert provider.provider_name == 'openai'
    
    def test_unsupported_provider(self):
        config = LLMConfig(
            provider='unsupported',
            api_key='test_key',
            api_url='https://example.com',
            model='test-model'
        )
        
        with pytest.raises(ValueError):
            ProviderFactory.create_provider(config)
    
    def test_get_supported_providers(self):
        providers = ProviderFactory.get_supported_providers()
        
        assert LLMProvider.DEEPSEEK in providers
        assert LLMProvider.GEMINI in providers
        assert LLMProvider.OPENAI in providers
