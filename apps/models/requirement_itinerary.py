from django.db import models
from .base import BaseModel
from .requirement import Requirement
from .itinerary import Itinerary


class RequirementItinerary(BaseModel):
    """需求与行程关联关系表"""
    id = models.AutoField(primary_key=True, verbose_name='自增主键', db_comment='自增主键ID')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, to_field='requirement_id', verbose_name='需求', db_comment='关联至requirements表的主键')
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, to_field='itinerary_id', verbose_name='行程', db_comment='关联至itineraries表的主键')
    
    class Meta:
        db_table = 'requirement_itinerary'
        verbose_name = '需求与行程关联关系'
        verbose_name_plural = '需求与行程关联关系'
        db_table_comment = '存储requirement与itinerary之间的一对多关联关系'
        unique_together = ('requirement', 'itinerary')
