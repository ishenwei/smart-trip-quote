import pytest
import sys
import os
import uuid

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 初始化Django
import django
try:
    # 强制使用SQLite内存数据库
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
    django.setup()
except Exception as e:
    print(f"Warning: Django setup failed: {e}")

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from apps.models.destinations import Destination
from apps.models.daily_schedule import DailySchedule
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant
from apps.models.itinerary import Itinerary
from apps.admin.views import get_filtered_resources
from datetime import datetime, timedelta


@pytest.mark.django_db
class TestDailyScheduleFilter(TestCase):
    """测试动态过滤功能"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建测试用户
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        
        # 创建测试行程
        self.itinerary = Itinerary.objects.create(
            itinerary_name='测试行程',
            description='测试行程描述',
            travel_purpose='LEISURE',
            start_date=datetime.now().date(),
            end_date=datetime.now().date() + timedelta(days=3),
            contact_person='张三',
            contact_phone='13800138000',
            departure_city='北京',
            return_city='北京',
            current_status='DRAFT',
            created_by='test_user'
        )
        
        # 创建测试目的地
        self.destination_beijing = Destination.objects.create(
            destination_id=uuid.uuid4(),
            itinerary=self.itinerary,
            destination_order=1,
            city_name='北京',
            country_code='CN',
            arrival_date=datetime.now().date(),
            departure_date=datetime.now().date() + timedelta(days=1)
        )
        
        self.destination_shanghai = Destination.objects.create(
            destination_id=uuid.uuid4(),
            itinerary=self.itinerary,
            destination_order=2,
            city_name='上海',
            country_code='CN',
            arrival_date=datetime.now().date() + timedelta(days=1),
            departure_date=datetime.now().date() + timedelta(days=2)
        )
        
        # 创建测试景点
        self.attraction_beijing = Attraction.objects.create(
            attraction_id=uuid.uuid4(),
            attraction_code='ATTR-BJ-001',
            attraction_name='故宫博物院',
            country_code='CN',
            city_name='北京',
            status='ACTIVE'
        )
        
        self.attraction_shanghai = Attraction.objects.create(
            attraction_id=uuid.uuid4(),
            attraction_code='ATTR-SH-001',
            attraction_name='外滩',
            country_code='CN',
            city_name='上海',
            status='ACTIVE'
        )
        
        # 创建测试餐厅
        self.restaurant_beijing = Restaurant.objects.create(
            restaurant_id=uuid.uuid4(),
            restaurant_code='REST-BJ-001',
            restaurant_name='全聚德烤鸭',
            country_code='CN',
            city_name='北京',
            cuisine_type='中餐',
            price_range='$$$',
            status='ACTIVE'
        )
        
        self.restaurant_shanghai = Restaurant.objects.create(
            restaurant_id=uuid.uuid4(),
            restaurant_code='REST-SH-001',
            restaurant_name='南翔小笼包',
            country_code='CN',
            city_name='上海',
            cuisine_type='中餐',
            price_range='$$',
            status='ACTIVE'
        )
        
        # 创建测试酒店
        self.hotel_beijing = Hotel.objects.create(
            hotel_id=uuid.uuid4(),
            hotel_code='HOTEL-BJ-001',
            hotel_name='北京饭店',
            country_code='CN',
            city_name='北京',
            hotel_star=5,
            status='ACTIVE'
        )
        
        self.hotel_shanghai = Hotel.objects.create(
            hotel_id=uuid.uuid4(),
            hotel_code='HOTEL-SH-001',
            hotel_name='上海外滩华尔道夫酒店',
            country_code='CN',
            city_name='上海',
            hotel_star=5,
            status='ACTIVE'
        )
        
        # 创建测试工厂
        self.factory = RequestFactory()
    
    def test_get_filtered_resources_with_beijing(self):
        """测试获取北京的过滤资源"""
        # 创建请求
        request = self.factory.get('/admin/get_filtered_resources/', {
            'destination_id': self.destination_beijing.destination_id
        })
        request.user = self.user
        
        # 执行视图函数
        response = get_filtered_resources(request)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        # 检查city_name
        self.assertEqual(response_data['city_name'], '北京')
        
        # 检查景点数据
        attractions = response_data['attractions']
        self.assertEqual(len(attractions), 1)
        self.assertEqual(attractions[0]['attraction_name'], '故宫博物院')
        
        # 检查餐厅数据
        restaurants = response_data['restaurants']
        self.assertEqual(len(restaurants), 1)
        self.assertEqual(restaurants[0]['restaurant_name'], '全聚德烤鸭')
        
        # 检查酒店数据
        hotels = response_data['hotels']
        self.assertEqual(len(hotels), 1)
        self.assertEqual(hotels[0]['hotel_name'], '北京饭店')
    
    def test_get_filtered_resources_with_shanghai(self):
        """测试获取上海的过滤资源"""
        # 创建请求
        request = self.factory.get('/admin/get_filtered_resources/', {
            'destination_id': self.destination_shanghai.destination_id
        })
        request.user = self.user
        
        # 执行视图函数
        response = get_filtered_resources(request)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        # 检查city_name
        self.assertEqual(response_data['city_name'], '上海')
        
        # 检查景点数据
        attractions = response_data['attractions']
        self.assertEqual(len(attractions), 1)
        self.assertEqual(attractions[0]['attraction_name'], '外滩')
        
        # 检查餐厅数据
        restaurants = response_data['restaurants']
        self.assertEqual(len(restaurants), 1)
        self.assertEqual(restaurants[0]['restaurant_name'], '南翔小笼包')
        
        # 检查酒店数据
        hotels = response_data['hotels']
        self.assertEqual(len(hotels), 1)
        self.assertEqual(hotels[0]['hotel_name'], '上海外滩华尔道夫酒店')
    
    def test_get_filtered_resources_without_destination(self):
        """测试未提供destination_id时的处理"""
        # 创建请求
        request = self.factory.get('/admin/get_filtered_resources/')
        request.user = self.user
        
        # 执行视图函数
        response = get_filtered_resources(request)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        # 检查所有资源列表为空
        self.assertEqual(len(response_data['attractions']), 0)
        self.assertEqual(len(response_data['restaurants']), 0)
        self.assertEqual(len(response_data['hotels']), 0)
    
    def test_get_filtered_resources_with_invalid_destination(self):
        """测试提供无效destination_id时的处理"""
        # 创建请求
        request = self.factory.get('/admin/get_filtered_resources/', {
            'destination_id': 'invalid_destination_id'
        })
        request.user = self.user
        
        # 执行视图函数
        response = get_filtered_resources(request)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        # 检查所有资源列表为空
        self.assertEqual(len(response_data['attractions']), 0)
        self.assertEqual(len(response_data['restaurants']), 0)
        self.assertEqual(len(response_data['hotels']), 0)
    
    def test_get_filtered_resources_with_no_matching_resources(self):
        """测试destination的city_name没有匹配资源时的处理"""
        # 创建一个新的destination，其city_name为"广州"，但没有对应的资源
        destination_guangzhou = Destination.objects.create(
            destination_id=uuid.uuid4(),
            itinerary=self.itinerary,
            destination_order=3,
            city_name='广州',
            country_code='CN',
            arrival_date=datetime.now().date() + timedelta(days=2),
            departure_date=datetime.now().date() + timedelta(days=3)
        )
        
        # 创建请求
        request = self.factory.get('/admin/get_filtered_resources/', {
            'destination_id': destination_guangzhou.destination_id
        })
        request.user = self.user
        
        # 执行视图函数
        response = get_filtered_resources(request)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应内容
        import json
        response_data = json.loads(response.content.decode('utf-8'))
        
        # 检查city_name
        self.assertEqual(response_data['city_name'], '广州')
        
        # 检查所有资源列表为空
        self.assertEqual(len(response_data['attractions']), 0)
        self.assertEqual(len(response_data['restaurants']), 0)
        self.assertEqual(len(response_data['hotels']), 0)
