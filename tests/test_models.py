import pytest
import os
import sys

# 设置Django环境，使用localhost:3308作为数据库主机
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_HOST'] = 'localhost'
os.environ['DATABASE_PORT'] = '3308'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

# 导入迁移命令
from django.core.management import call_command

# 在测试开始前运行迁移命令
call_command('migrate')

from django.db import IntegrityError
from apps.models.hotel import Hotel
from apps.models.attraction import Attraction
from apps.models.restaurant import Restaurant
from apps.models.itinerary import Itinerary
from apps.models.traveler_stats import TravelerStats
from apps.models.destinations import Destination
from apps.models.daily_schedule import DailySchedule
import uuid
from datetime import time, date, datetime


@pytest.mark.django_db
class TestHotelModel:
    """测试酒店模型的CRUD功能"""
    
    def test_create_hotel(self):
        """测试创建酒店"""
        hotel_data = {
            'hotel_code': f'test_{uuid.uuid4().hex[:8]}',
            'hotel_name': '测试酒店',
            'country_code': 'CN',
            'city_name': '北京',
            'district': '朝阳区',
            'address': '北京市朝阳区建国路88号',
            'hotel_star': 5,
            'hotel_type': 'LUXURY',
            'check_in_time': time(14, 0),
            'check_out_time': time(12, 0),
            'status': 'ACTIVE'
        }
        
        hotel = Hotel.objects.create(**hotel_data)
        
        assert hotel is not None
        assert hotel.hotel_name == '测试酒店'
        assert hotel.country_code == 'CN'
        assert hotel.city_name == '北京'
        assert hotel.status == 'ACTIVE'
    
    def test_read_hotel(self):
        """测试读取酒店"""
        # 先创建一个酒店
        hotel_code = f'test_{uuid.uuid4().hex[:8]}'
        hotel_data = {
            'hotel_code': hotel_code,
            'hotel_name': '测试酒店',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'status': 'ACTIVE'
        }
        hotel = Hotel.objects.create(**hotel_data)
        
        # 通过ID读取
        retrieved_hotel = Hotel.objects.get(hotel_id=hotel.hotel_id)
        assert retrieved_hotel is not None
        assert retrieved_hotel.hotel_code == hotel_code
        
        # 通过酒店代码读取
        retrieved_hotel_by_code = Hotel.objects.get(hotel_code=hotel_code)
        assert retrieved_hotel_by_code is not None
        assert retrieved_hotel_by_code.hotel_name == '测试酒店'
    
    def test_update_hotel(self):
        """测试更新酒店"""
        hotel_data = {
            'hotel_code': f'test_{uuid.uuid4().hex[:8]}',
            'hotel_name': '测试酒店',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'status': 'ACTIVE'
        }
        hotel = Hotel.objects.create(**hotel_data)
        
        # 更新酒店信息
        new_name = '更新后的测试酒店'
        new_address = '北京市朝阳区建国路99号'
        hotel.hotel_name = new_name
        hotel.address = new_address
        hotel.save()
        
        # 验证更新
        updated_hotel = Hotel.objects.get(hotel_id=hotel.hotel_id)
        assert updated_hotel.hotel_name == new_name
        assert updated_hotel.address == new_address
    
    def test_delete_hotel(self):
        """测试删除酒店"""
        hotel_data = {
            'hotel_code': f'test_{uuid.uuid4().hex[:8]}',
            'hotel_name': '测试酒店',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'status': 'ACTIVE'
        }
        hotel = Hotel.objects.create(**hotel_data)
        hotel_id = hotel.hotel_id
        
        # 删除酒店
        hotel.delete()
        
        # 验证删除
        with pytest.raises(Hotel.DoesNotExist):
            Hotel.objects.get(hotel_id=hotel_id)
    
    def test_unique_hotel_code(self):
        """测试酒店代码唯一性"""
        hotel_code = f'test_{uuid.uuid4().hex[:8]}'
        hotel_data = {
            'hotel_code': hotel_code,
            'hotel_name': '测试酒店',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'status': 'ACTIVE'
        }
        Hotel.objects.create(**hotel_data)
        
        # 尝试创建相同代码的酒店
        with pytest.raises(IntegrityError):
            Hotel.objects.create(**hotel_data)


