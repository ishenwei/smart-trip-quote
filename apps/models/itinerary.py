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
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'itinerary'
        verbose_name = '旅游行程规划'
        verbose_name_plural = '旅游行程规划'
