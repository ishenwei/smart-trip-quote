from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from typing import Dict, Any

from services.llm.service import LLMRequirementService, ProcessResult
from services.llm.config import LLMProvider


class ProcessRequirementView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_input = request.data.get('user_input')
        provider_name = request.data.get('provider')
        client_id = request.data.get('client_id')
        save_to_db = request.data.get('save_to_db', True)
        
        if not user_input:
            return Response(
                {'success': False, 'error': 'user_input is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provider = LLMProvider(provider_name) if provider_name else None
        except ValueError:
            return Response(
                {'success': False, 'error': f'Invalid provider: {provider_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
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
            
            http_status = status.HTTP_200_OK if result.success else status.HTTP_400_BAD_REQUEST
            
            return Response(response_data, status=http_status)
            
        except Exception as e:
            return Response(
                {'success': False, 'error': f'Processing error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProviderInfoView(APIView):
    permission_classes = [AllowAny]
    
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
    
    def get(self, request):
        client_id = request.query_params.get('client_id')
        
        service = LLMRequirementService()
        stats = service.get_rate_limit_stats(client_id)
        
        return Response(stats, status=status.HTTP_200_OK)


class CacheStatsView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        service = LLMRequirementService()
        stats = service.get_cache_stats()
        
        return Response(stats, status=status.HTTP_200_OK)


class ClearCacheView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        service = LLMRequirementService()
        service.clear_cache()
        
        return Response(
            {'message': 'Cache cleared successfully'},
            status=status.HTTP_200_OK
        )


class ReloadConfigView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        service = LLMRequirementService()
        service.reload_configs()
        
        return Response(
            {'message': 'Configuration reloaded successfully'},
            status=status.HTTP_200_OK
        )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        from services.llm.config import ConfigManager
        
        config_manager = ConfigManager()
        available_providers = config_manager.get_available_providers()
        
        return Response({
            'status': 'healthy',
            'available_providers': [p.value for p in available_providers],
            'default_provider': config_manager.get_default_provider().value if config_manager.get_default_provider() else None
        }, status=status.HTTP_200_OK)
