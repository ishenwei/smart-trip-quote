#!/usr/bin/env python
"""测试webhook响应处理功能"""
import os
import sys
import json
from unittest import TestCase, mock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from tests.test_webhook import process_webhook_response

class TestWebhookProcessing(TestCase):
    """测试webhook响应处理功能"""
    
    def test_process_valid_webhook_response(self):
        """测试处理有效的webhook响应数据"""
        # 模拟有效的webhook响应数据
        mock_response_data = {
            "output": {
                "requirement_id": "TEST_20260302_001",
                "itinerary_name": "上海三日游",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03",
                "destinations": [
                    {
                        "destination_order": 1,
                        "city_name": "上海",
                        "country_code": "CN",
                        "arrival_date": "2026-04-01",
                        "departure_date": "2026-04-03"
                    }
                ],
                "traveler_stats": {
                    "total_travelers": 2,
                    "adults": 2,
                    "children": 0,
                    "infants": 0,
                    "seniors": 0
                },
                "daily_schedules": [
                    {
                        "day": 1,
                        "date": "2026-04-01",
                        "city": "上海",
                        "activities": [
                            {
                                "activity_title": "抵达上海",
                                "activity_type": "FLIGHT",
                                "activity_description": "乘坐飞机抵达上海",
                                "start_time": "10:00:00",
                                "end_time": "12:00:00",
                                "id_reference": "flight123"
                            },
                            {
                                "activity_title": "入住酒店",
                                "activity_type": "CHECK_IN",
                                "activity_description": "入住市中心酒店",
                                "start_time": "14:00:00",
                                "end_time": "15:00:00",
                                "id_reference": "hotel123"
                            }
                        ]
                    }
                ]
            }
        }
        
        # 模拟数据库操作
        with mock.patch('tests.test_webhook.transaction.atomic') as mock_atomic:
            mock_atomic.return_value.__enter__.return_value = None
            mock_atomic.return_value.__exit__.return_value = None
            
            with mock.patch('tests.test_webhook.create_itinerary') as mock_create_itinerary:
                mock_itinerary = mock.MagicMock()
                mock_itinerary.itinerary_id = 'TEST_ITINERARY_001'
                mock_itinerary.itinerary_name = '上海三日游'
                mock_create_itinerary.return_value = mock_itinerary
                
                with mock.patch('tests.test_webhook.create_destinations') as mock_create_destinations:
                    with mock.patch('tests.test_webhook.create_traveler_stats') as mock_create_traveler_stats:
                        with mock.patch('tests.test_webhook.create_daily_schedules') as mock_create_daily_schedules:
                            # 调用函数
                            result = process_webhook_response(mock_response_data)
                            
                            # 验证结果
                            self.assertTrue(result)
                            mock_create_itinerary.assert_called_once()
                            mock_create_destinations.assert_called_once()
                            mock_create_traveler_stats.assert_called_once()
                            mock_create_daily_schedules.assert_called_once()
    
    def test_process_webhook_response_without_output(self):
        """测试处理没有output字段的webhook响应数据"""
        # 模拟没有output字段的webhook响应数据
        mock_response_data = {
            "requirement_id": "TEST_20260302_001",
            "itinerary_name": "上海三日游",
            "start_date": "2026-04-01",
            "end_date": "2026-04-03",
            "destinations": [],
            "traveler_stats": {},
            "daily_schedules": []
        }
        
        # 模拟数据库操作
        with mock.patch('tests.test_webhook.transaction.atomic') as mock_atomic:
            mock_atomic.return_value.__enter__.return_value = None
            mock_atomic.return_value.__exit__.return_value = None
            
            with mock.patch('tests.test_webhook.create_itinerary') as mock_create_itinerary:
                mock_itinerary = mock.MagicMock()
                mock_itinerary.itinerary_id = 'TEST_ITINERARY_001'
                mock_itinerary.itinerary_name = '上海三日游'
                mock_create_itinerary.return_value = mock_itinerary
                
                with mock.patch('tests.test_webhook.create_destinations'):
                    with mock.patch('tests.test_webhook.create_traveler_stats'):
                        with mock.patch('tests.test_webhook.create_daily_schedules'):
                            # 调用函数
                            result = process_webhook_response(mock_response_data)
                            
                            # 验证结果
                            self.assertTrue(result)
    
    def test_process_webhook_response_missing_requirement_id(self):
        """测试处理缺少requirement_id字段的webhook响应数据"""
        # 模拟缺少requirement_id字段的webhook响应数据
        mock_response_data = {
            "output": {
                "itinerary_name": "上海三日游",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03"
            }
        }
        
        # 调用函数
        result = process_webhook_response(mock_response_data)
        
        # 验证结果
        self.assertFalse(result)
    
    def test_process_webhook_response_missing_itinerary_name(self):
        """测试处理缺少itinerary_name字段的webhook响应数据"""
        # 模拟缺少itinerary_name字段的webhook响应数据
        mock_response_data = {
            "output": {
                "requirement_id": "TEST_20260302_001",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03"
            }
        }
        
        # 调用函数
        result = process_webhook_response(mock_response_data)
        
        # 验证结果
        self.assertFalse(result)
    
    def test_process_webhook_response_db_error(self):
        """测试处理数据库操作失败的情况"""
        # 模拟有效的webhook响应数据
        mock_response_data = {
            "output": {
                "requirement_id": "TEST_20260302_001",
                "itinerary_name": "上海三日游",
                "start_date": "2026-04-01",
                "end_date": "2026-04-03",
                "destinations": [],
                "traveler_stats": {},
                "daily_schedules": []
            }
        }
        
        # 模拟数据库操作失败
        with mock.patch('tests.test_webhook.create_itinerary') as mock_create_itinerary:
            mock_create_itinerary.side_effect = Exception("数据库连接失败")
            
            # 调用函数
            result = process_webhook_response(mock_response_data)
            
            # 验证结果
            self.assertFalse(result)

if __name__ == '__main__':
    import unittest
    unittest.main()
