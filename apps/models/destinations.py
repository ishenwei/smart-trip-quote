from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel
from .itinerary import Itinerary
import uuid


class Destination(BaseModel):
    destination_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='目的地ID', db_comment='目的地唯一标识符,使用UUID格式')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='destinations', verbose_name='行程', db_comment='关联的行程,外键关联itinerary表')
    destination_order = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='目的地顺序', db_comment='目的地在行程中的访问顺序')
    city_name = models.CharField(max_length=100, verbose_name='城市名称', db_comment='目的地城市名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码', db_comment='所在国家的ISO 3166-1 alpha-2代码,如CN、US等')
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name='地区（如省、州）', db_comment='所在地区或省份')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)], verbose_name='纬度', db_comment='地理纬度坐标,范围-90到90')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)], verbose_name='经度', db_comment='地理经度坐标,范围-180到180')
    arrival_date = models.DateField(verbose_name='抵达日期', db_comment='抵达该目的地的日期')
    departure_date = models.DateField(verbose_name='离开日期', db_comment='离开该目的地的日期')
    nights = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='住宿晚数', db_comment='在该目的地住宿的晚数,自动计算')

    def save(self, *args, **kwargs):
        # 计算住宿晚数
        if self.arrival_date and self.departure_date:
            self.nights = (self.departure_date - self.arrival_date).days
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.city_name

    class Meta:
        db_table = 'destinations'
        verbose_name = '目的地表'
        verbose_name_plural = '目的地表'
        db_table_comment = '行程目的地表,存储行程中包含的所有目的地城市信息,包括地理位置、抵达离开日期、住宿晚数等'
