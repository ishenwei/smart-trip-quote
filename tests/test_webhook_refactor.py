"""
Webhook 模块单元测试
测试 Serializer、Service 和 View 层的功能
"""
import json
from datetime import date, time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from apps.api.serializers.webhook_serializers import (
    ItineraryWebhookSerializer,
    RequirementWebhookSerializer,
    ItineraryOptimizationCallbackSerializer,
    N8nProcessRequirementSerializer,
    ActivitySerializer,
    DestinationSerializer,
    TravelerStatsSerializer,
    DailyScheduleSerializer,
)
from apps.api.services.webhook_services import (
    ItineraryService,
    RequirementService,
    ItineraryOptimizationService,
)
from apps.api.utils.logging_utils import LogSanitizer, SensitiveDataFilter


class ActivitySerializerTests(TestCase):
    """ActivitySerializer 测试"""
    
    def test_valid_activity(self):
        """测试有效活动数据"""
        data = {
            'activity_title': '游览景点',
            'activity_type': 'ATTRACTION',
            'start_time': '09:00:00',
            'end_time': '11:00:00',
            'activity_description': '参观博物馆'
        }
        serializer = ActivitySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_invalid_activity_type(self):
        """测试无效活动类型"""
        data = {
            'activity_title': '游览景点',
            'activity_type': 'INVALID_TYPE',
            'start_time': '09:00:00',
            'end_time': '11:00:00',
        }
        serializer = ActivitySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('activity_type', serializer.errors)
    
    def test_invalid_time_order(self):
        """测试时间顺序错误"""
        data = {
            'activity_title': '游览景点',
            'activity_type': 'ATTRACTION',
            'start_time': '11:00:00',
            'end_time': '09:00:00',
        }
        serializer = ActivitySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_time', serializer.errors)


class DestinationSerializerTests(TestCase):
    """DestinationSerializer 测试"""
    
    def test_valid_destination(self):
        """测试有效目的地数据"""
        data = {
            'destination_order': 1,
            'city_name': '上海',
            'country_code': 'CN',
            'arrival_date': '2026-04-01',
            'departure_date': '2026-04-03'
        }
        serializer = DestinationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_invalid_date_order(self):
        """测试日期顺序错误"""
        data = {
            'destination_order': 1,
            'city_name': '上海',
            'arrival_date': '2026-04-03',
            'departure_date': '2026-04-01'
        }
        serializer = DestinationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('departure_date', serializer.errors)


class TravelerStatsSerializerTests(TestCase):
    """TravelerStatsSerializer 测试"""
    
    def test_valid_traveler_stats(self):
        """测试有效旅行者统计"""
        data = {
            'adults': 2,
            'children': 1,
            'infants': 0,
            'seniors': 0
        }
        serializer = TravelerStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_zero_travelers(self):
        """测试零旅行者（无效）"""
        data = {
            'adults': 0,
            'children': 0,
            'infants': 0,
            'seniors': 0
        }
        serializer = TravelerStatsSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ItineraryWebhookSerializerTests(TestCase):
    """ItineraryWebhookSerializer 测试"""
    
    def test_valid_itinerary_data(self):
        """测试有效行程数据"""
        data = {
            'requirement_id': 'REQ_20260320_001',
            'itinerary_name': '北京三日游',
            'start_date': '2026-04-01',
            'end_date': '2026-04-03',
            'destinations': [
                {
                    'destination_order': 1,
                    'city_name': '北京',
                    'arrival_date': '2026-04-01',
                    'departure_date': '2026-04-03'
                }
            ],
            'traveler_stats': {
                'adults': 2,
                'children': 0,
                'infants': 0,
                'seniors': 0
            }
        }
        serializer = ItineraryWebhookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        data = {
            'itinerary_name': '北京三日游'
        }
        serializer = ItineraryWebhookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('requirement_id', serializer.errors)
        self.assertIn('start_date', serializer.errors)
        self.assertIn('end_date', serializer.errors)
    
    def test_empty_requirement_id(self):
        """测试空的 requirement_id"""
        data = {
            'requirement_id': '   ',
            'itinerary_name': '北京三日游',
            'start_date': '2026-04-01',
            'end_date': '2026-04-03'
        }
        serializer = ItineraryWebhookSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('requirement_id', serializer.errors)


