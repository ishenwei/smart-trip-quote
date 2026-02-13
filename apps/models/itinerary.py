from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from .base import BaseModel


class Itinerary(BaseModel):
    class TravelPurpose(models.TextChoices):
        LEISURE = 'LEISURE', '休闲'
        BUSINESS = 'BUSINESS', '商务'
        HONEYMOON = 'HONEYMOON', '蜜月'
        FAMILY = 'FAMILY', '家庭'
        ADVENTURE = 'ADVENTURE', '冒险'
        CULTURAL = 'CULTURAL', '文化'
        OTHER = 'OTHER', '其他'

    class BudgetFlexibility(models.TextChoices):
        STRICT = 'STRICT', '严格'
        MODERATE = 'MODERATE', '适中'
        FLEXIBLE = 'FLEXIBLE', '灵活'

    class CurrentStatus(models.TextChoices):
        DRAFT = 'DRAFT', '草稿'
        PENDING_REVIEW = 'PENDING_REVIEW', '待审核'
        CONFIRMED = 'CONFIRMED', '已确认'
        EXPIRED = 'EXPIRED', '已过期'
        CANCELLED = 'CANCELLED', '已取消'
        COMPLETED = 'COMPLETED', '已完成'

    class TemplateCategory(models.TextChoices):
        HONEYMOON = 'HONEYMOON', '蜜月'
        FAMILY = 'FAMILY', '家庭'
        ADVENTURE = 'ADVENTURE', '冒险'
        CITY_TOUR = 'CITY_TOUR', '城市游览'
        BEACH = 'BEACH', '海滩'
        CULTURAL = 'CULTURAL', '文化'
        CUSTOM = 'CUSTOM', '自定义'

    itinerary_id = models.CharField(max_length=20, primary_key=True, editable=False, verbose_name='行程唯一标识')
    itinerary_name = models.CharField(max_length=100, verbose_name='行程名称')
    description = models.TextField(null=True, blank=True, verbose_name='行程描述')
    travel_purpose = models.CharField(max_length=20, choices=TravelPurpose.choices, verbose_name='旅行目的')
    start_date = models.DateField(verbose_name='行程开始日期')
    end_date = models.DateField(verbose_name='行程结束日期')
    total_days = models.IntegerField(verbose_name='总天数')
    contact_person = models.CharField(max_length=100, verbose_name='联系人')
    contact_phone = models.CharField(max_length=20, verbose_name='联系电话')
    contact_company = models.CharField(max_length=100, null=True, blank=True, verbose_name='联系人单位')
    departure_city = models.CharField(max_length=100, verbose_name='出发城市')
    return_city = models.CharField(max_length=100, verbose_name='返回城市')
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name='总预算')
    budget_flexibility = models.CharField(max_length=10, choices=BudgetFlexibility.choices, null=True, blank=True, verbose_name='预算灵活性')
    current_status = models.CharField(max_length=20, choices=CurrentStatus.choices, verbose_name='当前状态')
    review_deadline = models.DateTimeField(null=True, blank=True, verbose_name='审核截止时间')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='行程有效期截止日期')
    confirmed_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='确认人（运营人员）')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='确认时间')
    is_template = models.BooleanField(default=False, verbose_name='是否为模板')
    template_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='模板名称')
    template_category = models.CharField(max_length=20, choices=TemplateCategory.choices, null=True, blank=True, verbose_name='模板分类')
    usage_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='模板使用次数')
    last_used = models.DateTimeField(null=True, blank=True, verbose_name='模板最后使用时间')
    created_by = models.CharField(max_length=50, verbose_name='创建人')
    updated_by = models.CharField(max_length=50, null=True, blank=True, verbose_name='更新人')
    version = models.IntegerField(default=1, verbose_name='版本号')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')
    itinerary_json_data = models.JSONField(null=True, blank=True, verbose_name='行程结构化JSON数据')

    def save(self, *args, **kwargs):
        # 计算总天数
        if self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days + 1
        
        # 版本号递增
        if self.pk:
            self.version += 1
        else:
            # 新创建记录，生成itinerary_id
            if not self.itinerary_id:
                from datetime import datetime
                import time
                
                # 确保原子性，使用时间戳和循环检测
                max_attempts = 100
                for attempt in range(max_attempts):
                    # 获取当前日期，格式化为YYYYMMDD
                    today = datetime.now().strftime('%Y%m%d')
                    
                    # 查询当日已存在的记录，找到最大的序号
                    prefix = f'ITI_{today}_'
                    existing_records = Itinerary.objects.filter(itinerary_id__startswith=prefix)
                    
                    # 提取最大序号
                    max_seq = 0
                    for record in existing_records:
                        try:
                            seq = int(record.itinerary_id.split('_')[-1])
                            if seq > max_seq:
                                max_seq = seq
                        except (ValueError, IndexError):
                            pass
                    
                    # 生成下一个序号
                    next_seq = max_seq + 1
                    new_id = f'{prefix}{next_seq:03d}'
                    
                    # 检查是否存在冲突
                    if not Itinerary.objects.filter(itinerary_id=new_id).exists():
                        self.itinerary_id = new_id
                        break
                    
                    # 避免无限循环，添加短暂延迟
                    time.sleep(0.01)
            
            # 确保新创建的记录状态为草稿状态
            if not self.current_status:
                self.current_status = self.CurrentStatus.DRAFT
        
        # 保存前更新JSON数据
        self.update_itinerary_json_data()
        
        super().save(*args, **kwargs)
    
    def update_itinerary_json_data(self):
        """更新行程的结构化JSON数据"""
        # 构建基础行程数据
        itinerary_data = {
            'itinerary_id': self.itinerary_id,
            'itinerary_name': self.itinerary_name,
            'description': self.description,
            'travel_purpose': self.travel_purpose,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_days': self.total_days,
            'contact_person': self.contact_person,
            'contact_phone': self.contact_phone,
            'contact_company': self.contact_company,
            'departure_city': self.departure_city,
            'return_city': self.return_city,
            'total_budget': str(self.total_budget) if self.total_budget else None,
            'budget_flexibility': self.budget_flexibility,
            'current_status': self.current_status,
            'review_deadline': self.review_deadline.isoformat() if self.review_deadline else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'confirmed_by': self.confirmed_by,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'is_template': self.is_template,
            'template_name': self.template_name,
            'template_category': self.template_category,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'version': self.version,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 添加目的地数据
        destinations = []
        try:
            for dest in self.destinations.all():
                destination_data = {
                    'destination_id': str(dest.destination_id),
                    'destination_order': dest.destination_order,
                    'city_name': dest.city_name,
                    'country_code': dest.country_code,
                    'region': dest.region,
                    'latitude': str(dest.latitude) if dest.latitude else None,
                    'longitude': str(dest.longitude) if dest.longitude else None,
                    'arrival_date': dest.arrival_date.isoformat() if dest.arrival_date else None,
                    'departure_date': dest.departure_date.isoformat() if dest.departure_date else None,
                    'nights': dest.nights
                }
                destinations.append(destination_data)
        except Exception:
            pass
        
        itinerary_data['destinations'] = destinations
        
        # 添加每日行程数据
        daily_schedules = []
        try:
            from .daily_schedule import DailySchedule
            schedules = DailySchedule.objects.filter(itinerary_id=self.itinerary_id).order_by('day_number', 'start_time')
            for schedule in schedules:
                schedule_data = {
                    'schedule_id': str(schedule.schedule_id),
                    'day_number': schedule.day_number,
                    'schedule_date': schedule.schedule_date.isoformat() if schedule.schedule_date else None,
                    'destination_id': str(schedule.destination_id) if schedule.destination_id else None,
                    'activity_type': schedule.activity_type,
                    'activity_title': schedule.activity_title,
                    'activity_description': schedule.activity_description,
                    'start_time': schedule.start_time.isoformat() if schedule.start_time else None,
                    'end_time': schedule.end_time.isoformat() if schedule.end_time else None,
                    'attraction_id': str(schedule.attraction_id) if schedule.attraction_id else None,
                    'hotel_id': str(schedule.hotel_id) if schedule.hotel_id else None,
                    'restaurant_id': str(schedule.restaurant_id) if schedule.restaurant_id else None,
                    'estimated_cost': str(schedule.estimated_cost) if schedule.estimated_cost else None,
                    'currency': schedule.currency,
                    'booking_status': schedule.booking_status,
                    'booking_reference': schedule.booking_reference,
                    'notes': schedule.notes
                }
                daily_schedules.append(schedule_data)
        except Exception:
            pass
        
        itinerary_data['daily_schedules'] = daily_schedules
        
        # 添加旅行者统计数据
        traveler_stats = []
        try:
            for stat in self.traveler_stats.all():
                stat_data = {
                    'stat_id': str(stat.stat_id),
                    'adult_count': stat.adult_count,
                    'child_count': stat.child_count,
                    'infant_count': stat.infant_count,
                    'senior_count': stat.senior_count,
                    'notes': stat.notes
                }
                traveler_stats.append(stat_data)
        except Exception:
            pass
        
        itinerary_data['traveler_stats'] = traveler_stats
        
        # 更新JSON数据字段
        self.itinerary_json_data = itinerary_data

    class Meta:
        db_table = 'itinerary'
        verbose_name = '旅游行程规划'
        verbose_name_plural = '旅游行程规划'
