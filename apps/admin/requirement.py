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
    # 指定主键URL参数名称，解决需求ID在URL中被编码的问题
    pk_url_kwarg = 'requirement_id'

    # ==================== 重构提取的公共方法 ====================

    def _get_itinerary_plan_js(self):
        """
        生成旅游行程规划按钮的JavaScript代码
        提取公共的fetch请求和消息处理逻辑
        """
        return '''
        document.addEventListener("DOMContentLoaded", function() {
            const btn = document.getElementById("itinerary-plan-btn");
            const messageDiv = document.getElementById("itinerary-plan-message");
            let isSubmitting = false;
            btn.addEventListener("click", function() {
                if (isSubmitting) return;
                isSubmitting = true;
                btn.disabled = true;
                btn.style.opacity = "0.6";
                btn.innerHTML = "处理中...";
                messageDiv.style.display = "none";
                const requirementId = btn.dataset.requirementId;
                fetch("/admin/requirement/" + requirementId + "/generate-itinerary/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json"
                    }
                })
                .then(response => {
                    return response.json().then(data => {
                        if (!response.ok) {
                            throw { status: response.status, data: data };
                        }
                        return data;
                    });
                })
                .then(data => {
                    if (data.success) {
                        messageDiv.style.backgroundColor = "#d4edda";
                        messageDiv.style.color = "#155724";
                        messageDiv.style.border = "1px solid #c3e6cb";
                        messageDiv.innerHTML = "旅游行程规划设计中，该操作可能需要一些时间，请稍后在旅游行程规划页面查看";
                    } else {
                        messageDiv.style.backgroundColor = "#f8d7da";
                        messageDiv.style.color = "#721c24";
                        messageDiv.style.border = "1px solid #f5c6cb";
                        messageDiv.innerHTML = "错误: " + (data.error || "生成行程规划失败");
                    }
                    messageDiv.style.display = "block";
                })
                .catch(error => {
                    messageDiv.style.backgroundColor = "#f8d7da";
                    messageDiv.style.color = "#721c24";
                    messageDiv.style.border = "1px solid #f5c6cb";
                    if (error.data && error.data.error) {
                        messageDiv.innerHTML = "错误: " + error.data.error;
                    } else {
                        messageDiv.innerHTML = "网络错误: " + (error.message || "请稍后重试");
                    }
                    messageDiv.style.display = "block";
                })
                .finally(() => {
                    isSubmitting = false;
                    btn.disabled = false;
                    btn.style.opacity = "1";
                    btn.innerHTML = "旅游行程规划";
                });
            });
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== "") {
                    const cookies = document.cookie.split("; ");
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + "=")) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
        });
        '''

    def _get_itinerary_plan_button_html(self, requirement_id):
        """
        生成旅游行程规划按钮的HTML结构
        
        Args:
            requirement_id: 需求ID
            
        Returns:
            包含按钮和消息容器的HTML字符串
        """
        return f'''
        <button type="button" id="itinerary-plan-btn" data-requirement-id="{requirement_id}"
        style="background-color: #007bff; color: white; padding: 8px 16px;
        border: none; border-radius: 4px; font-size: 14px; cursor: pointer;
        transition: background-color 0.2s ease;">
        旅游行程规划
        </button>
        <div id="itinerary-plan-message" style="margin-top: 10px; padding: 10px;
        border-radius: 4px; display: none;"></div>
        '''

    def _get_itinerary_plan_script(self, requirement_id):
        """
        生成完整的旅游行程规划按钮HTML和JavaScript
        
        Args:
            requirement_id: 需求ID
            
        Returns:
            完整的HTML+JavaScript字符串
        """
        html = self._get_itinerary_plan_button_html(requirement_id)
        html += '<script type="text/javascript">'
        html += '//<![CDATA['
        html += self._get_itinerary_plan_js()
        html += '//]]>'
        html += '</script>'
        return html

    def _get_related_itineraries(self, requirement):
        """
        获取与需求关联的行程规划列表
        
        Args:
            requirement: Requirement对象
            
        Returns:
            行程规划字典列表
        """
        from apps.models.requirement_itinerary import RequirementItinerary

        if not requirement:
            return []

        try:
            requirement_itineraries = RequirementItinerary.objects.filter(requirement=requirement)
            itineraries = []
            for ri in requirement_itineraries:
                itinerary = ri.itinerary
                itineraries.append({
                    'itinerary_id': itinerary.itinerary_id,
                    'itinerary_name': itinerary.itinerary_name,
                    'created_at': itinerary.created_at
                })
            return itineraries
        except Exception:
            return []
    
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
        cities = obj.destination_cities
        
        # 如果是字符串，尝试解析为列表（支持 JSON 和 Python 字面量格式）
        if isinstance(cities, str):
            try:
                # 先尝试 JSON 解析
                cities = json.loads(cities)
            except json.JSONDecodeError:
                try:
                    # 再尝试 Python 字面量解析（处理单引号的情况）
                    cities = ast.literal_eval(cities)
                except (ValueError, SyntaxError):
                    cities = None
        
        # 确保 cities 是列表
        if not isinstance(cities, list):
            cities = []
        
        if cities:
            city_names = []
            for city in cities[:3]:
                if isinstance(city, dict):
                    city_names.append(city.get('name', str(city)))
                else:
                    city_names.append(str(city))
            return ','.join(city_names) + ('...' if len(cities) > 3 else '')
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
    
    def itinerary_plan_button(self, obj):
        """生成旅游行程规划按钮"""
        return self._get_itinerary_plan_script(str(obj.pk))
    itinerary_plan_button.short_description = '操作'
    itinerary_plan_button.allow_tags = True

    # 添加按钮到详情页面顶部
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        # 使用公共方法生成按钮HTML和JavaScript
        extra_context['itinerary_plan_button'] = self._get_itinerary_plan_script(object_id)

        # 获取与当前需求关联的行程规划
        try:
            requirement = Requirement.objects.get(requirement_id=object_id)
            extra_context['itineraries'] = self._get_related_itineraries(requirement)
        except Requirement.DoesNotExist:
            extra_context['itineraries'] = []

        # 调用父类的change_view方法
        return super().change_view(request, object_id, form_url, extra_context)
    
    # 另一种添加按钮的方法，通过render_change_form
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # 获取需求ID
        object_id = obj.requirement_id if obj else ''

        # 使用公共方法生成按钮HTML和JavaScript
        context['itinerary_plan_button'] = self._get_itinerary_plan_script(object_id)

        # 获取与当前需求关联的行程规划
        context['itineraries'] = self._get_related_itineraries(obj)

        # 调用父类的render_change_form方法
        return super().render_change_form(request, context, add, change, form_url, obj)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/jquery.init.js',)
