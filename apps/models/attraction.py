from django.db import models
from .base import BaseModel, JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Attraction(BaseModel):
    ATTRACTION_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('UNDER_CONSTRUCTION', 'Under Construction'),
        ('CLOSED', 'Closed'),
    ]
    
    ATTRACTION_CATEGORY_CHOICES = [
        ('NATURAL', 'Natural'),
        ('HISTORICAL', 'Historical'),
        ('CULTURAL', 'Cultural'),
        ('RELIGIOUS', 'Religious'),
        ('MODERN', 'Modern'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('SHOPPING', 'Shopping'),
        ('OUTDOOR', 'Outdoor'),
        ('INDOOR', 'Indoor'),
        ('OTHER', 'Other'),
    ]
    
    attraction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='景点ID')
    attraction_code = models.CharField(max_length=50, unique=True, verbose_name='景点代码')
    attraction_name = models.CharField(max_length=200, verbose_name='景点名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码')
    city_name = models.CharField(max_length=100, verbose_name='城市名称')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='地区')
    address = models.TextField(blank=True, null=True, verbose_name='地址')
    category = models.CharField(max_length=50, choices=ATTRACTION_CATEGORY_CHOICES, blank=True, null=True, verbose_name='分类')
    subcategory = models.CharField(max_length=50, blank=True, null=True, verbose_name='子分类')
    tags = JSONField(blank=True, null=True, verbose_name='标签数组')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    highlights = JSONField(blank=True, null=True, verbose_name='景点特色')
    recommended_duration = models.IntegerField(validators=[MinValueValidator(1)], blank=True, null=True, verbose_name='建议游玩时长（分钟）')
    opening_hours = JSONField(blank=True, null=True, verbose_name='开放时间')
    best_season = JSONField(blank=True, null=True, verbose_name='最佳季节')
    is_always_open = models.BooleanField(default=False, verbose_name='是否24小时开放')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='门票价格')
    currency = models.CharField(max_length=3, default='CNY', verbose_name='货币')
    ticket_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='票种')
    booking_required = models.BooleanField(default=False, verbose_name='是否需要预订')
    booking_website = models.CharField(max_length=500, blank=True, null=True, verbose_name='预订网站')
    facilities = JSONField(blank=True, null=True, verbose_name='设施')
    popularity_score = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True, verbose_name='受欢迎度评分')
    visitor_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True, verbose_name='游客评分')
    review_count = models.IntegerField(default=0, verbose_name='评论数')
    main_image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='主图URL')
    image_gallery = JSONField(blank=True, null=True, verbose_name='图片库')
    video_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='视频URL')
    status = models.CharField(max_length=20, choices=ATTRACTION_STATUS_CHOICES, verbose_name='状态')
    created_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='创建人')
    updated_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='更新人')
    version = models.IntegerField(default=1, verbose_name='版本')
    
    def __str__(self):
        return self.attraction_name
    
    class Meta:
        db_table = 'attractions'
        verbose_name = '景点数据'
        verbose_name_plural = '景点数据'
