from rest_framework import serializers
from typing import Dict, Any


class RequirementProcessSerializer(serializers.Serializer):
    user_input = serializers.CharField(
        required=True,
        max_length=5000,
        help_text="用户的自然语言输入"
    )
    provider = serializers.ChoiceField(
        choices=['deepseek', 'gemini', 'openai'],
        required=False,
        help_text="LLM提供商（可选，默认使用配置的默认提供商）"
    )
    client_id = serializers.CharField(
        required=False,
        max_length=100,
        help_text="客户端ID，用于限流追踪"
    )
    save_to_db = serializers.BooleanField(
        required=False,
        default=True,
        help_text="是否保存到数据库"
    )
    
    def validate_user_input(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("用户输入不能为空")
        return value.strip()


class RequirementResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(help_text="处理是否成功")
    requirement_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="生成的需求ID"
    )
    raw_response = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="LLM原始响应"
    )
    structured_data = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="结构化的需求数据"
    )
    validation_errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="验证错误列表"
    )
    warnings = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="警告列表"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="错误信息"
    )
    llm_info = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="LLM调用信息"
    )
    conversation_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="对话ID，用于追踪多轮对话"
    )
    retry_count = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="重试次数"
    )
    suggestions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="建议列表"
    )


class ProviderInfoSerializer(serializers.Serializer):
    provider = serializers.CharField(help_text="提供商名称")
    model = serializers.CharField(help_text="模型名称")
    api_url = serializers.CharField(help_text="API地址")


class RateLimitStatsSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    requests_per_minute = serializers.IntegerField()
    requests_per_hour = serializers.IntegerField()
    burst_size = serializers.IntegerField()
    current_minute_requests = serializers.IntegerField()
    current_hour_requests = serializers.IntegerField()
    minute_remaining = serializers.IntegerField()
    hour_remaining = serializers.IntegerField()
    client_id = serializers.CharField(required=False, allow_null=True)
    client_minute_requests = serializers.IntegerField(required=False, allow_null=True)
    client_hour_requests = serializers.IntegerField(required=False, allow_null=True)
    client_minute_remaining = serializers.IntegerField(required=False, allow_null=True)
    client_hour_remaining = serializers.IntegerField(required=False, allow_null=True)


class CacheStatsSerializer(serializers.Serializer):
    total_entries = serializers.IntegerField()
    total_hits = serializers.IntegerField()
    cache_size_mb = serializers.FloatField()


class ConfigUpdateSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(
        choices=['deepseek', 'gemini', 'openai'],
        required=True
    )
    api_key = serializers.CharField(required=False, allow_blank=True)
    api_url = serializers.URLField(required=False, allow_blank=True)
    model = serializers.CharField(required=False, allow_blank=True)
    temperature = serializers.FloatField(required=False, min_value=0, max_value=2)
    max_tokens = serializers.IntegerField(required=False, min_value=1, max_value=10000)
    timeout = serializers.IntegerField(required=False, min_value=1, max_value=300)
    enable_cache = serializers.BooleanField(required=False)
    cache_ttl = serializers.IntegerField(required=False, min_value=0)
