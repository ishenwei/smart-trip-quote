import os
import sys
import django
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    from django.test import TestCase, RequestFactory, Client
    from django.contrib.auth.models import User
    from django.contrib.messages.storage.fallback import FallbackStorage
    from apps.models import Requirement
    from apps.admin.views import generate_itinerary
    from apps.admin.requirement import RequirementAdmin
    from django.contrib.admin.sites import AdminSite
    from django.shortcuts import get_object_or_404
    DJANGO_AVAILABLE = True
except Exception as e:
    print(f"警告: Django初始化失败，将使用mock模式运行测试: {str(e)}")
    DJANGO_AVAILABLE = False


class TestReport:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def add_result(self, test_name: str, passed: bool, message: str = "", details: str = ""):
        self.test_results.append({
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*80)
        print("测试结果汇总")
        print("="*80)
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests} ✓")
        print(f"失败: {self.failed_tests} ✗")
        print(f"通过率: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"执行时间: {duration:.2f}秒")
        print("="*80)
        
        if self.failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ✗ {result['test_name']}")
                    if result['message']:
                        print(f"    原因: {result['message']}")
                    if result['details']:
                        print(f"    详情: {result['details']}")
    
    def save_report(self, filename: str = None):
        if filename is None:
            filename = f"itinerary_webhook_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'pass_rate': f"{(self.passed_tests/self.total_tests*100):.1f}%",
                'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat()
            },
            'test_results': self.test_results
        }
        
        report_path = os.path.join(os.path.dirname(__file__), 'reports', filename)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存到: {report_path}")


class MockRequest:
    def __init__(self, user, method='POST', data=None):
        self.user = user
        self.auser = user
        self.method = method
        self.POST = data or {}
        self.GET = {}
        self.session = {}
        self.COOKIES = {}
        self._messages = FallbackStorage(self)
        self.META = {
            'HTTP_X_CSRFTOKEN': 'test-csrf-token',
            'REMOTE_ADDR': '127.0.0.1',
            'SCRIPT_NAME': ''
        }
        self.resolver_match = Mock()
        self.resolver_match.url_name = 'admin:apps_requirement_changelist'


