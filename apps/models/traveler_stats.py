from django.db import models
from django.core.validators import MinValueValidator
from .base import BaseModel
from .itinerary import Itinerary
import uuid


class TravelerStats(BaseModel):
    stat_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='统计ID')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='traveler_stats', verbose_name='行程')
    adult_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='成人数')
    child_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='儿童数')
    infant_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='婴儿数')
    senior_count = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='老人数')
    notes = models.TextField(null=True, blank=True, verbose_name='备注')

    class Meta:
        db_table = 'traveler_stats'
        verbose_name = '出行人员统计表'
        verbose_name_plural = '出行人员统计表'
