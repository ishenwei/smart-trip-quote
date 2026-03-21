"""
Webhook 数据序列化器和验证器
用于验证和处理来自 n8n webhook 的数据
"""
from rest_framework import serializers
from datetime import date, datetime, time
from typing import List, Dict, Any, Optional


class FlexibleDateField(serializers.DateField):
    """支持多种格式的日期字段"""
    def to_internal_value(self, data):
        if data is None or data == '':
            return None
        if isinstance(data, date):
            return data
        # 尝试多种格式
        formats = ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']
        for fmt in formats:
            try:
                return datetime.strptime(str(data), fmt).date()
            except:
                pass
        # 尝试 ISO 格式变体
        try:
            return serializers.DateField().to_internal_value(data)
        except:
            pass
        raise serializers.ValidationError(f'无效的日期格式: {data}')


class FlexibleDateTimeField(serializers.DateTimeField):
    """支持多种格式的日期时间字段"""
    def to_internal_value(self, data):
        if data is None or data == '':
            return None
        if isinstance(data, datetime):
            return data
        formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']
        for fmt in formats:
            try:
                return datetime.strptime(str(data), fmt)
            except:
                pass
        try:
            return serializers.DateTimeField().to_internal_value(data)
        except:
            pass
        raise serializers.ValidationError(f'无效的日期时间格式: {data}')


class ActivitySerializer(serializers.Serializer):
    """活动数据序列化器"""
    activity_title = serializers.CharField(max_length=200)
    activity_type = serializers.CharField(max_length=50)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    activity_description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    id_reference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate_activity_type(self, value):
        """验证活动类型"""
        valid_types = [
            'FLIGHT', 'TRAIN', 'ATTRACTION', 'MEAL', 
            'TRANSPORT', 'SHOPPING', 'FREE', 
            'CHECK_IN', 'CHECK_OUT', 'OTHER'
        ]
        if value not in valid_types:
            raise serializers.ValidationError(
                f'无效的活动类型: {value}。必须是以下之一: {", ".join(valid_types)}'
            )
        return value
    
    def validate(self, data):
        """验证时间顺序"""
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError({
                    'end_time': '结束时间必须晚于开始时间'
                })
        return data


class DestinationSerializer(serializers.Serializer):
    """目的地数据序列化器"""
    destination_order = serializers.IntegerField(min_value=1)
    city_name = serializers.CharField(max_length=100)
    country_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    arrival_date = serializers.DateField()
    departure_date = serializers.DateField()
    
    def validate(self, data):
        """验证日期逻辑"""
        if data.get('arrival_date') and data.get('departure_date'):
            if data['arrival_date'] > data['departure_date']:
                raise serializers.ValidationError({
                    'departure_date': '离开日期必须晚于或等于到达日期'
                })
        return data
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for field in ['arrival_date', 'departure_date']:
            if field in ret and ret[field]:
                if hasattr(ret[field], 'isoformat'):
                    ret[field] = ret[field].isoformat()
        return ret


class TravelerStatsSerializer(serializers.Serializer):
    """旅行者统计数据序列化器"""
    adults = serializers.IntegerField(min_value=0, default=0)
    children = serializers.IntegerField(min_value=0, default=0)
    infants = serializers.IntegerField(min_value=0, default=0)
    seniors = serializers.IntegerField(min_value=0, default=0)
    
    def validate(self, data):
        """验证旅行者数量"""
        total = sum(data.values())
        if total <= 0:
            raise serializers.ValidationError('至少需要一名旅行者')
        return data


class DailyScheduleSerializer(serializers.Serializer):
    """每日行程数据序列化器"""
    day = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    city = serializers.CharField(max_length=100)
    activities = ActivitySerializer(many=True, required=False, default=list)
    
    def validate(self, data):
        """验证日期和天数"""
        if data.get('day') and data.get('date'):
            # 基本的日期验证
            if not isinstance(data['date'], date):
                raise serializers.ValidationError({'date': '日期格式无效'})
        return data
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'date' in ret and ret['date']:
            if hasattr(ret['date'], 'isoformat'):
                ret['date'] = ret['date'].isoformat()
        return ret


