from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from easymde.widgets import EasyMDEEditor
import os
import sys
import logging
from ..models import (
    Itinerary,
    TravelerStats,
    Destination,
    DailySchedule,
    RequirementItinerary
)

# 模块级别的日志输出，确保在Django加载时执行
print("====================================", file=sys.stdout, flush=True)
print("itinerary.py 模块加载 ", file=sys.stdout, flush=True)
print("====================================", file=sys.stdout, flush=True)
sys.stdout.flush()

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
    fields = ('destination_order', 'city_name', 'arrival_date', 'departure_date', 'nights')
    readonly_fields = ('nights',)
    ordering = ('destination_order',)

# 定义DailySchedule的内联编辑类
class DayScheduleInline(admin.TabularInline):
    model = DailySchedule
    extra = 0
    classes = ('compact',)
    
    # 自定义 CSS 调整列宽
    class Media:
        css = {
            'all': ('admin/css/custom_inline.css',)
        }
    
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
                '<a href="{0}" class="admin-icon-button" title="删除" style="margin-right: 4px; display: inline-block; width: 20px; height: 20px; text-align: center; line-height: 20px; border: 1px solid #ccc; border-radius: 3px; background-color: #f8f9fa; color: #333; text-decoration: none;">❌</a>',
                delete_url
            )
        return ''
    
    edit_daily_schedule.short_description = '操作'
    edit_daily_schedule.allow_tags = True
    
    delete_daily_schedule.short_description = '删除'
    delete_daily_schedule.allow_tags = True
    
    # 合并开始和结束时间
    def time_range(self, obj):
        if obj and obj.start_time and obj.end_time:
            start = str(obj.start_time)[:5]  # 去掉秒
            end = str(obj.end_time)[:5]
            return f'{start}~{end}'
        elif obj and obj.start_time:
            return str(obj.start_time)[:5]
        return ''
    time_range.short_description = '时间'
    
    # 酒店显示名称（带链接）
    def hotel_name(self, obj):
        if obj and obj.hotel_id:
            edit_url = reverse('admin:apps_hotel_change', args=[obj.hotel_id.hotel_id])
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                edit_url,
                obj.hotel_id.hotel_name
            )
        return ''
    hotel_name.short_description = '酒店'
    hotel_name.allow_tags = True
    
    # 餐厅显示名称（带链接）
    def restaurant_name(self, obj):
        if obj and obj.restaurant_id:
            edit_url = reverse('admin:apps_restaurant_change', args=[obj.restaurant_id.restaurant_id])
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                edit_url,
                obj.restaurant_id.restaurant_name
            )
        return ''
    restaurant_name.short_description = '餐厅'
    restaurant_name.allow_tags = True
    
    # 将自定义方法添加到只读字段
    readonly_fields = (
        'edit_daily_schedule',
        'delete_daily_schedule',
        'day_number',
        'schedule_date',
        'destination_id',
        'activity_type',
        'activity_title',
        'activity_description',
        'time_range',
        'attraction_id',
        'hotel_name',
        'restaurant_name',
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
        'day_number',
        'schedule_date',
        'destination_id',
        'time_range',
        'activity_type',
        'activity_title',
        'activity_description',
        'attraction_id',
        'hotel_name',
        'restaurant_name',
        'notes',
        'delete_daily_schedule',
        #'estimated_cost',
        #'currency',
        #'booking_status',
        #'booking_reference',
    )
    
    # 添加新增按钮
    def get_formset(self, request, obj=None, **kwargs):
        # 重写formset类，跳过验证
        from django.forms import BaseInlineFormSet
        
        class SkipValidationFormSet(BaseInlineFormSet):
            def clean(self):
                # 跳过验证
                return
            
            def is_valid(self):
                # 始终返回True，跳过验证
                return True
        
        # 使用自定义的表单集类
        kwargs['formset'] = SkipValidationFormSet
        formset = super().get_formset(request, obj, **kwargs)
        formset.day_number = self.day_number
        # 确保表单集有必要的属性，避免Django admin系统报错
        formset.new_objects = []
        formset.changed_objects = []
        formset.deleted_objects = []
        return formset
    
    # 重写模板以添加新增按钮
    template = 'admin/day_schedule_inline.html'

