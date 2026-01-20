import pytest
from services.llm.security import SecurityManager


class TestSecurityManager:
    
    @pytest.fixture
    def security_manager(self):
        return SecurityManager()
    
    def test_mask_api_key(self, security_manager):
        api_key = 'sk-test-api-key-1234567890'
        
        masked = security_manager.mask_api_key(api_key, visible_chars=4)
        
        assert masked == 'sk-t*******************'
    
    def test_mask_api_key_short_key(self, security_manager):
        api_key = 'abc'
        
        masked = security_manager.mask_api_key(api_key, visible_chars=4)
        
        assert masked == '***'
    
    def test_mask_api_key_default_visible_chars(self, security_manager):
        api_key = 'sk-test-api-key-1234567890'
        
        masked = security_manager.mask_api_key(api_key)
        
        assert masked.startswith('sk-')
        assert '*' in masked
        assert len(masked) == len(api_key)
    
    def test_hash_sensitive_data(self, security_manager):
        data = 'sensitive_password_123'
        
        hashed = security_manager.hash_sensitive_data(data)
        
        assert len(hashed) == 64
        assert hashed != data
    
    def test_hash_sensitive_data_consistency(self, security_manager):
        data = 'test_data'
        
        hash1 = security_manager.hash_sensitive_data(data)
        hash2 = security_manager.hash_sensitive_data(data)
        
        assert hash1 == hash2
    
    def test_validate_api_key_format_openai(self, security_manager):
        valid_key = 'sk-proj-abc123def456'
        invalid_key = 'invalid-key'
        
        assert security_manager.validate_api_key_format(valid_key, 'openai') is True
        assert security_manager.validate_api_key_format(invalid_key, 'openai') is False
    
    def test_validate_api_key_format_deepseek(self, security_manager):
        valid_key = 'sk-abc123def456'
        invalid_key = 'invalid-key'
        
        assert security_manager.validate_api_key_format(valid_key, 'deepseek') is True
        assert security_manager.validate_api_key_format(invalid_key, 'deepseek') is False
    
    def test_validate_api_key_format_gemini(self, security_manager):
        valid_key = 'AIzaSyD-very-long-api-key-here'
        invalid_key = 'short'
        
        assert security_manager.validate_api_key_format(valid_key, 'gemini') is True
        assert security_manager.validate_api_key_format(invalid_key, 'gemini') is False
    
    def test_sanitize_log_data(self, security_manager):
        data = {
            'username': 'test_user',
            'api_key': 'sk-secret-key-123',
            'password': 'secret123',
            'normal_field': 'normal_value'
        }
        
        sanitized = security_manager.sanitize_log_data(data)
        
        assert sanitized['username'] == 'test_user'
        assert sanitized['normal_field'] == 'normal_value'
        assert 'sk-' in sanitized['api_key']
        assert '*' in sanitized['api_key']
        assert '*' in sanitized['password']
        assert sanitized['api_key'] != 'sk-secret-key-123'
        assert sanitized['password'] != 'secret123'
    
    def test_sanitize_log_data_nested(self, security_manager):
        data = {
            'user': {
                'name': 'test',
                'api_key': 'sk-secret'
            },
            'token': 'secret-token'
        }
        
        sanitized = security_manager.sanitize_log_data(data)
        
        assert '*' in sanitized['user']['api_key']
        assert '*' in sanitized['token']
    
    def test_cache_api_key(self, security_manager):
        provider = 'openai'
        api_key = 'sk-test-key'
        
        security_manager.cache_api_key(provider, api_key)
        
        cached = security_manager.get_cached_api_key(provider)
        
        assert cached == api_key
    
    def test_get_cached_api_key_not_found(self, security_manager):
        cached = security_manager.get_cached_api_key('nonexistent')
        
        assert cached is None
    
    def test_clear_cache(self, security_manager):
        security_manager.cache_api_key('openai', 'sk-key1')
        security_manager.cache_api_key('deepseek', 'sk-key2')
        
        security_manager.clear_cache()
        
        assert security_manager.get_cached_api_key('openai') is None
        assert security_manager.get_cached_api_key('deepseek') is None
