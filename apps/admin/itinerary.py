from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from ..models import (
    Itinerary,
    TravelerStats,
    Destination,
    DailySchedule
)

# 定义TravelerStats的内联编辑类
class TravelerStatsInline(admin.TabularInline):
    model = TravelerStats
    extra = 1
    verbose_name = '出行人员统计'
    verbose_name_plural = '出行人员统计'
    classes = ('compact',)

# 定义Destination的内联编辑类
class DestinationInline(admin.TabularInline):
    model = Destination
    extra = 1
    verbose_name = '目的地'
    verbose_name_plural = '目的地'
    classes = ('compact',)

# 定义DailySchedule的内联编辑类
class DailyScheduleInline(admin.TabularInline):
    model = DailySchedule
    extra = 1
    verbose_name = '每日行程活动'
    verbose_name_plural = '每日行程活动'
    classes = ('compact',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# 动态生成每天的行程内联类
class DayScheduleInline(admin.TabularInline):
    model = DailySchedule
    extra = 1
    classes = ('compact',)
    
    def __init__(self, day_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.day_number = day_number
        self.verbose_name = f'第{day_number}天行程'
        self.verbose_name_plural = f'第{day_number}天行程'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(day_number=self.day_number)
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'day_number':
            kwargs['initial'] = self.day_number
            # 设置为只读，确保天数不会被修改
            kwargs['widget'] = admin.widgets.AdminTextInputWidget(attrs={'readonly': True, 'size': '5'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

# 自定义Itinerary的Admin类
class ItineraryAdmin(admin.ModelAdmin):
    # 权限控制
    def has_add_permission(self, request):
        return request.user.has_perm('apps.add_itinerary')
    
    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('apps.change_itinerary')
    
    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('apps.delete_itinerary')
    
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('apps.view_itinerary')
    
    # 列表显示字段
    list_display = (
        'itinerary_id',
        'itinerary_name',
        'contact_person',
        'contact_phone',
        'start_date',
        'end_date',
        'total_days',
        'current_status',
        'created_by',
        'created_at'
    )
    
    # 搜索字段
    search_fields = (
        'itinerary_id',
        'itinerary_name',
        'description',
        'contact_person',
        'contact_phone',
        'departure_city',
        'return_city',
        'created_by'
    )
    
    # 筛选字段
    list_filter = (
        'current_status',
        'budget_flexibility',
        'is_template',
        'template_category',
        'start_date',
        'end_date'
    )
    
    # 排序字段
    ordering = ('-created_at',)
    
    # 详情页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': (
                ('itinerary_name',),
                ('description',),
                ('travel_purpose',),
                ('start_date', 'end_date', 'total_days'),
                ('departure_city', 'return_city')
            ),
            'classes': ('compact',)
        }),
        ('联系信息', {
            'fields': (
                ('contact_person', 'contact_phone'),
                ('contact_company',)
            ),
            'classes': ('compact',)
        }),
        ('预算信息', {
            'fields': (
                ('total_budget', 'budget_flexibility')
            ),
            'classes': ('compact',)
        }),
        ('状态信息', {
            'fields': (
                ('current_status',),
                ('review_deadline', 'expiration_date'),
                ('confirmed_by', 'confirmed_at')
            ),
            'classes': ('compact',)
        }),
        ('模板信息', {
            'fields': (
                ('is_template',),
                ('template_name', 'template_category'),
                ('usage_count', 'last_used')
            ),
            'classes': ('collapse', 'compact')
        }),
        ('管理信息', {
            'fields': (
                ('created_by', 'updated_by'),
                ('version',),
                ('is_deleted', 'deleted_at')
            ),
            'classes': ('collapse', 'compact')
        })
    )
    
    # 基本内联编辑
    inlines = [
        TravelerStatsInline,
        DestinationInline
    ]
    
    # 内联编辑的额外配置
    def get_formset_kwargs(self, *args, **kwargs):
        return super().get_formset_kwargs(*args, **kwargs)
    
    # 只读字段
    readonly_fields = (
        'total_days',
        'created_at',
        'updated_at',
        'version'
    )
    
    # 表单字段尺寸调整
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '40'})},
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 3, 'cols': 60})},
        models.IntegerField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '10', 'type': 'number'})},
        models.DecimalField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '15', 'type': 'number'})},
        models.DateField: {'widget': admin.widgets.AdminDateWidget(attrs={'size': '12'})},
    }
    
    # 动态生成行程内联
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        
        if obj and obj.total_days:
            for day in range(1, obj.total_days + 1):
                inline = DayScheduleInline(day, self.model, self.admin_site)
                inline_instances.append(inline)
        
        return inline_instances
    
    # 保存时的处理
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        else:
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
    
    # 保存内联时的处理
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not hasattr(instance, 'created_by') and hasattr(request, 'user'):
                instance.created_by = request.user.username
            instance.save()
        formset.save_m2m()

# 注册模型到Admin
admin.site.register(Itinerary, ItineraryAdmin)