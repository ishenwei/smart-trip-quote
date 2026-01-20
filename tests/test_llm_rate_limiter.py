import pytest
import time
from services.llm.config import RateLimitConfig
from services.llm.rate_limiter import RateLimiter


class TestRateLimiter:
    
    @pytest.fixture
    def config(self):
        return RateLimitConfig(
            requests_per_minute=10,
            requests_per_hour=100,
            burst_size=5,
            enabled=True
        )
    
    @pytest.fixture
    def limiter(self, config):
        return RateLimiter(config)
    
    def test_is_allowed_when_enabled(self, limiter):
        allowed, reason = limiter.is_allowed()
        
        assert allowed is True
        assert reason is None
    
    def test_is_allowed_when_disabled(self):
        config = RateLimitConfig(enabled=False)
        limiter = RateLimiter(config)
        
        allowed, reason = limiter.is_allowed()
        
        assert allowed is True
    
    def test_record_request(self, limiter):
        limiter.record_request()
        
        stats = limiter.get_stats()
        assert stats['current_minute_requests'] == 1
        assert stats['current_hour_requests'] == 1
    
    def test_rate_limit_per_minute(self, limiter):
        for _ in range(10):
            limiter.record_request()
        
        allowed, reason = limiter.is_allowed()
        
        assert allowed is False
        assert 'per minute' in reason
    
    def test_rate_limit_per_hour(self):
        config = RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=10,
            burst_size=5,
            enabled=True
        )
        limiter = RateLimiter(config)
        
        for _ in range(10):
            limiter.record_request()
        
        allowed, reason = limiter.is_allowed()
        
        assert allowed is False
        assert 'per hour' in reason
    
    def test_burst_rate_limit(self):
        config = RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=1000,
            burst_size=3,
            enabled=True
        )
        limiter = RateLimiter(config)
        
        for _ in range(3):
            limiter.record_request()
        
        allowed, reason = limiter.is_allowed()
        
        assert allowed is False
        assert 'burst' in reason.lower()
    
    def test_client_specific_rate_limiting(self, limiter):
        client_id = 'test_client'
        
        for _ in range(10):
            limiter.record_request(client_id)
        
        allowed, reason = limiter.is_allowed(client_id)
        
        assert allowed is False
        assert 'per minute' in reason
    
    def test_different_clients_separate_limits(self, limiter):
        client1 = 'client1'
        client2 = 'client2'
        
        for _ in range(10):
            limiter.record_request(client1)
        
        allowed1, _ = limiter.is_allowed(client1)
        allowed2, _ = limiter.is_allowed(client2)
        
        assert allowed1 is False
        assert allowed2 is True
    
    def test_get_stats(self, limiter):
        limiter.record_request()
        limiter.record_request()
        
        stats = limiter.get_stats()
        
        assert stats['enabled'] is True
        assert stats['requests_per_minute'] == 10
        assert stats['requests_per_hour'] == 100
        assert stats['burst_size'] == 5
        assert stats['current_minute_requests'] == 2
        assert stats['current_hour_requests'] == 2
        assert stats['minute_remaining'] == 8
        assert stats['hour_remaining'] == 98
    
    def test_get_stats_with_client_id(self, limiter):
        client_id = 'test_client'
        limiter.record_request(client_id)
        
        stats = limiter.get_stats(client_id)
        
        assert stats['client_id'] == client_id
        assert stats['client_minute_requests'] == 1
        assert stats['client_hour_requests'] == 1
        assert stats['client_minute_remaining'] == 9
        assert stats['client_hour_remaining'] == 99
    
    def test_reset(self, limiter):
        limiter.record_request()
        limiter.record_request()
        
        limiter.reset()
        
        stats = limiter.get_stats()
        assert stats['current_minute_requests'] == 0
        assert stats['current_hour_requests'] == 0
    
    def test_cleanup_old_requests(self, limiter):
        limiter.record_request()
        time.sleep(1.1)
        
        stats = limiter.get_stats()
        assert stats['current_minute_requests'] == 0
