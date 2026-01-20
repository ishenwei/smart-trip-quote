from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.utils import timezone
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


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = [
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
    
    list_filter = [
        StatusFilter,
        SourceTypeFilter,
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
        'template_name'
    ]
    
    list_editable = ['status']
    
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
                'origin_code',
                'origin_type',
                'destination_cities'
            )
        }),
        ('行程信息', {
            'fields': (
                'trip_days',
                'group_adults',
                'group_children',
                'group_seniors',
                'group_total',
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
                'source_type',
                'status',
                'assumptions'
            )
        }),
        ('审核信息', {
            'fields': (
                'created_by',
                'reviewed_by'
            )
        }),
        ('模板信息', {
            'fields': (
                'is_template',
                'template_name',
                'template_category'
            )
        }),
        ('其他信息', {
            'fields': (
                'expires_at',
                'extension'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def destination_display(self, obj):
        cities = obj.destination_cities if isinstance(obj.destination_cities, list) else []
        if cities:
            city_names = []
            for city in cities[:3]:
                if isinstance(city, dict):
                    city_names.append(city.get('name', str(city)))
                else:
                    city_names.append(str(city))
            return ', '.join(city_names) + ('...' if len(cities) > 3 else '')
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
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username if request.user.is_authenticated else None
        super().save_model(request, obj, form, change)
    
    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(request, f'成功创建需求 {obj.requirement_id}。')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        self.message_user(request, f'成功更新需求 {obj.requirement_id}。')
        return super().response_change(request, obj)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
