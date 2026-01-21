#!/usr/bin/env python
"""
测试不同数据量和格式的origin_input和requirement_json_data在Admin页面中的展示效果
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


def create_test_requirements():
    """创建测试数据"""
    print("开始创建测试数据...")
    
    # 测试用例1: 短文本原始输入 + 简单JSON结构
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
        'origin_input': '我想从北京去上海玩3天，希望住舒适型酒店，预算5000-8000元，包含往返机票。'
    }
    
    # 测试用例2: 长文本原始输入 + 复杂JSON结构
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
        'origin_input': long_input,
        'extension': {
            'special_requests': ['儿童餐食', '婴儿床'],
            'contact_info': {
                'name': '张先生',
                'phone': '138****8888'
            }
        }
    }
    
    # 测试用例3: 空输入 + 空JSON结构
    test_data_3 = {
        'base_info': {
            'origin': {
                'name': '未指定',
                'code': '',
                'type': ''
            },
            'destination_cities': ['未指定'],
            'trip_days': 1,
            'group_size': {
                'adults': 1,
                'children': 0,
                'seniors': 0,
                'total': 1
            },
            'travel_date': {
                'start_date': None,
                'end_date': None,
                'is_flexible': True
            }
        },
        'preferences': {
            'transportation': {
                'type': '',
                'notes': ''
            },
            'accommodation': {
                'level': '',
                'requirements': ''
            },
            'itinerary': {
                'rhythm': '',
                'tags': [],
                'special_constraints': {
                    'must_visit_spots': [],
                    'avoid_activities': []
                }
            }
        },
        'budget': {
            'level': '',
            'currency': 'CNY',
            'range': {
                'min': None,
                'max': None
            },
            'budget_notes': ''
        },
        'metadata': {
            'source_type': 'NaturalLanguage',
            'status': 'PendingReview',
            'assumptions': []
        },
        'origin_input': '',
        'requirement_json_data': {}
    }
    
    # 创建测试数据
    test_cases = [
        ('短文本输入 + 简单JSON', test_data_1),
        ('长文本输入 + 复杂JSON', test_data_2),
        ('空输入 + 空JSON', test_data_3)
    ]
    
    for name, data in test_cases:
        try:
            requirement = RequirementService.create_requirement_from_json(data)
            print(f"✓ 成功创建测试数据: {name}")
            print(f"  Requirement ID: {requirement.requirement_id}")
            print(f"  Origin Input长度: {len(data.get('origin_input', ''))} 字符")
            print(f"  JSON数据复杂度: {len(json.dumps(data))} 字符")
            print()
        except Exception as e:
            print(f"✗ 创建测试数据失败: {name}")
            print(f"  错误信息: {str(e)}")
            print()
    
    print("测试数据创建完成！")
    print("请登录Admin页面查看展示效果:")
    print("http://localhost:7000/admin/apps/requirement/")


if __name__ == '__main__':
    create_test_requirements()
