import time
import threading
from collections import deque, defaultdict
from typing import Optional
from datetime import datetime, timedelta
from .config import RateLimitConfig


class RateLimiter:
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests_per_minute = config.requests_per_minute
        self._requests_per_hour = config.requests_per_hour
        self._burst_size = config.burst_size
        self._enabled = config.enabled
        
        self._minute_requests = deque()
        self._hour_requests = deque()
        self._lock = threading.Lock()
        
        self._client_minute_requests = defaultdict(deque)
        self._client_hour_requests = defaultdict(deque)
        self._client_lock = threading.Lock()
    
    def is_allowed(self, client_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if not self._enabled:
            return True, None
        
        now = time.time()
        
        with self._lock:
            self._cleanup_old_requests(now)
            
            if len(self._minute_requests) >= self._requests_per_minute:
                return False, f"Rate limit exceeded: {self._requests_per_minute} requests per minute"
            
            if len(self._hour_requests) >= self._requests_per_hour:
                return False, f"Rate limit exceeded: {self._requests_per_hour} requests per hour"
            
            if len(self._minute_requests) - len([t for t in self._minute_requests if now - t < 1]) >= self._burst_size:
                return False, f"Burst rate limit exceeded: {self._burst_size} requests per second"
        
        if client_id:
            with self._client_lock:
                self._cleanup_client_requests(client_id, now)
                
                client_minute = self._client_minute_requests[client_id]
                client_hour = self._client_hour_requests[client_id]
                
                if len(client_minute) >= self._requests_per_minute:
                    return False, f"Client rate limit exceeded: {self._requests_per_minute} requests per minute"
                
                if len(client_hour) >= self._requests_per_hour:
                    return False, f"Client rate limit exceeded: {self._requests_per_hour} requests per hour"
        
        return True, None
    
    def record_request(self, client_id: Optional[str] = None):
        if not self._enabled:
            return
        
        now = time.time()
        
        with self._lock:
            self._minute_requests.append(now)
            self._hour_requests.append(now)
        
        if client_id:
            with self._client_lock:
                self._client_minute_requests[client_id].append(now)
                self._client_hour_requests[client_id].append(now)
    
    def _cleanup_old_requests(self, now: float):
        minute_ago = now - 60
        hour_ago = now - 3600
        
        while self._minute_requests and self._minute_requests[0] < minute_ago:
            self._minute_requests.popleft()
        
        while self._hour_requests and self._hour_requests[0] < hour_ago:
            self._hour_requests.popleft()
    
    def _cleanup_client_requests(self, client_id: str, now: float):
        minute_ago = now - 60
        hour_ago = now - 3600
        
        client_minute = self._client_minute_requests[client_id]
        client_hour = self._client_hour_requests[client_id]
        
        while client_minute and client_minute[0] < minute_ago:
            client_minute.popleft()
        
        while client_hour and client_hour[0] < hour_ago:
            client_hour.popleft()
    
    def get_stats(self, client_id: Optional[str] = None) -> dict:
        now = time.time()
        
        with self._lock:
            self._cleanup_old_requests(now)
            
            stats = {
                'enabled': self._enabled,
                'requests_per_minute': self._requests_per_minute,
                'requests_per_hour': self._requests_per_hour,
                'burst_size': self._burst_size,
                'current_minute_requests': len(self._minute_requests),
                'current_hour_requests': len(self._hour_requests),
                'minute_remaining': self._requests_per_minute - len(self._minute_requests),
                'hour_remaining': self._requests_per_hour - len(self._hour_requests)
            }
        
        if client_id:
            with self._client_lock:
                self._cleanup_client_requests(client_id, now)
                
                client_minute = self._client_minute_requests[client_id]
                client_hour = self._client_hour_requests[client_id]
                
                stats.update({
                    'client_id': client_id,
                    'client_minute_requests': len(client_minute),
                    'client_hour_requests': len(client_hour),
                    'client_minute_remaining': self._requests_per_minute - len(client_minute),
                    'client_hour_remaining': self._requests_per_hour - len(client_hour)
                })
        
        return stats
    
    def reset(self):
        with self._lock:
            self._minute_requests.clear()
            self._hour_requests.clear()
        
        with self._client_lock:
            self._client_minute_requests.clear()
            self._client_hour_requests.clear()
