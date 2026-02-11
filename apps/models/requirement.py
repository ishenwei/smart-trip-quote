from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .base import BaseModel, JSONField


class Requirement(BaseModel):
    class SourceType(models.TextChoices):
        NATURAL_LANGUAGE = 'NaturalLanguage', '自然语言输入'
        FORM_INPUT = 'FormInput', '表单输入'
    
    class Status(models.TextChoices):
        PENDING_REVIEW = 'PendingReview', '待审核'
        CONFIRMED = 'Confirmed', '已确认'
        EXPIRED = 'Expired', '已过期'
    
    class TransportationType(models.TextChoices):
        ROUND_TRIP_FLIGHT = 'RoundTripFlight', '双飞'
        ONE_WAY_FLIGHT = 'OneWayFlight', '单飞'
        HIGH_SPEED_TRAIN = 'HighSpeedTrain', '高铁'
        TRAIN = 'Train', '火车'
        SELF_DRIVING = 'SelfDriving', '自驾'
        OTHER = 'Other', '其他'
    
    class HotelLevel(models.TextChoices):
        ECONOMY = 'Economy', '经济型'
        COMFORT = 'Comfort', '舒适型'
        PREMIUM = 'Premium', '高档型'
        LUXURY = 'Luxury', '豪华型'
    
    class TripRhythm(models.TextChoices):
        RELAXED = 'Relaxed', '悠闲'
        MODERATE = 'Moderate', '适中'
        INTENSE = 'Intense', '紧凑'
    
    class BudgetLevel(models.TextChoices):
        ECONOMY = 'Economy', '经济'
        COMFORT = 'Comfort', '舒适'
        HIGH_END = 'HighEnd', '高端'
        LUXURY = 'Luxury', '奢华'
    
    requirement_id = models.CharField(max_length=20, primary_key=True, editable=False, verbose_name='需求ID')
    origin_input = models.TextField(blank=True, verbose_name='客户原始输入')
    requirement_json_data = JSONField(verbose_name='JSON结构数据', default=dict)
    
    origin_name = models.CharField(max_length=100, verbose_name='出发地名称')
    origin_code = models.CharField(max_length=10, blank=True, verbose_name='出发地代码')
    origin_type = models.CharField(max_length=20, blank=True, verbose_name='出发地类型')
    
    destination_cities = JSONField(verbose_name='目的地城市列表', default=list)
    
    trip_days = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='出行天数'
    )
    
    group_adults = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='成人数量'
    )
    group_children = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='儿童数量'
    )
    group_seniors = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='老人数量'
    )
    group_total = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='总人数'
    )
    
    travel_start_date = models.DateField(null=True, blank=True, verbose_name='出行开始日期')
    travel_end_date = models.DateField(null=True, blank=True, verbose_name='出行结束日期')
    travel_date_flexible = models.BooleanField(default=False, verbose_name='日期是否灵活')
    
    transportation_type = models.CharField(
        max_length=20,
        choices=TransportationType.choices,
        blank=True,
        verbose_name='大交通方式'
    )
    transportation_notes = models.TextField(blank=True, verbose_name='交通偏好说明')
    
    hotel_level = models.CharField(
        max_length=20,
        choices=HotelLevel.choices,
        blank=True,
        verbose_name='酒店等级'
    )
    hotel_requirements = models.TextField(blank=True, verbose_name='住宿特殊要求')
    
    trip_rhythm = models.CharField(
        max_length=20,
        choices=TripRhythm.choices,
        blank=True,
        verbose_name='行程节奏'
    )
    preference_tags = JSONField(verbose_name='偏好标签', default=list, blank=True)
    must_visit_spots = JSONField(verbose_name='必游景点', default=list, blank=True)
    avoid_activities = JSONField(verbose_name='避免活动', default=list, blank=True)
    
    budget_level = models.CharField(
        max_length=20,
        choices=BudgetLevel.choices,
        blank=True,
        verbose_name='预算等级'
    )
    budget_currency = models.CharField(max_length=10, default='CNY', verbose_name='预算货币')
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='最低预算'
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='最高预算'
    )
    budget_notes = models.TextField(blank=True, verbose_name='预算说明')
    
    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.NATURAL_LANGUAGE,
        verbose_name='需求来源'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_REVIEW,
        verbose_name='需求状态'
    )
    
    assumptions = JSONField(verbose_name='系统推断说明', default=list)
    
    created_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='创建人')
    reviewed_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='审核人')
    
    is_template = models.BooleanField(default=False, verbose_name='是否模板')
    template_name = models.CharField(max_length=200, blank=True, verbose_name='模板名称')
    template_category = models.CharField(max_length=100, blank=True, verbose_name='模板分类')
    
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    
    extension = JSONField(verbose_name='扩展字段', default=dict, blank=True)
    
    class Meta:
        db_table = 'requirements'
        verbose_name = '旅游需求管理'
        verbose_name_plural = '旅游需求管理'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requirement_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_template']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.requirement_id} - {self.origin_name} 至 {self.destination_cities}"
    
    def save(self, *args, **kwargs):
        # 新创建记录，生成requirement_id
        if not self.pk:
            if not self.requirement_id:
                from datetime import datetime
                import time
                
                # 确保原子性，使用时间戳和循环检测
                max_attempts = 100
                for attempt in range(max_attempts):
                    # 获取当前日期，格式化为YYYYMMDD
                    today = datetime.now().strftime('%Y%m%d')
                    
                    # 查询当日已存在的记录，找到最大的序号
                    prefix = f'REQ_{today}_'
                    existing_records = Requirement.objects.filter(requirement_id__startswith=prefix)
                    
                    # 提取最大序号
                    max_seq = 0
                    for record in existing_records:
                        try:
                            seq = int(record.requirement_id.split('_')[-1])
                            if seq > max_seq:
                                max_seq = seq
                        except (ValueError, IndexError):
                            pass
                    
                    # 生成下一个序号
                    next_seq = max_seq + 1
                    new_id = f'{prefix}{next_seq:03d}'
                    
                    # 检查是否存在冲突
                    if not Requirement.objects.filter(requirement_id=new_id).exists():
                        self.requirement_id = new_id
                        break
                    
                    # 避免无限循环，添加短暂延迟
                    time.sleep(0.01)
        
        super().save(*args, **kwargs)
    
    def clean(self):
        if self.travel_end_date and self.travel_start_date:
            if self.travel_end_date < self.travel_start_date:
                raise ValidationError({'travel_end_date': '结束日期不能早于开始日期'})
        
        if self.trip_days and self.travel_start_date and self.travel_end_date:
            calculated_days = (self.travel_end_date - self.travel_start_date).days + 1
            if calculated_days != self.trip_days:
                raise ValidationError({'trip_days': f'出行天数({self.trip_days})与日期范围({calculated_days}天)不一致'})
        
        total_people = self.group_adults + self.group_children + self.group_seniors
        if total_people != self.group_total:
            raise ValidationError({'group_total': f'总人数({self.group_total})与各类型人数之和({total_people})不一致'})
        
        if self.budget_min and self.budget_max:
            if self.budget_min > self.budget_max:
                raise ValidationError({'budget_min': '最低预算不能高于最高预算'})
    
    def to_json(self):
        return {
            'requirement_id': self.requirement_id,
            'base_info': {
                'origin': {
                    'name': self.origin_name,
                    'code': self.origin_code,
                    'type': self.origin_type
                },
                'destination_cities': self.destination_cities,
                'trip_days': self.trip_days,
                'group_size': {
                    'adults': self.group_adults,
                    'children': self.group_children,
                    'seniors': self.group_seniors,
                    'total': self.group_total
                },
                'travel_date': {
                    'start_date': self.travel_start_date.strftime('%Y-%m-%d') if self.travel_start_date else None,
                    'end_date': self.travel_end_date.strftime('%Y-%m-%d') if self.travel_end_date else None,
                    'is_flexible': self.travel_date_flexible
                }
            },
            'preferences': {
                'transportation': {
                    'type': self.transportation_type,
                    'notes': self.transportation_notes
                },
                'accommodation': {
                    'level': self.hotel_level,
                    'requirements': self.hotel_requirements
                },
                'itinerary': {
                    'rhythm': self.trip_rhythm,
                    'tags': self.preference_tags,
                    'special_constraints': {
                        'must_visit_spots': self.must_visit_spots,
                        'avoid_activities': self.avoid_activities
                    }
                }
            },
            'budget': {
                'level': self.budget_level,
                'currency': self.budget_currency,
                'range': {
                    'min': float(self.budget_min) if self.budget_min else None,
                    'max': float(self.budget_max) if self.budget_max else None
                },
                'budget_notes': self.budget_notes
            },
            'metadata': {
                'source_type': self.source_type,
                'status': self.status,
                'assumptions': self.assumptions,
                'is_template': self.is_template,
                'template_info': {
                    'name': self.template_name,
                    'category': self.template_category
                },
                'audit_trail': {
                    'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.created_at else None,
                    'updated_at': self.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ') if self.updated_at else None,
                    'created_by': self.created_by,
                    'reviewed_by': self.reviewed_by
                }
            },
            'extension': self.extension
        }
    
    def confirm(self, reviewer=None):
        self.status = self.Status.CONFIRMED
        if reviewer:
            self.reviewed_by = reviewer
        self.save()
    
    def expire(self):
        self.status = self.Status.EXPIRED
        self.save()
    
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    @classmethod
    def get_available_templates(cls):
        return cls.objects.filter(is_template=True)
