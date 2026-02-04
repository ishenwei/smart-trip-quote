from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from .base import BaseModel
import uuid


class DailySchedule(BaseModel):
    class ActivityType(models.TextChoices):
        FLIGHT = 'FLIGHT', '航班'
        TRAIN = 'TRAIN', '火车'
        ATTRACTION = 'ATTRACTION', '景点'
        MEAL = 'MEAL', '餐饮'
        TRANSPORT = 'TRANSPORT', '交通'
        SHOPPING = 'SHOPPING', '购物'
        FREE = 'FREE', '自由活动'
        CHECK_IN = 'CHECK_IN', '入住'
        CHECK_OUT = 'CHECK_OUT', '退房'
        OTHER = 'OTHER', '其他'
    
    class BookingStatus(models.TextChoices):
        NOT_BOOKED = 'NOT_BOOKED', '未预订'
        PENDING = 'PENDING', '待确认'
        CONFIRMED = 'CONFIRMED', '已确认'
        CANCELLED = 'CANCELLED', '已取消'
    
    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='活动ID')
    itinerary_id = models.ForeignKey('Itinerary', on_delete=models.CASCADE, to_field='itinerary_id', verbose_name='行程ID')
    day_number = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='第几天')
    schedule_date = models.DateField(verbose_name='活动日期')
    destination_id = models.ForeignKey('Destination', on_delete=models.SET_NULL, null=True, blank=True, to_field='destination_id', verbose_name='目的地ID')
    activity_type = models.CharField(max_length=30, choices=ActivityType.choices, verbose_name='活动类型')
    activity_title = models.CharField(max_length=200, verbose_name='活动标题')
    activity_description = models.TextField(null=True, blank=True, verbose_name='活动描述')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    attraction_id = models.ForeignKey('Attraction', on_delete=models.SET_NULL, null=True, blank=True, to_field='attraction_id', verbose_name='关联景点ID')
    hotel_id = models.ForeignKey('Hotel', on_delete=models.SET_NULL, null=True, blank=True, to_field='hotel_id', verbose_name='关联酒店ID')
    restaurant_id = models.ForeignKey('Restaurant', on_delete=models.SET_NULL, null=True, blank=True, to_field='restaurant_id', verbose_name='关联餐厅ID')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='预估费用')
    currency = models.CharField(max_length=3, default='CNY', verbose_name='货币')
    # budget_id = models.ForeignKey('BudgetBreakdown', on_delete=models.SET_NULL, null=True, blank=True, to_field='budget_id', verbose_name='预算细分')
    booking_status = models.CharField(max_length=15, choices=BookingStatus.choices, null=True, blank=True, verbose_name='预订状态')
    booking_reference = models.CharField(max_length=100, null=True, blank=True, verbose_name='预订参考号')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # 验证结束时间必须晚于开始时间
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError({'end_time': '结束时间必须晚于开始时间'})
        
        # 验证只能关联一个资源（景点、酒店或餐厅）
        resource_count = 0
        if self.attraction_id:
            resource_count += 1
        if self.hotel_id:
            resource_count += 1
        if self.restaurant_id:
            resource_count += 1
        
        if resource_count > 1:
            raise ValidationError('一个活动只能关联一个资源（景点、酒店或餐厅）')
        
        # 验证activity_type为ATTRACTION时必须关联attraction_id
        if self.activity_type == self.ActivityType.ATTRACTION and not self.attraction_id:
            raise ValidationError('活动类型为景点时必须关联景点ID')
        
        # 验证activity_type为MEAL时建议关联restaurant_id
        if self.activity_type == self.ActivityType.MEAL and not self.restaurant_id:
            raise ValidationError('活动类型为餐饮时建议关联餐厅ID')
        
        # 验证activity_type为CHECK_IN或CHECK_OUT时建议关联hotel_id
        if self.activity_type in [self.ActivityType.CHECK_IN, self.ActivityType.CHECK_OUT] and not self.hotel_id:
            raise ValidationError('活动类型为入住或退房时必须关联酒店ID')
    
    class Meta:
        db_table = 'daily_schedules'
        verbose_name = '每日行程活动表'
        verbose_name_plural = '每日行程活动表'
        ordering = ['itinerary_id', 'day_number', 'start_time']
        indexes = [
            models.Index(fields=['itinerary_id']),
            models.Index(fields=['schedule_date']),
            models.Index(fields=['destination_id']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['attraction_id']),
            models.Index(fields=['hotel_id']),
            models.Index(fields=['restaurant_id']),
        ]