@pytest.mark.django_db
class TestAttractionModel:
    """测试景点模型的CRUD功能"""
    
    def test_create_attraction(self):
        """测试创建景点"""
        attraction_data = {
            'attraction_code': f'test_{uuid.uuid4().hex[:8]}',
            'attraction_name': '测试景点',
            'country_code': 'CN',
            'city_name': '北京',
            'category': 'HISTORICAL',
            'status': 'ACTIVE'
        }
        
        attraction = Attraction.objects.create(**attraction_data)
        
        assert attraction is not None
        assert attraction.attraction_name == '测试景点'
        assert attraction.country_code == 'CN'
        assert attraction.city_name == '北京'
        assert attraction.status == 'ACTIVE'
    
    def test_read_attraction(self):
        """测试读取景点"""
        # 先创建一个景点
        attraction_code = f'test_{uuid.uuid4().hex[:8]}'
        attraction_data = {
            'attraction_code': attraction_code,
            'attraction_name': '测试景点',
            'country_code': 'CN',
            'city_name': '北京',
            'status': 'ACTIVE'
        }
        attraction = Attraction.objects.create(**attraction_data)
        
        # 通过ID读取
        retrieved_attraction = Attraction.objects.get(attraction_id=attraction.attraction_id)
        assert retrieved_attraction is not None
        assert retrieved_attraction.attraction_code == attraction_code
        
        # 通过景点代码读取
        retrieved_attraction_by_code = Attraction.objects.get(attraction_code=attraction_code)
        assert retrieved_attraction_by_code is not None
        assert retrieved_attraction_by_code.attraction_name == '测试景点'
    
    def test_update_attraction(self):
        """测试更新景点"""
        attraction_data = {
            'attraction_code': f'test_{uuid.uuid4().hex[:8]}',
            'attraction_name': '测试景点',
            'country_code': 'CN',
            'city_name': '北京',
            'status': 'ACTIVE'
        }
        attraction = Attraction.objects.create(**attraction_data)
        
        # 更新景点信息
        new_name = '更新后的测试景点'
        new_category = 'CULTURAL'
        attraction.attraction_name = new_name
        attraction.category = new_category
        attraction.save()
        
        # 验证更新
        updated_attraction = Attraction.objects.get(attraction_id=attraction.attraction_id)
        assert updated_attraction.attraction_name == new_name
        assert updated_attraction.category == new_category
    
    def test_delete_attraction(self):
        """测试删除景点"""
        attraction_data = {
            'attraction_code': f'test_{uuid.uuid4().hex[:8]}',
            'attraction_name': '测试景点',
            'country_code': 'CN',
            'city_name': '北京',
            'status': 'ACTIVE'
        }
        attraction = Attraction.objects.create(**attraction_data)
        attraction_id = attraction.attraction_id
        
        # 删除景点
        attraction.delete()
        
        # 验证删除
        with pytest.raises(Attraction.DoesNotExist):
            Attraction.objects.get(attraction_id=attraction_id)
    
    def test_unique_attraction_code(self):
        """测试景点代码唯一性"""
        attraction_code = f'test_{uuid.uuid4().hex[:8]}'
        attraction_data = {
            'attraction_code': attraction_code,
            'attraction_name': '测试景点',
            'country_code': 'CN',
            'city_name': '北京',
            'status': 'ACTIVE'
        }
        Attraction.objects.create(**attraction_data)
        
        # 尝试创建相同代码的景点
        with pytest.raises(IntegrityError):
            Attraction.objects.create(**attraction_data)


