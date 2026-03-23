from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.utils import timezone
import json
import ast
from apps.models import Requirement
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


class RequirementAdmin(admin.ModelAdmin):
    # 自定义模板，在详情页底部渲染行程规划按钮
    change_form_template = 'admin/requirement_change_form.html'

    # 指定主键URL参数名称，解决需求ID在URL中被编码的问题
    pk_url_kwarg = 'requirement_id'

    list_display = [
        'display_requirement_id',
        'origin_name',
        'destination_display',
        'group_total',
        'travel_date_range',
        'trip_days',
        'contact_person',
        'contact_phone',
        'contact_company',
        'status_badge',
        'created_by',
        'created_at'
    ]
    
    # 取消默认的链接生成，使用自定义方法
    list_display_links = None
    
    list_filter = [
        TransportationTypeFilter,
        HotelLevelFilter,
        TripRhythmFilter,
        BudgetLevelFilter,
        TemplateFilter,
        DateFlexibilityFilter,
        GroupSizeFilter,
        TripDurationFilter,
        'created_at'
    ]
    
    search_fields = [
        'requirement_id',
        'origin_name',
        'destination_cities',
        'created_by',
        'reviewed_by',
        'template_name',
        'contact_person',
        'contact_phone',
        'contact_company'
    ]
    
    list_editable = []
    
    list_per_page = 25
    
    ordering = ['-created_at']
    
    date_hierarchy = 'created_at'
    
    actions = [
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
    
    fieldsets = (
                ('基本信息', {
                    'fields': (
                        'requirement_id',
                        'origin_name',
                        'origin_type',
                        'destination_cities',
                        'district',
                        'contact_person',
                        'contact_phone',
                        'contact_company'
                    )
                }),
        ('团队人数', {
            'fields': (
                'group_adults',
                'group_children',
                'group_seniors',
                'group_total'
            )
        }),
        ('行程信息', {
            'fields': (
                'trip_days',
                'travel_start_date',
                'travel_end_date',
                'travel_date_flexible'
            )
        }),
        ('交通偏好', {
            'fields': (
                'transportation_type',
                'transportation_notes'
            )
        }),
        ('住宿偏好', {
            'fields': (
                'hotel_level',
                'hotel_requirements'
            )
        }),
        ('行程节奏与偏好', {
            'fields': (
                'trip_rhythm',
                'preference_tags',
                'must_visit_spots',
                'avoid_activities'
            )
        }),
        ('预算信息', {
            'fields': (
                'budget_level',
                'budget_currency',
                'budget_min',
                'budget_max',
                'budget_notes'
            )
        }),
        ('审核信息', {
            'fields': (
                'status',
                'created_by',
                'reviewed_by'
            )
        }),
        
        #('模板信息', {
        #    'fields': (
        #        'is_template',
        #        'template_name',
        #        'template_category'
        #    )
        #}),
        #('其他信息', {
        #    'fields': (
        #        'expires_at',
        #        'extension'
        #    )
        #}),

        ('原始输入与JSON数据', {
            'fields': (
                'source_type',
                'assumptions',
                'origin_input_display',
                'requirement_json_data_display'
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['requirement_id', 'created_at', 'updated_at', 'origin_input_display', 'requirement_json_data_display', 'origin_type', 'group_total', 'travel_end_date', 'source_type', 'assumptions']
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                ('基本信息', {
                    'fields': (
                        'origin_name',
                        'origin_type',
                        'destination_cities',
                        'district',
                        'contact_person',
                        'contact_phone',
                        'contact_company'
                    )
                }),
                ('原始输入与JSON数据', {
                    'fields': (
                        'origin_input_display',
                        'requirement_json_data_display',
                        'source_type',
                        'assumptions'
                    ),
                    'classes': ('collapse',),
                }),
                ('团队人数', {
                    'fields': (
                        'group_adults',
                        'group_children',
                        'group_seniors',
                        'group_total'
                    )
                }),
                ('行程信息', {
                    'fields': (
                        'trip_days',
                        'travel_start_date',
                        'travel_end_date',
                        'travel_date_flexible'
                    )
                }),
                ('交通偏好', {
                    'fields': (
                        'transportation_type',
                        'transportation_notes'
                    )
                }),
                ('住宿偏好', {
                    'fields': (
                        'hotel_level',
                        'hotel_requirements'
                    )
                }),
                ('行程节奏与偏好', {
                    'fields': (
                        'trip_rhythm',
                        'preference_tags',
                        'must_visit_spots',
                        'avoid_activities'
                    )
                }),
                ('预算信息', {
                    'fields': (
                        'budget_level',
                        'budget_currency',
                        'budget_min',
                        'budget_max',
                        'budget_notes'
                    )
                }),
                ('需求状态', {
                    'fields': (
                        'status',
                    )
                }),
                ('审核信息', {
                    'fields': (
                        'created_by',
                        'reviewed_by'
                    )
                }),
                #('模板信息', {
                #    'fields': (
                #        'is_template',
                #        'template_name',
                #        'template_category'
                #    )
                #}),
                #('其他信息', {
                #    'fields': (
                #        'expires_at',
                #        'extension'
                #    )
                #}),
            )
        return super().get_fieldsets(request, obj)
    
    def destination_display(self, obj):
        # 直接显示原始数据，不做转换
        if obj.destination_cities:
            return str(obj.destination_cities)
        return '-'
    destination_display.short_description = '目的地'
    
    def travel_date_range(self, obj):
        if obj.travel_start_date and obj.travel_end_date:
            return f"{obj.travel_start_date} 至 {obj.travel_end_date}"
        elif obj.travel_start_date:
            return f"{obj.travel_start_date} 起"
        else:
            return '-'
    travel_date_range.short_description = '出行日期'
    
    def status_badge(self, obj):
        colors = {
            'PendingReview': '#ffc107',
            'Confirmed': '#28a745',
            'Expired': '#6c757d'
        }
        color = colors.get(obj.status, '#007bff')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = '状态'
    status_badge.allow_tags = True
    
    def is_template_badge(self, obj):
        if obj.is_template:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">模板</span>'
            )
        return '-'
    is_template_badge.short_description = '类型'
    is_template_badge.allow_tags = True
    
    def delete_model(self, request, obj):
        obj.delete()
        self.message_user(request, f'成功删除需求 {obj.requirement_id}。')
    
    def delete_queryset(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'成功删除 {count} 条需求记录。')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    def has_add_permission(self, request):
        return request.user.has_perm('apps.add_requirement')
    
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('apps.change_requirement')
    
    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('apps.delete_requirement')
    
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('apps.view_requirement')
    
    # 重写get_object方法，确保正确处理需求ID
    def get_object(self, request, object_id, from_field=None):
        """获取需求对象，确保需求ID不被URL编码"""
        # 直接使用需求ID查询，不进行任何编码处理
        queryset = self.get_queryset(request)
        field = from_field or self.model._meta.pk.name
        try:
            # 确保object_id是字符串，并且不进行URL解码
            if field == 'requirement_id':
                return queryset.get(requirement_id=object_id)
            return super().get_object(request, object_id, from_field)
        except (self.model.DoesNotExist, ValueError, TypeError):
            return None
    
    # 重写get_change_url方法，确保生成正确的编辑链接
    def get_change_url(self, obj=None, object_id=None):
        """生成需求的编辑链接，确保需求ID不被URL编码"""
        from django.urls import reverse
        if obj:
            return reverse('smart_trip_admin:apps_requirement_change', args=[obj.requirement_id])
        elif object_id:
            return reverse('smart_trip_admin:apps_requirement_change', args=[object_id])
        return super().get_change_url(obj, object_id)
    
    # 自定义方法，用于显示需求ID并生成正确的编辑链接
    def display_requirement_id(self, obj):
        """显示需求ID并生成正确的编辑链接"""
        from django.urls import reverse
        from django.utils.html import format_html
        # 直接使用需求ID生成链接，不进行URL编码
        change_url = reverse('smart_trip_admin:apps_requirement_change', args=[obj.requirement_id])
        return format_html('<a href="{0}">{1}</a>', change_url, obj.requirement_id)
    
    display_requirement_id.short_description = '需求ID'
    display_requirement_id.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        # 计算出行结束日期
        if obj.travel_start_date and obj.trip_days:
            from datetime import timedelta
            obj.travel_end_date = obj.travel_start_date + timedelta(days=obj.trip_days - 1)
        
        if not change:
            obj.created_by = request.user.username if request.user.is_authenticated else None
        
        # 保存基础数据
        super().save_model(request, obj, form, change)
        
        # 重新生成JSON数据并更新
        if change:
            # 重新从数据库获取最新数据，确保所有字段都已保存
            obj.refresh_from_db()
            # 生成完整的JSON数据结构
            updated_json_data = obj.to_json()
            # 更新JSON数据字段，完全覆盖旧数据
            obj.requirement_json_data = updated_json_data
            # 再次保存，只更新JSON数据字段
            super().save_model(request, obj, form, change=False)
        else:
            # 创建时，更新requirement_json_data中的requirement_id
            if obj.requirement_json_data:
                obj.requirement_json_data['requirement_id'] = obj.requirement_id
                super().save_model(request, obj, form, change=False)
    
    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(request, f'成功创建需求 {obj.requirement_id}。')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        self.message_user(request, f'成功更新需求 {obj.requirement_id}。')
        return HttpResponseRedirect(request.path)
    
    def origin_input_display(self, obj):
        """格式化展示原始输入"""
        if not obj.origin_input:
            return '-'
        # 使用pre标签保持原始格式和换行
        return format_html(
            '<pre style="background-color: #f8f9fa; padding: 10px; border: 1px solid #e9ecef; border-radius: 4px; max-height: 300px; overflow-y: auto;">{}</pre>',
            obj.origin_input
        )
    origin_input_display.short_description = '客户原始输入'
    origin_input_display.allow_tags = True
    
    def requirement_json_data_display(self, obj):
        """格式化展示JSON数据"""
        import json
        if not obj.requirement_json_data:
            return '-'
        try:
            # 确保数据是字典格式
            if isinstance(obj.requirement_json_data, str):
                data = json.loads(obj.requirement_json_data)
            else:
                data = obj.requirement_json_data
            # 格式化JSON
            formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
            # 返回HTML格式，使用pre标签保持缩进
            return format_html(
                '<pre style="background-color: #f8f9fa; padding: 10px; border: 1px solid #e9ecef; border-radius: 4px; max-height: 400px; overflow-y: auto;">{}</pre>',
                formatted_json
            )
        except Exception as e:
            return format_html(
                '<span style="color: #dc3545;">JSON解析错误: {}</span>',
                str(e)
            )
    requirement_json_data_display.short_description = 'JSON结构数据'
    requirement_json_data_display.allow_tags = True
    

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/jquery.init.js',)
