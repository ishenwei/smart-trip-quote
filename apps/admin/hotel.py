from django.contrib import admin
from ..models.hotel import Hotel


class HotelAdmin(admin.ModelAdmin):
    # 列表显示字段
    list_display = (
        'hotel_name', 'hotel_code', 'brand_name', 'country_code', 'city_name', 
        'hotel_star', 'hotel_type', 'status', 'guest_rating', 'min_price'
    )
    
    # 搜索字段
    search_fields = (
        'hotel_name', 'hotel_code', 'brand_name', 'country_code', 'city_name', 
        'address', 'description'
    )
    
    # 筛选条件
    list_filter = (
        'status', 'hotel_type', 'hotel_star', 'country_code', 'city_name'
    )
    
    # 排序方式
    ordering = ('-created_at',)
    
    # 详细页面字段分组
    fieldsets = (
        (
            '基本信息', {
                'fields': (
                    'hotel_code', 'hotel_name', 'brand_name', 'country_code', 
                    'city_name', 'district', 'address', 'latitude', 'longitude'
                )
            }
        ),
        (
            '详细信息', {
                'fields': (
                    'hotel_star', 'hotel_type', 'tags', 'description', 
                    'check_in_time', 'check_out_time'
                )
            }
        ),
        (
            '联系信息', {
                'fields': ('contact_phone', 'contact_email', 'website')
            }
        ),
        (
            '设施信息', {
                'fields': ('amenities', 'room_facilities', 'business_facilities', 'room_types')
            }
        ),
        (
            '价格信息', {
                'fields': (
                    'price_range', 'currency', 'min_price', 'max_price'
                )
            }
        ),
        (
            '评分信息', {
                'fields': (
                    'popularity_score', 'guest_rating', 'review_count'
                )
            }
        ),
        (
            '图片信息', {
                'fields': ('main_image_url', 'image_gallery')
            }
        ),
        (
            '管理信息', {
                'fields': ('status', 'created_by', 'updated_by', 'version'),
                'classes': ('collapse',)
            }
        ),
    )
