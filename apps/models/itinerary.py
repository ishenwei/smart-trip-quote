from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from .base import BaseModel
import uuid


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

    itinerary_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='行程唯一标识')
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
        
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'itinerary'
        verbose_name = '旅游行程规划'
        verbose_name_plural = '旅游行程规划'
