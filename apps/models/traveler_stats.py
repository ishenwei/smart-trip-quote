from django.db import models
from django.core.validators import MinValueValidator
from .base import BaseModel
from .itinerary import Itinerary
import uuid


class TravelerStats(BaseModel):
    stat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='统计ID', db_comment='统计记录唯一标识符,使用UUID格式')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='traveler_stats', verbose_name='行程', db_comment='关联的行程,外键关联itinerary表')
    adult_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='成人数', db_comment='成人数量,一般指18-60岁')
    child_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='儿童数', db_comment='儿童数量,一般指3-12岁')
    infant_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='婴儿数', db_comment='婴儿数量,一般指0-2岁')
    senior_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='老人数', db_comment='老人数量,一般指60岁以上')
    notes = models.TextField(null=True, blank=True, verbose_name='备注', db_comment='备注信息')

    class Meta:
        db_table = 'traveler_stats'
        verbose_name = '出行人员统计表'
        verbose_name_plural = '出行人员统计表'
        db_table_comment = '出行人员统计表,存储行程中出行人员的分类统计信息,包括成人、儿童、婴儿、老人等人数统计'
