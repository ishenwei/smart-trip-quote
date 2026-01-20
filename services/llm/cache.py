import json
import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheManager:
    _instance = None
    _cache: Dict[str, Dict[str, Any]] = {}
    _lock = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        import threading
        self._lock = threading.Lock()
    
    def _generate_key(self, prompt: str, provider: str, model: str, **kwargs) -> str:
        key_data = {
            'prompt': prompt,
            'provider': provider,
            'model': model,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, provider: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        key = self._generate_key(prompt, provider, model, **kwargs)
        
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if entry['expires_at'] > time.time():
                    entry['hits'] += 1
                    entry['last_accessed'] = time.time()
                    return entry['data']
                else:
                    del self._cache[key]
        
        return None
    
    def set(self, prompt: str, provider: str, model: str, data: Dict[str, Any], ttl: int = 3600, **kwargs):
        key = self._generate_key(prompt, provider, model, **kwargs)
        
        with self._lock:
            self._cache[key] = {
                'data': data,
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'hits': 0,
                'last_accessed': time.time()
            }
    
    def delete(self, prompt: str, provider: str, model: str, **kwargs):
        key = self._generate_key(prompt, provider, model, **kwargs)
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        now = time.time()
        
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry['expires_at'] <= now
            ]
            
            for key in expired_keys:
                del self._cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_entries = len(self._cache)
            total_hits = sum(entry['hits'] for entry in self._cache.values())
            
            return {
                'total_entries': total_entries,
                'total_hits': total_hits,
                'cache_size_mb': sum(len(str(entry)) for entry in self._cache.values()) / (1024 * 1024)
            }
