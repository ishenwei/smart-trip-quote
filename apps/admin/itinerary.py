from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from ..models import (
    Itinerary,
    TravelerStats,
    Destination,
    DailySchedule
)

# 定义TravelerStats的内联编辑类
class TravelerStatsInline(admin.TabularInline):
    model = TravelerStats
    extra = 0
    verbose_name = '出行人员统计'
    verbose_name_plural = '出行人员统计'
    classes = ('compact',)

# 定义Destination的内联编辑类
class DestinationInline(admin.TabularInline):
    model = Destination
    extra = 0
    verbose_name = '目的地'
    verbose_name_plural = '目的地'
    classes = ('compact',)

# 定义DailySchedule的内联编辑类
class DailyScheduleInline(admin.TabularInline):
    model = DailySchedule
    extra = 0
    verbose_name = '每日行程活动'
    verbose_name_plural = '每日行程活动'
    classes = ('compact',)
    
    # 添加编辑和删除按钮
    def edit_daily_schedule(self, obj):
        if obj:
            edit_url = reverse('admin:apps_dailyschedule_change', args=[obj.schedule_id])
            return format_html(
                '<a href="{0}" class="admin-icon-button" title="编辑" style="margin-right: 4px; display: inline-block; width: 20px; height: 20px; text-align: center; line-height: 20px; border: 1px solid #ccc; border-radius: 3px; background-color: #f8f9fa; color: #333; text-decoration: none;">✏️</a>',
                edit_url
            )
        return ''
    
    def delete_daily_schedule(self, obj):
        if obj:
            delete_url = reverse('admin:apps_dailyschedule_delete', args=[obj.schedule_id])
            return format_html(
                '<a href="{0}" class="admin-icon-button" title="删除" style="margin-right: 4px; display: inline-block; width: 20px; height: 20px; text-align: center; line-height: 20px; border: 1px solid #ccc; border-radius: 3px; background-color: #f8f9fa; color: #333; text-decoration: none;">✕</a>',
                delete_url
            )
        return ''
    
    edit_daily_schedule.short_description = '操作'
    edit_daily_schedule.allow_tags = True
    
    delete_daily_schedule.short_description = '删除'
    delete_daily_schedule.allow_tags = True
    
    # 将自定义方法添加到只读字段
    readonly_fields = (
        'edit_daily_schedule',
        'delete_daily_schedule',
        'day_number',
        'schedule_date',
        'city_name',
        'activity_type',
        'activity_title',
        'activity_description',
        'start_time',
        'end_time',
        'attraction_id',
        'hotel_id',
        'restaurant_id',
        'estimated_cost',
        'currency',
        'booking_status',
        'booking_reference',
        'notes',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at'
    )
    
    # 定义显示的字段
    fields = (
        'edit_daily_schedule',
        'delete_daily_schedule',
        'day_number',
        'schedule_date',
        'city_name',
        'activity_type',
        'activity_title',
        'activity_description',
        'start_time',
        'end_time',
        'attraction_id',
        'hotel_id',
        'restaurant_id',
        'estimated_cost',
        'currency',
        'booking_status',
        'booking_reference',
        'notes'
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# 动态生成每天的行程内联类
class DayScheduleInline(admin.TabularInline):
    model = DailySchedule
    extra = 0
    classes = ('compact',)
    
    def __init__(self, day_number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.day_number = day_number
        self.verbose_name = f'第{day_number}天行程'
        self.verbose_name_plural = f'第{day_number}天行程'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(day_number=self.day_number)
    
    # 添加编辑和删除按钮
    def edit_daily_schedule(self, obj):
        if obj:
            edit_url = reverse('admin:apps_dailyschedule_change', args=[obj.schedule_id])
            return format_html(
                '<a href="{0}" class="admin-icon-button" title="编辑" style="margin-right: 4px; display: inline-block; width: 20px; height: 20px; text-align: center; line-height: 20px; border: 1px solid #ccc; border-radius: 3px; background-color: #f8f9fa; color: #333; text-decoration: none;">✏️</a>',
                edit_url
            )
        return ''
    
    def delete_daily_schedule(self, obj):
        if obj:
            delete_url = reverse('admin:apps_dailyschedule_delete', args=[obj.schedule_id])
            return format_html(
                '<a href="{0}" class="admin-icon-button" title="删除" style="margin-right: 4px; display: inline-block; width: 20px; height: 20px; text-align: center; line-height: 20px; border: 1px solid #ccc; border-radius: 3px; background-color: #f8f9fa; color: #333; text-decoration: none;">✕</a>',
                delete_url
            )
        return ''
    
    edit_daily_schedule.short_description = '操作'
    edit_daily_schedule.allow_tags = True
    
    delete_daily_schedule.short_description = '删除'
    delete_daily_schedule.allow_tags = True
    
    # 将自定义方法添加到只读字段
    readonly_fields = (
        'edit_daily_schedule',
        'delete_daily_schedule',
        'day_number',
        'schedule_date',
        'city_name',
        'activity_type',
        'activity_title',
        'activity_description',
        'start_time',
        'end_time',
        'attraction_id',
        'hotel_id',
        'restaurant_id',
        'estimated_cost',
        'currency',
        'booking_status',
        'booking_reference',
        'notes',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at'
    )
    
    # 定义显示的字段
    fields = (
        'edit_daily_schedule',
        'delete_daily_schedule',
        'day_number',
        'schedule_date',
        'city_name',
        'activity_type',
        'activity_title',
        'activity_description',
        'start_time',
        'end_time',
        'attraction_id',
        'hotel_id',
        'restaurant_id',
        'estimated_cost',
        'currency',
        'booking_status',
        'booking_reference',
        'notes'
    )
    
    # 添加新增按钮
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.day_number = self.day_number
        return formset
    
    # 重写模板以添加新增按钮
    template = 'admin/day_schedule_inline.html'

# 自定义Itinerary的Admin类
class ItineraryAdmin(admin.ModelAdmin):
    # 自定义模板
    change_form_template = 'admin/itinerary_change_form.html'
    
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
        # 移除对不存在字段的设置
        super().save_model(request, obj, form, change)
    
    # 保存内联时的处理
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            # 移除对不存在字段的设置
            instance.save()
        formset.save_m2m()
    
    # 重写change_view方法，在详情页底部添加预览按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['preview_button'] = self.preview_itinerary(obj)
        return super().change_view(request, object_id, form_url, extra_context)
    
    # 添加行程详情预览按钮
    def preview_itinerary(self, obj):
        preview_url = reverse('preview_itinerary', args=[obj.itinerary_id])
        return format_html(
            '<a href="{0}" target="_blank" class="preview-button" style="display: inline-flex; align-items: center; padding: 8px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 13px; line-height: 1.4; transition: background-color 0.2s ease, transform 0.1s ease;">\n'  # noqa
            '    <span class="preview-icon" style="margin-right: 6px;">👁️</span> 行程详情预览\n'  # noqa
            '</a>\n'  # noqa
            '<style>\n'  # noqa
            '    .preview-button:hover {{\n'  # noqa
            '        background-color: #45a049;\n'  # noqa
            '        transform: translateY(-1px);\n'  # noqa
            '    }}\n'  # noqa
            '    .preview-button:focus {{\n'  # noqa
            '        outline: 2px solid #4CAF50;\n'  # noqa
            '        outline-offset: 2px;\n'  # noqa
            '    }}\n'  # noqa
            '    .preview-button:active {{\n'  # noqa
            '        transform: translateY(0);\n'  # noqa
            '    }}\n'  # noqa
            '</style>',
            preview_url
        )
    
    preview_itinerary.short_description = '预览操作'
    preview_itinerary.allow_tags = True

# 为DailySchedule创建Admin类
class DailyScheduleAdmin(admin.ModelAdmin):
    # 自定义模板
    change_form_template = 'admin/dailyschedule_change_form_simple.html'
    delete_confirmation_template = 'admin/dailyschedule_delete_confirmation_simple.html'
    
    # 列表显示字段
    list_display = (
        'schedule_id',
        'itinerary_id',
        'day_number',
        'schedule_date',
        'city_name',
        'activity_type',
        'activity_title',
        'start_time',
        'end_time',
        'created_at'
    )
    
    # 搜索字段
    search_fields = (
        'schedule_id',
        'itinerary_id__itinerary_id',
        'city_name',
        'activity_title'
    )
    
    # 筛选字段
    list_filter = (
        'day_number',
        'activity_type',
        'booking_status'
    )
    
    # 详情页字段分组
    fieldsets = (
        ('基本信息', {
            'fields': (
                ('itinerary_id', 'day_number'),
                ('schedule_date', 'city_name'),
                ('activity_type', 'activity_title'),
                ('activity_description',),
                ('start_time', 'end_time')
            ),
            'classes': ('compact',)
        }),
        ('关联资源', {
            'fields': (
                ('attraction_id', 'hotel_id', 'restaurant_id'),
            ),
            'classes': ('compact',)
        }),
        ('费用信息', {
            'fields': (
                ('estimated_cost', 'currency'),
            ),
            'classes': ('compact',)
        }),
        ('预订信息', {
            'fields': (
                ('booking_status', 'booking_reference'),
                ('notes',)
            ),
            'classes': ('compact',)
        }),
        ('管理信息', {
            'fields': (
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse', 'compact')
        })
    )
    
    # 只读字段
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    # 表单字段尺寸调整
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '40'})},
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 3, 'cols': 60})},
        models.IntegerField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '10', 'type': 'number'})},
        models.DecimalField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '15', 'type': 'number'})},
        models.DateField: {'widget': admin.widgets.AdminDateWidget(attrs={'size': '12'})},
        models.TimeField: {'widget': admin.widgets.AdminTimeWidget(attrs={'size': '10'})},
    }
    
    # 重写add_view方法，处理URL参数传入的默认值
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # 从URL参数中获取默认值
        itinerary_id = request.GET.get('itinerary_id')
        day_number = request.GET.get('day_number')
        
        # 如果有参数，设置到extra_context中
        if itinerary_id:
            extra_context['default_itinerary_id'] = itinerary_id
        if day_number:
            extra_context['default_day_number'] = day_number
        
        return super().add_view(request, form_url, extra_context)
    
    # 重写get_form方法，设置默认值
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 对于新增操作，设置默认值
        if not obj:
            itinerary_id = request.GET.get('itinerary_id')
            day_number = request.GET.get('day_number')
            
            if itinerary_id:
                form.base_fields['itinerary_id'].initial = itinerary_id
            if day_number:
                form.base_fields['day_number'].initial = day_number
        
        return form
    
    # 保存时的处理
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        else:
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
    
    # 重写response_change，修改后重定向到详情页
    def response_change(self, request, obj):
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        
        opts = self.model._meta
        # 保存成功后重定向到详情页，并显示成功消息
        self.message_user(request, f'{opts.verbose_name} "{obj}" 保存成功。')
        return HttpResponseRedirect(reverse('admin:apps_dailyschedule_change', args=[obj.pk]))
    
    # 重写response_add，添加后重定向到详情页
    def response_add(self, request, obj, post_url_continue=None):
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        
        opts = self.model._meta
        # 保存成功后重定向到详情页，并显示成功消息
        self.message_user(request, f'{opts.verbose_name} "{obj}" 创建成功。')
        return HttpResponseRedirect(reverse('admin:apps_dailyschedule_change', args=[obj.pk]))

# 注册模型到Admin
admin.site.register(Itinerary, ItineraryAdmin)
admin.site.register(DailySchedule, DailyScheduleAdmin)