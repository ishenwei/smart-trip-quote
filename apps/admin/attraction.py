from django.contrib import admin
from ..models.attraction import Attraction


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    # 列表显示字段
    list_display = (
        'attraction_name', 'attraction_code', 'country_code', 'city_name', 
        'category', 'status', 'popularity_score', 'visitor_rating'
    )
    
    # 搜索字段
    search_fields = (
        'attraction_name', 'attraction_code', 'country_code', 'city_name', 
        'category', 'description'
    )
    
    # 筛选条件
    list_filter = (
        'status', 'category', 'country_code', 'city_name', 
        'booking_required', 'is_always_open'
    )
    
    # 排序方式
    ordering = ('-created_at',)
    
    # 详细页面字段分组
    fieldsets = (
        (
            '基本信息', {
                'fields': (
                    'attraction_code', 'attraction_name', 'country_code', 
                    'city_name', 'region', 'address', 'category', 'subcategory'
                )
            }
        ),
        (
            '详细信息', {
                'fields': (
                    'tags', 'description', 'highlights', 'recommended_duration', 
                    'opening_hours', 'best_season', 'is_always_open'
                )
            }
        ),
        (
            '门票信息', {
                'fields': (
                    'ticket_price', 'currency', 'ticket_type', 'booking_required', 
                    'booking_website'
                )
            }
        ),
        (
            '其他信息', {
                'fields': (
                    'facilities', 'popularity_score', 'visitor_rating', 'review_count', 
                    'main_image_url', 'image_gallery', 'video_url'
                )
            }
        ),
        (
            '管理信息', {
                'fields': ('status', 'created_by', 'updated_by', 'version'),
                'classes': ('collapse',)
            }
        ),
    )
