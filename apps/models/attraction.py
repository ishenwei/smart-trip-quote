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
    
    attraction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='景点ID', db_comment='景点唯一标识符,使用UUID格式')
    attraction_code = models.CharField(max_length=50, unique=True, verbose_name='景点代码', db_comment='景点唯一编码,用于系统内部标识和检索')
    attraction_name = models.CharField(max_length=200, verbose_name='景点名称', db_comment='景点中文名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码', db_comment='所在国家的ISO 3166-1 alpha-2代码,如CN、US等')
    city_name = models.CharField(max_length=100, verbose_name='城市名称', db_comment='景点所在城市名称')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='地区', db_comment='景点所在地区或省份')
    address = models.TextField(blank=True, null=True, verbose_name='地址', db_comment='景点详细地址')
    category = models.CharField(max_length=50, choices=ATTRACTION_CATEGORY_CHOICES, blank=True, null=True, verbose_name='分类', db_comment='景点主分类,如自然景观、历史古迹、文化景点等')
    subcategory = models.CharField(max_length=50, blank=True, null=True, verbose_name='子分类', db_comment='景点子分类,用于更精细的分类')
    tags = JSONField(blank=True, null=True, verbose_name='标签数组', db_comment='景点标签数组,存储关键词如亲子、拍照、必游等')
    description = models.TextField(blank=True, null=True, verbose_name='描述', db_comment='景点详细描述介绍')
    highlights = JSONField(blank=True, null=True, verbose_name='景点特色', db_comment='景点特色亮点列表')
    recommended_duration = models.IntegerField(validators=[MinValueValidator(1)], blank=True, null=True, verbose_name='建议游玩时长（分钟）', db_comment='建议游玩时长,单位为分钟')
    opening_hours = JSONField(blank=True, null=True, verbose_name='开放时间', db_comment='开放时间JSON数据,包含每日开放时段')
    best_season = models.CharField(max_length=50, blank=True, null=True, verbose_name='最佳季节', db_comment='最佳游览季节')
    is_always_open = models.BooleanField(default=False, verbose_name='是否24小时开放', db_comment='标识景点是否全天开放')
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='门票价格', db_comment='门票价格')
    currency = models.CharField(max_length=3, default='CNY', verbose_name='货币', db_comment='价格货币代码,如CNY、USD等')
    ticket_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='票种', db_comment='门票类型,如成人票、儿童票、套票等')
    booking_required = models.BooleanField(default=False, verbose_name='是否需要预订', db_comment='标识是否需要提前预订')
    booking_website = models.CharField(max_length=500, blank=True, null=True, verbose_name='预订网站', db_comment='官方预订网站URL')
    facilities = JSONField(blank=True, null=True, verbose_name='设施', db_comment='景点设施列表,如停车场、餐厅、洗手间等')
    popularity_score = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True, verbose_name='受欢迎度评分', db_comment='景点受欢迎度评分,范围0-5')
    visitor_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True, verbose_name='游客评分', db_comment='游客综合评分,范围0-5')
    review_count = models.IntegerField(default=0, verbose_name='评论数', db_comment='累计评论数量')
    main_image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='主图URL', db_comment='景点主图片URL')
    image_gallery = JSONField(blank=True, null=True, verbose_name='图片库', db_comment='景点图片库URL数组')
    video_url = models.CharField(max_length=500, blank=True, null=True, verbose_name='视频URL', db_comment='景点宣传视频URL')
    status = models.CharField(max_length=20, choices=ATTRACTION_STATUS_CHOICES, verbose_name='状态', db_comment='景点当前状态,如营业中、关闭、维修中等')
    created_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='创建人', db_comment='记录创建人用户名')
    updated_by = models.CharField(max_length=50, blank=True, null=True, verbose_name='更新人', db_comment='记录更新人用户名')
    version = models.IntegerField(default=1, verbose_name='版本', db_comment='数据版本号,用于版本控制')
    
    def __str__(self):
        return self.attraction_name
    
    class Meta:
        db_table = 'attractions'
        verbose_name = '景点数据'
        verbose_name_plural = '景点数据'
        db_table_comment = '景点信息表,存储全球旅游景点的详细信息,包括景点基本信息、门票价格、开放时间、设施服务、评分评价等数据'
