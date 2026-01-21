#!/usr/bin/env python
"""
测试客户原始输入文字是否被正确记录到数据库中
"""

import os
import sys
import json
from datetime import datetime

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.models import Requirement
from services.llm.persistence import RequirementService


def test_origin_input_saving():
    """测试origin_input字段的保存功能"""
    print("开始测试客户原始输入文字的保存功能...")
    
    # 测试用例1: 短文本输入
    short_input = '我想从北京去上海玩3天，希望住舒适型酒店，预算5000-8000元，包含往返机票。'
    test_data_1 = {
        'base_info': {
            'origin': {
                'name': '北京',
                'code': 'BJS',
                'type': 'city'
            },
            'destination_cities': ['上海'],
            'trip_days': 3,
            'group_size': {
                'adults': 2,
                'children': 0,
                'seniors': 0,
                'total': 2
            },
            'travel_date': {
                'start_date': '2026-02-01',
                'end_date': '2026-02-03',
                'is_flexible': False
            }
        },
        'preferences': {
            'transportation': {
                'type': 'RoundTripFlight',
                'notes': '希望选择早上的航班'
            },
            'accommodation': {
                'level': 'Comfort',
                'requirements': '需要安静的房间'
            },
            'itinerary': {
                'rhythm': 'Relaxed',
                'tags': ['购物', '美食'],
                'special_constraints': {
                    'must_visit_spots': ['外滩', '豫园'],
                    'avoid_activities': ['高强度运动']
                }
            }
        },
        'budget': {
            'level': 'Comfort',
            'currency': 'CNY',
            'range': {
                'min': 5000,
                'max': 8000
            },
            'budget_notes': '包含往返机票'
        },
        'metadata': {
            'source_type': 'NaturalLanguage',
            'status': 'PendingReview',
            'assumptions': ['默认使用舒适型酒店', '默认选择双飞']
        },
        'origin_input': short_input
    }
    
    # 测试用例2: 长文本输入
    long_input = '''
您好！我计划在2026年春节期间和家人一起去三亚旅游，具体需求如下：

1. 出行人数：4人（2个成人，2个儿童，分别是6岁和8岁）
2. 出行时间：2026年2月1日至2月7日，共7天
3. 交通方式：希望选择双飞，最好是直飞航班
4. 住宿要求：
   - 酒店等级：豪华型
   - 房间要求：需要2间房，都要有海景阳台
   - 其他：希望酒店有儿童俱乐部和游泳池
5. 行程安排：
   - 节奏：适中，不要太紧凑
   - 必去景点：亚龙湾、蜈支洲岛、天涯海角
   - 偏好：喜欢海滩活动，希望安排一些水上项目
6. 预算：
   - 总预算：20000-25000元
   - 包含：往返机票、酒店住宿、主要景点门票

请帮我安排一个合适的行程，谢谢！
    '''.strip()
    
    test_data_2 = {
        'base_info': {
            'origin': {
                'name': '广州',
                'code': 'CAN',
                'type': 'city'
            },
            'destination_cities': ['三亚'],
            'trip_days': 7,
            'group_size': {
                'adults': 2,
                'children': 2,
                'seniors': 0,
                'total': 4
            },
            'travel_date': {
                'start_date': '2026-02-01',
                'end_date': '2026-02-07',
                'is_flexible': False
            }
        },
        'preferences': {
            'transportation': {
                'type': 'RoundTripFlight',
                'notes': '希望选择直飞航班，时间最好在上午'
            },
            'accommodation': {
                'level': 'Luxury',
                'requirements': '需要2间房，都要有海景阳台，酒店有儿童俱乐部和游泳池'
            },
            'itinerary': {
                'rhythm': 'Moderate',
                'tags': ['海滩', '水上活动', '家庭游'],
                'special_constraints': {
                    'must_visit_spots': ['亚龙湾', '蜈支洲岛', '天涯海角'],
                    'avoid_activities': ['高强度运动', '长时间车程']
                }
            }
        },
        'budget': {
            'level': 'Luxury',
            'currency': 'CNY',
            'range': {
                'min': 20000,
                'max': 25000
            },
            'budget_notes': '包含往返机票、酒店住宿、主要景点门票'
        },
        'metadata': {
            'source_type': 'NaturalLanguage',
            'status': 'PendingReview',
            'assumptions': ['默认使用豪华型酒店', '默认选择双飞', '默认安排家庭友好型活动']
        },
        'origin_input': long_input
    }
    
    # 创建测试数据
    test_cases = [
        ('短文本输入', short_input, test_data_1),
        ('长文本输入', long_input, test_data_2)
    ]
    
    for name, expected_input, data in test_cases:
        try:
            print(f"\n测试 {name}:")
            print(f"预期输入长度: {len(expected_input)} 字符")
            
            # 创建需求
            requirement = RequirementService.create_requirement_from_json(data)
            print(f"✓ 成功创建需求: {requirement.requirement_id}")
            
            # 从数据库重新获取需求
            db_requirement = Requirement.objects.get(requirement_id=requirement.requirement_id)
            actual_input = db_requirement.origin_input
            print(f"数据库中实际输入长度: {len(actual_input)} 字符")
            
            # 验证输入是否正确保存
            if actual_input == expected_input:
                print(f"✓ 输入内容匹配")
            else:
                print(f"✗ 输入内容不匹配")
                print(f"预期前20个字符: '{expected_input[:20]}...'")
                print(f"实际前20个字符: '{actual_input[:20]}...'")
            
            # 验证requirement_json_data是否正确保存
            if db_requirement.requirement_json_data:
                print(f"✓ requirement_json_data 已保存")
                if isinstance(db_requirement.requirement_json_data, dict):
                    print(f"  JSON数据类型: 字典")
                    print(f"  JSON数据包含origin_input: {'origin_input' in db_requirement.requirement_json_data}")
            else:
                print(f"✗ requirement_json_data 未保存")
                
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
    
    # 测试更新功能
    print("\n测试更新功能:")
    try:
        # 获取最近创建的需求
        latest_req = Requirement.objects.order_by('-created_at').first()
        if latest_req:
            print(f"更新需求: {latest_req.requirement_id}")
            
            # 新的输入内容
            new_input = '这是更新后的测试输入，用于测试更新功能是否正常工作。'
            update_data = {
                'origin_input': new_input
            }
            
            # 更新需求
            updated_req = RequirementService.update_requirement_from_json(latest_req.requirement_id, update_data)
            print(f"✓ 成功更新需求")
            
            # 验证更新是否成功
            db_updated_req = Requirement.objects.get(requirement_id=updated_req.requirement_id)
            if db_updated_req.origin_input == new_input:
                print(f"✓ 更新后输入内容匹配")
            else:
                print(f"✗ 更新后输入内容不匹配")
        else:
            print(f"✗ 没有找到可更新的需求")
            
    except Exception as e:
        print(f"✗ 更新测试失败: {str(e)}")
    
    print("\n测试完成！")


if __name__ == '__main__':
    test_origin_input_saving()
