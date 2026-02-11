from rest_framework import serializers
from .models import Requirement


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        from .validators import RequirementValidator
        RequirementValidator.validate_all(data)
        return data


class RequirementDetailSerializer(serializers.ModelSerializer):
    base_info = serializers.SerializerMethodField()
    preferences = serializers.SerializerMethodField()
    budget = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = Requirement
        fields = [
            'requirement_id',
            'base_info',
            'preferences',
            'budget',
            'metadata',
            'extension'
        ]
    
    def get_base_info(self, obj):
        return {
            'origin': {
                'name': obj.origin_name,
                'code': obj.origin_code,
                'type': obj.origin_type
            },
            'destination_cities': obj.destination_cities,
            'trip_days': obj.trip_days,
            'group_size': {
                'adults': obj.group_adults,
                'children': obj.group_children,
                'seniors': obj.group_seniors,
                'total': obj.group_total
            },
            'travel_date': {
                'start_date': obj.travel_start_date.strftime('%Y-%m-%d') if obj.travel_start_date else None,
                'end_date': obj.travel_end_date.strftime('%Y-%m-%d') if obj.travel_end_date else None,
                'is_flexible': obj.travel_date_flexible
            }
        }
    
    def get_preferences(self, obj):
        return {
            'transportation': {
                'type': obj.transportation_type,
                'notes': obj.transportation_notes
            },
            'accommodation': {
                'level': obj.hotel_level,
                'requirements': obj.hotel_requirements
            },
            'itinerary': {
                'rhythm': obj.trip_rhythm,
                'tags': obj.preference_tags,
                'special_constraints': {
                    'must_visit_spots': obj.must_visit_spots,
                    'avoid_activities': obj.avoid_activities
                }
            }
        }
    
    def get_budget(self, obj):
        return {
            'level': obj.budget_level,
            'currency': obj.budget_currency,
            'range': {
                'min': float(obj.budget_min) if obj.budget_min else None,
                'max': float(obj.budget_max) if obj.budget_max else None
            },
            'budget_notes': obj.budget_notes
        }
    
    def get_metadata(self, obj):
        return {
            'source_type': obj.source_type,
            'status': obj.status,
            'assumptions': obj.assumptions,
            'is_template': obj.is_template,
            'template_info': {
                'name': obj.template_name,
                'category': obj.template_category
            },
            'audit_trail': {
                'created_at': obj.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') if obj.created_at else None,
                'updated_at': obj.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ') if obj.updated_at else None,
                'created_by': obj.created_by,
                'reviewed_by': obj.reviewed_by
            }
        }


class RequirementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'requirement_id',
            'origin_name',
            'origin_code',
            'origin_type',
            'destination_cities',
            'trip_days',
            'group_adults',
            'group_children',
            'group_seniors',
            'group_total',
            'travel_start_date',
            'travel_end_date',
            'travel_date_flexible',
            'transportation_type',
            'transportation_notes',
            'hotel_level',
            'hotel_requirements',
            'trip_rhythm',
            'preference_tags',
            'must_visit_spots',
            'avoid_activities',
            'budget_level',
            'budget_currency',
            'budget_min',
            'budget_max',
            'budget_notes',
            'source_type',
            'created_by',
            'assumptions',
            'extension'
        ]
        extra_kwargs = {
            'preference_tags': {'required': False, 'allow_blank': True},
            'must_visit_spots': {'required': False, 'allow_blank': True},
            'avoid_activities': {'required': False, 'allow_blank': True},
            'extension': {'required': False, 'allow_blank': True},
        }
    
    def validate(self, data):
        from .validators import RequirementValidator
        RequirementValidator.validate_all(data)
        return data


class RequirementUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'origin_name',
            'origin_code',
            'origin_type',
            'destination_cities',
            'trip_days',
            'group_adults',
            'group_children',
            'group_seniors',
            'group_total',
            'travel_start_date',
            'travel_end_date',
            'travel_date_flexible',
            'transportation_type',
            'transportation_notes',
            'hotel_level',
            'hotel_requirements',
            'trip_rhythm',
            'preference_tags',
            'must_visit_spots',
            'avoid_activities',
            'budget_level',
            'budget_currency',
            'budget_min',
            'budget_max',
            'budget_notes',
            'assumptions',
            'extension'
        ]
        extra_kwargs = {
            'preference_tags': {'required': False, 'allow_blank': True},
            'must_visit_spots': {'required': False, 'allow_blank': True},
            'avoid_activities': {'required': False, 'allow_blank': True},
            'extension': {'required': False, 'allow_blank': True},
        }
    
    def validate(self, data):
        from .validators import RequirementValidator
        RequirementValidator.validate_all(data)
        return data


class RequirementListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'requirement_id',
            'origin_name',
            'destination_cities',
            'trip_days',
            'group_total',
            'travel_start_date',
            'travel_end_date',
            'status',
            'is_template',
            'created_at',
            'updated_at'
        ]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = [
            'requirement_id',
            'template_name',
            'template_category',
            'origin_name',
            'destination_cities',
            'trip_days',
            'transportation_type',
            'hotel_level',
            'trip_rhythm',
            'budget_level',
            'preference_tags',
            'created_at',
            'updated_at'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['template_info'] = {
            'name': instance.template_name,
            'category': instance.template_category
        }
        return data


class TemplateCreateSerializer(serializers.ModelSerializer):
    source_requirement_id = serializers.CharField(write_only=True)
    
    class Meta:
        model = Requirement
        fields = [
            'source_requirement_id',
            'template_name',
            'template_category',
            'created_by'
        ]
    
    def validate(self, data):
        if not data.get('template_name'):
            raise serializers.ValidationError({'template_name': '模板名称不能为空'})
        if len(data.get('template_name', '')) > 200:
            raise serializers.ValidationError({'template_name': '模板名称长度不能超过200个字符'})
        return data
    
    def create(self, validated_data):
        from .template_manager import TemplateManager
        
        source_requirement_id = validated_data.pop('source_requirement_id')
        template_name = validated_data.pop('template_name')
        template_category = validated_data.pop('template_category', '')
        created_by = validated_data.pop('created_by', None)
        
        template = TemplateManager.create_template(
            source_requirement_id,
            template_name,
            template_category,
            created_by
        )
        
        return template


class RequirementStatusSerializer(serializers.Serializer):
    requirement_id = serializers.CharField()
    status = serializers.CharField()
    reviewer = serializers.CharField(required=False)
    
    def validate_status(self, value):
        valid_statuses = ['PendingReview', 'Confirmed', 'Expired']
        if value not in valid_statuses:
            raise serializers.ValidationError(f'状态必须是以下之一: {", ".join(valid_statuses)}')
        return value
    
    def validate(self, data):
        from .status_manager import RequirementStatusManager
        
        try:
            requirement = Requirement.objects.get(requirement_id=data['requirement_id'])
        except Requirement.DoesNotExist:
            raise serializers.ValidationError({'requirement_id': '需求不存在'})
        
        if not RequirementStatusManager.validate_status_transition(
            requirement.status,
            data['status']
        ):
            raise serializers.ValidationError({
                'status': f'无法从 {requirement.status} 转换到 {data["status"]}'
            })
        
        return data