@pytest.mark.django_db
class TestRestaurantModel:
    """测试餐厅模型的CRUD功能"""
    
    def test_create_restaurant(self):
        """测试创建餐厅"""
        restaurant_data = {
            'restaurant_code': f'test_{uuid.uuid4().hex[:8]}',
            'restaurant_name': '测试餐厅',
            'country_code': 'CN',
            'city_name': '北京',
            'district': '朝阳区',
            'address': '北京市朝阳区建国路88号',
            'cuisine_type': '中餐',
            'price_range': '$$$',
            'status': 'ACTIVE'
        }
        
        restaurant = Restaurant.objects.create(**restaurant_data)
        
        assert restaurant is not None
        assert restaurant.restaurant_name == '测试餐厅'
        assert restaurant.country_code == 'CN'
        assert restaurant.city_name == '北京'
        assert restaurant.status == 'ACTIVE'
    
    def test_read_restaurant(self):
        """测试读取餐厅"""
        # 先创建一个餐厅
        restaurant_code = f'test_{uuid.uuid4().hex[:8]}'
        restaurant_data = {
            'restaurant_code': restaurant_code,
            'restaurant_name': '测试餐厅',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'cuisine_type': '中餐',
            'price_range': '$$$',
            'status': 'ACTIVE'
        }
        restaurant = Restaurant.objects.create(**restaurant_data)
        
        # 通过ID读取
        retrieved_restaurant = Restaurant.objects.get(restaurant_id=restaurant.restaurant_id)
        assert retrieved_restaurant is not None
        assert retrieved_restaurant.restaurant_code == restaurant_code
        
        # 通过餐厅代码读取
        retrieved_restaurant_by_code = Restaurant.objects.get(restaurant_code=restaurant_code)
        assert retrieved_restaurant_by_code is not None
        assert retrieved_restaurant_by_code.restaurant_name == '测试餐厅'
    
    def test_update_restaurant(self):
        """测试更新餐厅"""
        restaurant_data = {
            'restaurant_code': f'test_{uuid.uuid4().hex[:8]}',
            'restaurant_name': '测试餐厅',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'cuisine_type': '中餐',
            'price_range': '$$$',
            'status': 'ACTIVE'
        }
        restaurant = Restaurant.objects.create(**restaurant_data)
        
        # 更新餐厅信息
        new_name = '更新后的测试餐厅'
        new_cuisine = '西餐'
        restaurant.restaurant_name = new_name
        restaurant.cuisine_type = new_cuisine
        restaurant.save()
        
        # 验证更新
        updated_restaurant = Restaurant.objects.get(restaurant_id=restaurant.restaurant_id)
        assert updated_restaurant.restaurant_name == new_name
        assert updated_restaurant.cuisine_type == new_cuisine
    
    def test_delete_restaurant(self):
        """测试删除餐厅"""
        restaurant_data = {
            'restaurant_code': f'test_{uuid.uuid4().hex[:8]}',
            'restaurant_name': '测试餐厅',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'cuisine_type': '中餐',
            'price_range': '$$$',
            'status': 'ACTIVE'
        }
        restaurant = Restaurant.objects.create(**restaurant_data)
        restaurant_id = restaurant.restaurant_id
        
        # 删除餐厅
        restaurant.delete()
        
        # 验证删除
        with pytest.raises(Restaurant.DoesNotExist):
            Restaurant.objects.get(restaurant_id=restaurant_id)
    
    def test_unique_restaurant_code(self):
        """测试餐厅代码唯一性"""
        restaurant_code = f'test_{uuid.uuid4().hex[:8]}'
        restaurant_data = {
            'restaurant_code': restaurant_code,
            'restaurant_name': '测试餐厅',
            'country_code': 'CN',
            'city_name': '北京',
            'address': '北京市朝阳区建国路88号',
            'cuisine_type': '中餐',
            'price_range': '$$$',
            'status': 'ACTIVE'
        }
        Restaurant.objects.create(**restaurant_data)
        
        # 尝试创建相同代码的餐厅
        with pytest.raises(IntegrityError):
            Restaurant.objects.create(**restaurant_data)


