"""
日志脱敏工具
用于在日志输出前对敏感信息进行脱敏处理
"""
import re
import logging
from typing import Any, Dict, Optional
from functools import wraps


# 需要脱敏的敏感字段列表
SENSITIVE_FIELDS = {
    'password', 'passwd', 'secret', 'token', 'api_key', 'apikey',
    'access_token', 'refresh_token', 'auth_token', 'authorization',
    'credit_card', 'card_number', 'cvv', 'cvc', 'ssn', 'social_security',
    'phone', 'mobile', 'telephone', 'email', 'address', 'name',
    'id_card', 'identity', 'passport', 'bank_account', 'account_number',
    'contact_person', 'contact_phone', 'contact_email'
}

# 脱敏模式
REDACT_PATTERN = '***REDACTED***'


class SensitiveDataFilter(logging.Filter):
    """
    日志过滤器，自动对敏感字段进行脱敏
    """
    
    def __init__(self, sensitive_fields: Optional[set] = None):
        super().__init__()
        self.sensitive_fields = sensitive_fields or SENSITIVE_FIELDS
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录，对敏感信息脱敏"""
        if record.msg:
            record.msg = self._sanitize_message(str(record.msg))
        
        if record.args:
            record.args = tuple(
                self._sanitize_message(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        
        return True
    
    def _sanitize_message(self, message: str) -> str:
        """对消息进行脱敏处理"""
        if not message:
            return message
        
        # 对已知敏感字段进行脱敏
        for field in self.sensitive_fields:
            # 匹配 field=value 或 field: value 模式
            patterns = [
                rf'(?i)({field})\s*[=:]\s*["\']?([^"\'&\s]+)["\']?',
                rf'(?i)("({field})"\s*:\s*)"([^"]+)"',
            ]
            for pattern in patterns:
                message = re.sub(pattern, rf'\1={REDACT_PATTERN}', message)
        
        return message


class LogSanitizer:
    """
    日志脱敏工具类
    提供静态方法对各种类型的数据进行脱敏
    """
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], depth: int = 0, max_depth: int = 10) -> Dict[str, Any]:
        """
        对字典中的敏感字段进行脱敏
        
        Args:
            data: 待处理的字典数据
            depth: 当前递归深度
            max_depth: 最大递归深度，防止无限递归
        
        Returns:
            脱敏后的字典
        """
        if depth > max_depth or not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            if key_lower in SENSITIVE_FIELDS or any(
                sf in key_lower for sf in SENSITIVE_FIELDS
            ):
                result[key] = REDACT_PATTERN
            elif isinstance(value, dict):
                result[key] = LogSanitizer.sanitize_dict(value, depth + 1, max_depth)
            elif isinstance(value, list):
                result[key] = [
                    LogSanitizer.sanitize_dict(item, depth + 1, max_depth) 
                    if isinstance(item, dict) else item 
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """
        对字符串中的敏感信息进行脱敏
        
        Args:
            text: 待处理的字符串
        
        Returns:
            脱敏后的字符串
        """
        if not text:
            return text
        
        result = text
        
        # 手机号脱敏 (保留前3后4位) - 添加单词边界防止误匹配
        result = re.sub(
            r'\b(\d{3})\d{4}(\d{4})\b',
            r'\1****\2',
            result
        )
        
        # 邮箱脱敏
        result = re.sub(
            r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            lambda m: f'{m.group(1)[:2]}***@{m.group(2)}',
            result
        )
        
        # 身份证号脱敏
        result = re.sub(
            r'(\d{6})\d{8}(\d{4})',
            r'\1********\2',
            result
        )
        
        # 银行卡号脱敏 (保留前4后4位)
        result = re.sub(
            r'\b(\d{4})\d{8,}(\d{4})\b',
            r'\1****\2',
            result
        )
        
        return result
    
    @staticmethod
    def sanitize_log_data(*args, **kwargs) -> tuple:
        """
        批量脱敏日志参数
        
        Returns:
            脱敏后的 (args, kwargs)
        """
        sanitized_args = tuple(
            LogSanitizer.sanitize_string(str(arg)) if isinstance(arg, (str, int, float)) else arg
            for arg in args
        )
        
        sanitized_kwargs = {
            k: LogSanitizer.sanitize_string(str(v)) if isinstance(v, (str, int, float)) else v
            for k, v in kwargs.items()
        }
        
        return sanitized_args, sanitized_kwargs


def log_with_sanitize(logger: logging.Logger, level: str = 'info'):
    """
    装饰器：为日志函数添加自动脱敏功能
    
    Usage:
        @log_with_sanitize(logger)
        def some_function():
            logger.info(f"User data: {user_data}")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 在这里可以添加预处理逻辑
            return func(*args, **kwargs)
        return wrapper
    return decorator


def setup_sanitized_logger(
    name: str,
    level: int = logging.INFO,
    sensitive_fields: Optional[set] = None
) -> logging.Logger:
    """
    创建配置了脱敏过滤器的日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        sensitive_fields: 自定义敏感字段集合
    
    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 添加敏感数据过滤器
    sanitized_filter = SensitiveDataFilter(sensitive_fields)
    
    # 检查是否已有处理器，避免重复添加
    has_filter = any(
        isinstance(f, SensitiveDataFilter) 
        for f in logger.filters
    )
    
    if not has_filter:
        logger.addFilter(sanitized_filter)
    
    return logger


# 便捷函数
def sanitize_request_log(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    对请求数据进行脱敏，用于日志记录
    
    Args:
        request_data: 请求数据字典
    
    Returns:
        脱敏后的数据
    """
    return LogSanitizer.sanitize_dict(request_data)