# 定义RequirementItinerary的内联编辑类
class RequirementItineraryInline(admin.TabularInline):
    model = RequirementItinerary
    extra = 0
    verbose_name = '关联需求'
    verbose_name_plural = '关联需求'
    classes = ('compact',)
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def display_requirement_id(self, obj):
        """显示需求ID并生成可点击的链接"""
        if obj.requirement:
            change_url = reverse('smart_trip_admin:apps_requirement_change', args=[obj.requirement.requirement_id])
            return format_html(
                '<a href="{0}" style="color: #4178be; text-decoration: none; font-weight: 500;">{1}</a>',
                change_url,
                obj.requirement.requirement_id
            )
        return '-'
    
    display_requirement_id.short_description = '需求ID'
    display_requirement_id.allow_tags = True
    
    def display_requirement_name(self, obj):
        """显示需求名称"""
        if obj.requirement:
            return obj.requirement.origin_name or '-'
        return '-'
    
    display_requirement_name.short_description = '需求名称'
    
    def display_origin_city(self, obj):
        """显示出发地"""
        if obj.requirement:
            return obj.requirement.origin_name or '-'
        return '-'
    
    display_origin_city.short_description = '出发地'
    
    def display_created_at(self, obj):
        """显示创建时间"""
        if obj.requirement:
            return obj.requirement.created_at.strftime('%Y-%m-%d %H:%M') if obj.requirement.created_at else '-'
        return '-'
    
    display_created_at.short_description = '创建时间'
    
    readonly_fields = (
        'display_requirement_id',
        'display_requirement_name',
        'display_origin_city',
        'display_created_at',
        'created_at',
        'updated_at'
    )
    
    fields = (
        'display_requirement_id',
        'display_created_at'
    )

