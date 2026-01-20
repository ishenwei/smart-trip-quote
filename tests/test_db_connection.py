import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.models import Requirement, RequirementValidator, RequirementStatusManager, TemplateManager


def test_database_connection():
    print("=== 测试数据库连接 ===")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ 数据库连接成功")
            print(f"  数据库版本: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"  当前数据库: {db_name[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()")
            table_count = cursor.fetchone()
            print(f"  表数量: {table_count[0]}")
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False


def test_requirement_model():
    print("\n=== 测试 Requirement 模型 ===")
    try:
        requirement_id = 'REQ-TEST-001'
        
        sample_data = {
            'requirement_id': requirement_id,
            'origin_name': '北京',
            'origin_code': 'BJS',
            'origin_type': 'International',
            'destination_cities': [
                {'name': '西安', 'code': 'SIA', 'stay_days': 3},
                {'name': '成都', 'code': 'CTU', 'stay_days': 2}
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
            'created_by': 'test_user',
            'reviewed_by': None,
            'is_template': False,
            'template_name': '',
            'template_category': '',
            'extension': {}
        }
        
        RequirementValidator.validate_all(sample_data)
        print("✓ 数据验证通过")
        
        requirement = Requirement.objects.create(**sample_data)
        print(f"✓ 需求创建成功: {requirement.requirement_id}")
        
        retrieved = Requirement.objects.get(requirement_id=requirement_id)
        print(f"✓ 需求查询成功: {retrieved.origin_name} 至 {[city['name'] for city in retrieved.destination_cities]}")
        
        json_data = retrieved.to_json()
        print(f"✓ JSON 导出成功，包含 {len(json_data)} 个顶级字段")
        
        return requirement
    except Exception as e:
        print(f"✗ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_status_manager(requirement):
    print("\n=== 测试状态管理器 ===")
    try:
        requirement_id = requirement.requirement_id
        
        RequirementStatusManager.confirm_requirement(requirement_id, reviewer='admin')
        print(f"✓ 需求确认成功")
        
        requirement.refresh_from_db()
        print(f"  当前状态: {requirement.get_status_display()}")
        print(f"  审核人: {requirement.reviewed_by}")
        
        stats = RequirementStatusManager.get_status_statistics()
        print(f"✓ 状态统计: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ 状态管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_manager(requirement):
    print("\n=== 测试模板管理器 ===")
    try:
        source_requirement_id = requirement.requirement_id
        template_id = 'TPL-TEST-001'
        
        template = TemplateManager.create_template(
            source_requirement_id,
            template_name='测试模板',
            template_category='TestCategory',
            created_by='admin'
        )
        print(f"✓ 模板创建成功: {template.requirement_id}")
        print(f"  模板名称: {template.template_name}")
        print(f"  模板分类: {template.template_category}")
        
        templates = TemplateManager.list_templates()
        print(f"✓ 模板列表查询成功，共 {templates['total_count']} 个模板")
        
        categories = TemplateManager.get_template_categories()
        print(f"✓ 模板分类查询成功: {categories}")
        
        new_requirement = TemplateManager.use_template(
            template.requirement_id,
            new_requirement_id='REQ-TEST-002',
            created_by='user_001'
        )
        print(f"✓ 使用模板创建需求成功: {new_requirement.requirement_id}")
        
        return True
    except Exception as e:
        print(f"✗ 模板管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    print("\n=== 清理测试数据 ===")
    try:
        deleted_count = Requirement.objects.filter(
            requirement_id__startswith='REQ-TEST'
        ).delete()
        print(f"✓ 清理了 {deleted_count[0]} 条测试需求记录")
        
        deleted_count = Requirement.objects.filter(
            requirement_id__startswith='TPL-TEST'
        ).delete()
        print(f"✓ 清理了 {deleted_count[0]} 条测试模板记录")
        
        return True
    except Exception as e:
        print(f"✗ 清理测试数据失败: {e}")
        return False


def main():
    print("=== MariaDB 数据库连接测试 ===\n")
    
    if not test_database_connection():
        print("\n数据库连接失败，请检查配置")
        return
    
    requirement = test_requirement_model()
    if not requirement:
        print("\n模型测试失败，请检查代码")
        return
    
    if not test_status_manager(requirement):
        print("\n状态管理器测试失败，请检查代码")
        cleanup_test_data()
        return
    
    if not test_template_manager(requirement):
        print("\n模板管理器测试失败，请检查代码")
        cleanup_test_data()
        return
    
    cleanup_test_data()
    
    print("\n=== 所有测试通过 ===")
    print("✓ 数据库连接正常")
    print("✓ 模型功能正常")
    print("✓ 状态管理正常")
    print("✓ 模板管理正常")


if __name__ == '__main__':
    main()
