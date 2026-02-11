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
        ('原始输入与JSON数据', {
            'fields': (
                'origin_input_display',
                'requirement_json_data_display'
            ),
            'classes': ('collapse',),
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
    
    readonly_fields = ['requirement_id', 'created_at', 'updated_at', 'origin_input_display', 'requirement_json_data_display']
    
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
    
    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(request, f'成功创建需求 {obj.requirement_id}。')
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        self.message_user(request, f'成功更新需求 {obj.requirement_id}。')
        return super().response_change(request, obj)
    
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
        # 先创建HTML按钮和消息容器
        html = '<button type="button" id="itinerary-plan-btn" data-requirement-id="' + str(obj.pk) + '" '
        html += 'style="background-color: #007bff; color: white; padding: 8px 16px; '
        html += 'border: none; border-radius: 4px; font-size: 14px; cursor: pointer; '
        html += 'transition: background-color 0.2s ease;">'
        html += '旅游行程规划'
        html += '</button>'
        html += '<div id="itinerary-plan-message" style="margin-top: 10px; padding: 10px; '
        html += 'border-radius: 4px; display: none;"></div>'
        
        # 创建JavaScript代码，使用CDATA包装以避免与Django模板冲突
        html += '<script type="text/javascript">'
        html += '//<![CDATA['
        html += 'document.addEventListener("DOMContentLoaded", function() {'
        html += '    const btn = document.getElementById("itinerary-plan-btn");'
        html += '    const messageDiv = document.getElementById("itinerary-plan-message");'
        html += '    let isSubmitting = false;'
        html += '    btn.addEventListener("click", function() {'
        html += '        if (isSubmitting) return;'
        html += '        isSubmitting = true;'
        html += '        btn.disabled = true;'
        html += '        btn.style.opacity = "0.6";'
        html += '        btn.innerHTML = "处理中...";'
        html += '        messageDiv.style.display = "none";'
        html += '        const requirementId = btn.dataset.requirementId;'
        html += '        fetch("/admin/apps/requirement/" + requirementId + "/generate-itinerary/", {'
        html += '            method: "POST",'
        html += '            headers: {'
        html += '                "X-CSRFToken": getCookie("csrftoken"),'  
        html += '                "Content-Type": "application/json"'  
        html += '            }'
        html += '        })'
        html += '        .then(response => response.json())'
        html += '        .then(data => {'
        html += '            if (data.success) {'
        html += '                messageDiv.style.backgroundColor = "#d4edda";'
        html += '                messageDiv.style.color = "#155724";'
        html += '                messageDiv.style.border = "1px solid #c3e6cb";'
        html += '                messageDiv.innerHTML = "旅游行程规划设计中，该操作可能需要一些时间，请稍后在旅游行程规划页面查看";'
        html += '            } else {'
        html += '                messageDiv.style.backgroundColor = "#f8d7da";'
        html += '                messageDiv.style.color = "#721c24";'
        html += '                messageDiv.style.border = "1px solid #f5c6cb";'
        html += '                messageDiv.innerHTML = "错误: " + (data.error || "生成行程规划失败");'
        html += '            }'
        html += '            messageDiv.style.display = "block";'
        html += '        })'
        html += '        .catch(error => {'
        html += '            messageDiv.style.backgroundColor = "#f8d7da";'
        html += '            messageDiv.style.color = "#721c24";'
        html += '            messageDiv.style.border = "1px solid #f5c6cb";'
        html += '            messageDiv.innerHTML = "网络错误: 请稍后重试";'
        html += '            messageDiv.style.display = "block";'
        html += '        })'
        html += '        .finally(() => {'
        html += '            isSubmitting = false;'
        html += '            btn.disabled = false;'
        html += '            btn.style.opacity = "1";'
        html += '            btn.innerHTML = "旅游行程规划";'
        html += '        });'
        html += '    });'
        html += '    function getCookie(name) {'
        html += '        let cookieValue = null;'
        html += '        if (document.cookie && document.cookie !== "") {'
        html += '            const cookies = document.cookie.split(";" );'
        html += '            for (let i = 0; i < cookies.length; i++) {'
        html += '                const cookie = cookies[i].trim();'
        html += '                if (cookie.substring(0, name.length + 1) === (name + "=")) {'
        html += '                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));'
        html += '                    break;'
        html += '                }'
        html += '            }'
        html += '        }'
        html += '        return cookieValue;'
        html += '    }'
        html += '});'
        html += '//]]>'
        html += '</script>'
        
        # 直接返回HTML字符串，不使用format_html
        return html
    itinerary_plan_button.short_description = '操作'
    itinerary_plan_button.allow_tags = True

    # 添加按钮到详情页面顶部
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        
        # 直接生成一个简单的按钮HTML，不依赖于requirement对象
        # 这样即使找不到requirement对象，按钮也能显示
        simple_button_html = '''
        <button type="button" id="itinerary-plan-btn" data-requirement-id="''' + object_id + '''" 
        style="background-color: #007bff; color: white; padding: 8px 16px; 
        border: none; border-radius: 4px; font-size: 14px; cursor: pointer; 
        transition: background-color 0.2s ease;">
        旅游行程规划
        </button>
        <div id="itinerary-plan-message" style="margin-top: 10px; padding: 10px; 
        border-radius: 4px; display: none;"></div>
        
        <script type="text/javascript">
        //<![CDATA[
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
                fetch("/admin/apps/requirement/" + requirementId + "/generate-itinerary/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),  
                        "Content-Type": "application/json"  
                    }
                })
                .then(response => response.json())
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
                    messageDiv.innerHTML = "网络错误: 请稍后重试";
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
        //]]>
        </script>
        '''
        
        # 直接将按钮HTML添加到extra_context
        extra_context['itinerary_plan_button'] = simple_button_html
        
        # 调用父类的change_view方法
        return super().change_view(request, object_id, form_url, extra_context)
    
    # 另一种添加按钮的方法，通过render_change_form
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # 直接生成一个简单的按钮HTML
        if obj:
            object_id = obj.requirement_id
        else:
            object_id = ''
        
        simple_button_html = '''
        <button type="button" id="itinerary-plan-btn" data-requirement-id="''' + object_id + '''" 
        style="background-color: #007bff; color: white; padding: 8px 16px; 
        border: none; border-radius: 4px; font-size: 14px; cursor: pointer; 
        transition: background-color 0.2s ease;">
        旅游行程规划
        </button>
        <div id="itinerary-plan-message" style="margin-top: 10px; padding: 10px; 
        border-radius: 4px; display: none;"></div>
        
        <script type="text/javascript">
        //<![CDATA[
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
                fetch("/admin/apps/requirement/" + requirementId + "/generate-itinerary/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),  
                        "Content-Type": "application/json"  
                    }
                })
                .then(response => response.json())
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
                    messageDiv.innerHTML = "网络错误: 请稍后重试";
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
        //]]>
        </script>
        '''
        
        # 将按钮HTML添加到context
        context['itinerary_plan_button'] = simple_button_html
        
        # 调用父类的render_change_form方法
        return super().render_change_form(request, context, add, change, form_url, obj)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/jquery.init.js',)