class RequirementWebhookSerializerTests(TestCase):
    """RequirementWebhookSerializer 测试"""
    
    def test_valid_requirement_data(self):
        """测试有效需求数据"""
        data = {
            'structured_data': {
                'base_info': {
                    'origin': {'name': '上海', 'code': 'SHA'},
                    'destination_cities': ['北京'],
                    'trip_days': 3,
                    'group_size': {'adults': 2, 'total': 2},
                    'travel_date': {
                        'start_date': '2026-04-01',
                        'end_date': '2026-04-03'
                    }
                }
            }
        }
        serializer = RequirementWebhookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_output_field_extraction(self):
        """测试 output 字段提取"""
        data = {
            'output': {
                'structured_data': {
                    'base_info': {
                        'origin': {'name': '上海'},
                        'trip_days': 3
                    }
                }
            }
        }
        serializer = RequirementWebhookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIn('base_info', serializer.validated_data.get('structured_data', {}))
    
    def test_list_input_handling(self):
        """测试列表输入处理"""
        data = [
            {
                'structured_data': {
                    'base_info': {'trip_days': 3}
                }
            }
        ]
        serializer = RequirementWebhookSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        data = {}
        serializer = RequirementWebhookSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class ItineraryOptimizationCallbackSerializerTests(TestCase):
    """ItineraryOptimizationCallbackSerializer 测试"""
    
    def test_valid_callback_data(self):
        """测试有效回调数据"""
        data = {
            'itinerary_id': 'ITN_20260320_001',
            'description': '优化后的行程描述'
        }
        serializer = ItineraryOptimizationCallbackSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_empty_itinerary_id(self):
        """测试空的 itinerary_id"""
        data = {
            'itinerary_id': '',
            'description': '优化后的行程描述'
        }
        serializer = ItineraryOptimizationCallbackSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('itinerary_id', serializer.errors)


