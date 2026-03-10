from django.contrib import admin
from django import forms
from ..models.hotel import Hotel
from ..models.country_code import CountryCodeDict


class HotelForm(forms.ModelForm):
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
        model = Hotel
        fields = '__all__'


class HotelAdmin(admin.ModelAdmin):
    # 使用自定义表单
    form = HotelForm
    
    # 列表显示字段
    list_display = (
        'hotel_name', 'brand_name', 'get_country_display', 'city_name', 
        'hotel_star', 'hotel_type', 'status', 'guest_rating', 'min_price'
    )
    
    def get_country_display(self, obj):
        """
        显示国家中文名称
        """
        return obj.get_country_name()
    
    get_country_display.short_description = '国家'
    
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