class ItineraryWebhookTest:
    def __init__(self):
        self.report = TestReport()
        self.factory = RequestFactory()
        self.client = Client()
        self.site = AdminSite()
        self.admin = RequirementAdmin(Requirement, self.site)
        self.test_requirement = None
        self.test_user = None
        
    def setup_test_data(self):
        print("设置测试数据...")
        
        if not DJANGO_AVAILABLE:
            print("⚠ Django不可用，使用mock数据")
            self.test_user = Mock(username='test_webhook_user')
            self.test_requirement = Mock(
                requirement_id='REQ-WEBHOOK-TEST-001',
                pk='test-pk-001',
                origin_name='北京',
                origin_code='BJS',
                origin_type='International',
                destination_cities=[
                    {'name': '西安', 'code': 'SIA', 'stay_days': 3},
                    {'name': '成都', 'code': 'CTU', 'stay_days': 2}
                ],
                trip_days=5,
                group_adults=2,
                group_children=1,
                group_seniors=0,
                group_total=3,
                travel_start_date=datetime.strptime('2026-05-01', '%Y-%m-%d'),
                travel_end_date=datetime.strptime('2026-05-05', '%Y-%m-%d'),
                travel_date_flexible=False,
                transportation_type='HighSpeedTrain',
                transportation_notes='优先选二等座',
                hotel_level='Comfort',
                hotel_requirements='需要一间家庭房',
                trip_rhythm='Moderate',
                preference_tags=['History', 'Food'],
                must_visit_spots=['秦始皇兵马俑博物馆'],
                avoid_activities=['徒步登山'],
                budget_level='Comfort',
                budget_currency='CNY',
                budget_min=5000,
                budget_max=8000,
                budget_notes='包含大交通',
                source_type='NaturalLanguage',
                status='PendingReview',
                assumptions=[],
                created_by='test_user',
                is_template=False
            )
            self.test_requirement.to_json = Mock(return_value={
                'requirement_id': 'REQ-WEBHOOK-TEST-001',
                'base_info': {
                    'origin': {
                        'name': '北京',
                        'code': 'BJS',
                        'type': 'International'
                    },
                    'destination_cities': [
                        {'name': '西安', 'code': 'SIA', 'stay_days': 3},
                        {'name': '成都', 'code': 'CTU', 'stay_days': 2}
                    ],
                    'trip_days': 5,
                    'group_size': {
                        'adults': 2,
                        'children': 1,
                        'seniors': 0,
                        'total': 3
                    },
                    'travel_date': {
                        'start_date': '2026-05-01',
                        'end_date': '2026-05-05',
                        'is_flexible': False
                    }
                },
                'preferences': {
                    'transportation': {
                        'type': 'HighSpeedTrain',
                        'notes': '优先选二等座'
                    },
                    'accommodation': {
                        'level': 'Comfort',
                        'requirements': '需要一间家庭房'
                    },
                    'trip_rhythm': 'Moderate',
                    'preference_tags': ['History', 'Food'],
                    'must_visit_spots': ['秦始皇兵马俑博物馆'],
                    'avoid_activities': ['徒步登山']
                },
                'budget': {
                    'level': 'Comfort',
                    'currency': 'CNY',
                    'min': 5000,
                    'max': 8000,
                    'notes': '包含大交通'
                }
            })
            print(f"✓ 测试数据设置完成 (mock模式)")
            print(f"  - 测试用户: {self.test_user.username}")
            print(f"  - 测试需求: {self.test_requirement.requirement_id}")
            return
        
        User.objects.filter(username='test_webhook_user').delete()
        Requirement.objects.filter(requirement_id__startswith='REQ-WEBHOOK-TEST').delete()
        
        self.test_user = User.objects.create_superuser(
            username='test_webhook_user',
            email='test@example.com',
            password='test_password'
        )
        
        self.test_requirement = Requirement.objects.create(
            requirement_id='REQ-WEBHOOK-TEST-001',
            origin_name='北京',
            origin_code='BJS',
            origin_type='International',
            destination_cities=[
                {'name': '西安', 'code': 'SIA', 'stay_days': 3},
                {'name': '成都', 'code': 'CTU', 'stay_days': 2}
            ],
            trip_days=5,
            group_adults=2,
            group_children=1,
            group_seniors=0,
            group_total=3,
            travel_start_date='2026-05-01',
            travel_end_date='2026-05-05',
            travel_date_flexible=False,
            transportation_type='HighSpeedTrain',
            transportation_notes='优先选二等座',
            hotel_level='Comfort',
            hotel_requirements='需要一间家庭房',
            trip_rhythm='Moderate',
            preference_tags=['History', 'Food'],
            must_visit_spots=['秦始皇兵马俑博物馆'],
            avoid_activities=['徒步登山'],
            budget_level='Comfort',
            budget_currency='CNY',
            budget_min=5000,
            budget_max=8000,
            budget_notes='包含大交通',
            source_type='NaturalLanguage',
            status='PendingReview',
            assumptions=[],
            created_by='test_user',
            is_template=False
        )
        
        print(f"✓ 测试数据设置完成")
        print(f"  - 测试用户: {self.test_user.username}")
        print(f"  - 测试需求: {self.test_requirement.requirement_id}")
    
    def test_1_webhook_request_structure(self):
        print("\n测试1: 验证webhook请求数据结构")
        
        try:
            webhook_data = self.test_requirement.to_json()
            
            required_fields = [
                'requirement_id',
                'base_info',
                'preferences',
                'budget'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in webhook_data:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.report.add_result(
                    "webhook请求数据结构",
                    True,
                    f"包含所有必需字段: {len(required_fields)}个"
                )
                print("✓ webhook数据结构完整")
            else:
                self.report.add_result(
                    "webhook请求数据结构",
                    False,
                    "缺少必需字段",
                    f"缺失: {', '.join(missing_fields)}"
                )
                print(f"✗ 缺少必需字段: {', '.join(missing_fields)}")
                
        except Exception as e:
            self.report.add_result(
                "webhook请求数据结构",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_2_webhook_success_scenario(self):
        print("\n测试2: 测试webhook成功调用场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.text = AsyncMock(return_value='{"status": "success"}')
                    
                    mock_post = AsyncMock()
                    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
                    mock_post.__aexit__ = AsyncMock()
                    
                    mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_post)
                    mock_session.return_value.__aexit__ = AsyncMock()
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                        
                        if result.status_code == 200:
                            json_data = json.loads(result.content)
                            if json_data.get('success'):
                                self.report.add_result(
                                    "webhook成功调用场景",
                                    True,
                                    "webhook调用成功"
                                )
                                print("✓ webhook调用成功")
                            else:
                                self.report.add_result(
                                    "webhook成功调用场景",
                                    False,
                                    json_data.get('error', '未知错误')
                                )
                                print(f"✗ webhook调用失败: {json_data.get('error', '未知错误')}")
                        else:
                            self.report.add_result(
                                "webhook成功调用场景",
                                False,
                                f"HTTP状态码错误: {result.status_code}"
                            )
                            print(f"✗ HTTP状态码错误: {result.status_code}")
                        
        except Exception as e:
            self.report.add_result(
                "webhook成功调用场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_3_webhook_network_error(self):
        print("\n测试3: 测试网络异常场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_session.return_value.__aenter__.side_effect = Exception("Network error")
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                    
                    json_data = json.loads(result.content)
                    
                    if not json_data.get('success'):
                        self.report.add_result(
                            "网络异常场景",
                            True,
                            "网络异常被正确处理"
                        )
                        print("✓ 网络异常被正确处理")
                    else:
                        self.report.add_result(
                            "网络异常场景",
                            False,
                            "网络异常未被正确处理"
                        )
                        print("✗ 网络异常未被正确处理")
                        
        except Exception as e:
            self.report.add_result(
                "网络异常场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_4_webhook_unavailable(self):
        print("\n测试4: 测试webhook不可用场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = ''
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                    mock_get_object.return_value = self.test_requirement
                    
                    result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                
                json_data = json.loads(result.content)
                
                if result.status_code == 500 and 'webhook URL未配置' in json_data.get('error', ''):
                    self.report.add_result(
                        "webhook不可用场景",
                        True,
                        "webhook URL未配置被正确检测"
                    )
                    print("✓ webhook URL未配置被正确检测")
                else:
                    self.report.add_result(
                        "webhook不可用场景",
                        False,
                        "webhook不可用场景处理不正确"
                    )
                    print("✗ webhook不可用场景处理不正确")
                    
        except Exception as e:
            self.report.add_result(
                "webhook不可用场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_5_webhook_api_key_missing(self):
        print("\n测试5: 测试API密钥缺失场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = ''
                
                with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                    mock_get_object.return_value = self.test_requirement
                    
                    result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                
                json_data = json.loads(result.content)
                
                if result.status_code == 500 and 'API密钥未配置' in json_data.get('error', ''):
                    self.report.add_result(
                        "API密钥缺失场景",
                        True,
                        "API密钥未配置被正确检测"
                    )
                    print("✓ API密钥未配置被正确检测")
                else:
                    self.report.add_result(
                        "API密钥缺失场景",
                        False,
                        "API密钥缺失场景处理不正确"
                    )
                    print("✗ API密钥缺失场景处理不正确")
                    
        except Exception as e:
            self.report.add_result(
                "API密钥缺失场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_6_webhook_server_error(self):
        print("\n测试6: 测试webhook服务器错误场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_response = AsyncMock()
                    mock_response.status = 500
                    mock_response.text = AsyncMock(return_value='Internal Server Error')
                    
                    mock_post = AsyncMock()
                    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
                    mock_post.__aexit__ = AsyncMock()
                    
                    mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_post)
                    mock_session.return_value.__aexit__ = AsyncMock()
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                    
                    json_data = json.loads(result.content)
                    
                    if not json_data.get('success'):
                        self.report.add_result(
                            "webhook服务器错误场景",
                            True,
                            "服务器错误被正确处理"
                        )
                        print("✓ 服务器错误被正确处理")
                    else:
                        self.report.add_result(
                            "webhook服务器错误场景",
                            False,
                            "服务器错误未被正确处理"
                        )
                        print("✗ 服务器错误未被正确处理")
                        
        except Exception as e:
            self.report.add_result(
                "webhook服务器错误场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_7_webhook_timeout(self):
        print("\n测试7: 测试webhook超时场景")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_session.return_value.__aenter__.side_effect = asyncio.TimeoutError("Request timeout")
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                    
                    json_data = json.loads(result.content)
                    
                    if not json_data.get('success'):
                        self.report.add_result(
                            "webhook超时场景",
                            True,
                            "超时错误被正确处理"
                        )
                        print("✓ 超时错误被正确处理")
                    else:
                        self.report.add_result(
                            "webhook超时场景",
                            False,
                            "超时错误未被正确处理"
                        )
                        print("✗ 超时错误未被正确处理")
                        
        except Exception as e:
            self.report.add_result(
                "webhook超时场景",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_8_webhook_request_headers(self):
        print("\n测试8: 验证webhook请求头")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                captured_headers = {}
                
                def capture_post(*args, **kwargs):
                    captured_headers.update(kwargs.get('headers', {}))
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.text = AsyncMock(return_value='Success')
                    mock_post = AsyncMock()
                    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
                    mock_post.__aexit__ = AsyncMock()
                    return mock_post
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_session.return_value.__aenter__ = AsyncMock(side_effect=capture_post)
                    mock_session.return_value.__aexit__ = AsyncMock()
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                    
                    required_headers = ['Content-Type', 'X-API-Key', 'X-Request-ID']
                    missing_headers = []
                    
                    for header in required_headers:
                        if header not in captured_headers:
                            missing_headers.append(header)
                    
                    if not missing_headers:
                        self.report.add_result(
                            "webhook请求头验证",
                            True,
                            f"包含所有必需请求头: {len(required_headers)}个"
                        )
                        print("✓ webhook请求头完整")
                        print(f"  请求头: {list(captured_headers.keys())}")
                    else:
                        self.report.add_result(
                            "webhook请求头验证",
                            False,
                            "缺少必需请求头",
                            f"缺失: {', '.join(missing_headers)}"
                        )
                        print(f"✗ 缺少必需请求头: {', '.join(missing_headers)}")
                        
        except Exception as e:
            self.report.add_result(
                "webhook请求头验证",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_9_webhook_retry_mechanism(self):
        print("\n测试9: 测试webhook重试机制")
        
        try:
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                attempt_count = [0]
                
                def create_mock_post():
                    attempt_count[0] += 1
                    
                    mock_response = AsyncMock()
                    
                    if attempt_count[0] < 3:
                        mock_response.status = 500
                        mock_response.text = AsyncMock(return_value='Server Error')
                    else:
                        mock_response.status = 200
                        mock_response.text = AsyncMock(return_value='Success')
                    
                    mock_post = AsyncMock()
                    mock_post.__aenter__ = AsyncMock(return_value=mock_response)
                    mock_post.__aexit__ = AsyncMock()
                    return mock_post
                
                with patch('aiohttp.ClientSession') as mock_session:
                    mock_session.return_value.__aenter__ = AsyncMock(side_effect=create_mock_post)
                    mock_session.return_value.__aexit__ = AsyncMock()
                    
                    with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                        mock_get_object.return_value = self.test_requirement
                        
                        result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
                    
                    if attempt_count[0] > 1:
                        self.report.add_result(
                            "webhook重试机制",
                            True,
                            f"重试机制正常工作，共尝试 {attempt_count[0]} 次"
                        )
                        print(f"✓ 重试机制正常工作，共尝试 {attempt_count[0]} 次")
                    else:
                        self.report.add_result(
                            "webhook重试机制",
                            False,
                            "重试机制未触发"
                        )
                        print("✗ 重试机制未触发")
                        
        except Exception as e:
            self.report.add_result(
                "webhook重试机制",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_10_requirement_data_validation(self):
        print("\n测试10: 测试需求数据验证")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "需求数据验证",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            invalid_requirement = Requirement.objects.create(
                requirement_id='REQ-WEBHOOK-TEST-002',
                origin_name='上海',
                origin_code='SHA',
                origin_type='International',
                destination_cities=[],
                trip_days=0,
                group_adults=0,
                group_children=0,
                group_seniors=0,
                group_total=0,
                travel_start_date='2026-05-01',
                travel_end_date='2026-05-05',
                travel_date_flexible=False,
                transportation_type='HighSpeedTrain',
                hotel_level='Comfort',
                trip_rhythm='Moderate',
                preference_tags=[],
                must_visit_spots=[],
                avoid_activities=[],
                budget_level='Comfort',
                budget_currency='CNY',
                budget_min=5000,
                budget_max=8000,
                source_type='NaturalLanguage',
                status='PendingReview',
                assumptions=[],
                created_by='test_user',
                is_template=False
            )
            
            request = MockRequest(self.test_user, method='POST')
            
            with patch('django.conf.settings') as mock_settings:
                mock_settings.N8N_WEBHOOK_URL = 'https://test-n8n.example.com/webhook'
                mock_settings.N8N_API_KEY = 'test-api-key-12345'
                
                with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                    mock_get_object.return_value = invalid_requirement
                    
                    result = asyncio.run(generate_itinerary(request, str(invalid_requirement.pk)))
                
                json_data = json.loads(result.content)
                
                if result.status_code == 400 and not json_data.get('success'):
                    self.report.add_result(
                        "需求数据验证",
                        True,
                        "无效数据被正确拒绝"
                    )
                    print(f"✓ 无效数据被正确拒绝: {json_data.get('error', '')}")
                else:
                    self.report.add_result(
                        "需求数据验证",
                        False,
                        "无效数据未被正确拒绝"
                    )
                    print("✗ 无效数据未被正确拒绝")
                    
        except Exception as e:
            self.report.add_result(
                "需求数据验证",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_11_http_method_validation(self):
        print("\n测试11: 测试HTTP方法验证")
        
        try:
            request = MockRequest(self.test_user, method='GET')
            
            with patch('django.shortcuts.get_object_or_404') as mock_get_object:
                mock_get_object.return_value = self.test_requirement
                
                result = asyncio.run(generate_itinerary(request, str(self.test_requirement.pk)))
            
            if result.status_code == 405:
                self.report.add_result(
                    "HTTP方法验证",
                    True,
                    "非POST请求被正确拒绝"
                )
                print("✓ 非POST请求被正确拒绝")
            else:
                self.report.add_result(
                    "HTTP方法验证",
                    False,
                    "HTTP方法验证不正确"
                )
                print("✗ HTTP方法验证不正确")
                
        except Exception as e:
            self.report.add_result(
                "HTTP方法验证",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_12_button_exists_in_detail_page(self):
        print("\n测试12: 验证旅游行程规划按钮在详情页中存在")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "旅游行程规划按钮存在性检查",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            button_exists = 'itinerary-plan-btn' in response_content
            button_text = '旅游行程规划' in response_content
            message_div = 'itinerary-plan-message' in response_content
            
            if button_exists and button_text and message_div:
                self.report.add_result(
                    "旅游行程规划按钮存在性检查",
                    True,
                    "按钮、文本和消息容器都存在"
                )
                print("✓ 按钮在详情页中正确显示")
            else:
                details = []
                if not button_exists:
                    details.append("按钮ID不存在")
                if not button_text:
                    details.append("按钮文本不存在")
                if not message_div:
                    details.append("消息容器不存在")
                
                self.report.add_result(
                    "旅游行程规划按钮存在性检查",
                    False,
                    "按钮元素不完整",
                    ", ".join(details)
                )
                print(f"✗ 按钮元素不完整: {', '.join(details)}")
                
        except Exception as e:
            self.report.add_result(
                "旅游行程规划按钮存在性检查",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_13_button_click_event_binding(self):
        print("\n测试13: 验证按钮点击事件绑定")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "按钮点击事件绑定",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            event_binding = 'addEventListener("click"' in response_content
            fetch_call = 'fetch("/admin/apps/requirement/' in response_content
            generate_itinerary_endpoint = '/generate-itinerary/' in response_content
            post_method = 'method: "POST"' in response_content
            
            checks = {
                '事件绑定': event_binding,
                'API调用': fetch_call,
                '端点路径': generate_itinerary_endpoint,
                'POST方法': post_method
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "按钮点击事件绑定",
                    True,
                    "所有事件绑定检查通过"
                )
                print("✓ 按钮点击事件正确绑定")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "按钮点击事件绑定",
                    False,
                    "事件绑定不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 事件绑定不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "按钮点击事件绑定",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_14_button_state_during_request(self):
        print("\n测试14: 测试按钮请求期间状态")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "按钮请求期间状态",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_disabled_state = 'btn.disabled = true' in response_content
            has_opacity_change = 'btn.style.opacity = "0.6"' in response_content
            has_loading_text = 'btn.innerHTML = "处理中..."' in response_content
            has_submitting_flag = 'isSubmitting = true' in response_content
            has_prevent_duplicate = 'if (isSubmitting) return;' in response_content
            
            checks = {
                '禁用状态': has_disabled_state,
                '透明度变化': has_opacity_change,
                '加载文本': has_loading_text,
                '提交标志': has_submitting_flag,
                '防止重复提交': has_prevent_duplicate
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "按钮请求期间状态",
                    True,
                    "所有状态管理检查通过"
                )
                print("✓ 按钮状态管理完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "按钮请求期间状态",
                    False,
                    "状态管理不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 状态管理不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "按钮请求期间状态",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_15_error_message_display(self):
        print("\n测试15: 测试错误消息显示")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "错误消息显示",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_error_handling = '.catch(error =>' in response_content
            has_error_display = 'messageDiv.style.backgroundColor = "#f8d7da"' in response_content
            has_error_text = 'messageDiv.style.color = "#721c24"' in response_content
            has_error_border = 'messageDiv.style.border = "1px solid #f5c6cb"' in response_content
            has_network_error_msg = '网络错误: 请稍后重试' in response_content
            
            checks = {
                '错误处理': has_error_handling,
                '错误背景色': has_error_display,
                '错误文本色': has_error_text,
                '错误边框': has_error_border,
                '网络错误消息': has_network_error_msg
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "错误消息显示",
                    True,
                    "所有错误消息检查通过"
                )
                print("✓ 错误消息显示完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "错误消息显示",
                    False,
                    "错误消息显示不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 错误消息显示不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "错误消息显示",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_16_success_message_display(self):
        print("\n测试16: 测试成功消息显示")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "成功消息显示",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_success_handling = 'if (data.success)' in response_content
            has_success_display = 'messageDiv.style.backgroundColor = "#d4edda"' in response_content
            has_success_text = 'messageDiv.style.color = "#155724"' in response_content
            has_success_border = 'messageDiv.style.border = "1px solid #c3e6cb"' in response_content
            has_success_message = '旅游行程规划设计中' in response_content
            
            checks = {
                '成功处理': has_success_handling,
                '成功背景色': has_success_display,
                '成功文本色': has_success_text,
                '成功边框': has_success_border,
                '成功消息': has_success_message
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "成功消息显示",
                    True,
                    "所有成功消息检查通过"
                )
                print("✓ 成功消息显示完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "成功消息显示",
                    False,
                    "成功消息显示不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 成功消息显示不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "成功消息显示",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_17_csrf_token_handling(self):
        print("\n测试17: 测试CSRF令牌处理")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "CSRF令牌处理",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_get_cookie_func = 'function getCookie(name)' in response_content
            has_csrf_header = '"X-CSRFToken": getCookie("csrftoken")' in response_content
            has_cookie_parsing = 'document.cookie.split' in response_content
            
            checks = {
                'getCookie函数': has_get_cookie_func,
                'CSRF令牌头': has_csrf_header,
                'Cookie解析': has_cookie_parsing
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "CSRF令牌处理",
                    True,
                    "所有CSRF处理检查通过"
                )
                print("✓ CSRF令牌处理完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "CSRF令牌处理",
                    False,
                    "CSRF处理不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ CSRF处理不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "CSRF令牌处理",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_18_button_state_restoration(self):
        print("\n测试18: 测试按钮状态恢复")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "按钮状态恢复",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_finally_block = '.finally(() =>' in response_content
            has_enable_button = 'btn.disabled = false' in response_content
            has_restore_opacity = 'btn.style.opacity = "1"' in response_content
            has_restore_text = 'btn.innerHTML = "旅游行程规划"' in response_content
            has_reset_flag = 'isSubmitting = false' in response_content
            
            checks = {
                'finally块': has_finally_block,
                '启用按钮': has_enable_button,
                '恢复透明度': has_restore_opacity,
                '恢复文本': has_restore_text,
                '重置标志': has_reset_flag
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "按钮状态恢复",
                    True,
                    "所有状态恢复检查通过"
                )
                print("✓ 按钮状态恢复完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "按钮状态恢复",
                    False,
                    "状态恢复不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 状态恢复不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "按钮状态恢复",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_19_requirement_id_parameter(self):
        print("\n测试19: 测试需求ID参数传递")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "需求ID参数传递",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_data_attribute = 'data-requirement-id' in response_content
            has_id_retrieval = 'btn.dataset.requirementId' in response_content
            has_id_in_url = 'requirementId' in response_content
            
            checks = {
                'data属性': has_data_attribute,
                'ID获取': has_id_retrieval,
                'URL中使用': has_id_in_url
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "需求ID参数传递",
                    True,
                    "所有ID传递检查通过"
                )
                print("✓ 需求ID参数传递完整")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "需求ID参数传递",
                    False,
                    "ID传递不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ ID传递不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "需求ID参数传递",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def test_20_webhook_endpoint_url(self):
        print("\n测试20: 验证webhook端点URL")
        
        try:
            if not DJANGO_AVAILABLE:
                self.report.add_result(
                    "webhook端点URL验证",
                    False,
                    "Django不可用，跳过此测试"
                )
                print("⚠ Django不可用，跳过此测试")
                return
            
            request = MockRequest(self.test_user, method='GET')
            
            response = self.admin.change_view(
                request,
                str(self.test_requirement.pk),
                extra_context={}
            )
            
            response_content = response.content.decode('utf-8')
            
            has_correct_endpoint = '/generate-itinerary/' in response_content
            has_correct_method = 'method: "POST"' in response_content
            has_content_type = 'Content-Type' in response_content
            
            checks = {
                '端点URL': has_correct_endpoint,
                '请求方法': has_correct_method,
                '内容类型': has_content_type
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                self.report.add_result(
                    "webhook端点URL验证",
                    True,
                    "所有端点URL检查通过"
                )
                print("✓ webhook端点URL配置正确")
            else:
                failed_checks = [k for k, v in checks.items() if not v]
                self.report.add_result(
                    "webhook端点URL验证",
                    False,
                    "端点URL配置不完整",
                    f"缺失: {', '.join(failed_checks)}"
                )
                print(f"✗ 端点URL配置不完整: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.report.add_result(
                "webhook端点URL验证",
                False,
                f"测试异常: {str(e)}"
            )
            print(f"✗ 测试异常: {str(e)}")
    
    def run_all_tests(self):
        print("="*80)
        print("旅游行程规划按钮与n8n webhook功能测试")
        print("="*80)
        
        try:
            self.setup_test_data()
            
            tests = [
                self.test_1_webhook_request_structure,
                self.test_2_webhook_success_scenario,
                self.test_3_webhook_network_error,
                self.test_4_webhook_unavailable,
                self.test_5_webhook_api_key_missing,
                self.test_6_webhook_server_error,
                self.test_7_webhook_timeout,
                self.test_8_webhook_request_headers,
                self.test_9_webhook_retry_mechanism,
                self.test_10_requirement_data_validation,
                self.test_11_http_method_validation,
                self.test_12_button_exists_in_detail_page,
                self.test_13_button_click_event_binding,
                self.test_14_button_state_during_request,
                self.test_15_error_message_display,
                self.test_16_success_message_display,
                self.test_17_csrf_token_handling,
                self.test_18_button_state_restoration,
                self.test_19_requirement_id_parameter,
                self.test_20_webhook_endpoint_url
            ]
            
            for test in tests:
                try:
                    test()
                except Exception as e:
                    print(f"✗ 测试执行异常: {str(e)}")
                    self.report.add_result(
                        f"{test.__name__}",
                        False,
                        f"测试执行异常: {str(e)}"
                    )
            
            self.report.print_summary()
            self.report.save_report()
            
        except Exception as e:
            print(f"✗ 测试套件执行失败: {str(e)}")
            self.report.add_result(
                "测试套件执行",
                False,
                f"测试套件执行失败: {str(e)}"
            )
            self.report.print_summary()
            self.report.save_report()
        
        finally:
            print("\n清理测试数据...")
            try:
                if DJANGO_AVAILABLE:
                    if self.test_requirement:
                        Requirement.objects.filter(
                            requirement_id__startswith='REQ-WEBHOOK-TEST'
                        ).delete()
                    if self.test_user:
                        User.objects.filter(username='test_webhook_user').delete()
                    print("✓ 测试数据清理完成")
                else:
                    print("✓ Mock模式，无需清理")
            except Exception as e:
                print(f"⚠ 测试数据清理异常: {str(e)}")


def main():
    tester = ItineraryWebhookTest()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
