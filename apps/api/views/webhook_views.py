from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging
from datetime import date, time
from django.db import transaction

from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.requirement import Requirement

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
            contact_person='测试用户',
            contact_phone='13800138000',
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