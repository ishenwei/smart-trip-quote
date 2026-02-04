from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base import BaseModel
from .itinerary import Itinerary
import uuid


class Destination(BaseModel):
    destination_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='目的地ID')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='destinations', verbose_name='行程')
    destination_order = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='目的地顺序')
    city_name = models.CharField(max_length=100, verbose_name='城市名称')
    country_code = models.CharField(max_length=2, verbose_name='国家代码')
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name='地区（如省、州）')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)], verbose_name='纬度')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)], verbose_name='经度')
    arrival_date = models.DateField(verbose_name='抵达日期')
    departure_date = models.DateField(verbose_name='离开日期')
    nights = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='住宿晚数')

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
