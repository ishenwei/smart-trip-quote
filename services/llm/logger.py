import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime
from .config import LoggingConfig


class LLMLogger:
    _instance = None
    _logger = None
    _config: Optional[LoggingConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self._config = LoggingConfig()
        self._setup_logger()
    
    def _setup_logger(self):
        self._logger = logging.getLogger('llm_service')
        self._logger.setLevel(getattr(logging, self._config.level.upper()))
        
        formatter = logging.Formatter(self._config.log_format)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        if self._config.log_file:
            file_handler = logging.FileHandler(self._config.log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
    
    def update_config(self, config: LoggingConfig):
        self._config = config
        
        self._logger.handlers.clear()
        self._setup_logger()
    
    def log_request(self, provider: str, model: str, prompt: str, client_id: Optional[str] = None):
        if not self._config.enable_request_logging:
            return
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'llm_request',
            'provider': provider,
            'model': model,
            'client_id': client_id,
            'prompt_length': len(prompt) if prompt else 0,
            'prompt_preview': (prompt[:100] + '...') if (prompt and len(prompt) > 100) else (prompt or '')
        }
        
        self._logger.info(f"LLM Request: {log_data}")
    
    def log_response(self, provider: str, model: str, response_time: float, 
                     tokens_used: Optional[int], success: bool, 
                     error: Optional[str] = None, client_id: Optional[str] = None):
        if not self._config.enable_response_logging:
            return
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'llm_response',
            'provider': provider,
            'model': model,
            'response_time': response_time,
            'tokens_used': tokens_used,
            'success': success,
            'error': error,
            'client_id': client_id
        }
        
        if success:
            self._logger.info(f"LLM Response: {log_data}")
        else:
            self._logger.error(f"LLM Response Error: {log_data}")
    
    def log_extraction(self, success: bool, errors: list, warnings: list):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'data_extraction',
            'success': success,
            'errors_count': len(errors),
            'warnings_count': len(warnings),
            'errors': errors[:5],
            'warnings': warnings[:5]
        }
        
        if success:
            self._logger.info(f"Data Extraction: {log_data}")
        else:
            self._logger.warning(f"Data Extraction Failed: {log_data}")
    
    def log_persistence(self, action: str, requirement_id: str, success: bool, error: Optional[str] = None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'data_persistence',
            'action': action,
            'requirement_id': requirement_id,
            'success': success,
            'error': error
        }
        
        if success:
            self._logger.info(f"Data Persistence: {log_data}")
        else:
            self._logger.error(f"Data Persistence Error: {log_data}")
    
    def log_rate_limit(self, client_id: Optional[str], allowed: bool, reason: Optional[str] = None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'rate_limit_check',
            'client_id': client_id,
            'allowed': allowed,
            'reason': reason
        }
        
        if allowed:
            self._logger.debug(f"Rate Limit: {log_data}")
        else:
            self._logger.warning(f"Rate Limit Blocked: {log_data}")
    
    def log_cache_hit(self, provider: str, model: str, prompt_length: int):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'cache_hit',
            'provider': provider,
            'model': model,
            'prompt_length': prompt_length
        }
        
        self._logger.debug(f"Cache Hit: {log_data}")
    
    def log_cache_miss(self, provider: str, model: str, prompt_length: int):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'cache_miss',
            'provider': provider,
            'model': model,
            'prompt_length': prompt_length
        }
        
        self._logger.debug(f"Cache Miss: {log_data}")
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        self._logger.error(f"Error: {log_data}")
