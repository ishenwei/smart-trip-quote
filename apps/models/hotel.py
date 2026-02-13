from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .base import BaseModel, JSONField
import uuid


class Hotel(BaseModel):
    class HotelType(models.TextChoices):
        LUXURY = 'LUXURY', '奢华酒店'
        BUSINESS = 'BUSINESS', '商务酒店'
        RESORT = 'RESORT', '度假酒店'
        BOUTIQUE = 'BOUTIQUE', '精品酒店'
        HOSTEL = 'HOSTEL', '青年旅舍'
        APARTMENT = 'APARTMENT', '公寓酒店'
        HOMESTAY = 'HOMESTAY', '民宿'
        MOTEL = 'MOTEL', '汽车旅馆'
        OTHER = 'OTHER', '其他'
    
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', '营业中'
        INACTIVE = 'INACTIVE', '未营业'
        RENOVATING = 'RENOVATING', '装修中'
        CLOSED = 'CLOSED', '已关闭'
    
    hotel_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='酒店ID', db_comment='酒店唯一标识符,使用UUID格式')
    hotel_code = models.CharField(max_length=50, unique=True, verbose_name='酒店代码', db_comment='酒店唯一编码,用于系统内部标识和检索')
    hotel_name = models.CharField(max_length=200, verbose_name='酒店名称', db_comment='酒店中文名称')
    brand_name = models.CharField(max_length=100, blank=True, verbose_name='品牌名称', db_comment='酒店所属品牌名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码', db_comment='所在国家的ISO 3166-1 alpha-2代码,如CN、US等')
    city_name = models.CharField(max_length=100, verbose_name='城市名称', db_comment='酒店所在城市名称')
    district = models.CharField(max_length=100, blank=True, verbose_name='区域', db_comment='酒店所在区域或商圈')
    address = models.TextField(verbose_name='地址', db_comment='酒店详细地址')
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='纬度',
        db_comment='地理纬度坐标,范围-90到90'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='经度',
        db_comment='地理经度坐标,范围-180到180'
    )
    hotel_star = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='星级',
        db_comment='酒店星级,范围1-5'
    )
    hotel_type = models.CharField(
        max_length=50,
        choices=HotelType.choices,
        blank=True,
        verbose_name='酒店类型',
        db_comment='酒店类型,如奢华酒店、商务酒店、度假酒店等'
    )
    tags = JSONField(verbose_name='标签', default=dict, db_comment='酒店标签字典,存储关键词如商务、亲子、度假等')
    description = models.TextField(blank=True, verbose_name='描述', db_comment='酒店详细描述介绍')
    check_in_time = models.TimeField(default='14:00', verbose_name='入住时间', db_comment='标准入住时间')
    check_out_time = models.TimeField(default='12:00', verbose_name='退房时间', db_comment='标准退房时间')
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name='联系电话', db_comment='酒店联系电话')
    contact_email = models.CharField(max_length=255, blank=True, verbose_name='联系邮箱', db_comment='酒店联系邮箱')
    website = models.CharField(max_length=500, blank=True, verbose_name='网站', db_comment='酒店官方网站URL')
    amenities = JSONField(verbose_name='设施', default=dict, db_comment='酒店设施字典,如WiFi、停车场、健身房等')
    room_facilities = JSONField(verbose_name='房间设施', default=dict, db_comment='房间内设施字典,如空调、电视、保险箱等')
    business_facilities = JSONField(verbose_name='商务设施', default=dict, db_comment='商务设施字典,如会议室、商务中心等')
    room_types = JSONField(verbose_name='房型信息', default=dict, db_comment='房型信息字典,包含各种房型及其描述')
    price_range = models.CharField(max_length=50, blank=True, verbose_name='价格范围', db_comment='价格范围描述,如经济型、中档、高档等')
    currency = models.CharField(max_length=3, default='CNY', verbose_name='货币', db_comment='价格货币代码,如CNY、USD等')
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='最低价格',
        db_comment='最低房价'
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='最高价格',
        db_comment='最高房价'
    )
    popularity_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='受欢迎度评分',
        db_comment='酒店受欢迎度评分,范围0-5'
    )
    guest_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name='客人评分',
        db_comment='客人综合评分,范围0-5'
    )
    review_count = models.IntegerField(default=0, verbose_name='评论数', db_comment='累计评论数量')
    main_image_url = models.CharField(max_length=500, blank=True, verbose_name='主图URL', db_comment='酒店主图片URL')
    image_gallery = JSONField(verbose_name='图片库', default=list, db_comment='酒店图片库URL数组')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='状态',
        db_comment='酒店当前状态,如营业中、未营业、装修中、已关闭'
    )
    created_by = models.CharField(max_length=50, blank=True, verbose_name='创建人', db_comment='记录创建人用户名')
    updated_by = models.CharField(max_length=50, blank=True, verbose_name='更新人', db_comment='记录更新人用户名')
    version = models.IntegerField(default=1, verbose_name='版本', db_comment='数据版本号,用于版本控制')
    
    class Meta:
        db_table = 'hotels'
        verbose_name = '酒店数据'
        verbose_name_plural = '酒店数据'
        ordering = ['-created_at']
        db_table_comment = '酒店信息表,存储全球酒店住宿的详细信息,包括酒店基本信息、房型设施、价格范围、评分评价等数据'
        indexes = [
            models.Index(fields=['hotel_code']),
            models.Index(fields=['hotel_name']),
            models.Index(fields=['country_code']),
            models.Index(fields=['city_name']),
            models.Index(fields=['hotel_star']),
            models.Index(fields=['hotel_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.hotel_name} ({self.hotel_code})"
    
    def clean(self):
        # 验证国家代码格式
        if self.country_code and len(self.country_code) != 2:
            raise ValidationError({'country_code': '国家代码必须是2个字符（ISO 3166-1 alpha-2）'})
        
        # 验证星级范围
        if self.hotel_star and (self.hotel_star < 1 or self.hotel_star > 5):
            raise ValidationError({'hotel_star': '星级必须在1-5之间'})
        
        # 验证评分范围
        for field_name in ['popularity_score', 'guest_rating']:
            value = getattr(self, field_name)
            if value is not None and (value < 0 or value > 5):
                raise ValidationError({field_name: '评分必须在0-5之间'})
        
        # 验证评论数
        if self.review_count < 0:
            raise ValidationError({'review_count': '评论数不能为负数'})
        
        # 验证价格
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValidationError({'min_price': '最低价格不能大于最高价格'})
