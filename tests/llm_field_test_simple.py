"""
简化的LLM字段识别测试脚本
用于快速验证关键功能
"""

import os
import sys
import json
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from services.llm.service import LLMRequirementService


def test_field_recognition():
    """测试字段识别功能"""
    service = LLMRequirementService()
    
    test_cases = [
        {
            "name": "出发地识别",
            "input": "从北京去上海旅游5天",
            "expected_fields": {
                "base_info.origin.name": "北京",
                "base_info.destination_cities[0].name": "上海",
                "base_info.trip_days": 5
            }
        },
        {
            "name": "人数识别",
            "input": "从北京去上海旅游5天，2个成人，1个儿童",
            "expected_fields": {
                "base_info.group_size.adults": 2,
                "base_info.group_size.children": 1,
                "base_info.group_size.total": 3
            }
        },
        {
            "name": "交通方式识别",
            "input": "从北京去上海旅游5天，坐高铁",
            "expected_fields": {
                "preferences.transportation.type": "HighSpeedTrain"
            }
        },
        {
            "name": "酒店等级识别",
            "input": "从北京去上海旅游5天，豪华酒店",
            "expected_fields": {
                "preferences.accommodation.level": "Luxury"
            }
        },
        {
            "name": "行程节奏识别",
            "input": "从北京去上海旅游5天，行程轻松",
            "expected_fields": {
                "preferences.itinerary.rhythm": "Relaxed"
            }
        },
        {
            "name": "预算识别",
            "input": "从北京去上海旅游5天，预算5000到10000元",
            "expected_fields": {
                "budget.level": "Comfort",
                "budget.range.min": 5000,
                "budget.range.max": 10000
            }
        },
        {
            "name": "默认值应用",
            "input": "从北京去上海旅游5天",
            "expected_fields": {
                "preferences.accommodation.level": "Comfort",
                "preferences.itinerary.rhythm": "Moderate",
                "budget.level": "Comfort"
            }
        }
    ]
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    print("="*80)
    print("LLM字段识别测试")
    print("="*80)
    
    for test_case in test_cases:
        print(f"\n{'-'*80}")
        print(f"测试: {test_case['name']}")
        print(f"输入: {test_case['input']}")
        
        try:
            result = service.process_requirement_sync(
                user_input=test_case['input'],
                save_to_db=False
            )
            
            if not result.success:
                print(f"✗ 失败: {result.error}")
                results["failed"] += 1
                results["details"].append({
                    "name": test_case['name'],
                    "status": "failed",
                    "error": result.error
                })
                continue
            
            actual = result.structured_data
            expected = test_case['expected_fields']
            
            matched = True
            mismatched = []
            
            for field_path, expected_value in expected.items():
                actual_value = get_nested_value(actual, field_path)
                
                if actual_value != expected_value:
                    matched = False
                    mismatched.append({
                        "field": field_path,
                        "expected": expected_value,
                        "actual": actual_value
                    })
            
            if matched:
                print(f"✓ 通过")
                results["passed"] += 1
                results["details"].append({
                    "name": test_case['name'],
                    "status": "passed"
                })
            else:
                print(f"✗ 失败")
                print(f"不匹配的字段:")
                for m in mismatched:
                    print(f"  - {m['field']}: 期望 {m['expected']}, 实际 {m['actual']}")
                results["failed"] += 1
                results["details"].append({
                    "name": test_case['name'],
                    "status": "failed",
                    "mismatched": mismatched
                })
        
        except Exception as e:
            print(f"✗ 异常: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "name": test_case['name'],
                "status": "error",
                "error": str(e)
            })
    
    print(f"\n{'='*80}")
    print("测试结果汇总")
    print(f"{'='*80}")
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    return results


def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """从嵌套字典中获取值"""
    keys = path.replace('[', '.').replace(']', '').split('.')
    value = data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and key.isdigit():
            index = int(key)
            if 0 <= index < len(value):
                value = value[index]
            else:
                return None
        else:
            return None
    
    return value


if __name__ == '__main__':
    results = test_field_recognition()
    
    print(f"\n{'='*80}")
    print("详细结果")
    print(f"{'='*80}")
    for detail in results['details']:
        print(f"\n{detail['name']}: {detail['status']}")
        if detail['status'] == 'failed' and 'mismatched' in detail:
            for m in detail['mismatched']:
                print(f"  - {m['field']}: 期望 {m['expected']}, 实际 {m['actual']}")
