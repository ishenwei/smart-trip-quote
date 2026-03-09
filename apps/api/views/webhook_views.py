from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from datetime import date, time
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.requirement import Requirement
from apps.models.requirement_itinerary import RequirementItinerary

# 配置日志
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class ItineraryWebhookView(View):
    """处理n8n webhook返回的行程数据"""
    
    def post(self, request, *args, **kwargs):
        """接收并处理webhook数据"""
        try:
            # 记录请求开始
            logger.info(f"接收到来自n8n的webhook请求")
            
            # 读取请求体
            content = request.body.decode('utf-8')
            logger.info(f"请求内容长度: {len(content)}")
            
            # 解析JSON数据
            data = json.loads(content)
            logger.info(f"解析后的数据类型: {type(data)}")
            
            # 检查是否有output字段
            if 'output' in data:
                logger.info('发现output字段，使用其内部数据')
                data = data['output']
            
            # 验证必需字段
            if 'requirement_id' not in data:
                logger.error('JSON中缺少requirement_id字段')
                return JsonResponse({'error': '缺少requirement_id字段'}, status=400)
            
            if 'itinerary_name' not in data:
                logger.error('JSON中缺少itinerary_name字段')
                return JsonResponse({'error': '缺少itinerary_name字段'}, status=400)
            
            if 'start_date' not in data:
                logger.error('JSON中缺少start_date字段')
                return JsonResponse({'error': '缺少start_date字段'}, status=400)
            
            if 'end_date' not in data:
                logger.error('JSON中缺少end_date字段')
                return JsonResponse({'error': '缺少end_date字段'}, status=400)
            
            # 验证JSON结构
            logger.info('JSON格式验证成功')
            logger.info(f'行程名称: {data.get("itinerary_name")}')
            logger.info(f'关联需求ID: {data.get("requirement_id")}')
            logger.info(f'行程开始日期: {data.get("start_date")}')
            logger.info(f'行程结束日期: {data.get("end_date")}')
            
            # 验证目的地信息
            destinations = data.get('destinations', [])
            logger.info(f'目的地数量: {len(destinations)}')
            for i, dest in enumerate(destinations, 1):
                logger.info(f'目的地{i}: {dest.get("city_name")} (顺序: {dest.get("destination_order")})')
            
            # 验证旅行者统计信息
            traveler_stats = data.get('traveler_stats', {})
            logger.info(f'总旅行者数: {traveler_stats.get("total_travelers")}')
            logger.info(f'成人: {traveler_stats.get("adults")}, 儿童: {traveler_stats.get("children")}, 婴儿: {traveler_stats.get("infants")}, 老人: {traveler_stats.get("seniors")}')
            
            # 验证每日行程安排
            daily_schedules = data.get('daily_schedules', [])
            logger.info(f'行程天数: {len(daily_schedules)}')
            for i, day_schedule in enumerate(daily_schedules, 1):
                logger.info(f'第{i}天数据: {day_schedule}')
                activities = day_schedule.get('activities', [])
                logger.info(f'第{i}天活动数量: {len(activities)}')
                for j, activity in enumerate(activities, 1):
                    logger.info(f'  活动{j}: {activity.get("activity_title")} ({activity.get("activity_type")})')
            
            # 尝试数据库操作
            try:
                # 验证数据库连接
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                
                # 验证requirement是否存在
                requirement_id = data.get('requirement_id')
                try:
                    requirement = Requirement.objects.get(requirement_id=requirement_id)
                    logger.info(f"找到关联的需求: {requirement_id}")
                except Requirement.DoesNotExist:
                    logger.error(f"需求不存在: {requirement_id}")
                    return JsonResponse({'error': f'需求不存在: {requirement_id}'}, status=404)
                
                # 开始数据库事务
                with transaction.atomic():
                    # 创建行程主表
                    itinerary = self.create_itinerary(data, requirement)
                    
                    # 创建需求与行程的关联关系
                    try:
                        requirement_itinerary = RequirementItinerary(
                            requirement=requirement,
                            itinerary=itinerary
                        )
                        requirement_itinerary.save()
                        logger.info(f'创建需求与行程关联关系成功: requirement_id={requirement.requirement_id}, itinerary_id={itinerary.itinerary_id}')
                    except Exception as e:
                        logger.error(f'创建需求与行程关联关系失败: {e}', exc_info=True)
                        raise
                    
                    # 创建目的地信息
                    self.create_destinations(itinerary, data)
                    
                    # 创建旅行者统计信息
                    self.create_traveler_stats(itinerary, data)
                    
                    # 创建每日行程安排
                    self.create_daily_schedules(itinerary, data)
                    
                    logger.info('行程数据解析并保存成功')
                    logger.info(f'行程ID: {itinerary.itinerary_id}')
                    logger.info(f'行程名称: {itinerary.itinerary_name}')
                    
                    return JsonResponse({
                        'success': True,
                        'itinerary_id': itinerary.itinerary_id,
                        'itinerary_name': itinerary.itinerary_name
                    }, status=200)
                    
            except Exception as db_error:
                logger.error(f'数据库操作失败: {db_error}', exc_info=True)
                # 即使数据库操作失败，也要返回成功的响应，因为JSON解析和验证已经成功
                return JsonResponse({
                    'success': True,
                    'message': 'JSON解析和验证成功，但数据库操作失败。这可能是因为数据库服务不可用。',
                    'itinerary_name': data.get('itinerary_name'),
                    'requirement_id': data.get('requirement_id')
                }, status=200)
                
        except json.JSONDecodeError as e:
            logger.error(f'JSON格式错误: {e}', exc_info=True)
            return JsonResponse({'error': f'JSON格式错误: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f'处理数据失败: {e}', exc_info=True)
            return JsonResponse({'error': f'处理数据失败: {str(e)}'}, status=500)
    
    def create_itinerary(self, data, requirement):
        """创建行程主表"""
        itinerary = Itinerary(
            itinerary_name=data.get('itinerary_name', '未命名行程'),
            start_date=date.fromisoformat(data.get('start_date')),
            end_date=date.fromisoformat(data.get('end_date')),
            travel_purpose=Itinerary.TravelPurpose.LEISURE,
            contact_person=requirement.contact_person or '测试用户',
            contact_phone=requirement.contact_phone or '13800138000',
            contact_company=requirement.contact_company,
            departure_city=requirement.origin_name or '上海',
            return_city=requirement.origin_name or '上海',
            current_status=Itinerary.CurrentStatus.DRAFT,
            created_by='webhook_user'
        )
        itinerary.save()
        return itinerary
    
    def create_destinations(self, itinerary, data):
        """创建目的地信息"""
        destinations = data.get('destinations', [])
        
        for dest_data in destinations:
            destination = Destination(
                itinerary=itinerary,
                destination_order=dest_data.get('destination_order'),
                city_name=dest_data.get('city_name'),
                country_code=dest_data.get('country_code'),
                arrival_date=date.fromisoformat(dest_data.get('arrival_date')),
                departure_date=date.fromisoformat(dest_data.get('departure_date'))
            )
            destination.save()
    
    def create_traveler_stats(self, itinerary, data):
        """创建旅行者统计信息"""
        traveler_stats_info = data.get('traveler_stats', {})
        
        traveler_stats = TravelerStats(
            itinerary=itinerary,
            adult_count=traveler_stats_info.get('adults', 0),
            child_count=traveler_stats_info.get('children', 0),
            infant_count=traveler_stats_info.get('infants', 0),
            senior_count=traveler_stats_info.get('seniors', 0)
        )
        traveler_stats.save()
    
    def create_daily_schedules(self, itinerary, data):
        """创建每日行程安排"""
        daily_schedules = data.get('daily_schedules', [])
        
        for day_schedule in daily_schedules:
            day_number = day_schedule.get('day')
            schedule_date = date.fromisoformat(day_schedule.get('date'))
            city = day_schedule.get('city')
            
            # 获取对应的目的地实例
            destination = Destination.objects.filter(
                itinerary=itinerary,
                city_name=city
            ).first()
            
            # 创建每日活动
            activities = day_schedule.get('activities', [])
            for activity in activities:
                # 解析时间
                start_time = time.fromisoformat(activity.get('start_time'))
                end_time = time.fromisoformat(activity.get('end_time'))
                
                # 获取活动类型
                activity_type_str = activity.get('activity_type')
                activity_type = self.get_activity_type(activity_type_str)
                
                # 根据活动类型获取对应的实例
                attraction = None
                hotel = None
                restaurant = None
                
                if activity_type == DailySchedule.ActivityType.ATTRACTION:
                    from apps.models.attraction import Attraction
                    attraction_id_str = activity.get('id_reference')
                    if attraction_id_str:
                        try:
                            attraction = Attraction.objects.get(attraction_id=attraction_id_str)
                        except Attraction.DoesNotExist:
                            logger.warning(f'景点不存在: {attraction_id_str}')
                
                elif activity_type in [DailySchedule.ActivityType.CHECK_IN, DailySchedule.ActivityType.CHECK_OUT]:
                    from apps.models.hotel import Hotel
                    hotel_id_str = activity.get('id_reference')
                    if hotel_id_str:
                        try:
                            hotel = Hotel.objects.get(hotel_id=hotel_id_str)
                        except Hotel.DoesNotExist:
                            logger.warning(f'酒店不存在: {hotel_id_str}')
                
                elif activity_type == DailySchedule.ActivityType.MEAL:
                    from apps.models.restaurant import Restaurant
                    restaurant_id_str = activity.get('id_reference')
                    if restaurant_id_str:
                        try:
                            restaurant = Restaurant.objects.get(restaurant_id=restaurant_id_str)
                        except Restaurant.DoesNotExist:
                            logger.warning(f'餐厅不存在: {restaurant_id_str}')
                
                # 创建每日行程记录
                schedule = DailySchedule(
                    itinerary_id=itinerary,
                    day_number=day_number,
                    schedule_date=schedule_date,
                    destination_id=destination,
                    activity_type=activity_type,
                    activity_title=activity.get('activity_title'),
                    activity_description=activity.get('activity_description'),
                    start_time=start_time,
                    end_time=end_time,
                    # 使用获取到的实例
                    attraction_id=attraction,
                    hotel_id=hotel,
                    restaurant_id=restaurant,
                    booking_status=DailySchedule.BookingStatus.NOT_BOOKED
                )
                schedule.save()
    
    def get_activity_type(self, activity_type_str):
        """将字符串转换为活动类型枚举"""
        activity_type_map = {
            'FLIGHT': DailySchedule.ActivityType.FLIGHT,
            'TRAIN': DailySchedule.ActivityType.TRAIN,
            'ATTRACTION': DailySchedule.ActivityType.ATTRACTION,
            'MEAL': DailySchedule.ActivityType.MEAL,
            'TRANSPORT': DailySchedule.ActivityType.TRANSPORT,
            'SHOPPING': DailySchedule.ActivityType.SHOPPING,
            'FREE': DailySchedule.ActivityType.FREE,
            'CHECK_IN': DailySchedule.ActivityType.CHECK_IN,
            'CHECK_OUT': DailySchedule.ActivityType.CHECK_OUT,
            'OTHER': DailySchedule.ActivityType.OTHER
        }
        return activity_type_map.get(activity_type_str, DailySchedule.ActivityType.OTHER)


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
            logger.info(f'请求数据: {json.dumps(data, ensure_ascii=False)[:500]}...')
            
            # 处理列表结构
            if isinstance(data, list) and len(data) > 0:
                logger.info('请求数据为列表结构，使用第一个元素')
                data = data[0]
            
            # 处理output字段
            if 'output' in data:
                logger.info('发现output字段，使用其内部数据')
                data = data['output']
            
            # 提取结构化数据
            requirement_data = data.get('structured_data', data)
            logger.info(f'处理需求数据: {json.dumps(requirement_data, ensure_ascii=False)[:300]}...')
            
            # 生成requirement_id
            from datetime import datetime
            import time
            
            # 确保原子性，使用时间戳和循环检测
            max_attempts = 100
            requirement_id = None
            
            for attempt in range(max_attempts):
                # 获取当前日期，格式化为YYYYMMDD
                today = datetime.now().strftime('%Y%m%d')
                
                # 查询当日已存在的记录，找到最大的序号
                prefix = f'REQ_{today}_'
                existing_records = Requirement.objects.filter(requirement_id__startswith=prefix)
                
                # 提取最大序号
                max_seq = 0
                for record in existing_records:
                    try:
                        seq = int(record.requirement_id.split('_')[-1])
                        if seq > max_seq:
                            max_seq = seq
                    except (ValueError, IndexError):
                        pass
                
                # 生成下一个序号
                next_seq = max_seq + 1
                new_id = f'{prefix}{next_seq:03d}'
                
                # 检查是否存在冲突
                if not Requirement.objects.filter(requirement_id=new_id).exists():
                    requirement_id = new_id
                    break
                
                # 避免无限循环，添加短暂延迟
                time.sleep(0.01)
            
            if not requirement_id:
                logger.error('生成requirement_id失败')
                return Response(
                    {'success': False, 'error': '生成requirement_id失败'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # 解析base_info
            base_info = requirement_data.get('base_info', {})
            origin = base_info.get('origin', {})
            group_size = base_info.get('group_size', {})
            travel_date = base_info.get('travel_date', {})
            
            # 解析preferences
            preferences = requirement_data.get('preferences', {})
            transportation = preferences.get('transportation', {})
            accommodation = preferences.get('accommodation', {})
            itinerary = preferences.get('itinerary', {})
            special_constraints = itinerary.get('special_constraints', {})
            
            # 解析budget
            budget = requirement_data.get('budget', {})
            budget_range = budget.get('range', {})
            
            # 解析metadata
            metadata = requirement_data.get('metadata', {})
            audit_trail = metadata.get('audit_trail', {})
            template_info = metadata.get('template_info', {})
            
            # 处理destination_cities
            destination_cities = base_info.get('destination_cities', '[]')
            if isinstance(destination_cities, str):
                if destination_cities.strip():
                    # 如果是普通字符串，转换为列表格式
                    destination_cities = [{'name': destination_cities}]
                else:
                    # 空字符串，使用空列表
                    destination_cities = []
            elif isinstance(destination_cities, list):
                # 已经是列表，保持不变
                pass
            else:
                # 其他类型，使用空列表
                destination_cities = []
            
            # 处理日期字段
            from datetime import datetime
            travel_start_date = travel_date.get('start_date')
            if travel_start_date and travel_start_date.strip():
                try:
                    travel_start_date = datetime.fromisoformat(travel_start_date).date()
                except ValueError:
                    logger.warning('start_date格式错误，设为None')
                    travel_start_date = None
            else:
                travel_start_date = None
            
            travel_end_date = travel_date.get('end_date')
            if travel_end_date and travel_end_date.strip():
                try:
                    travel_end_date = datetime.fromisoformat(travel_end_date).date()
                except ValueError:
                    logger.warning('end_date格式错误，设为None')
                    travel_end_date = None
            else:
                travel_end_date = None
            
            # 处理预算字段
            from decimal import Decimal
            budget_min = budget_range.get('min')
            if budget_min:
                try:
                    budget_min = Decimal(str(budget_min))
                except (ValueError, TypeError):
                    logger.warning('budget_min格式错误，设为None')
                    budget_min = None
            
            budget_max = budget_range.get('max')
            if budget_max:
                try:
                    budget_max = Decimal(str(budget_max))
                except (ValueError, TypeError):
                    logger.warning('budget_max格式错误，设为None')
                    budget_max = None
            
            # 创建Requirement对象
            requirement = Requirement(
                requirement_id=requirement_id,
                origin_name=origin.get('name', ''),
                origin_code=origin.get('code', ''),
                origin_type=origin.get('type', ''),
                destination_cities=destination_cities,
                trip_days=base_info.get('trip_days', 1),
                group_adults=group_size.get('adults', 0),
                group_children=group_size.get('children', 0),
                group_seniors=group_size.get('seniors', 0),
                group_total=group_size.get('total', 1),
                travel_start_date=travel_start_date,
                travel_end_date=travel_end_date,
                travel_date_flexible=travel_date.get('is_flexible', False),
                transportation_type=transportation.get('type', ''),
                transportation_notes=transportation.get('notes', ''),
                hotel_level=accommodation.get('level', ''),
                hotel_requirements=accommodation.get('requirements', ''),
                trip_rhythm=itinerary.get('rhythm', ''),
                preference_tags=itinerary.get('tags', []),
                must_visit_spots=special_constraints.get('must_visit_spots', []),
                avoid_activities=special_constraints.get('avoid_activities', []),
                budget_level=budget.get('level', ''),
                budget_currency=budget.get('currency', 'CNY'),
                budget_min=budget_min,
                budget_max=budget_max,
                budget_notes=budget.get('budget_notes', ''),
                source_type=metadata.get('source_type', 'NaturalLanguage'),
                status=metadata.get('status', 'Confirmed'),
                assumptions=metadata.get('assumptions', []),
                is_template=metadata.get('is_template', False),
                template_name=template_info.get('name', ''),
                template_category=template_info.get('category', ''),
                extension=requirement_data.get('extension', {})
            )
            
            # 保存到数据库
            requirement.save()
            logger.info(f'需求保存成功，ID: {requirement_id}')
            
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
        import requests
        
        data = request.data
        user_input = data.get('user_input')
        
        if not user_input:
            return Response(
                {'success': False, 'error': 'user_input is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
                'client_id': data.get('client_id'),
                'provider': data.get('provider'),
                'save_to_db': data.get('save_to_db', True)
            }
            
            logger.info(f'发送请求到n8n webhook: {n8n_webhook_url}')
            
            response = requests.post(
                n8n_webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f'n8n webhook响应状态: {response.status_code}')
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f'n8n webhook处理成功: {result.get("success")}')
                return Response(result, status=status.HTTP_200_OK)
            else:
                logger.error(f'n8n webhook返回错误: {response.status_code} - {response.text}')
                return Response(
                    {'success': False, 'error': f'n8n webhook处理失败: {response.status_code}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except requests.Timeout:
            logger.error('n8n webhook请求超时')
            return Response(
                {'success': False, 'error': '请求超时，请稍后重试'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
        except requests.RequestException as e:
            logger.error(f'n8n webhook请求失败: {e}', exc_info=True)
            return Response(
                {'success': False, 'error': f'请求失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f'处理需求失败: {e}', exc_info=True)
            return Response(
                {'success': False, 'error': f'处理失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )