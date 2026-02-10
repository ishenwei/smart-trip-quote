from django.contrib import admin
from ..models.restaurant import Restaurant


class RestaurantAdmin(admin.ModelAdmin):
    # 列表显示字段
    list_display = (
        'restaurant_name', 'restaurant_code', 'country_code', 'city_name', 
        'cuisine_type', 'restaurant_type', 'price_range', 'status', 'avg_price_per_person'
    )
    
    # 搜索字段
    search_fields = (
        'restaurant_name', 'restaurant_code', 'country_code', 'city_name', 
        'cuisine_type', 'description', 'chef_name'
    )
    
    # 筛选条件
    list_filter = (
        'status', 'restaurant_type', 'cuisine_type', 'country_code', 'city_name', 
        'price_range', 'reservation_required', 'is_24_hours', 'private_rooms_available'
    )
    
    # 排序方式
    ordering = ('-created_at',)
    
    # 详细页面字段分组
    fieldsets = (
        (
            '基本信息', {
                'fields': (
                    'restaurant_code', 'restaurant_name', 'country_code', 
                    'city_name', 'district', 'address', 'cuisine_type', 
                    'sub_cuisine_types', 'restaurant_type'
                )
            }
        ),
        (
            '详细信息', {
                'fields': (
                    'tags', 'description', 'signature_dishes', 'chef_name', 
                    'year_established'
                )
            }
        ),
        (
            '营业信息', {
                'fields': (
                    'opening_hours', 'is_24_hours', 'contact_phone', 'contact_email', 
                    'website'
                )
            }
        ),
        (
            '预订信息', {
                'fields': (
                    'reservation_required', 'reservation_website'
                )
            }
        ),
        (
            '价格信息', {
                'fields': (
                    'price_range', 'avg_price_per_person'
                )
            }
        ),
        (
            '设施信息', {
                'fields': (
                    'amenities', 'seating_capacity', 'private_rooms_available', 
                    'dietary_options', 'alcohol_served'
                )
            }
        ),
        (
            '评分信息', {
                'fields': (
                    'popularity_score', 'food_rating', 'service_rating', 'review_count'
                )
            }
        ),
        (
            '图片信息', {
                'fields': ('main_image_url',)
            }
        ),
        (
            '管理信息', {
                'fields': ('status', 'created_by', 'updated_by', 'version'),
                'classes': ('collapse',)
            }
        ),
    )
