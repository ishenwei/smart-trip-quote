import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from datetime import datetime, timedelta
from apps.models import Requirement
from apps.admin.requirement import RequirementAdmin
from apps.admin_ext.filters import (
    StatusFilter, SourceTypeFilter, TransportationTypeFilter,
    HotelLevelFilter, TripRhythmFilter, BudgetLevelFilter,
    TemplateFilter, DateFlexibilityFilter, GroupSizeFilter, TripDurationFilter
)
from apps.admin_ext.actions import (
    mark_as_confirmed, mark_as_expired, mark_as_pending_review,
    mark_as_template, unmark_as_template, set_reviewer,
    clear_reviewer, copy_as_template
)


class MockRequest:
    def __init__(self, user):
        self.user = user
        self.session = {}
        self._messages = FallbackStorage(self)


class RequirementAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = RequirementAdmin(Requirement, self.site)
        self.factory = RequestFactory()
        
        User.objects.filter(username__in=['admin', 'user', 'noperm']).delete()
        Requirement.objects.filter(requirement_id__startswith='REQ-ADMIN').delete()
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password'
        )
        
        content_type = ContentType.objects.get_for_model(Requirement)
        add_perm = Permission.objects.get(
            content_type=content_type,
            codename='add_requirement'
        )
        change_perm = Permission.objects.get(
            content_type=content_type,
            codename='change_requirement'
        )
        delete_perm = Permission.objects.get(
            content_type=content_type,
            codename='delete_requirement'
        )
        view_perm = Permission.objects.get(
            content_type=content_type,
            codename='view_requirement'
        )
        
        self.normal_user.user_permissions.add(
            add_perm, change_perm, delete_perm, view_perm
        )
        
        self.requirement = Requirement.objects.create(
            requirement_id='REQ-ADMIN-001',
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
    
    def test_admin_registration(self):
        print("测试1: Admin注册")
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.admin.model, Requirement)
        print("✓ Requirement模型已成功注册到Admin")
    
    def test_list_display(self):
        print("\n测试2: 列表显示字段")
        expected_fields = [
            'requirement_id',
            'origin_name',
            'destination_display',
            'trip_days',
            'group_total',
            'travel_date_range',
            'status',
            'status_badge',
            'source_type',
            'is_template_badge',
            'created_at'
        ]
        self.assertEqual(self.admin.list_display, expected_fields)
        print(f"✓ 列表显示字段配置正确: {len(expected_fields)} 个字段")
    
    def test_list_filter(self):
        print("\n测试3: 列表筛选器")
        filter_classes = [
            StatusFilter,
            SourceTypeFilter,
            TransportationTypeFilter,
            HotelLevelFilter,
            TripRhythmFilter,
            BudgetLevelFilter,
            TemplateFilter,
            DateFlexibilityFilter,
            GroupSizeFilter,
            TripDurationFilter
        ]
        for filter_class in filter_classes:
            self.assertIn(filter_class, self.admin.list_filter)
        print(f"✓ 列表筛选器配置正确: {len(filter_classes)} 个筛选器")
    
    def test_search_fields(self):
        print("\n测试4: 搜索字段")
        expected_search_fields = [
            'requirement_id',
            'origin_name',
            'destination_cities',
            'created_by',
            'reviewed_by',
            'template_name'
        ]
        self.assertEqual(self.admin.search_fields, expected_search_fields)
        print(f"✓ 搜索字段配置正确: {len(expected_search_fields)} 个字段")
    
    def test_list_editable(self):
        print("\n测试5: 可编辑字段")
        self.assertEqual(self.admin.list_editable, ['status'])
        print("✓ 可编辑字段配置正确: status")
    
    def test_list_per_page(self):
        print("\n测试6: 每页显示数量")
        self.assertEqual(self.admin.list_per_page, 25)
        print("✓ 每页显示数量配置正确: 25")
    
    def test_ordering(self):
        print("\n测试7: 默认排序")
        self.assertEqual(self.admin.ordering, ['-created_at'])
        print("✓ 默认排序配置正确: 按创建时间降序")
    
    def test_date_hierarchy(self):
        print("\n测试8: 日期层级")
        self.assertEqual(self.admin.date_hierarchy, 'created_at')
        print("✓ 日期层级配置正确: created_at")
    
    def test_actions(self):
        print("\n测试9: 批量操作")
        expected_actions = [
            'mark_as_confirmed',
            'mark_as_expired',
            'mark_as_pending_review',
            'mark_as_template',
            'unmark_as_template',
            'set_reviewer',
            'clear_reviewer',
            'copy_as_template',
            'delete_selected'
        ]
        for action in expected_actions:
            self.assertIn(action, self.admin.actions)
        print(f"✓ 批量操作配置正确: {len(expected_actions)} 个操作")
    
    def test_custom_methods(self):
        print("\n测试10: 自定义显示方法")
        
        request = MockRequest(self.superuser)
        
        destination_display = self.admin.destination_display(self.requirement)
        self.assertIn('西安', destination_display)
        self.assertIn('成都', destination_display)
        print("✓ destination_display方法工作正常")
        
        travel_date_range = self.admin.travel_date_range(self.requirement)
        self.assertIn('2026-05-01', travel_date_range)
        self.assertIn('2026-05-05', travel_date_range)
        print("✓ travel_date_range方法工作正常")
        
        status_badge = self.admin.status_badge(self.requirement)
        self.assertIn('待审核', status_badge)
        print("✓ status_badge方法工作正常")
        
        is_template_badge = self.admin.is_template_badge(self.requirement)
        self.assertEqual(is_template_badge, '-')
        print("✓ is_template_badge方法工作正常")
    
    def test_permissions(self):
        print("\n测试11: 权限控制")
        
        request = MockRequest(self.superuser)
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_view_permission(request))
        print("✓ 超级用户拥有所有权限")
        
        request = MockRequest(self.normal_user)
        self.assertTrue(self.admin.has_add_permission(request))
        self.assertTrue(self.admin.has_change_permission(request))
        self.assertTrue(self.admin.has_delete_permission(request))
        self.assertTrue(self.admin.has_view_permission(request))
        print("✓ 普通用户拥有所有权限")
        
        no_perm_user = User.objects.create_user(
            username='noperm',
            email='noperm@example.com',
            password='password'
        )
        request = MockRequest(no_perm_user)
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))
        self.assertFalse(self.admin.has_view_permission(request))
        print("✓ 无权限用户无法访问")
    
    def test_save_model(self):
        print("\n测试12: 保存模型")
        
        request = MockRequest(self.superuser)
        new_requirement = Requirement(
            requirement_id='REQ-ADMIN-002',
            origin_name='上海',
            destination_cities=['杭州'],
            trip_days=3,
            group_total=2,
            group_adults=2,
            group_children=0,
            group_seniors=0,
            preference_tags=[],
            must_visit_spots=[],
            avoid_activities=[],
            assumptions=[],
            extension={}
        )
        
        self.admin.save_model(request, new_requirement, None, change=False)
        self.assertEqual(new_requirement.created_by, 'admin')
        print("✓ 新建需求时自动设置创建人")
        
        new_requirement.refresh_from_db()
        self.assertIsNotNone(new_requirement.created_at)
        print("✓ 自动设置创建时间")
    
    def test_delete_model(self):
        print("\n测试13: 删除模型")
        
        request = MockRequest(self.superuser)
        
        delete_req = Requirement.objects.create(
            requirement_id='REQ-ADMIN-DELETE',
            origin_name='深圳',
            destination_cities=['香港'],
            trip_days=2,
            group_total=1,
            group_adults=1,
            group_children=0,
            group_seniors=0,
            preference_tags=[],
            must_visit_spots=[],
            avoid_activities=[],
            assumptions=[],
            extension={}
        )
        
        requirement_id = delete_req.requirement_id
        
        self.admin.delete_model(request, delete_req)
        
        with self.assertRaises(Requirement.DoesNotExist):
            Requirement.objects.get(requirement_id=requirement_id)
        print("✓ 删除模型功能正常")
    
    def test_delete_queryset(self):
        print("\n测试14: 批量删除")
        
        req2 = Requirement.objects.create(
            requirement_id='REQ-ADMIN-003',
            origin_name='广州',
            destination_cities=['深圳'],
            trip_days=2,
            group_total=1,
            group_adults=1,
            group_children=0,
            group_seniors=0,
            preference_tags=[],
            must_visit_spots=[],
            avoid_activities=[],
            assumptions=[],
            extension={}
        )
        
        req3 = Requirement.objects.create(
            requirement_id='REQ-ADMIN-004',
            origin_name='杭州',
            destination_cities=['苏州'],
            trip_days=2,
            group_total=1,
            group_adults=1,
            group_children=0,
            group_seniors=0,
            preference_tags=[],
            must_visit_spots=[],
            avoid_activities=[],
            assumptions=[],
            extension={}
        )
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(
            requirement_id__in=['REQ-ADMIN-003', 'REQ-ADMIN-004']
        )
        
        self.admin.delete_queryset(request, queryset)
        
        self.assertEqual(Requirement.objects.filter(
            requirement_id__in=['REQ-ADMIN-003', 'REQ-ADMIN-004']
        ).count(), 0)
        print("✓ 批量删除功能正常")
    
    def test_actions_mark_as_confirmed(self):
        print("\n测试15: 标记为已确认操作")
        
        self.requirement.status = 'PendingReview'
        self.requirement.reviewed_by = None
        self.requirement.save()
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        mark_as_confirmed(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertEqual(self.requirement.status, 'Confirmed')
        self.assertEqual(self.requirement.reviewed_by, 'admin')
        print("✓ 标记为已确认操作正常")
    
    def test_actions_mark_as_expired(self):
        print("\n测试16: 标记为已过期操作")
        
        self.requirement.status = 'PendingReview'
        self.requirement.save()
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        mark_as_expired(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertEqual(self.requirement.status, 'Expired')
        print("✓ 标记为已过期操作正常")
    
    def test_actions_mark_as_pending_review(self):
        print("\n测试17: 标记为待审核操作")
        
        self.requirement.status = 'Confirmed'
        self.requirement.save()
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        mark_as_pending_review(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertEqual(self.requirement.status, 'PendingReview')
        print("✓ 标记为待审核操作正常")
    
    def test_actions_mark_as_template(self):
        print("\n测试18: 标记为模板操作")
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        mark_as_template(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertTrue(self.requirement.is_template)
        print("✓ 标记为模板操作正常")
    
    def test_actions_unmark_as_template(self):
        print("\n测试19: 取消模板标记操作")
        
        self.requirement.is_template = True
        self.requirement.save()
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        unmark_as_template(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertFalse(self.requirement.is_template)
        print("✓ 取消模板标记操作正常")
    
    def test_actions_set_reviewer(self):
        print("\n测试20: 设置审核人操作")
        
        request = MockRequest(self.normal_user)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        set_reviewer(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertEqual(self.requirement.reviewed_by, 'user')
        print("✓ 设置审核人操作正常")
    
    def test_actions_clear_reviewer(self):
        print("\n测试21: 清除审核人操作")
        
        self.requirement.reviewed_by = 'admin'
        self.requirement.save()
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        clear_reviewer(self.admin, request, queryset)
        
        self.requirement.refresh_from_db()
        self.assertIsNone(self.requirement.reviewed_by)
        print("✓ 清除审核人操作正常")
    
    def test_actions_copy_as_template(self):
        print("\n测试22: 复制为模板操作")
        
        request = MockRequest(self.superuser)
        queryset = Requirement.objects.filter(requirement_id='REQ-ADMIN-001')
        
        initial_count = Requirement.objects.count()
        copy_as_template(self.admin, request, queryset)
        
        self.assertEqual(Requirement.objects.count(), initial_count + 1)
        
        template = Requirement.objects.filter(is_template=True).first()
        self.assertIsNotNone(template)
        self.assertIn('copy', template.requirement_id)
        print("✓ 复制为模板操作正常")
    
    def test_get_queryset(self):
        print("\n测试23: 查询集优化")
        
        request = MockRequest(self.superuser)
        queryset = self.admin.get_queryset(request)
        
        self.assertIsNotNone(queryset)
        print("✓ 查询集优化正常")
    
    def test_fieldsets(self):
        print("\n测试24: 字段分组")
        
        fieldsets = self.admin.fieldsets
        self.assertIsNotNone(fieldsets)
        self.assertIsInstance(fieldsets, tuple)
        
        fieldset_names = [fs[0] for fs in fieldsets]
        expected_names = [
            '基本信息',
            '行程信息',
            '交通偏好',
            '住宿偏好',
            '行程节奏与偏好',
            '预算信息',
            '需求状态',
            '审核信息',
            '模板信息',
            '其他信息'
        ]
        
        for name in expected_names:
            self.assertIn(name, fieldset_names)
        
        print(f"✓ 字段分组配置正确: {len(fieldsets)} 个分组")
    
    def test_readonly_fields(self):
        print("\n测试25: 只读字段")
        
        readonly_fields = self.admin.readonly_fields
        self.assertIn('created_at', readonly_fields)
        self.assertIn('updated_at', readonly_fields)
        print("✓ 只读字段配置正确: created_at, updated_at")


def run_all_tests():
    print("=== Requirement Admin 功能测试 ===\n")
    
    test = RequirementAdminTest()
    test.setUp()
    
    tests = [
        test.test_admin_registration,
        test.test_list_display,
        test.test_list_filter,
        test.test_search_fields,
        test.test_list_editable,
        test.test_list_per_page,
        test.test_ordering,
        test.test_date_hierarchy,
        test.test_actions,
        test.test_custom_methods,
        test.test_permissions,
        test.test_save_model,
        test.test_delete_model,
        test.test_delete_queryset,
        test.test_actions_mark_as_confirmed,
        test.test_actions_mark_as_expired,
        test.test_actions_mark_as_pending_review,
        test.test_actions_mark_as_template,
        test.test_actions_unmark_as_template,
        test.test_actions_set_reviewer,
        test.test_actions_clear_reviewer,
        test.test_actions_copy_as_template,
        test.test_get_queryset,
        test.test_fieldsets,
        test.test_readonly_fields
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("\n✓ 所有测试通过!")
    else:
        print(f"\n✗ 有 {failed} 个测试失败")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
