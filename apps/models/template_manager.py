from django.db import transaction
from django.core.exceptions import ValidationError


class TemplateManager:
    
    @staticmethod
    def create_template(
        source_requirement_id,
        template_name,
        template_category,
        created_by=None,
        clear_sensitive_data=True
    ):
        from .requirement import Requirement
        try:
            source = Requirement.objects.get(requirement_id=source_requirement_id)
        except Requirement.DoesNotExist:
            raise ValueError(f'源需求不存在: {source_requirement_id}')
        
        if not template_name:
            raise ValidationError({'template_name': '模板名称不能为空'})
        if len(template_name) > 200:
            raise ValidationError({'template_name': '模板名称长度不能超过200个字符'})
        
        template_data = TemplateManager._prepare_template_data(
            source,
            template_name,
            template_category,
            created_by,
            clear_sensitive_data
        )
        
        with transaction.atomic():
            template = Requirement.objects.create(**template_data)
        
        return template
    
    @staticmethod
    def _prepare_template_data(source, template_name, template_category, created_by, clear_sensitive_data):
        from .requirement import Requirement
        # 模板的requirement_id由Requirement模型的save方法自动生成
        # 不再使用TPL-前缀，让它和普通需求一样使用REQ_YYYYMMDD_XXX格式
        template_data = {
            'origin_name': source.origin_name,
            'origin_code': source.origin_code,
            'origin_type': source.origin_type,
            'destination_cities': source.destination_cities,
            'trip_days': source.trip_days,
            'group_adults': 0,
            'group_children': 0,
            'group_seniors': 0,
            'group_total': 0,
            'travel_start_date': None,
            'travel_end_date': None,
            'travel_date_flexible': True,
            'transportation_type': source.transportation_type,
            'transportation_notes': source.transportation_notes,
            'hotel_level': source.hotel_level,
            'hotel_requirements': source.hotel_requirements,
            'trip_rhythm': source.trip_rhythm,
            'preference_tags': source.preference_tags,
            'must_visit_spots': source.must_visit_spots,
            'avoid_activities': source.avoid_activities,
            'budget_level': source.budget_level,
            'budget_currency': source.budget_currency,
            'budget_min': None,
            'budget_max': None,
            'budget_notes': '',
            'source_type': Requirement.SourceType.FORM_INPUT,
            'status': Requirement.Status.CONFIRMED,
            'assumptions': source.assumptions,
            'created_by': created_by or source.created_by,
            'reviewed_by': created_by or source.created_by,
            'is_template': True,
            'template_name': template_name,
            'template_category': template_category,
            'expires_at': None,
            'extension': source.extension
        }
        
        return template_data
    
    @staticmethod
    def update_template(
        template_id,
        template_name=None,
        template_category=None,
        update_data=None
    ):
        from .requirement import Requirement
        try:
            template = Requirement.objects.get(requirement_id=template_id)
        except Requirement.DoesNotExist:
            raise ValueError(f'模板不存在: {template_id}')
        
        if not template.is_template:
            raise ValueError(f'该需求不是模板: {template_id}')
        
        if template_name is not None:
            if not template_name:
                raise ValidationError({'template_name': '模板名称不能为空'})
            if len(template_name) > 200:
                raise ValidationError({'template_name': '模板名称长度不能超过200个字符'})
            template.template_name = template_name
        
        if template_category is not None:
            if len(template_category) > 100:
                raise ValidationError({'template_category': '模板分类长度不能超过100个字符'})
            template.template_category = template_category
        
        if update_data:
            updatable_fields = [
                'destination_cities', 'trip_days', 'transportation_type',
                'transportation_notes', 'hotel_level', 'hotel_requirements',
                'trip_rhythm', 'preference_tags', 'must_visit_spots',
                'avoid_activities', 'budget_level', 'budget_currency',
                'assumptions', 'extension'
            ]
            
            for field, value in update_data.items():
                if field in updatable_fields:
                    setattr(template, field, value)
        
        template.save()
        return template
    
    @staticmethod
    def delete_template(template_id):
        from .requirement import Requirement
        try:
            template = Requirement.objects.get(requirement_id=template_id)
        except Requirement.DoesNotExist:
            raise ValueError(f'模板不存在: {template_id}')
        
        if not template.is_template:
            raise ValueError(f'该需求不是模板: {template_id}')
        
        template.delete()
        return True
    
    @staticmethod
    def get_template(template_id):
        from .requirement import Requirement
        try:
            template = Requirement.objects.get(requirement_id=template_id)
            if not template.is_template:
                raise ValueError(f'该需求不是模板: {template_id}')
            return template
        except Requirement.DoesNotExist:
            raise ValueError(f'模板不存在: {template_id}')
    
    @staticmethod
    def list_templates(
        category=None,
        search_keyword=None,
        page=1,
        page_size=20
    ):
        from .requirement import Requirement
        from django.db.models import Q
        queryset = Requirement.objects.filter(is_template=True)
        
        if category:
            queryset = queryset.filter(template_category=category)
        
        if search_keyword:
            queryset = queryset.filter(
                Q(template_name__icontains=search_keyword) |
                Q(template_category__icontains=search_keyword) |
                Q(destination_cities__icontains=search_keyword)
            )
        
        total_count = queryset.count()
        
        offset = (page - 1) * page_size
        templates = queryset[offset:offset + page_size]
        
        return {
            'templates': list(templates),
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
    
    @staticmethod
    def get_template_categories():
        from .requirement import Requirement
        templates = Requirement.objects.filter(
            is_template=True
        ).exclude(
            template_category__isnull=True
        ).exclude(
            template_category=''
        ).values_list('template_category', flat=True).distinct()
        
        return list(templates)
    
    @staticmethod
    def use_template(template_id, created_by=None):
        from .requirement import Requirement
        try:
            template = Requirement.objects.get(requirement_id=template_id)
        except Requirement.DoesNotExist:
            raise ValueError(f'模板不存在: {template_id}')
        
        if not template.is_template:
            raise ValueError(f'该需求不是模板: {template_id}')
        
        # 不再需要传入new_requirement_id，由Requirement模型的save方法自动生成
        requirement_data = {
            'origin_name': template.origin_name,
            'origin_code': template.origin_code,
            'origin_type': template.origin_type,
            'destination_cities': template.destination_cities,
            'trip_days': template.trip_days,
            'group_adults': template.group_adults,
            'group_children': template.group_children,
            'group_seniors': template.group_seniors,
            'group_total': template.group_total,
            'travel_start_date': template.travel_start_date,
            'travel_end_date': template.travel_end_date,
            'travel_date_flexible': template.travel_date_flexible,
            'transportation_type': template.transportation_type,
            'transportation_notes': template.transportation_notes,
            'hotel_level': template.hotel_level,
            'hotel_requirements': template.hotel_requirements,
            'trip_rhythm': template.trip_rhythm,
            'preference_tags': template.preference_tags,
            'must_visit_spots': template.must_visit_spots,
            'avoid_activities': template.avoid_activities,
            'budget_level': template.budget_level,
            'budget_currency': template.budget_currency,
            'budget_min': template.budget_min,
            'budget_max': template.budget_max,
            'budget_notes': template.budget_notes,
            'source_type': Requirement.SourceType.FORM_INPUT,
            'status': Requirement.Status.PENDING_REVIEW,
            'assumptions': template.assumptions,
            'created_by': created_by,
            'reviewed_by': '',
            'is_template': False,
            'template_name': '',
            'template_category': '',
            'expires_at': None,
            'extension': template.extension
        }
        
        with transaction.atomic():
            requirement = Requirement.objects.create(**requirement_data)
        
        # 添加使用模板的记录到assumptions
        requirement.assumptions.append({
            'field': 'requirement_id',
            'inferred_value': requirement.requirement_id,
            'reason': f'从模板 {template_id} 创建'
        })
        requirement.save()
        
        return requirement
    
    @staticmethod
    def duplicate_template(template_id, new_template_name, created_by=None):
        from .requirement import Requirement
        try:
            template = Requirement.objects.get(requirement_id=template_id)
        except Requirement.DoesNotExist:
            raise ValueError(f'模板不存在: {template_id}')
        
        if not template.is_template:
            raise ValueError(f'该需求不是模板: {template_id}')
        
        new_template_data = TemplateManager._prepare_template_data(
            template,
            new_template_name,
            template.template_category,
            created_by,
            clear_sensitive_data=False
        )
        
        with transaction.atomic():
            new_template = Requirement.objects.create(**new_template_data)
        
        return new_template
