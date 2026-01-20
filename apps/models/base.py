from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        abstract = True


class JSONField(models.TextField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def to_python(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value
    
    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value, ensure_ascii=False)
