from typing import Dict, Any, Optional, List
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.models import Requirement


class RequirementService:
    
    @staticmethod
    def create_requirement_from_json(data: Dict[str, Any]) -> Requirement:
        base_info = data.get('base_info', {})
        preferences = data.get('preferences', {})
        budget = data.get('budget', {})
        metadata = data.get('metadata', {})
        
        origin = base_info.get('origin', {})
        group_size = base_info.get('group_size', {})
        travel_date = base_info.get('travel_date', {})
        transportation = preferences.get('transportation', {})
        accommodation = preferences.get('accommodation', {})
        itinerary = preferences.get('itinerary', {})
        budget_range = budget.get('range', {})
        
        origin_name = origin.get('name') or '未指定'
        origin_code = origin.get('code') or ''
        origin_type = origin.get('type') or ''
        
        destination_cities = base_info.get('destination_cities') or ['未指定']
        
        trip_days = base_info.get('trip_days') or 1
        
        group_adults = group_size.get('adults') or 0
        group_children = group_size.get('children') or 0
        group_seniors = group_size.get('seniors') or 0
        group_total = group_size.get('total') or 1
        
        travel_start_date = RequirementService._parse_date(travel_date.get('start_date'))
        travel_end_date = RequirementService._parse_date(travel_date.get('end_date'))
        travel_date_flexible = travel_date.get('is_flexible') or False
        
        transportation_type = transportation.get('type') or ''
        transportation_notes = transportation.get('notes') or ''
        
        hotel_level = accommodation.get('level') or ''
        hotel_requirements = accommodation.get('requirements') or ''
        
        trip_rhythm = itinerary.get('rhythm') or ''
        preference_tags = itinerary.get('tags') or []
        must_visit_spots = itinerary.get('special_constraints', {}).get('must_visit_spots') or []
        avoid_activities = itinerary.get('special_constraints', {}).get('avoid_activities') or []
        
        budget_level = budget.get('level') or ''
        budget_currency = budget.get('currency') or 'CNY'
        budget_min = budget_range.get('min')
        budget_max = budget_range.get('max')
        budget_notes = budget.get('budget_notes') or ''
        
        source_type = metadata.get('source_type') or 'NaturalLanguage'
        status = metadata.get('status') or 'PendingReview'
        assumptions = metadata.get('assumptions') or []
        
        extension = data.get('extension') or {}
        
        requirement = Requirement(
            requirement_id=data.get('requirement_id'),
            
            origin_name=origin_name,
            origin_code=origin_code,
            origin_type=origin_type,
            
            destination_cities=destination_cities,
            
            trip_days=trip_days,
            
            group_adults=group_adults,
            group_children=group_children,
            group_seniors=group_seniors,
            group_total=group_total,
            
            travel_start_date=travel_start_date,
            travel_end_date=travel_end_date,
            travel_date_flexible=travel_date_flexible,
            
            transportation_type=transportation_type,
            transportation_notes=transportation_notes,
            
            hotel_level=hotel_level,
            hotel_requirements=hotel_requirements,
            
            trip_rhythm=trip_rhythm,
            preference_tags=preference_tags,
            must_visit_spots=must_visit_spots,
            avoid_activities=avoid_activities,
            
            budget_level=budget_level,
            budget_currency=budget_currency,
            budget_min=budget_min,
            budget_max=budget_max,
            budget_notes=budget_notes,
            
            source_type=source_type,
            status=status,
            assumptions=assumptions,
            
            extension=extension
        )
        
        requirement.save()
        
        return requirement
    
    @staticmethod
    def update_requirement_from_json(requirement_id: str, data: Dict[str, Any]) -> Requirement:
        requirement = Requirement.objects.get(requirement_id=requirement_id)
        
        base_info = data.get('base_info', {})
        preferences = data.get('preferences', {})
        budget = data.get('budget', {})
        metadata = data.get('metadata', {})
        
        origin = base_info.get('origin', {})
        group_size = base_info.get('group_size', {})
        travel_date = base_info.get('travel_date', {})
        transportation = preferences.get('transportation', {})
        accommodation = preferences.get('accommodation', {})
        itinerary = preferences.get('itinerary', {})
        budget_range = budget.get('range', {})
        
        if 'origin' in base_info:
            requirement.origin_name = origin.get('name', requirement.origin_name)
            requirement.origin_code = origin.get('code', requirement.origin_code)
            requirement.origin_type = origin.get('type', requirement.origin_type)
        
        if 'destination_cities' in base_info:
            requirement.destination_cities = base_info['destination_cities']
        
        if 'trip_days' in base_info:
            requirement.trip_days = base_info['trip_days']
        
        if 'group_size' in base_info:
            requirement.group_adults = group_size.get('adults', requirement.group_adults)
            requirement.group_children = group_size.get('children', requirement.group_children)
            requirement.group_seniors = group_size.get('seniors', requirement.group_seniors)
            requirement.group_total = group_size.get('total', requirement.group_total)
        
        if 'travel_date' in base_info:
            if 'start_date' in travel_date:
                requirement.travel_start_date = RequirementService._parse_date(travel_date['start_date'])
            if 'end_date' in travel_date:
                requirement.travel_end_date = RequirementService._parse_date(travel_date['end_date'])
            if 'is_flexible' in travel_date:
                requirement.travel_date_flexible = travel_date['is_flexible']
        
        if 'transportation' in preferences:
            requirement.transportation_type = transportation.get('type', requirement.transportation_type)
            requirement.transportation_notes = transportation.get('notes', requirement.transportation_notes)
        
        if 'accommodation' in preferences:
            requirement.hotel_level = accommodation.get('level', requirement.hotel_level)
            requirement.hotel_requirements = accommodation.get('requirements', requirement.hotel_requirements)
        
        if 'itinerary' in preferences:
            requirement.trip_rhythm = itinerary.get('rhythm', requirement.trip_rhythm)
            requirement.preference_tags = itinerary.get('tags', requirement.preference_tags)
            special_constraints = itinerary.get('special_constraints', {})
            if 'must_visit_spots' in special_constraints:
                requirement.must_visit_spots = special_constraints['must_visit_spots']
            if 'avoid_activities' in special_constraints:
                requirement.avoid_activities = special_constraints['avoid_activities']
        
        if 'budget' in budget:
            requirement.budget_level = budget.get('level', requirement.budget_level)
            requirement.budget_currency = budget.get('currency', requirement.budget_currency)
            if 'range' in budget:
                if 'min' in budget_range:
                    requirement.budget_min = budget_range['min']
                if 'max' in budget_range:
                    requirement.budget_max = budget_range['max']
            requirement.budget_notes = budget.get('budget_notes', requirement.budget_notes)
        
        if 'status' in metadata:
            requirement.status = metadata['status']
        
        if 'assumptions' in metadata:
            requirement.assumptions = metadata['assumptions']
        
        if 'extension' in data:
            requirement.extension = data['extension']
        
        requirement.save()
        
        return requirement
    
    @staticmethod
    def get_requirement_by_id(requirement_id: str) -> Optional[Requirement]:
        try:
            return Requirement.objects.get(requirement_id=requirement_id)
        except Requirement.DoesNotExist:
            return None
    
    @staticmethod
    def list_requirements(filters: Optional[Dict[str, Any]] = None) -> List[Requirement]:
        queryset = Requirement.objects.all()
        
        if filters:
            if 'status' in filters:
                queryset = queryset.filter(status=filters['status'])
            if 'source_type' in filters:
                queryset = queryset.filter(source_type=filters['source_type'])
            if 'is_template' in filters:
                queryset = queryset.filter(is_template=filters['is_template'])
            if 'created_by' in filters:
                queryset = queryset.filter(created_by=filters['created_by'])
        
        return list(queryset)
    
    @staticmethod
    def delete_requirement(requirement_id: str) -> bool:
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            requirement.delete()
            return True
        except Requirement.DoesNotExist:
            return False
    
    @staticmethod
    @transaction.atomic
    def bulk_create_requirements(data_list: List[Dict[str, Any]]) -> List[Requirement]:
        requirements = []
        for data in data_list:
            try:
                requirement = RequirementService.create_requirement_from_json(data)
                requirements.append(requirement)
            except ValidationError as e:
                raise ValueError(f"Failed to create requirement: {e}")
        return requirements
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def search_requirements(query: str) -> List[Requirement]:
        from django.db.models import Q
        
        queryset = Requirement.objects.filter(
            Q(requirement_id__icontains=query) |
            Q(origin_name__icontains=query) |
            Q(destination_cities__icontains=query) |
            Q(created_by__icontains=query)
        )
        
        return list(queryset)
