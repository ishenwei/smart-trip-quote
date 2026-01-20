from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Dict, Any

from services.llm.service import LLMRequirementService, ProcessResult
from services.llm.config import LLMProvider
from apps.api.serializers.llm_serializer import (
    RequirementProcessSerializer,
    RequirementResponseSerializer,
    ProviderInfoSerializer,
    RateLimitStatsSerializer,
    CacheStatsSerializer,
    ConfigUpdateSerializer
)


class ProcessRequirementView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="处理用户的自然语言旅游需求输入，通过LLM转换为结构化数据",
        request_body=RequirementProcessSerializer,
        responses={
            200: RequirementResponseSerializer,
            400: "请求参数错误",
            429: "请求过于频繁",
            500: "服务器内部错误"
        },
        tags=['LLM服务']
    )
    def post(self, request):
        serializer = RequirementProcessSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': 'Invalid request data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        user_input = data['user_input']
        provider_name = data.get('provider')
        client_id = data.get('client_id')
        save_to_db = data.get('save_to_db', True)
        
        try:
            provider = LLMProvider(provider_name) if provider_name else None
        except ValueError:
            return Response(
                {'success': False, 'error': f'Invalid provider: {provider_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = LLMRequirementService()
        result = service.process_requirement_sync(
            user_input=user_input,
            provider=provider,
            client_id=client_id,
            save_to_db=save_to_db
        )
        
        response_data = {
            'success': result.success,
            'requirement_id': result.requirement_id,
            'raw_response': result.raw_response,
            'structured_data': result.structured_data,
            'validation_errors': result.validation_result.errors if result.validation_result else None,
            'warnings': result.warnings,
            'error': result.error
        }
        
        if result.llm_response:
            response_data['llm_info'] = {
                'provider': result.llm_response.provider,
                'model': result.llm_response.model,
                'tokens_used': result.llm_response.tokens_used,
                'response_time': result.llm_response.response_time
            }
        
        if result.conversation_id:
            response_data['conversation_id'] = result.conversation_id
        
        if result.retry_count > 0:
            response_data['retry_count'] = result.retry_count
        
        if result.suggestions:
            response_data['suggestions'] = result.suggestions
        
        http_status = status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST
        
        return Response(response_data, status=http_status)


class ProviderInfoView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="获取当前LLM提供商信息",
        manual_parameters=[
            openapi.Parameter(
                'provider',
                openapi.IN_QUERY,
                description="提供商名称（可选）",
                type=openapi.TYPE_STRING,
                enum=['deepseek', 'gemini', 'openai']
            )
        ],
        responses={
            200: ProviderInfoSerializer,
            400: "请求参数错误",
            404: "提供商未配置"
        },
        tags=['LLM服务']
    )
    def get(self, request):
        provider_name = request.query_params.get('provider')
        
        try:
            provider = LLMProvider(provider_name) if provider_name else None
        except ValueError:
            return Response(
                {'error': f'Invalid provider: {provider_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = LLMRequirementService()
            provider_info = service.get_provider_info(provider)
            
            return Response(provider_info, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )


class RateLimitStatsView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="获取限流统计信息",
        manual_parameters=[
            openapi.Parameter(
                'client_id',
                openapi.IN_QUERY,
                description="客户端ID（可选）",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: RateLimitStatsSerializer
        },
        tags=['LLM服务']
    )
    def get(self, request):
        client_id = request.query_params.get('client_id')
        
        service = LLMRequirementService()
        stats = service.get_rate_limit_stats(client_id)
        
        return Response(stats, status=status.HTTP_200_OK)


class CacheStatsView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="获取缓存统计信息",
        responses={
            200: CacheStatsSerializer
        },
        tags=['LLM服务']
    )
    def get(self, request):
        service = LLMRequirementService()
        stats = service.get_cache_stats()
        
        return Response(stats, status=status.HTTP_200_OK)


class ClearCacheView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="清除LLM响应缓存",
        responses={
            200: "缓存已清除"
        },
        tags=['LLM服务']
    )
    def post(self, request):
        service = LLMRequirementService()
        service.clear_cache()
        
        return Response(
            {'message': 'Cache cleared successfully'},
            status=status.HTTP_200_OK
        )


class ReloadConfigView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="重新加载配置文件",
        responses={
            200: "配置已重新加载"
        },
        tags=['LLM服务']
    )
    def post(self, request):
        service = LLMRequirementService()
        service.reload_configs()
        
        return Response(
            {'message': 'Configuration reloaded successfully'},
            status=status.HTTP_200_OK
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="健康检查",
        responses={
            200: "服务正常"
        },
        tags=['LLM服务']
    )
    def get(self, request):
        from services.llm.config import ConfigManager
        
        config_manager = ConfigManager()
        available_providers = config_manager.get_available_providers()
        
        return Response({
            'status': 'healthy',
            'available_providers': [p.value for p in available_providers],
            'default_provider': config_manager.get_default_provider().value if config_manager.get_default_provider() else None
        }, status=status.HTTP_200_OK)