class ItineraryWebhookSerializer(serializers.Serializer):
    """
    行程 Webhook 数据验证器
    验证 n8n 返回的行程数据
    """
    requirement_id = serializers.CharField(max_length=50)
    itinerary_name = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    destinations = DestinationSerializer(many=True, required=False, default=list)
    traveler_stats = TravelerStatsSerializer(required=False, default=dict)
    daily_schedules = DailyScheduleSerializer(many=True, required=False, default=list)
    
    def validate_requirement_id(self, value):
        """验证 requirement_id 格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('requirement_id 不能为空')
        return value.strip()
    
    def validate(self, data):
        """整体验证"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # 验证日期范围
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({
                    'end_date': '结束日期必须晚于或等于开始日期'
                })
        
        return data


class OriginSerializer(serializers.Serializer):
    """出发地信息序列化器"""
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    type = serializers.CharField(max_length=50, required=False, allow_blank=True)


class GroupSizeSerializer(serializers.Serializer):
    """团队规模序列化器"""
    adults = serializers.IntegerField(min_value=0, default=0)
    children = serializers.IntegerField(min_value=0, default=0)
    seniors = serializers.IntegerField(min_value=0, default=0)
    total = serializers.IntegerField(min_value=1, default=1)


class TravelDateSerializer(serializers.Serializer):
    """旅行日期序列化器"""
    start_date = FlexibleDateField(required=False, allow_null=True)
    end_date = FlexibleDateField(required=False, allow_null=True)
    is_flexible = serializers.BooleanField(default=False)
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for field in ['start_date', 'end_date']:
            if field in ret and ret[field]:
                if hasattr(ret[field], 'isoformat'):
                    ret[field] = ret[field].isoformat()
        return ret


class TransportationSerializer(serializers.Serializer):
    """交通偏好序列化器"""
    type = serializers.CharField(max_length=50, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AccommodationSerializer(serializers.Serializer):
    """住宿偏好序列化器"""
    level = serializers.CharField(max_length=50, required=False, allow_blank=True)
    requirements = serializers.CharField(max_length=500, required=False, allow_blank=True)


class SpecialConstraintsSerializer(serializers.Serializer):
    """特殊约束序列化器"""
    must_visit_spots = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        default=list
    )
    avoid_activities = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        default=list
    )


class ItineraryPreferencesSerializer(serializers.Serializer):
    """行程偏好序列化器"""
    rhythm = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
    special_constraints = SpecialConstraintsSerializer(required=False, default=dict)


class BudgetRangeSerializer(serializers.Serializer):
    """预算范围序列化器"""
    min = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    max = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)


class BudgetSerializer(serializers.Serializer):
    """预算信息序列化器"""
    level = serializers.CharField(max_length=50, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=10, default='CNY')
    range = BudgetRangeSerializer(required=False)
    budget_notes = serializers.CharField(max_length=500, required=False, allow_blank=True)


class BaseInfoSerializer(serializers.Serializer):
    """基础信息序列化器"""
    origin = OriginSerializer(required=False)
    destination_cities = serializers.JSONField(required=False, default=list)
    trip_days = serializers.IntegerField(min_value=1, default=1)
    group_size = GroupSizeSerializer(required=False)
    travel_date = TravelDateSerializer(required=False)
    
    def validate_destination_cities(self, value):
        """验证目的地城市"""
        if isinstance(value, str):
            return [{'name': value}] if value.strip() else []
        if not isinstance(value, list):
            return []
        return value


class PreferencesSerializer(serializers.Serializer):
    """偏好设置序列化器"""
    transportation = TransportationSerializer(required=False)
    accommodation = AccommodationSerializer(required=False)
    itinerary = ItineraryPreferencesSerializer(required=False)