class N8nProcessRequirementSerializerTests(TestCase):
    """N8nProcessRequirementSerializer 测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        data = {
            'user_input': '我想去北京玩三天',
            'save_to_db': True
        }
        serializer = N8nProcessRequirementSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_empty_user_input(self):
        """测试空的用户输入"""
        data = {
            'user_input': '',
            'save_to_db': True
        }
        serializer = N8nProcessRequirementSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_input', serializer.errors)


class LogSanitizerTests(TestCase):
    """LogSanitizer 测试"""
    
    def test_sanitize_dict_basic(self):
        """测试基本字典脱敏"""
        data = {
            'name': '张三',
            'password': 'secret123',
            'email': 'test@example.com',
            'normal_field': 'value'
        }
        result = LogSanitizer.sanitize_dict(data)
        self.assertEqual(result['name'], '***REDACTED***')
        self.assertEqual(result['password'], '***REDACTED***')
        self.assertNotEqual(result['email'], 'test@example.com')
        self.assertEqual(result['normal_field'], 'value')
    
    def test_sanitize_dict_nested(self):
        """测试嵌套字典脱敏"""
        data = {
            'user': {
                'name': '张三',
                'credentials': {
                    'password': 'secret123',
                    'token': 'abc123'
                }
            }
        }
        result = LogSanitizer.sanitize_dict(data)
        self.assertEqual(result['user']['name'], '***REDACTED***')
        self.assertEqual(result['user']['credentials']['password'], '***REDACTED***')
        self.assertEqual(result['user']['credentials']['token'], '***REDACTED***')
    
    def test_sanitize_string_phone(self):
        """测试手机号脱敏"""
        phone = '13812345678'
        result = LogSanitizer.sanitize_string(phone)
        self.assertEqual(result, '138****5678')
    
    def test_sanitize_string_email(self):
        """测试邮箱脱敏"""
        email = 'testuser@example.com'
        result = LogSanitizer.sanitize_string(email)
        self.assertIn('***', result)
        self.assertIn('@example.com', result)
    
    def test_sanitize_string_id_card(self):
        """测试身份证号脱敏"""
        id_card = '110101199001011234'
        result = LogSanitizer.sanitize_string(id_card)
        # 验证脱敏生效（中间8位被替换为 ********）
        self.assertIn('********', result)
        self.assertEqual(len(result), 18)


class SensitiveDataFilterTests(TestCase):
    """SensitiveDataFilter 测试"""
    
    def test_filter_basic(self):
        """测试基本过滤"""
        import logging
        
        filter_instance = SensitiveDataFilter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='password=secret123',
            args=(),
            exc_info=None
        )
        
        filter_instance.filter(record)
        self.assertEqual(record.msg, 'password=***REDACTED***')


class ItineraryServiceTests(TestCase):
    """ItineraryService 测试（部分 Mock）"""
    
    @patch('apps.api.services.webhook_services.Requirement')
    def test_validate_requirement_exists_found(self, MockRequirement):
        """测试需求存在验证 - 找到"""
        from apps.models.requirement import Requirement
        
        mock_requirement = MagicMock(spec=Requirement)
        MockRequirement.objects.get.return_value = mock_requirement
        
        valid, requirement, error = ItineraryService.validate_requirement_exists('REQ_20260320_001')
        
        self.assertTrue(valid)
        self.assertEqual(requirement, mock_requirement)
        self.assertIsNone(error)
    
    @patch('apps.api.services.webhook_services.Requirement')
    def test_validate_requirement_exists_not_found(self, MockRequirement):
        """测试需求存在验证 - 未找到"""
        from apps.models.requirement import Requirement
        
        MockRequirement.DoesNotExist = Requirement.DoesNotExist
        MockRequirement.objects.get.side_effect = Requirement.DoesNotExist()
        
        valid, requirement, error = ItineraryService.validate_requirement_exists('REQ_NOT_EXIST')
        
        self.assertFalse(valid)
        self.assertIsNone(requirement)
        self.assertIn('不存在', error)


class RequirementServiceTests(TestCase):
    """RequirementService 测试"""
    
    def test_parse_date_valid(self):
        """测试日期解析 - 有效"""
        result = RequirementService.parse_date('2026-04-01')
        self.assertEqual(result, date(2026, 4, 1))
    
    def test_parse_date_invalid(self):
        """测试日期解析 - 无效"""
        result = RequirementService.parse_date('invalid-date')
        self.assertIsNone(result)
    
    def test_parse_date_empty(self):
        """测试日期解析 - 空值"""
        result = RequirementService.parse_date('')
        self.assertIsNone(result)
        result = RequirementService.parse_date(None)
        self.assertIsNone(result)
    
    def test_parse_decimal_valid(self):
        """测试 Decimal 解析 - 有效"""
        from decimal import Decimal
        result = RequirementService.parse_decimal('123.45')
        self.assertEqual(result, Decimal('123.45'))
    
    def test_parse_decimal_invalid(self):
        """测试 Decimal 解析 - 无效"""
        result = RequirementService.parse_decimal('invalid')
        self.assertIsNone(result)


class ItineraryOptimizationServiceTests(TestCase):
    """ItineraryOptimizationService 测试"""
    
    @patch('apps.api.services.webhook_services.Itinerary')
    def test_validate_itinerary_exists_found(self, MockItinerary):
        """测试行程存在验证 - 找到"""
        from apps.models.itinerary import Itinerary
        
        mock_itinerary = MagicMock(spec=Itinerary)
        MockItinerary.objects.get.return_value = mock_itinerary
        
        valid, itinerary, error = ItineraryOptimizationService.validate_itinerary_exists('ITN_20260320_001')
        
        self.assertTrue(valid)
        self.assertEqual(itinerary, mock_itinerary)
        self.assertIsNone(error)
    
    @patch('apps.api.services.webhook_services.Itinerary')
    def test_validate_itinerary_exists_not_found(self, MockItinerary):
        """测试行程存在验证 - 未找到"""
        from apps.models.itinerary import Itinerary
        
        MockItinerary.DoesNotExist = Itinerary.DoesNotExist
        MockItinerary.objects.get.side_effect = Itinerary.DoesNotExist()
        
        valid, itinerary, error = ItineraryOptimizationService.validate_itinerary_exists('ITN_NOT_EXIST')
        
        self.assertFalse(valid)
        self.assertIsNone(itinerary)
        self.assertIn('不存在', error)
