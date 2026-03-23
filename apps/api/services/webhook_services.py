"""
Webhook 业务逻辑服务层
处理 webhook 数据的业务逻辑，与 View 层解耦
"""
import logging
from datetime import date, time, datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional, Tuple
from django.db import transaction

from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.requirement import Requirement
from apps.models.requirement_itinerary import RequirementItinerary

logger = logging.getLogger(__name__)


class ItineraryService:
    """
    行程服务类
    处理行程相关的业务逻辑
    """
    
    ACTIVITY_TYPE_MAP = {
        'FLIGHT': DailySchedule.ActivityType.FLIGHT,
        'TRAIN': DailySchedule.ActivityType.TRAIN,
        'ATTRACTION': DailySchedule.ActivityType.ATTRACTION,
        'MEAL': DailySchedule.ActivityType.MEAL,
        'TRANSPORT': DailySchedule.ActivityType.TRANSPORT,
        'SHOPPING': DailySchedule.ActivityType.SHOPPING,
        'FREE': DailySchedule.ActivityType.FREE,
        'CHECK_IN': DailySchedule.ActivityType.CHECK_IN,
        'CHECK_OUT': DailySchedule.ActivityType.CHECK_OUT,
        'OTHER': DailySchedule.ActivityType.OTHER,
    }
    
    @classmethod
    def validate_requirement_exists(cls, requirement_id: str) -> Tuple[bool, Optional[Requirement], Optional[str]]:
        """
        验证需求是否存在
        
        Returns:
            (是否成功, Requirement对象, 错误信息)
        """
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            return True, requirement, None
        except Requirement.DoesNotExist:
            return False, None, f'需求不存在: {requirement_id}'
        except Exception as e:
            logger.error(f'查询需求失败: {e}', exc_info=True)
            return False, None, f'查询需求失败: {str(e)}'
    
    @classmethod
    @transaction.atomic
    def create_itinerary(cls, data: Dict[str, Any], requirement: Requirement) -> Tuple[bool, Optional[Itinerary], Optional[str]]:
        """
        创建行程及其关联数据
        
        Args:
            data: 验证后的行程数据
            requirement: 关联的需求对象
        
        Returns:
            (是否成功, Itinerary对象, 错误信息)
        """
        try:
            itinerary = cls._create_itinerary_main(data, requirement)
            
            cls._create_destinations(itinerary, data)
            
            cls._create_traveler_stats(itinerary, data)
            
            cls._create_daily_schedules(itinerary, data)
            
            cls._create_requirement_itinerary_relation(requirement, itinerary)
            
            # 更新 itinerary_json_data 和 itinerary_quote_json_data
            itinerary.update_itinerary_json_data()
            itinerary.update_itinerary_quote_json_data()
            itinerary.save()
            
            logger.info(f'行程创建成功: itinerary_id={itinerary.itinerary_id}, name={itinerary.itinerary_name}')
            
            return True, itinerary, None
            
        except Exception as e:
            logger.error(f'创建行程失败: {e}', exc_info=True)
            return False, None, f'创建行程失败: {str(e)}'
    
    @classmethod
    def _create_itinerary_main(cls, data: Dict[str, Any], requirement: Requirement) -> Itinerary:
        """创建行程主表"""
        start_date_val = data.get('start_date')
        end_date_val = data.get('end_date')
        itinerary = Itinerary(
            itinerary_name=data.get('itinerary_name', '未命名行程'),
            start_date=start_date_val if isinstance(start_date_val, date) else date.fromisoformat(start_date_val),
            end_date=end_date_val if isinstance(end_date_val, date) else date.fromisoformat(end_date_val),
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
    
    @classmethod
    def _create_destinations(cls, itinerary: Itinerary, data: Dict[str, Any]) -> None:
        """创建目的地信息"""
        destinations = data.get('destinations', [])
        
        for dest_data in destinations:
            arrival_date_val = dest_data.get('arrival_date')
            departure_date_val = dest_data.get('departure_date')
            destination = Destination(
                itinerary=itinerary,
                destination_order=dest_data.get('destination_order'),
                city_name=dest_data.get('city_name'),
                country_code=dest_data.get('country_code'),
                arrival_date=arrival_date_val if isinstance(arrival_date_val, date) else date.fromisoformat(arrival_date_val),
                departure_date=departure_date_val if isinstance(departure_date_val, date) else date.fromisoformat(departure_date_val)
            )
            destination.save()
    
    @classmethod
    def _create_traveler_stats(cls, itinerary: Itinerary, data: Dict[str, Any]) -> None:
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
    
    @classmethod
    def _create_daily_schedules(cls, itinerary: Itinerary, data: Dict[str, Any]) -> None:
        """创建每日行程安排"""
        daily_schedules = data.get('daily_schedules', [])
        
        for day_schedule in daily_schedules:
            day_number = day_schedule.get('day')
            schedule_date_val = day_schedule.get('date')
            schedule_date = schedule_date_val if isinstance(schedule_date_val, date) else date.fromisoformat(schedule_date_val)
            city = day_schedule.get('city')
            
            destination = Destination.objects.filter(
                itinerary=itinerary,
                city_name=city
            ).first()
            
            activities = day_schedule.get('activities', [])
            for activity in activities:
                start_time_val = activity.get('start_time')
                end_time_val = activity.get('end_time')
                start_time = start_time_val if isinstance(start_time_val, time) else time.fromisoformat(start_time_val)
                end_time = end_time_val if isinstance(end_time_val, time) else time.fromisoformat(end_time_val)
                
                activity_type = cls.ACTIVITY_TYPE_MAP.get(
                    activity.get('activity_type'),
                    DailySchedule.ActivityType.OTHER
                )
                
                attraction = cls._resolve_attraction(activity, activity_type)
                hotel = cls._resolve_hotel(activity, activity_type)
                restaurant = cls._resolve_restaurant(activity, activity_type)
                
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
                    attraction_id=attraction,
                    hotel_id=hotel,
                    restaurant_id=restaurant,
                    booking_status=DailySchedule.BookingStatus.NOT_BOOKED
                )
                schedule.save()
    
    @classmethod
    def _resolve_attraction(cls, activity: Dict[str, Any], activity_type) -> Optional[Any]:
        """解析景点引用"""
        if activity_type != DailySchedule.ActivityType.ATTRACTION:
            return None
        
        from apps.models.attraction import Attraction
        attraction_id_str = activity.get('id_reference')
        if not attraction_id_str:
            return None
        
        try:
            return Attraction.objects.get(attraction_id=attraction_id_str)
        except Attraction.DoesNotExist:
            logger.warning(f'景点不存在: {attraction_id_str}')
            return None
    
    @classmethod
    def _resolve_hotel(cls, activity: Dict[str, Any], activity_type) -> Optional[Any]:
        """解析酒店引用"""
        if activity_type not in [
            DailySchedule.ActivityType.CHECK_IN, 
            DailySchedule.ActivityType.CHECK_OUT
        ]:
            return None
        
        from apps.models.hotel import Hotel
        hotel_id_str = activity.get('id_reference')
        if not hotel_id_str:
            return None
        
        try:
            return Hotel.objects.get(hotel_id=hotel_id_str)
        except Hotel.DoesNotExist:
            logger.warning(f'酒店不存在: {hotel_id_str}')
            return None
    
    @classmethod
    def _resolve_restaurant(cls, activity: Dict[str, Any], activity_type) -> Optional[Any]:
        """解析餐厅引用"""
        if activity_type != DailySchedule.ActivityType.MEAL:
            return None
        
        from apps.models.restaurant import Restaurant
        restaurant_id_str = activity.get('id_reference')
        if not restaurant_id_str:
            return None
        
        try:
            return Restaurant.objects.get(restaurant_id=restaurant_id_str)
        except Restaurant.DoesNotExist:
            logger.warning(f'餐厅不存在: {restaurant_id_str}')
            return None
    
    @classmethod
    def _create_requirement_itinerary_relation(cls, requirement: Requirement, itinerary: Itinerary) -> None:
        """创建需求与行程的关联关系"""
        requirement_itinerary = RequirementItinerary(
            requirement=requirement,
            itinerary=itinerary
        )
        requirement_itinerary.save()
        logger.info(
            f'创建需求与行程关联关系成功: '
            f'requirement_id={requirement.requirement_id}, '
            f'itinerary_id={itinerary.itinerary_id}'
        )