class TemplateInfoSerializer(serializers.Serializer):
    """模板信息序列化器"""
    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)


class AuditTrailSerializer(serializers.Serializer):
    """审计追踪序列化器"""
    created_at = FlexibleDateTimeField(required=False, allow_null=True)
    updated_at = FlexibleDateTimeField(required=False, allow_null=True)


class MetadataSerializer(serializers.Serializer):
    """元数据序列化器"""
    source_type = serializers.CharField(max_length=50, default='NaturalLanguage')
    status = serializers.CharField(max_length=50, default='Confirmed')
    assumptions = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=list
    )
    is_template = serializers.BooleanField(default=False)
    template_info = TemplateInfoSerializer(required=False)
    audit_trail = AuditTrailSerializer(required=False)


class StructuredDataSerializer(serializers.Serializer):
    """结构化数据验证器"""
    base_info = BaseInfoSerializer(required=False)
    preferences = PreferencesSerializer(required=False)
    budget = BudgetSerializer(required=False)
    metadata = MetadataSerializer(required=False)
    extension = serializers.JSONField(required=False, default=dict)


class RequirementWebhookSerializer(serializers.Serializer):
    """
    需求 Webhook 数据验证器
    验证 n8n 返回的需求解析数据
    """
    user_input = serializers.CharField(max_length=10000, required=False, allow_blank=True)
    structured_data = StructuredDataSerializer(required=False)
    requirement_id = serializers.CharField(max_length=50, required=False)
    llm_info = serializers.JSONField(required=False, allow_null=True)
    
    def validate(self, data):
        """整体验证"""
        structured_data = data.get('structured_data', {})
        
        # 至少需要 structured_data 或 user_input 其中之一
        if not structured_data and not data.get('user_input'):
            raise serializers.ValidationError(
                '至少需要提供 structured_data 或 user_input 之一'
            )
        
        return data
    
    def to_internal_value(self, data):
        """自定义反序列化，处理各种数据格式"""
        # 处理列表结构
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        # 处理 output 字段
        if 'output' in data:
            data = data['output']
        
        return super().to_internal_value(data)


class ItineraryOptimizationCallbackSerializer(serializers.Serializer):
    """
    行程优化回调数据验证器
    验证 n8n 返回的行程优化结果
    """
    itinerary_id = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate_itinerary_id(self, value):
        """验证 itinerary_id 格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('itinerary_id 不能为空')
        return value.strip()
    
    def validate(self, data):
        """验证描述长度"""
        description = data.get('description', '')
        if description and len(description) > 50000:
            raise serializers.ValidationError({
                'description': '描述内容过长，最大支持50000字符'
            })
        return data
    
    def to_internal_value(self, data):
        """自定义反序列化，处理各种数据格式"""
        # 处理 output 字段
        if isinstance(data, dict) and 'output' in data:
            data = data['output']
        
        return super().to_internal_value(data)


class ItineraryQuoteCallbackSerializer(serializers.Serializer):
    """
    行程报价回调数据验证器
    验证 n8n 返回的行程报价结果
    """
    itinerary_id = serializers.CharField(max_length=50)
    itinerary_quote = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate_itinerary_id(self, value):
        """验证 itinerary_id 格式"""
        if not value or not value.strip():
            raise serializers.ValidationError('itinerary_id 不能为空')
        return value.strip()


class N8nProcessRequirementSerializer(serializers.Serializer):
    """
    通过 N8N 处理需求的请求验证器
    """
    user_input = serializers.CharField(max_length=10000)
    client_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    provider = serializers.CharField(max_length=50, required=False, allow_blank=True)
    save_to_db = serializers.BooleanField(default=True)
    
    def validate_user_input(self, value):
        """验证用户输入"""
        if not value or not value.strip():
            raise serializers.ValidationError('user_input 不能为空')
        return value.strip()
