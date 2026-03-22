from django.contrib import admin
from django import forms
from ..models.restaurant import Restaurant
from ..models.country_code import CountryCodeDict


class RestaurantForm(forms.ModelForm):
    # 国家选择下拉菜单
    country_code = forms.ChoiceField(
        choices=[('', '请选择国家')],  # 空选项
        required=False,
        label='国家',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'width: 100%;'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 获取所有国家代码和名称
        countries = CountryCodeDict.get_all_countries()
        # 转换为选项列表，按中文名称排序
        country_choices = sorted(
            [(code, name) for code, name in countries.items()],
            key=lambda x: x[1]
        )
        # 添加空选项并设置选项
        self.fields['country_code'].choices = [('', '请选择国家')] + country_choices
        # 如果有当前值，设置默认选中
        if self.instance and self.instance.country_code:
            self.fields['country_code'].initial = self.instance.country_code

    class Meta:
        model = Restaurant
        fields = '__all__'


class RestaurantAdmin(admin.ModelAdmin):
    # 使用自定义表单
    form = RestaurantForm
    
    # 列表显示字段
    list_display = (
        'restaurant_name', 'get_country_display', 'city_name', 
        'cuisine_type', 'restaurant_type', 'price_range', 'status', 'avg_price_per_person'
    )
    
    def get_country_display(self, obj):
        """
        显示国家中文名称
        """
        return obj.get_country_name()
    
    get_country_display.short_description = '国家'
    
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
                    'restaurant_name', 'country_code', 
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
                    'price_range', 'pricing_strategy'
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
