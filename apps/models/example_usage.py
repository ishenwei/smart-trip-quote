import os
import sys
import django

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
from apps.models import Requirement, RequirementValidator, RequirementStatusManager, TemplateManager


def create_sample_requirement():
    sample_data = {
        'requirement_id': 'REQ-20260120-001',
        'origin_name': '北京',
        'origin_code': 'BJS',
        'origin_type': 'International',
        'destination_cities': [
            {
                'name': '西安',
                'code': 'SIA',
                'stay_days': 3
            },
            {
                'name': '成都',
                'code': 'CTU',
                'stay_days': 2
            }
        ],
        'trip_days': 5,
        'group_adults': 2,
        'group_children': 1,
        'group_seniors': 0,
        'group_total': 3,
        'travel_start_date': '2026-05-01',
        'travel_end_date': '2026-05-05',
        'travel_date_flexible': False,
        'transportation_type': 'HighSpeedTrain',
        'transportation_notes': '优先选二等座，希望在上午出发',
        'hotel_level': 'Comfort',
        'hotel_requirements': '需要一间家庭房，最好靠近地铁站，带早餐',
        'trip_rhythm': 'Moderate',
        'preference_tags': ['History', 'Food', 'CityScape'],
        'must_visit_spots': ['秦始皇兵马俑博物馆', '大唐不夜城'],
        'avoid_activities': ['徒步登山'],
        'budget_level': 'Comfort',
        'budget_currency': 'CNY',
        'budget_min': 5000,
        'budget_max': 8000,
        'budget_notes': '包含大交通，不含购物支出',
        'source_type': 'NaturalLanguage',
        'status': 'PendingReview',
        'assumptions': [
            {
                'field': 'transportation.type',
                'inferred_value': 'HighSpeedTrain',
                'reason': '用户提到"坐火车快一点"，推断为高铁'
            }
        ],
        'created_by': 'user_12345',
        'reviewed_by': None,
        'is_template': False,
        'template_name': '',
        'template_category': '',
        'extension': {}
    }
    
    try:
        RequirementValidator.validate_all(sample_data)
        print("数据验证通过！")
    except Exception as e:
        print(f"数据验证失败: {e}")
        return None
    
    try:
        requirement = Requirement.objects.create(**sample_data)
        print(f"需求创建成功！ID: {requirement.requirement_id}")
        return requirement
    except Exception as e:
        print(f"需求创建失败: {e}")
        return None


def demonstrate_status_transitions():
    print("\n=== 状态流转演示 ===")
    
    requirement_id = 'REQ-20260120-001'
    
    print(f"1. 确认需求 {requirement_id}")
    try:
        requirement = RequirementStatusManager.confirm_requirement(
            requirement_id,
            reviewer='admin_001'
        )
        print(f"   状态已更新为: {requirement.get_status_display()}")
    except Exception as e:
        print(f"   操作失败: {e}")
    
    print(f"\n2. 检查状态统计")
    stats = RequirementStatusManager.get_status_statistics()
    print(f"   状态统计: {stats}")
    
    print(f"\n3. 设置过期时间")
    try:
        requirement = RequirementStatusManager.set_expiry_time(
            requirement_id,
            hours=24
        )
        print(f"   过期时间已设置: {requirement.expires_at}")
    except Exception as e:
        print(f"   操作失败: {e}")


def demonstrate_template_operations():
    print("\n=== 模板功能演示 ===")
    
    source_requirement_id = 'REQ-20260120-001'
    
    print(f"1. 从需求创建模板")
    try:
        template = TemplateManager.create_template(
            source_requirement_id,
            template_name='西安成都亲子五日游',
            template_category='FamilyTour',
            created_by='admin_001'
        )
        print(f"   模板创建成功！ID: {template.requirement_id}")
        print(f"   模板名称: {template.template_name}")
        print(f"   模板分类: {template.template_category}")
    except Exception as e:
        print(f"   操作失败: {e}")
        return None
    
    print(f"\n2. 列出所有模板")
    templates = TemplateManager.list_templates()
    print(f"   模板总数: {templates['total_count']}")
    for template in templates['templates']:
        print(f"   - {template.template_name} ({template.template_category})")
    
    print(f"\n3. 获取模板分类")
    categories = TemplateManager.get_template_categories()
    print(f"   模板分类: {categories}")
    
    print(f"\n4. 使用模板创建新需求")
    try:
        new_requirement = TemplateManager.use_template(
            template.requirement_id,
            new_requirement_id='REQ-20260120-002',
            created_by='user_67890'
        )
        print(f"   新需求创建成功！ID: {new_requirement.requirement_id}")
        print(f"   状态: {new_requirement.get_status_display()}")
    except Exception as e:
        print(f"   操作失败: {e}")
    
    return template


def demonstrate_json_output():
    print("\n=== JSON 输出演示 ===")
    
    try:
        requirement = Requirement.objects.get(requirement_id='REQ-20260120-001')
        json_data = requirement.to_json()
        
        print(f"需求 ID: {json_data['requirement_id']}")
        print(f"出发地: {json_data['base_info']['origin']['name']}")
        print(f"目的地: {[city['name'] for city in json_data['base_info']['destination_cities']]}")
        print(f"出行天数: {json_data['base_info']['trip_days']} 天")
        print(f"出行人数: {json_data['base_info']['group_size']['total']} 人")
        print(f"交通方式: {json_data['preferences']['transportation']['type']}")
        print(f"酒店等级: {json_data['preferences']['accommodation']['level']}")
        print(f"行程节奏: {json_data['preferences']['itinerary']['rhythm']}")
        print(f"预算等级: {json_data['budget']['level']}")
        print(f"预算范围: {json_data['budget']['range']['min']} - {json_data['budget']['range']['max']} {json_data['budget']['currency']}")
        print(f"需求状态: {json_data['metadata']['status']}")
        print(f"需求来源: {json_data['metadata']['source_type']}")
        
        print("\n完整 JSON 数据:")
        import json
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"操作失败: {e}")


def main():
    print("=== 旅游需求模型演示 ===\n")
    
    print("1. 创建示例需求")
    requirement = create_sample_requirement()
    
    if requirement:
        demonstrate_status_transitions()
        demonstrate_template_operations()
        demonstrate_json_output()
    
    print("\n=== 演示完成 ===")


if __name__ == '__main__':
    main()
