from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.models.itinerary import Itinerary

from apps.api.serializers.webhook_serializers import (
    ItineraryWebhookSerializer,
    RequirementWebhookSerializer,
    ItineraryOptimizationCallbackSerializer,
    ItineraryQuoteCallbackSerializer,
    N8nProcessRequirementSerializer,
)
from apps.api.services.webhook_services import (
    ItineraryService,
    RequirementService,
    ItineraryOptimizationService,
    N8nIntegrationService,
)
from apps.api.utils.logging_utils import LogSanitizer, sanitize_request_log

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ItineraryWebhookView(View):
    """处理n8n webhook返回的行程数据"""
    
    def post(self, request, *args, **kwargs):
        """接收并处理webhook数据"""
        try:
            logger.info('接收到来自n8n的webhook请求')
            
            content = request.body.decode('utf-8')
            logger.info(f'请求内容长度: {len(content)}')
            
            data = json.loads(content)
            logger.info(f'解析后的数据类型: {type(data)}')
            
            if 'output' in data:
                logger.info('发现output字段，使用其内部数据')
                data = data['output']
            
            serializer = ItineraryWebhookSerializer(data=data)
            if not serializer.is_valid():
                errors = serializer.errors
                logger.error(f'数据验证失败: {errors}')
                return JsonResponse({
                    'success': False,
                    'error': '数据验证失败',
                    'validation_errors': errors
                }, status=400)
            
            validated_data = serializer.validated_data
            
            logger.info(f'行程名称: {validated_data.get("itinerary_name")}')
            logger.info(f'关联需求ID: {validated_data.get("requirement_id")}')
            logger.info(f'行程开始日期: {validated_data.get("start_date")}')
            logger.info(f'行程结束日期: {validated_data.get("end_date")}')
            
            destinations = validated_data.get('destinations', [])
            logger.info(f'目的地数量: {len(destinations)}')
            for i, dest in enumerate(destinations, 1):
                logger.info(f'目的地{i}: {dest.get("city_name")} (顺序: {dest.get("destination_order")})')
            
            traveler_stats = validated_data.get('traveler_stats', {})
            logger.info(f'总旅行者数: {traveler_stats.get("adults", 0) + traveler_stats.get("children", 0) + traveler_stats.get("seniors", 0)}')
            
            daily_schedules = validated_data.get('daily_schedules', [])
            logger.info(f'行程天数: {len(daily_schedules)}')
            
            requirement_id = validated_data.get('requirement_id')
            valid, requirement, error_msg = ItineraryService.validate_requirement_exists(requirement_id)
            if not valid:
                logger.error(error_msg)
                return JsonResponse({'error': error_msg}, status=404)
            
            success, itinerary, error_msg = ItineraryService.create_itinerary(
                validated_data, requirement
            )
            
            if not success:
                logger.error(f'创建行程失败: {error_msg}')
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            
            logger.info('行程数据解析并保存成功')
            logger.info(f'行程ID: {itinerary.itinerary_id}')
            logger.info(f'行程名称: {itinerary.itinerary_name}')
            
            return JsonResponse({
                'success': True,
                'itinerary_id': itinerary.itinerary_id,
                'itinerary_name': itinerary.itinerary_name
            }, status=200)
            
        except json.JSONDecodeError as e:
            logger.error(f'JSON格式错误: {e}', exc_info=True)
            return JsonResponse({'error': f'JSON格式错误: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f'处理数据失败: {e}', exc_info=True)
            return JsonResponse({'error': f'处理数据失败: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class RequirementWebhookView(APIView):
    """处理n8n webhook返回的旅游需求数据"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="接收并处理来自n8n webhook的旅游需求解析结果",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_input', 'structured_data'],
            properties={
                'user_input': openapi.Schema(type=openapi.TYPE_STRING, description='用户输入的自然语言需求'),
                'structured_data': openapi.Schema(type=openapi.TYPE_OBJECT, description='LLM解析后的结构化数据'),
                'requirement_id': openapi.Schema(type=openapi.TYPE_STRING, description='需求ID'),
                'llm_info': openapi.Schema(type=openapi.TYPE_OBJECT, description='LLM相关信息'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'requirement_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'structured_data': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: "请求参数错误",
            500: "服务器内部错误"
        },
        tags=['Webhook服务']
    )
    def post(self, request, *args, **kwargs):
        """接收并处理webhook数据"""
        try:
            logger.info('接收到来自n8n的需求解析webhook请求')
            
            data = request.data
            
            if isinstance(data, list) and len(data) > 0:
                logger.info('请求数据为列表结构，使用第一个元素')
                data = data[0]
            
            if 'output' in data:
                logger.info('发现output字段，使用其内部数据')
                data = data['output']
            
            # 打印接收到的原始数据，查看n8n返回的日期格式
            logger.info(f'接收到的原始数据: {json.dumps(data, indent=2, ensure_ascii=False)[:2000]}')
            
            serializer = RequirementWebhookSerializer(data=data)
            if not serializer.is_valid():
                errors = serializer.errors
                logger.error(f'数据验证失败: {errors}')
                return Response({
                    'success': False,
                    'error': '数据验证失败',
                    'validation_errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            requirement_data = validated_data.get('structured_data', validated_data)
            
            # 转换日期对象为字符串，避免JSON序列化错误
            def convert_dates(obj):
                if isinstance(obj, dict):
                    return {k: convert_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_dates(item) for item in obj]
                elif hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return obj
            
            requirement_data = convert_dates(requirement_data)
            
            logger.info(f'处理需求数据: {json.dumps(LogSanitizer.sanitize_dict(requirement_data), ensure_ascii=False)[:300]}...')
            
            success, requirement_id, error_msg = RequirementService.generate_requirement_id()
            if not success:
                logger.error(error_msg)
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            success, requirement, error_msg = RequirementService.create_requirement(
                requirement_id, requirement_data
            )
            
            if not success:
                logger.error(error_msg)
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            response_data = {
                'success': True,
                'requirement_id': requirement_id,
                'structured_data': requirement_data,
                'validation_errors': None,
                'warnings': [],
                'error': None
            }
            
            logger.info('需求解析数据处理成功')
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'处理需求解析数据失败: {e}', exc_info=True)
            return Response(
                {'success': False, 'error': f'处理数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ProcessRequirementViaN8nView(APIView):
    """通过n8n webhook处理旅游需求"""
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        operation_description="通过n8n webhook处理用户的自然语言旅游需求输入",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_input'],
            properties={
                'user_input': openapi.Schema(type=openapi.TYPE_STRING, description='用户输入的自然语言需求'),
                'save_to_db': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否保存到数据库'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'requirement_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'structured_data': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: "请求参数错误",
            500: "服务器内部错误"
        },
        tags=['LLM服务']
    )
    def post(self, request):
        """通过n8n webhook处理需求"""
        from django.conf import settings
        
        data = request.data
        
        serializer = N8nProcessRequirementSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': '请求参数错误', 'validation_errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        user_input = validated_data.get('user_input')
        
        logger.info(f'通过n8n webhook处理需求: {user_input[:100]}...')
        
        try:
            n8n_webhook_url = getattr(settings, 'N8N_REQUIREMENT_WEBHOOK_URL', '')
            
            if not n8n_webhook_url:
                logger.error('N8N_REQUIREMENT_WEBHOOK_URL未配置')
                return Response(
                    {'success': False, 'error': 'n8n webhook URL未配置'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            payload = {
                'user_input': user_input,
                'client_id': validated_data.get('client_id'),
                'provider': validated_data.get('provider'),
                'save_to_db': validated_data.get('save_to_db', True)
            }
            
            success, result, error_msg = N8nIntegrationService.send_to_n8n(
                n8n_webhook_url, payload
            )
            
            if success:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f'处理需求失败: {e}', exc_info=True)
            return Response(
                {'success': False, 'error': f'处理失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ItineraryOptimizationCallbackView(View):
    """处理n8n webhook返回的行程优化结果"""
    
    def post(self, request, *args, **kwargs):
        try:
            logger.info("接收到行程优化callback请求")
            
            content = request.body.decode('utf-8')
            logger.info(f"请求内容长度: {len(content)}")
            
            data = json.loads(content)
            
            serializer = ItineraryOptimizationCallbackSerializer(data=data)
            if not serializer.is_valid():
                errors = serializer.errors
                logger.error(f'数据验证失败: {errors}')
                return JsonResponse({
                    'success': False,
                    'error': '数据验证失败',
                    'validation_errors': errors
                }, status=400)
            
            validated_data = serializer.validated_data
            itinerary_id = validated_data.get('itinerary_id')
            description = validated_data.get('description', '')
            
            logger.info(f"准备更新行程: {itinerary_id}")
            logger.info(f"description长度: {len(description)}")
            
            valid, itinerary, error_msg = ItineraryOptimizationService.validate_itinerary_exists(itinerary_id)
            if not valid:
                logger.error(error_msg)
                return JsonResponse({'success': False, 'error': error_msg}, status=404)
            
            success, error_msg = ItineraryOptimizationService.update_description(
                itinerary, description
            )
            
            if not success:
                logger.error(error_msg)
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            
            logger.info(f"行程优化成功: {itinerary_id}, description已更新")
            
            return JsonResponse({
                'success': True, 
                'message': f'行程 {itinerary_id} 的description已更新'
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return JsonResponse({'success': False, 'error': f'JSON解析失败: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"处理行程优化callback失败: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'处理失败: {str(e)}'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ItineraryQuoteCallbackView(View):
    """处理n8n webhook返回的行程报价结果"""
    
    def post(self, request, *args, **kwargs):
        try:
            logger.info("接收到行程报价callback请求")
            
            content = request.body.decode('utf-8')
            logger.info(f"请求内容长度: {len(content)}")
            
            data = json.loads(content)
            
            serializer = ItineraryQuoteCallbackSerializer(data=data)
            if not serializer.is_valid():
                errors = serializer.errors
                logger.error(f'数据验证失败: {errors}')
                return JsonResponse({
                    'success': False,
                    'error': '数据验证失败',
                    'validation_errors': errors
                }, status=400)
            
            validated_data = serializer.validated_data
            itinerary_id = validated_data.get('itinerary_id')
            itinerary_quote = validated_data.get('itinerary_quote', '')
            
            logger.info(f"准备更新行程报价: {itinerary_id}")
            
            valid, itinerary, error_msg = ItineraryOptimizationService.validate_itinerary_exists(itinerary_id)
            if not valid:
                logger.error(error_msg)
                return JsonResponse({'success': False, 'error': error_msg}, status=404)
            
            # 保存报价
            itinerary.itinerary_quote = itinerary_quote
            itinerary.save(update_fields=['itinerary_quote', 'updated_at'])
            
            logger.info(f"行程报价更新成功: {itinerary_id}")
            
            return JsonResponse({
                'success': True, 
                'message': f'行程 {itinerary_id} 的报价已更新'
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return JsonResponse({'success': False, 'error': f'JSON解析失败: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"处理行程报价callback失败: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'处理失败: {str(e)}'}, status=500)
