from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .base import BaseModel, JSONField
import uuid


class Restaurant(BaseModel):
    class RestaurantType(models.TextChoices):
        FINE_DINING = 'FINE_DINING', '精致餐饮'
        CASUAL = 'CASUAL', '休闲餐饮'
        FAST_FOOD = 'FAST_FOOD', '快餐'
        CAFE = 'CAFE', '咖啡馆'
        BAR = 'BAR', '酒吧'
        STREET_FOOD = 'STREET_FOOD', '街头美食'
        BUFFET = 'BUFFET', '自助餐'
        OTHER = 'OTHER', '其他'
    
    class PriceRange(models.TextChoices):
        LOW = '$', '经济型'
        MEDIUM = '$$', '中档'
        HIGH = '$$$', '高档'
        LUXURY = '$$$$', '奢华'
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', '营业中'
        INACTIVE = 'INACTIVE', '未营业'
        TEMPORARILY_CLOSED = 'TEMPORARILY_CLOSED', '临时关闭'
        PERMANENTLY_CLOSED = 'PERMANENTLY_CLOSED', '永久关闭'
    
    restaurant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='餐厅ID')
    restaurant_code = models.CharField(max_length=50, unique=True, verbose_name='餐厅代码')
    restaurant_name = models.CharField(max_length=200, verbose_name='餐厅名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码')
    city_name = models.CharField(max_length=100, verbose_name='城市名称')
    district = models.CharField(max_length=100, blank=True, verbose_name='区域')
    address = models.TextField(verbose_name='地址')
    cuisine_type = models.CharField(max_length=100, verbose_name='菜系')
    sub_cuisine_types = JSONField(verbose_name='子菜系数组', default=list)
    restaurant_type = models.CharField(
        max_length=50,
        choices=RestaurantType.choices,
        blank=True,
        verbose_name='餐厅类型'
    )
    tags = JSONField(verbose_name='标签', default=dict)
    description = models.TextField(blank=True, verbose_name='描述')
    signature_dishes = JSONField(verbose_name='招牌菜', default=dict)
    chef_name = models.CharField(max_length=100, blank=True, verbose_name='主厨名字')
    year_established = models.IntegerField(blank=True, null=True, verbose_name='建立年份')
    opening_hours = JSONField(verbose_name='营业时间', default=dict)
    is_24_hours = models.BooleanField(default=False, verbose_name='是否24小时营业')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话')
    contact_email = models.CharField(max_length=255, blank=True, verbose_name='联系邮箱')
    website = models.CharField(max_length=500, blank=True, verbose_name='网站')
    reservation_required = models.BooleanField(default=False, verbose_name='是否需要预订')
    reservation_website = models.CharField(max_length=500, blank=True, verbose_name='预订网站')
    price_range = models.CharField(
        max_length=50,
        choices=PriceRange.choices,
        verbose_name='价格范围'
    )
    avg_price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='人均价格'
    )
    amenities = JSONField(verbose_name='设施', default=dict)
    seating_capacity = models.IntegerField(blank=True, null=True, verbose_name='座位数')
    private_rooms_available = models.BooleanField(default=False, verbose_name='是否有包间')
    dietary_options = JSONField(verbose_name='饮食选项', default=dict)
    alcohol_served = models.BooleanField(blank=True, null=True, verbose_name='是否提供酒精饮料')
    popularity_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='受欢迎度评分'
    )
    food_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='食物评分'
    )
    service_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='服务评分'
    )
    review_count = models.IntegerField(default=0, verbose_name='评论数')
    main_image_url = models.CharField(max_length=500, blank=True, verbose_name='主图URL')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='状态'
    )
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人')
    updated_by = models.CharField(max_length=50, blank=True, verbose_name='更新人')
    version = models.IntegerField(default=1, verbose_name='版本')
    
    class Meta:
        db_table = 'restaurants'
        verbose_name = '餐厅数据'
        verbose_name_plural = '餐厅数据'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['restaurant_code']),
            models.Index(fields=['restaurant_name']),
            models.Index(fields=['country_code']),
            models.Index(fields=['city_name']),
            models.Index(fields=['cuisine_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.restaurant_name} ({self.restaurant_code})"
    
    def clean(self):
        # 验证国家代码格式
        if self.country_code and len(self.country_code) != 2:
            raise ValidationError({'country_code': '国家代码必须是2个字符（ISO 3166-1 alpha-2）'})
        
        # 验证评分范围
        for field_name in ['popularity_score', 'food_rating', 'service_rating']:
            value = getattr(self, field_name)
            if value is not None and (value < 0 or value > 5):
                raise ValidationError({field_name: '评分必须在0-5之间'})
        
        # 验证建立年份
        if self.year_established:
            import datetime
            current_year = datetime.datetime.now().year
            if self.year_established > current_year:
                raise ValidationError({'year_established': '建立年份不能超过当前年份'})
        
        # 验证评论数
        if self.review_count < 0:
            raise ValidationError({'review_count': '评论数不能为负数'})
        
        # 验证座位数
        if self.seating_capacity and self.seating_capacity < 0:
            raise ValidationError({'seating_capacity': '座位数不能为负数'})