class RequirementService:
    """
    需求服务类
    处理需求相关的业务逻辑
    """
    
    @classmethod
    def generate_requirement_id(cls) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        生成唯一的 requirement_id
        
        Returns:
            (是否成功, requirement_id, 错误信息)
        """
        import time
        
        max_attempts = 100
        for attempt in range(max_attempts):
            today = datetime.now().strftime('%Y%m%d')
            prefix = f'REQ_{today}_'
            
            existing_records = Requirement.objects.filter(requirement_id__startswith=prefix)
            
            max_seq = 0
            for record in existing_records:
                try:
                    seq = int(record.requirement_id.split('_')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except (ValueError, IndexError):
                    pass
            
            next_seq = max_seq + 1
            new_id = f'{prefix}{next_seq:03d}'
            
            if not Requirement.objects.filter(requirement_id=new_id).exists():
                return True, new_id, None
            
            time.sleep(0.01)
        
        return False, None, '生成requirement_id失败: 达到最大重试次数'
    
    @classmethod
    def parse_date(cls, date_str: Optional[str]) -> Optional[date]:
        """解析日期字符串"""
        if not date_str or not date_str.strip():
            return None
        
        try:
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            logger.warning(f'日期格式错误: {date_str}')
            return None
    
    @classmethod
    def parse_decimal(cls, value: Any) -> Optional[Decimal]:
        """解析 Decimal 值"""
        if not value:
            return None
        
        try:
            return Decimal(str(value))
        except (ValueError, TypeError, InvalidOperation):
            logger.warning(f'Decimal 格式错误: {value}')
            return None
    
    @classmethod
    def create_requirement(cls, requirement_id: str, data: Dict[str, Any]) -> Tuple[bool, Optional[Requirement], Optional[str]]:
        """
        创建需求记录
        
        Args:
            requirement_id: 需求ID
            data: 验证后的需求数据
        
        Returns:
            (是否成功, Requirement对象, 错误信息)
        """
        try:
            requirement_data = cls._extract_requirement_fields(requirement_id, data)
            
            requirement = Requirement(**requirement_data)
            requirement.save()
            
            logger.info(f'需求保存成功: requirement_id={requirement_id}')
            
            return True, requirement, None
            
        except Exception as e:
            logger.error(f'创建需求失败: {e}', exc_info=True)
            return False, None, f'创建需求失败: {str(e)}'
    
    @classmethod
    def _extract_requirement_fields(cls, requirement_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """提取需求字段"""
        contact_person = data.get('contact_name', '')
        contact_phone = data.get('contact_phone', '')
        contact_email = data.get('contact_email', '')
        
        base_info = data.get('base_info', {})
        preferences = data.get('preferences', {})
        budget = data.get('budget', {})
        metadata = data.get('metadata', {})
        
        origin = base_info.get('origin', {})
        group_size = base_info.get('group_size', {})
        travel_date = base_info.get('travel_date', {})
        transportation = preferences.get('transportation', {})
        accommodation = preferences.get('accommodation', {})
        itinerary_pref = preferences.get('itinerary', {})
        special_constraints = itinerary_pref.get('special_constraints', {})
        budget_range = budget.get('range', {})
        template_info = metadata.get('template_info', {})
        
        destination_cities_list = base_info.get('destination_cities', [])
        if isinstance(destination_cities_list, str):
            destination_cities_list = [{'name': destination_cities_list}] if destination_cities_list.strip() else []
        
        # 将 destination_cities 数组转换为逗号分隔的字符串
        if isinstance(destination_cities_list, list):
            destination_cities = ','.join([
                city.get('name', str(city)) if isinstance(city, dict) else str(city)
                for city in destination_cities_list
            ])
        else:
            destination_cities = ''
        
        return {
            'requirement_id': requirement_id,
            'origin_name': origin.get('name', ''),
            'origin_code': origin.get('code', ''),
            'origin_type': origin.get('type', ''),
            'destination_cities': destination_cities,
            'trip_days': base_info.get('trip_days', 1),
            'group_adults': group_size.get('adults', 0),
            'group_children': group_size.get('children', 0),
            'group_seniors': group_size.get('seniors', 0),
            'group_total': group_size.get('total', 1),
            'travel_start_date': cls.parse_date(travel_date.get('start_date')),
            'travel_end_date': cls.parse_date(travel_date.get('end_date')),
            'travel_date_flexible': travel_date.get('is_flexible', False),
            'transportation_type': transportation.get('type', ''),
            'transportation_notes': transportation.get('notes', ''),
            'hotel_level': accommodation.get('level', ''),
            'hotel_requirements': accommodation.get('requirements', ''),
            'trip_rhythm': itinerary_pref.get('rhythm', ''),
            'preference_tags': itinerary_pref.get('tags', []),
            'must_visit_spots': special_constraints.get('must_visit_spots', []),
            'avoid_activities': special_constraints.get('avoid_activities', []),
            'budget_level': budget.get('level', ''),
            'budget_currency': budget.get('currency', 'CNY'),
            'budget_min': cls.parse_decimal(budget_range.get('min')),
            'budget_max': cls.parse_decimal(budget_range.get('max')),
            'budget_notes': budget.get('budget_notes', ''),
            'contact_person': contact_person,
            'contact_phone': contact_phone,
            'contact_email': contact_email,
            'source_type': metadata.get('source_type', 'NaturalLanguage'),
            'status': metadata.get('status', 'Confirmed'),
            'assumptions': metadata.get('assumptions', []),
            'is_template': metadata.get('is_template', False),
            'template_name': template_info.get('name', ''),
            'template_category': template_info.get('category', ''),
            'extension': data.get('extension', {})
        }


class ItineraryOptimizationService:
    """
    行程优化服务类
    处理行程优化的业务逻辑
    """
    
    @classmethod
    def validate_itinerary_exists(cls, itinerary_id: str) -> Tuple[bool, Optional[Itinerary], Optional[str]]:
        """
        验证行程是否存在
        
        Returns:
            (是否成功, Itinerary对象, 错误信息)
        """
        try:
            itinerary = Itinerary.objects.get(itinerary_id=itinerary_id)
            return True, itinerary, None
        except Itinerary.DoesNotExist:
            return False, None, f'行程不存在: {itinerary_id}'
        except Exception as e:
            logger.error(f'查询行程失败: {e}', exc_info=True)
            return False, None, f'查询行程失败: {str(e)}'
    
    @classmethod
    def update_description(cls, itinerary: Itinerary, description: str) -> Tuple[bool, Optional[str]]:
        """
        更新行程描述
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            itinerary.description = description or ''
            itinerary.save()
            logger.info(f'行程描述更新成功: itinerary_id={itinerary.itinerary_id}')
            return True, None
        except Exception as e:
            logger.error(f'更新行程描述失败: {e}', exc_info=True)
            return False, f'更新行程描述失败: {str(e)}'


class N8nIntegrationService:
    """
    N8N 集成服务类
    处理与 N8N 交互的业务逻辑
    """
    
    @classmethod
    def send_to_n8n(cls, webhook_url: str, payload: Dict[str, Any], timeout: int = 30) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        发送请求到 N8N webhook
        
        Args:
            webhook_url: N8N webhook URL
            payload: 请求数据
            timeout: 超时时间（秒）
        
        Returns:
            (是否成功, 响应数据, 错误信息)
        """
        import requests
        
        try:
            logger.info(f'发送请求到 n8n webhook: {webhook_url}')
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f'n8n webhook 处理成功: {result.get("success")}')
                return True, result, None
            else:
                error_msg = f'n8n webhook 返回错误: {response.status_code}'
                logger.error(f'{error_msg} - {response.text}')
                return False, None, error_msg
                
        except requests.Timeout:
            error_msg = 'n8n webhook 请求超时'
            logger.error(error_msg)
            return False, None, error_msg
        except requests.RequestException as e:
            error_msg = f'n8n webhook 请求失败: {str(e)}'
            logger.error(error_msg, exc_info=True)
            return False, None, error_msg