@pytest.mark.django_db
class TestItineraryModel:
    """测试行程模型及其关联模型的CRUD功能"""
    
    def test_create_itinerary_with_related_models(self):
        """测试创建行程及其关联模型"""
        # 创建行程
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 5)
        itinerary_data = {
            'itinerary_name': '测试行程',
            'description': '这是一个测试行程',
            'travel_purpose': 'LEISURE',
            'start_date': start_date,
            'end_date': end_date,
            'contact_person': '张三',
            'contact_phone': '13800138000',
            'departure_city': '北京',
            'return_city': '北京',
            'total_budget': 10000.00,
            'budget_flexibility': 'MODERATE',
            'current_status': 'DRAFT',
            'created_by': 'test_user'
        }
        
        itinerary = Itinerary.objects.create(**itinerary_data)
        
        # 验证行程创建
        assert itinerary is not None
        assert itinerary.itinerary_name == '测试行程'
        assert itinerary.total_days == 5  # 计算得出
        
        # 创建出行人员统计
        traveler_stats_data = {
            'itinerary': itinerary,
            'adult_count': 2,
            'child_count': 1,
            'infant_count': 0,
            'senior_count': 0,
            'notes': '测试出行人员'
        }
        traveler_stats = TravelerStats.objects.create(**traveler_stats_data)
        
        # 验证出行人员统计创建
        assert traveler_stats is not None
        assert traveler_stats.itinerary == itinerary
        assert traveler_stats.adult_count == 2
        
        # 创建目的地
        destination_data = {
            'itinerary': itinerary,
            'destination_order': 1,
            'city_name': '上海',
            'country_code': 'CN',
            'arrival_date': start_date,
            'departure_date': date(2026, 3, 3)
        }
        destination = Destination.objects.create(**destination_data)
        
        # 验证目的地创建
        assert destination is not None
        assert destination.itinerary == itinerary
        assert destination.nights == 2  # 计算得出
        
        # 创建每日行程
        daily_schedule_data = {
            'itinerary_id': itinerary,
            'day_number': 1,
            'schedule_date': start_date,
            'city_name': '上海',
            'activity_type': 'ATTRACTION',
            'activity_title': '测试活动',
            'start_time': time(9, 0),
            'end_time': time(11, 0)
        }
        daily_schedule = DailySchedule.objects.create(**daily_schedule_data)
        
        # 验证每日行程创建
        assert daily_schedule is not None
        assert daily_schedule.itinerary_id == itinerary
    
    def test_read_itinerary_with_related_models(self):
        """测试查询行程及其关联模型"""
        # 创建行程
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 5)
        itinerary_data = {
            'itinerary_name': '测试行程',
            'travel_purpose': 'LEISURE',
            'start_date': start_date,
            'end_date': end_date,
            'contact_person': '张三',
            'contact_phone': '13800138000',
            'departure_city': '北京',
            'return_city': '北京',
            'current_status': 'DRAFT',
            'created_by': 'test_user'
        }
        itinerary = Itinerary.objects.create(**itinerary_data)
        
        # 创建关联模型
        TravelerStats.objects.create(
            itinerary=itinerary,
            adult_count=2,
            child_count=1
        )
        
        Destination.objects.create(
            itinerary=itinerary,
            destination_order=1,
            city_name='上海',
            country_code='CN',
            arrival_date=start_date,
            departure_date=date(2026, 3, 3)
        )
        
        DailySchedule.objects.create(
            itinerary_id=itinerary,
            day_number=1,
            schedule_date=start_date,
            city_name='上海',
            activity_type='ATTRACTION',
            activity_title='测试活动',
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        
        # 通过ID查询行程
        retrieved_itinerary = Itinerary.objects.get(itinerary_id=itinerary.itinerary_id)
        assert retrieved_itinerary is not None
        assert retrieved_itinerary.itinerary_name == '测试行程'
        
        # 查询关联模型
        assert retrieved_itinerary.traveler_stats.count() == 1
        assert retrieved_itinerary.destinations.count() == 1
        assert DailySchedule.objects.filter(itinerary_id=retrieved_itinerary).count() == 1
    
    def test_update_itinerary_with_related_models(self):
        """测试更新行程及其关联模型"""
        # 创建行程
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 5)
        itinerary_data = {
            'itinerary_name': '测试行程',
            'travel_purpose': 'LEISURE',
            'start_date': start_date,
            'end_date': end_date,
            'contact_person': '张三',
            'contact_phone': '13800138000',
            'departure_city': '北京',
            'return_city': '北京',
            'current_status': 'DRAFT',
            'created_by': 'test_user'
        }
        itinerary = Itinerary.objects.create(**itinerary_data)
        
        # 创建关联模型
        traveler_stats = TravelerStats.objects.create(
            itinerary=itinerary,
            adult_count=2,
            child_count=1
        )
        
        # 更新行程
        itinerary.itinerary_name = '更新后的测试行程'
        itinerary.total_budget = 15000.00
        itinerary.updated_by = 'test_user'
        itinerary.save()
        
        # 验证行程更新
        updated_itinerary = Itinerary.objects.get(itinerary_id=itinerary.itinerary_id)
        assert updated_itinerary.itinerary_name == '更新后的测试行程'
        assert updated_itinerary.total_budget == 15000.00
        assert updated_itinerary.version > 1  # 版本号递增
        
        # 更新关联模型
        traveler_stats.adult_count = 3
        traveler_stats.notes = '更新后的出行人员'
        traveler_stats.save()
        
        # 验证关联模型更新
        updated_traveler_stats = TravelerStats.objects.get(stat_id=traveler_stats.stat_id)
        assert updated_traveler_stats.adult_count == 3
        assert updated_traveler_stats.notes == '更新后的出行人员'
    
    def test_cascade_delete_itinerary(self):
        """测试级联删除行程及其关联模型"""
        # 创建行程
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 5)
        itinerary_data = {
            'itinerary_name': '测试行程',
            'travel_purpose': 'LEISURE',
            'start_date': start_date,
            'end_date': end_date,
            'contact_person': '张三',
            'contact_phone': '13800138000',
            'departure_city': '北京',
            'return_city': '北京',
            'current_status': 'DRAFT',
            'created_by': 'test_user'
        }
        itinerary = Itinerary.objects.create(**itinerary_data)
        itinerary_id = itinerary.itinerary_id
        
        # 创建关联模型
        traveler_stats = TravelerStats.objects.create(
            itinerary=itinerary,
            adult_count=2,
            child_count=1
        )
        traveler_stats_id = traveler_stats.stat_id
        
        destination = Destination.objects.create(
            itinerary=itinerary,
            destination_order=1,
            city_name='上海',
            country_code='CN',
            arrival_date=start_date,
            departure_date=date(2026, 3, 3)
        )
        destination_id = destination.destination_id
        
        daily_schedule = DailySchedule.objects.create(
            itinerary_id=itinerary,
            day_number=1,
            schedule_date=start_date,
            city_name='上海',
            activity_type='ATTRACTION',
            activity_title='测试活动',
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        daily_schedule_id = daily_schedule.schedule_id
        
        # 删除行程
        itinerary.delete()
        
        # 验证行程已删除
        with pytest.raises(Itinerary.DoesNotExist):
            Itinerary.objects.get(itinerary_id=itinerary_id)
        
        # 验证关联模型级联删除
        with pytest.raises(TravelerStats.DoesNotExist):
            TravelerStats.objects.get(stat_id=traveler_stats_id)
        
        with pytest.raises(Destination.DoesNotExist):
            Destination.objects.get(destination_id=destination_id)
        
        with pytest.raises(DailySchedule.DoesNotExist):
            DailySchedule.objects.get(schedule_id=daily_schedule_id)
