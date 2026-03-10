from django.contrib import admin
from django import forms
from ..models.attraction import Attraction
from ..models.country_code import CountryCodeDict


class AttractionForm(forms.ModelForm):
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
        model = Attraction
        fields = '__all__'

    # 添加district字段的widget配置
    district = forms.CharField(
        required=False,
        label='区域和商圈',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'style': 'width: 100%;',
            'placeholder': '例如：朝阳区-三里屯商圈'
        })
    )


class AttractionAdmin(admin.ModelAdmin):
    # 使用自定义表单
    form = AttractionForm
    
    # 列表显示字段
    list_display = (
        'attraction_name', 'city_name', 'district', 'get_country_display', 
        'category', 'status', 'popularity_score', 'visitor_rating'
    )
    
    def get_country_display(self, obj):
        """
        显示国家中文名称
        """
        return obj.get_country_name()
    
    get_country_display.short_description = '国家'
    
    # 搜索字段
    search_fields = (
        'attraction_name', 'attraction_code', 'country_code', 'city_name', 'district', 
        'category', 'description'
    )
    
    # 筛选条件
    list_filter = (
        'status', 'category', 'country_code', 'city_name', 'district', 
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
                    'city_name', 'district', 'region', 'address', 'category', 'subcategory'
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