# 自定义Itinerary的Admin类
class ItineraryAdmin(admin.ModelAdmin):
    # 自定义模板
    change_form_template = 'admin/itinerary_change_form.html'
    
    # 指定主键URL参数名称，解决行程ID在URL中被编码的问题
    pk_url_kwarg = 'itinerary_id'
    
    # 引入 EasyMDE 的 CSS 和 JS
    class Media:
        css = {
            'all': ('easymde/easymde.min.css',)
        }
        js = ('easymde/easymde.min.js', 'easymde/easymde.init.js')
    
    # 重写get_object方法，确保正确处理行程ID
    def get_object(self, request, object_id, from_field=None):
        """获取行程对象，确保行程ID不被URL编码"""
        # 直接使用行程ID查询，不进行任何编码处理
        queryset = self.get_queryset(request)
        field = from_field or self.model._meta.pk.name
        try:
            # 确保object_id是字符串，并且不进行URL解码
            if field == 'itinerary_id':
                return queryset.get(itinerary_id=object_id)
            return super().get_object(request, object_id, from_field)
        except (self.model.DoesNotExist, ValueError, TypeError):
            return None

    # 重写get_change_url方法，确保生成正确的编辑链接
    def get_change_url(self, obj=None, object_id=None):
        """生成行程的编辑链接，确保行程ID不被URL编码"""
        from django.urls import reverse
        if obj:
            return reverse('smart_trip_admin:apps_itinerary_change', args=[obj.itinerary_id])
        elif object_id:
            return reverse('smart_trip_admin:apps_itinerary_change', args=[object_id])
        return super().get_change_url(obj, object_id)
    
    # 表单视图处理
    def _changeform_view(self, request, object_id, form_url, extra_context):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始_changeform_view - 用户: {request.user.username}, 对象ID: {object_id}, 请求方法: {request.method}")
        try:
            response = super()._changeform_view(request, object_id, form_url, extra_context)
            logger.info("_changeform_view 响应内容: %s" % response)
            logger.info(f"结束_changeform_view - 响应类型: {type(response).__name__}")
            return response
        except Exception as e:
            logger.error(f"_changeform_view 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] _changeform_view 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 表单获取
    def get_form(self, request, obj=None, **kwargs):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始get_form - 用户: {request.user.username}, 对象: {obj}")
        try:
            form = super().get_form(request, obj, **kwargs)
            logger.info(f"结束get_form - 表单类: {form.__name__}")
            return form
        except Exception as e:
            logger.error(f"get_form 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] get_form 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 表单字段处理
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        import logging
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始formfield_for_foreignkey - 字段: {db_field.name}, 用户: {request.user.username}")
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        logger.info(f"结束formfield_for_foreignkey - 字段: {db_field.name}")
        return formfield
    
    # 保存后的响应处理
    def response_change(self, request, obj):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始response_change - 用户: {request.user.username}, 对象: {obj}")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求数据: {request.POST}")
        try:
            response = super().response_change(request, obj)
            logger.info(f"结束response_change - 响应类型: {type(response).__name__}")
            return response
        except Exception as e:
            logger.error(f"response_change 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] response_change 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 保存表单前的处理
    def save_form(self, request, form, change):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始save_form - 用户: {request.user.username}, change: {change}")
        logger.info(f"表单数据: {form.cleaned_data if form.is_valid() else '表单无效'}")
        logger.info(f"表单错误: {form.errors if not form.is_valid() else '无错误'}")
        try:
            logger.info("开始调用 super().save_form()")
            result = super().save_form(request, form, change)
            logger.info(f"结束 super().save_form() - 结果: {result}")
            logger.info(f"save_form 返回对象: {result}, 对象ID: {result.pk if hasattr(result, 'pk') else '无'}")
            return result
        except Exception as e:
            logger.error(f"save_form 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] save_form 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 创建表单集
    def _create_formsets(self, request, obj, change):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始_create_formsets - 用户: {request.user.username}, 对象: {obj}, change: {change}")
        try:
            formsets, inline_instances = super()._create_formsets(request, obj, change)
            logger.info(f"结束_create_formsets - 表单集数量: {len(formsets)}, 内联实例数量: {len(inline_instances)}")
            return formsets, inline_instances
        except Exception as e:
            logger.error(f"_create_formsets 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] _create_formsets 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 保存内联表单前的处理
    def save_related(self, request, form, formsets, change):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始save_related - 用户: {request.user.username}, change: {change}")
        logger.info(f"表单对象: {form.instance}, 对象ID: {form.instance.pk}")
        logger.info(f"内联表单数量: {len(formsets)}")
        
        obj = form.instance
        try:
            # 处理表单集，对于DailySchedule表单集，确保它有必要的属性
            for formset in formsets:
                if formset.model == DailySchedule:
                    logger.info(f"处理DailySchedule表单集，确保必要属性")
                    # 确保表单集有必要的属性，避免Django admin系统报错
                    formset.new_objects = []
                    formset.changed_objects = []
                    formset.deleted_objects = []
                    logger.info(f"DailySchedule表单集属性设置完成")
            
            logger.info("开始调用 super().save_related()")
            super().save_related(request, form, formsets, change)
            logger.info("结束 super().save_related()")
            
            logger.info(f"save_related 完成 - 表单对象: {form.instance}, 对象ID: {form.instance.pk}")
        except Exception as e:
            logger.error(f"save_related 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] save_related 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 内联表单处理
    def get_formsets_with_inlines(self, request, obj=None):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始get_formsets_with_inlines - 用户: {request.user.username}, 对象: {obj}")
        try:
            formsets = []
            for inline, formset in super().get_formsets_with_inlines(request, obj):
                logger.info(f"处理内联表单 - Inline类: {inline.__class__.__name__}, 模型: {inline.model.__name__}")
                try:
                    # 不需要在这里初始化formset，直接返回给Django处理
                    formsets.append((inline, formset))
                    logger.info(f"内联表单添加成功 - Inline类: {inline.__class__.__name__}")
                except Exception as formset_error:
                    logger.error(f"内联表单添加失败 - Inline类: {inline.__class__.__name__}, 错误: {str(formset_error)}")
                    logger.error(f"表单添加异常详情: {traceback.format_exc()}")
                    raise
            
            logger.info(f"结束get_formsets_with_inlines - 内联表单数量: {len(formsets)}")
            logger.info(f"内联表单详情: {[f[0].__class__.__name__ for f in formsets]}")
            return formsets
        except Exception as e:
            logger.error(f"get_formsets_with_inlines 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] get_formsets_with_inlines 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 自定义方法，用于显示行程ID并生成正确的编辑链接
    def display_itinerary_id(self, obj):
        """显示行程ID并生成正确的编辑链接"""
        from django.urls import reverse
        from django.utils.html import format_html
        # 直接使用行程ID生成链接，不进行URL编码
        change_url = reverse('smart_trip_admin:apps_itinerary_change', args=[obj.itinerary_id])
        return format_html('<a href="{0}">{1}</a>', change_url, obj.itinerary_id)
    
    display_itinerary_id.short_description = '行程ID'
    display_itinerary_id.allow_tags = True

    # 自定义方法，用于显示目的地城市名称
    def display_destinations(self, obj):
        """显示行程关联的目的地城市名称，多个城市用逗号分隔"""
        from django.utils.html import format_html
        try:
            destinations = obj.destinations.all().order_by('destination_order')
            if not destinations:
                return '-'
            city_names = [dest.city_name for dest in destinations if dest.city_name]
            if not city_names:
                return '-'
            return '，'.join(city_names)
        except Exception:
            return '-'

    display_destinations.short_description = '目的地'

    # 列表显示字段
    list_display = (
        'display_itinerary_id',
        'itinerary_name',
        'contact_person',
        'contact_phone',
        'start_date',
        'departure_city',
        'display_destinations',
        'total_days',
        'status_badge',
        'created_at'
    )
    
    # 取消默认的链接生成，使用自定义方法
    list_display_links = None
    
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
                #('review_deadline', 'expiration_date'),
                ('confirmed_by')
            ),
            'classes': ('compact',)
        }),
        ('行程报价', {
            'fields': ('itinerary_quote',),
            'classes': ('compact',)
        }),
        ('管理信息', {
            'fields': (
                ('created_by', 'updated_by'),
                ('version',),
                'itinerary_json_data',
                'itinerary_quote_json_data'
            ),
            'classes': ('collapse', 'compact')
        })
    )
    
    # 基本内联编辑
    inlines = [
        RequirementItineraryInline,
        TravelerStatsInline,
        DestinationInline
    ]
    
    # 内联编辑的额外配置
    def get_formset_kwargs(self, *args, **kwargs):
        return super().get_formset_kwargs(*args, **kwargs)
    
    # 只读字段
    readonly_fields = (
        'total_days',
        'created_by',
        'updated_by',
        'created_at',
        'updated_at',
        'version',
        'itinerary_json_data',
        'itinerary_quote_json_data'
    )
    
    # 表单字段尺寸调整
    formfield_overrides = {
        models.CharField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '40'})},
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows': 10, 'cols': 60})},
        models.IntegerField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '10', 'type': 'number'})},
        models.DecimalField: {'widget': admin.widgets.AdminTextInputWidget(attrs={'size': '15', 'type': 'number'})},
        models.DateField: {'widget': admin.widgets.AdminDateWidget(attrs={'size': '12'})},
    }

    def get_form(self, request, obj=None, **kwargs):
        """重写 get_form 方法，为 description 和 itinerary_quote 字段使用 EasyMDEEditor"""
        form = super().get_form(request, obj, **kwargs)
        
        # 配置 EasyMDE 默认 preview 模式
        easymde_options = {'initialMode': 'preview'}
        
        # 为 description 字段配置 EasyMDEEditor
        if 'description' in form.base_fields:
            form.base_fields['description'].widget = EasyMDEEditor(easymde_options=easymde_options)
        
        # 为 itinerary_quote 字段配置 EasyMDEEditor
        if 'itinerary_quote' in form.base_fields:
            form.base_fields['itinerary_quote'].widget = EasyMDEEditor(easymde_options=easymde_options)
        
        return form
    
    # 动态生成行程内联
    def get_inline_instances(self, request, obj=None):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始get_inline_instances - 用户: {request.user.username}, 对象: {obj}")
        try:
            inline_instances = super().get_inline_instances(request, obj)
            logger.info(f"基础内联实例数量: {len(inline_instances)}")
            
            # 对于新增行程，默认显示第一天的日程
            if not obj:
                logger.info("新增行程 - 添加第一天日程内联")
                inline = DayScheduleInline(1, self.model, self.admin_site)
                inline.extra = 0  # 显示新增按钮, 但不显示空白记录
                inline_instances.append(inline)
            # 对于现有行程，根据总天数生成日程
            elif obj.total_days:
                logger.info(f"现有行程 - 总天数: {obj.total_days}, 生成日程内联")
                for day in range(1, obj.total_days + 1):
                    logger.info(f"添加第{day}天日程内联")
                    inline = DayScheduleInline(day, self.model, self.admin_site)
                    inline.extra = 0  # 显示新增按钮, 但不显示空白记录
                    inline_instances.append(inline)
            
            logger.info(f"结束get_inline_instances - 内联实例总数: {len(inline_instances)}")
            return inline_instances
        except Exception as e:
            logger.error(f"get_inline_instances 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] get_inline_instances 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
    # 保存时的处理
    def save_model(self, request, obj, form, change):
        import logging
        import sys
        import traceback
        from datetime import timedelta
        
        # 确保输出不缓冲
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 直接使用print语句确保输出，添加时间戳
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 输出到标准输出，确保Docker能够捕获
        print(f"[{timestamp}] =====================================", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 开始保存行程 - 直接输出", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 行程ID: {obj.itinerary_id}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 行程名称: {obj.itinerary_name}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 用户: {request.user.username}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 请求方法: {request.method}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 请求数据: {request.POST}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] =====================================", file=sys.stdout, flush=True)
        
        # 同时输出到标准错误，确保能够在Docker日志中看到
        print(f"[{timestamp}] 开始保存行程 - 标准错误输出", file=sys.stderr, flush=True)
        
        # 使用settings.py中配置的日志记录器
        logger = logging.getLogger('itinerary_admin')
        
        # 立即测试日志输出
        logger.info("测试日志输出 - 确保日志系统正常工作")
        
        # 尝试使用不同的日志级别
        logger.debug("调试信息 - 保存行程开始")
        logger.warning("警告信息 - 保存行程开始")
        logger.error("错误信息 - 保存行程开始")
        
        # 额外添加一些简单的print语句，确保能够在Docker日志中看到
        print("====================================", file=sys.stdout, flush=True)
        print("ITINERARY ADMIN LOG TEST", file=sys.stdout, flush=True)
        print("====================================", file=sys.stdout, flush=True)
        
        # 额外输出到标准错误
        print("====================================", file=sys.stderr, flush=True)
        print("ITINERARY ADMIN LOG TEST - 标准错误", file=sys.stderr, flush=True)
        print("====================================", file=sys.stderr, flush=True)
        
        # 强制刷新所有输出
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 设置创建人和更新人
        if not change:
            obj.created_by = request.user.username
        else:
            obj.updated_by = request.user.username
        
        # ========== 处理 start_date 变化时的自动调整逻辑 ==========
        if change:
            try:
                # 获取原始行程对象
                old_obj = Itinerary.objects.get(pk=obj.pk)
                old_start_date = old_obj.start_date
                new_start_date = obj.start_date
                
                # 检查 start_date 是否发生变化
                if old_start_date and new_start_date and old_start_date != new_start_date:
                    logger.info(f"检测到 start_date 发生变化: {old_start_date} -> {new_start_date}")
                    
                    # 1) 自动根据总天数调整结束日期(end_date)
                    if obj.total_days:
                        old_end_date = old_obj.end_date
                        new_end_date = new_start_date + timedelta(days=obj.total_days - 1)
                        obj.end_date = new_end_date
                        logger.info(f"自动调整 end_date: {old_end_date} -> {new_end_date}")
                    
                    # 2) 自动调整所有关联 Destination 的开始/结束日期
                    destinations = obj.destinations.all()
                    logger.info(f"开始调整 {destinations.count()} 个 Destination 的日期")
                    
                    for dest in destinations:
                        old_arrival = dest.arrival_date
                        old_departure = dest.departure_date
                        
                        # 计算日期偏移量
                        date_offset = (new_start_date - old_start_date).days
                        
                        # 调整 arrival_date
                        if dest.arrival_date:
                            dest.arrival_date = dest.arrival_date + timedelta(days=date_offset)
                        
                        # 调整 departure_date
                        if dest.departure_date:
                            dest.departure_date = dest.departure_date + timedelta(days=date_offset)
                        
                        dest.save()
                        logger.info(f"Destination {dest.city_name} 日期调整: arrival {old_arrival} -> {dest.arrival_date}, departure {old_departure} -> {dest.departure_date}")
                    
                    # 3) 自动调整所有关联 DailySchedule 的活动日期(schedule_date)
                    schedules = DailySchedule.objects.filter(itinerary_id=obj)
                    logger.info(f"开始调整 {schedules.count()} 个 DailySchedule 的日期")
                    
                    for schedule in schedules:
                        old_schedule_date = schedule.schedule_date
                        
                        # 计算日期偏移量
                        date_offset = (new_start_date - old_start_date).days
                        
                        # 调整 schedule_date
                        if schedule.schedule_date:
                            schedule.schedule_date = schedule.schedule_date + timedelta(days=date_offset)
                            schedule.save()
                            logger.info(f"DailySchedule {schedule.schedule_id} 日期调整: {old_schedule_date} -> {schedule.schedule_date}")
                    
                    logger.info("日期调整完成")
            except Itinerary.DoesNotExist:
                logger.warning("未找到原始行程对象，跳过日期调整逻辑")
            except Exception as e:
                logger.error(f"日期调整过程中发生异常: {str(e)}")
                logger.error(f"异常详情: {traceback.format_exc()}")
        
        # ========== 验证关联的记录（不包含DailySchedule） ==========
        from django.core.exceptions import ValidationError
        error_messages = []
        
        try:
            logger.info(f"开始保存行程: {obj.itinerary_id} - {obj.itinerary_name}, 用户: {request.user.username}")
            logger.info(f"请求数据: {request.POST}")
            
            # 验证关联的TravelerStats记录
            logger.info(f"验证关联的TravelerStats记录")
            traveler_stats = obj.traveler_stats.all()
            logger.info(f"找到 {traveler_stats.count()} 条TravelerStats记录")
            
            for i, stat in enumerate(traveler_stats, 1):
                logger.info(f"验证第{i}条TravelerStats记录")
                try:
                    stat.clean()
                    logger.info(f"第{i}条TravelerStats记录验证通过")
                except ValidationError as e:
                    error_msg = f"旅行者统计记录验证错误: {e}"
                    logger.error(error_msg)
                    error_messages.append(error_msg)
                except Exception as e:
                    error_msg = f"旅行者统计记录验证时发生异常: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"异常详情: {traceback.format_exc()}")
                    error_messages.append(error_msg)
            
            # 验证关联的Destination记录
            logger.info(f"验证关联的Destination记录")
            destinations = obj.destinations.all()
            logger.info(f"找到 {destinations.count()} 条Destination记录")
            
            for i, dest in enumerate(destinations, 1):
                logger.info(f"验证第{i}条Destination记录: {dest.city_name}")
                try:
                    dest.clean()
                    logger.info(f"第{i}条Destination记录验证通过: {dest.city_name}")
                except ValidationError as e:
                    error_msg = f"目的地记录 '{dest.city_name}' 验证错误: {e}"
                    logger.error(error_msg)
                    error_messages.append(error_msg)
                except Exception as e:
                    error_msg = f"目的地记录 '{dest.city_name}' 验证时发生异常: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"异常详情: {traceback.format_exc()}")
                    error_messages.append(error_msg)
            
            # 如果有验证错误，抛出异常
            if error_messages:
                logger.error(f"验证错误汇总: {error_messages}")
                raise ValidationError('\n'.join(error_messages))
            
            # 保存行程本身
            logger.info("保存行程本身")
            super().save_model(request, obj, form, change)
            logger.info(f"行程保存成功: {obj.itinerary_id}")
            
            logger.info(f"行程保存操作完成: {obj.itinerary_id}")
        except ValidationError as e:
            logger.error(f"保存行程时验证错误: {e}")
            # 重新抛出异常，确保错误信息显示在页面上
            raise
        except Exception as e:
            # 捕获其他异常并显示
            error_traceback = traceback.format_exc()
            logger.error(f"保存行程时发生异常: {str(e)}")
            logger.error(f"异常详情: {error_traceback}")
            error_messages.append(f"保存行程时出错: {str(e)}")
            raise ValidationError('\n'.join(error_messages))
    
    # 保存内联时的处理
    def save_formset(self, request, form, formset, change):
        import logging
        import sys
        import traceback
        
        # 确保输出不缓冲
        sys.stdout.flush()
        
        # 直接使用print语句确保输出，添加时间戳
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 输出到标准输出，确保Docker能够捕获
        print(f"[{timestamp}] =====================================", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 开始保存内联表单 - 直接输出", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 表单模型: {formset.model.__name__}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 表单数量: {len(formset.forms)}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 用户: {request.user.username}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] 请求方法: {request.method}", file=sys.stdout, flush=True)
        print(f"[{timestamp}] =====================================", file=sys.stdout, flush=True)
        sys.stdout.flush()
        
        # 使用全局配置的日志
        logger = logging.getLogger('itinerary_admin')
        
        # 立即测试日志输出
        logger.info("测试内联表单日志输出 - 确保日志系统正常工作")
        sys.stdout.flush()
        
        logger.info(f"开始保存内联表单: {formset.model.__name__}")
        logger.info(f"表单集数据: {formset.cleaned_data if hasattr(formset, 'cleaned_data') else 'No cleaned data'}")
        
        try:
            # 如果是DailySchedule表单集，跳过保存操作（由独立的编辑页面管理）
            if formset.model == DailySchedule:
                logger.info("跳过DailySchedule表单集的保存，由独立编辑页面管理")
                # 确保表单集有必要的属性，避免Django admin系统报错
                formset.new_objects = []
                formset.changed_objects = []
                formset.deleted_objects = []
                return
            
            instances = formset.save(commit=False)
            logger.info(f"找到 {len(instances)} 个实例需要保存")
            
            for instance in instances:
                if not instance.pk:
                    instance.created_by = request.user.username
                else:
                    instance.updated_by = request.user.username
                
                logger.info(f"保存实例: {instance}")
                instance.save()
            
            for obj in formset.deleted_objects:
                logger.info(f"删除实例: {obj}")
                obj.delete()
            
            formset.save_m2m()
            logger.info("内联表单保存成功")
        except Exception as e:
            error_traceback = traceback.format_exc()
            logger.error(f"保存内联表单时发生异常: {str(e)}")
            logger.error(f"异常详情: {error_traceback}")
            # 重新抛出异常，确保错误信息显示在页面上
            raise
    
    # 重写change_view方法，在详情页底部添加预览按钮，并确保正确处理行程ID
    def change_view(self, request, object_id, form_url='', extra_context=None):
        import logging
        import sys
        import traceback
        logger = logging.getLogger('itinerary_admin')
        logger.info(f"开始change_view - 用户: {request.user.username}, 对象ID: {object_id}, 请求方法: {request.method}")
        try:
            # 确保object_id是原始的行程ID，不进行URL解码
            # 直接使用object_id查询行程对象
            obj = self.get_object(request, object_id)
            
            extra_context = extra_context or {}
            if obj:
                try:
                    extra_context['preview_button'] = self.preview_itinerary(obj)
                    extra_context['quote_button'] = self.quote_itinerary(obj)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            
            # 调用父类方法处理请求
            response = super().change_view(request, object_id, form_url, extra_context)
            logger.info(f"结束change_view - 响应状态: {getattr(response, 'status_code', '未知')}")
            return response
        except Exception as e:
            logger.error(f"change_view 发生异常: {str(e)}")
            logger.error(f"异常详情: {traceback.format_exc()}")
            print(f"[ERROR] change_view 发生异常: {str(e)}", file=sys.stderr, flush=True)
            print(f"[ERROR] 异常详情: {traceback.format_exc()}", file=sys.stderr, flush=True)
            raise
    
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
    
    # 添加行程报价按钮
    def quote_itinerary(self, obj):
        return format_html(
            '<button id="quoteBtn" type="button" class="quote-button" onclick="quoteItinerary()" style="display: inline-flex; align-items: center; padding: 8px 15px; background-color: #FF9800; color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 13px; line-height: 1.4; cursor: pointer; border: none; transition: background-color 0.2s ease, transform 0.1s ease;">\n'  # noqa
            '    <span class="quote-icon" style="margin-right: 6px;">💰</span> 旅游行程报价\n'  # noqa
            '</button>\n'  # noqa
            '<style>\n'  # noqa
            '    .quote-button:hover {{\n'  # noqa
            '        background-color: #F57C00;\n'  # noqa
            '        transform: translateY(-1px);\n'  # noqa
            '    }}\n'  # noqa
            '    .quote-button:focus {{\n'  # noqa
            '        outline: 2px solid #FF9800;\n'  # noqa
            '        outline-offset: 2px;\n'  # noqa
            '    }}\n'  # noqa
            '    .quote-button:active {{\n'  # noqa
            '        transform: translateY(0);\n'  # noqa
            '    }}\n'  # noqa
            '    .quote-button:disabled {{\n'  # noqa
            '        background-color: #bdc3c7;\n'  # noqa
            '        cursor: not-allowed;\n'  # noqa
            '        transform: none;\n'  # noqa
            '    }}\n'  # noqa
            '</style>'
        )
    
    quote_itinerary.short_description = '报价操作'
    quote_itinerary.allow_tags = True
    
    def status_badge(self, obj):
        colors = {
            'DRAFT': '#17a2b8',  # 草稿 - 蓝绿色
            'PENDING_REVIEW': '#ffc107',  # 待审核 - 黄色
            'CONFIRMED': '#28a745',  # 已确认 - 绿色
            'EXPIRED': '#6c757d',  # 已过期 - 灰色
            'CANCELLED': '#dc3545',  # 已取消 - 红色
            'COMPLETED': '#6f42c1'  # 已完成 - 紫色
        }
        color = colors.get(obj.current_status, '#007bff')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '  
            'border-radius: 3px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_current_status_display()
        )
    status_badge.short_description = '状态'
    status_badge.allow_tags = True


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
        'destination_id',
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
        'destination_id__city_name',
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
                ('schedule_date', 'destination_id'),
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
    
    # 重写get_form方法，设置默认值和移除管理图标
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
        
        # 移除关联字段的管理图标
        for field_name in ['attraction_id', 'hotel_id', 'restaurant_id']:
            if field_name in form.base_fields:
                field = form.base_fields[field_name]
                if hasattr(field, 'widget'):
                    field.widget.can_add_related = False
                    field.widget.can_change_related = False
                    field.widget.can_delete_related = False
                    field.widget.can_view_related = False
        
        return form
    
    # 保存时的处理
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
        else:
            obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
    
    # 重写formfield_for_foreignkey方法，过滤下拉菜单并确保编辑时默认选中
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # 处理destination_id字段
        if db_field.name == 'destination_id':
            # 尝试从URL或请求中获取当前的itinerary_id
            itinerary_id = None
            
            # 从URL中获取itinerary_id（编辑页面）
            if 'object_id' in request.resolver_match.kwargs:
                try:
                    daily_schedule = self.model.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    itinerary_id = daily_schedule.itinerary_id
                    # 确保已选中的destination在查询集中
                    if daily_schedule.destination_id:
                        kwargs['initial'] = daily_schedule.destination_id
                except:
                    pass
            
            # 从请求参数中获取itinerary_id（新增页面）
            if not itinerary_id and 'itinerary_id' in request.GET:
                itinerary_id = request.GET.get('itinerary_id')
            
            # 如果有itinerary_id，过滤destination下拉菜单
            if itinerary_id:
                kwargs['queryset'] = Destination.objects.filter(itinerary=itinerary_id)
        
        # 处理attraction_id字段
        elif db_field.name == 'attraction_id':
            # 确保查询集包含所有景点
            kwargs['queryset'] = db_field.remote_field.model.objects.all()
            # 在编辑页面时，确保已选中的attraction在查询集中
            if 'object_id' in request.resolver_match.kwargs:
                try:
                    daily_schedule = self.model.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    if daily_schedule.attraction_id:
                        kwargs['initial'] = daily_schedule.attraction_id
                except:
                    pass
            # 设置formfield，移除管理图标
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            # 移除添加、编辑、删除和查看按钮
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
            return formfield
        
        # 处理hotel_id字段
        elif db_field.name == 'hotel_id':
            # 确保查询集包含所有酒店
            kwargs['queryset'] = db_field.remote_field.model.objects.all()
            # 在编辑页面时，确保已选中的hotel在查询集中
            if 'object_id' in request.resolver_match.kwargs:
                try:
                    daily_schedule = self.model.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    if daily_schedule.hotel_id:
                        kwargs['initial'] = daily_schedule.hotel_id
                except:
                    pass
            # 设置formfield，显示酒店名称并移除管理图标
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.hotel_name}" if hasattr(obj, 'hotel_name') else str(obj)
            # 移除添加、编辑、删除和查看按钮
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
            return formfield
        
        # 处理restaurant_id字段
        elif db_field.name == 'restaurant_id':
            # 确保查询集包含所有餐厅
            kwargs['queryset'] = db_field.remote_field.model.objects.all()
            # 在编辑页面时，确保已选中的restaurant在查询集中
            if 'object_id' in request.resolver_match.kwargs:
                try:
                    daily_schedule = self.model.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    if daily_schedule.restaurant_id:
                        kwargs['initial'] = daily_schedule.restaurant_id
                except:
                    pass
            # 设置formfield，显示餐厅名称并移除管理图标
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: f"{obj.restaurant_name}" if hasattr(obj, 'restaurant_name') else str(obj)
            # 移除添加、编辑、删除和查看按钮
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
            return formfield
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
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
    
    # 添加Media类，引用自定义的JavaScript文件
    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/daily_schedule_filter.js',
        )

