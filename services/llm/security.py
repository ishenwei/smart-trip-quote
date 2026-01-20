import hashlib
import os
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64


class SecurityManager:
    _instance = None
    _fernet = None
    _api_keys_cache: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if encryption_key:
            try:
                key_bytes = base64.urlsafe_b64decode(encryption_key.encode())
                self._fernet = Fernet(key_bytes)
            except Exception as e:
                print(f"Failed to initialize encryption: {e}")
                self._fernet = None
        else:
            self._fernet = None
    
    def encrypt_api_key(self, api_key: str) -> str:
        if not self._fernet:
            return api_key
        
        try:
            encrypted = self._fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            print(f"Encryption failed: {e}")
            return api_key
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        if not self._fernet:
            return encrypted_key
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption failed: {e}")
            return encrypted_key
    
    def hash_sensitive_data(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
    
    def mask_api_key(self, api_key: str, visible_chars: int = 4) -> str:
        if not api_key or len(api_key) <= visible_chars:
            return '*' * len(api_key)
        
        return api_key[:visible_chars] + '*' * (len(api_key) - visible_chars)
    
    def validate_api_key_format(self, api_key: str, provider: str) -> bool:
        if not api_key:
            return False
        
        provider_patterns = {
            'openai': lambda k: k.startswith('sk-') and len(k) > 20,
            'deepseek': lambda k: k.startswith('sk-') and len(k) > 20,
            'gemini': lambda k: len(k) > 20
        }
        
        validator = provider_patterns.get(provider.lower())
        if validator:
            return validator(api_key)
        
        return len(api_key) > 10
    
    def sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = data.copy()
        
        sensitive_keys = [
            'api_key', 'apikey', 'password', 'token', 'secret',
            'authorization', 'auth_token', 'access_token'
        ]
        
        for key in list(sanitized.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(sanitized[key], str):
                    sanitized[key] = self.mask_api_key(sanitized[key])
        
        return sanitized
    
    def cache_api_key(self, provider: str, api_key: str):
        self._api_keys_cache[provider] = api_key
    
    def get_cached_api_key(self, provider: str) -> Optional[str]:
        return self._api_keys_cache.get(provider)
    
    def clear_cache(self):
        self._api_keys_cache.clear()
