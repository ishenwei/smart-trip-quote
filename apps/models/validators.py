from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class RequirementValidator:
    
    @staticmethod
    def validate_requirement_id(requirement_id):
        if not requirement_id:
            raise ValidationError({'requirement_id': '需求ID不能为空'})
        if len(requirement_id) > 50:
            raise ValidationError({'requirement_id': '需求ID长度不能超过50个字符'})
        if not requirement_id.startswith('REQ-'):
            raise ValidationError({'requirement_id': '需求ID必须以REQ-开头'})
    
    @staticmethod
    def validate_origin(origin_name, origin_code=None, origin_type=None):
        if not origin_name:
            raise ValidationError({'origin_name': '出发地不能为空'})
        if len(origin_name) > 100:
            raise ValidationError({'origin_name': '出发地名称长度不能超过100个字符'})
        if origin_code and len(origin_code) > 10:
            raise ValidationError({'origin_code': '出发地代码长度不能超过10个字符'})
        if origin_type and origin_type not in ['Domestic', 'International', '']:
            raise ValidationError({'origin_type': '出发地类型必须是Domestic或International'})
    
    @staticmethod
    def validate_destination_cities(destination_cities):
        if not destination_cities:
            raise ValidationError({'destination_cities': '目的地城市不能为空'})
        if not isinstance(destination_cities, list):
            raise ValidationError({'destination_cities': '目的地城市必须是列表格式'})
        
        for city in destination_cities:
            if not isinstance(city, dict):
                raise ValidationError({'destination_cities': '每个目的地城市必须是字典格式'})
            if 'name' not in city or not city['name']:
                raise ValidationError({'destination_cities': '目的地城市必须包含name字段'})
            if 'stay_days' in city:
                try:
                    stay_days = int(city['stay_days'])
                    if stay_days < 1 or stay_days > 365:
                        raise ValidationError({'destination_cities': '停留天数必须在1-365天之间'})
                except (ValueError, TypeError):
                    raise ValidationError({'destination_cities': '停留天数必须是正整数'})
    
    @staticmethod
    def validate_trip_days(trip_days, travel_start_date, travel_end_date):
        from datetime import datetime
        
        if not trip_days or trip_days < 1:
            raise ValidationError({'trip_days': '出行天数必须是正整数'})
        if trip_days > 365:
            raise ValidationError({'trip_days': '出行天数不能超过365天'})
        
        if travel_start_date and travel_end_date:
            if isinstance(travel_start_date, str):
                travel_start_date = datetime.strptime(travel_start_date, '%Y-%m-%d').date()
            if isinstance(travel_end_date, str):
                travel_end_date = datetime.strptime(travel_end_date, '%Y-%m-%d').date()
            
            calculated_days = (travel_end_date - travel_start_date).days + 1
            if calculated_days != trip_days:
                raise ValidationError({'trip_days': f'出行天数({trip_days})与日期范围({calculated_days}天)不一致'})
    
    @staticmethod
    def validate_group_size(adults, children, seniors, total):
        if not total or total < 1:
            raise ValidationError({'group_total': '总人数必须是正整数'})
        if total > 100:
            raise ValidationError({'group_total': '总人数不能超过100人'})
        
        calculated_total = adults + children + seniors
        if calculated_total != total:
            raise ValidationError({'group_total': f'总人数({total})与各类型人数之和({calculated_total})不一致'})
        
        if adults < 0 or children < 0 or seniors < 0:
            raise ValidationError({'group_size': '各类型人数不能为负数'})
    
    @staticmethod
    def validate_travel_dates(start_date, end_date, flexible):
        from datetime import datetime
        
        if not start_date:
            raise ValidationError({'travel_start_date': '开始日期不能为空'})
        if not end_date:
            raise ValidationError({'travel_end_date': '结束日期不能为空'})
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if end_date < start_date:
            raise ValidationError({'travel_end_date': '结束日期不能早于开始日期'})
        
        max_date = datetime.now().date() + timedelta(days=365 * 2)
        if start_date > max_date:
            raise ValidationError({'travel_start_date': '开始日期不能超过2年后'})
        
        if (end_date - start_date).days > 365:
            raise ValidationError({'travel_dates': '出行日期范围不能超过365天'})
    
    @staticmethod
    def validate_transportation(transport_type, notes):
        valid_types = ['RoundTripFlight', 'OneWayFlight', 'HighSpeedTrain', 'Train', 'SelfDriving', 'Other', '']
        if transport_type not in valid_types:
            raise ValidationError({'transportation_type': f'交通类型必须是以下之一: {", ".join(valid_types)}'})
        
        if notes and len(notes) > 500:
            raise ValidationError({'transportation_notes': '交通偏好说明长度不能超过500个字符'})
    
    @staticmethod
    def validate_accommodation(hotel_level, requirements):
        valid_levels = ['Economy', 'Comfort', 'Premium', 'Luxury', '']
        if hotel_level not in valid_levels:
            raise ValidationError({'hotel_level': f'酒店等级必须是以下之一: {", ".join(valid_levels)}'})
        
        if requirements and len(requirements) > 500:
            raise ValidationError({'hotel_requirements': '住宿特殊要求长度不能超过500个字符'})
    
    @staticmethod
    def validate_itinerary(rhythm, tags, must_visit_spots, avoid_activities):
        valid_rhythms = ['Relaxed', 'Moderate', 'Intense', '']
        if rhythm not in valid_rhythms:
            raise ValidationError({'trip_rhythm': f'行程节奏必须是以下之一: {", ".join(valid_rhythms)}'})
        
        if tags:
            valid_tags = ['Culture', 'CityScape', 'Food', 'History', 'Nature', 'Shopping', 'Entertainment', 'Other']
            for tag in tags:
                if tag not in valid_tags:
                    raise ValidationError({'preference_tags': f'偏好标签必须是以下之一: {", ".join(valid_tags)}'})
        
        if must_visit_spots and len(must_visit_spots) > 20:
            raise ValidationError({'must_visit_spots': '必游景点数量不能超过20个'})
        
        if avoid_activities and len(avoid_activities) > 10:
            raise ValidationError({'avoid_activities': '避免活动数量不能超过10个'})
    
    @staticmethod
    def validate_budget(level, currency, min_budget, max_budget, notes):
        valid_levels = ['Economy', 'Comfort', 'HighEnd', 'Luxury', '']
        if level not in valid_levels:
            raise ValidationError({'budget_level': f'预算等级必须是以下之一: {", ".join(valid_levels)}'})
        
        if currency and len(currency) > 10:
            raise ValidationError({'budget_currency': '货币代码长度不能超过10个字符'})
        
        if min_budget and min_budget < 0:
            raise ValidationError({'budget_min': '最低预算不能为负数'})
        
        if max_budget and max_budget < 0:
            raise ValidationError({'budget_max': '最高预算不能为负数'})
        
        if min_budget and max_budget and min_budget > max_budget:
            raise ValidationError({'budget_min': '最低预算不能高于最高预算'})
        
        if notes and len(notes) > 500:
            raise ValidationError({'budget_notes': '预算说明长度不能超过500个字符'})
    
    @staticmethod
    def validate_metadata(source_type, status, is_template, template_name, template_category):
        valid_sources = ['NaturalLanguage', 'FormInput']
        if source_type not in valid_sources:
            raise ValidationError({'source_type': f'需求来源必须是以下之一: {", ".join(valid_sources)}'})
        
        valid_statuses = ['PendingReview', 'Confirmed', 'Expired']
        if status not in valid_statuses:
            raise ValidationError({'status': f'需求状态必须是以下之一: {", ".join(valid_statuses)}'})
        
        if is_template and not template_name:
            raise ValidationError({'template_name': '模板必须包含模板名称'})
        
        if template_name and len(template_name) > 200:
            raise ValidationError({'template_name': '模板名称长度不能超过200个字符'})
        
        if template_category and len(template_category) > 100:
            raise ValidationError({'template_category': '模板分类长度不能超过100个字符'})
    
    @staticmethod
    def validate_assumptions(assumptions):
        if not isinstance(assumptions, list):
            raise ValidationError({'assumptions': '系统推断说明必须是列表格式'})
        
        for assumption in assumptions:
            if not isinstance(assumption, dict):
                raise ValidationError({'assumptions': '每个推断必须是字典格式'})
            if 'field' not in assumption or not assumption['field']:
                raise ValidationError({'assumptions': '推断必须包含field字段'})
            if 'inferred_value' not in assumption:
                raise ValidationError({'assumptions': '推断必须包含inferred_value字段'})
            if 'reason' not in assumption or not assumption['reason']:
                raise ValidationError({'assumptions': '推断必须包含reason字段'})
    
    @staticmethod
    def validate_extension(extension):
        if not isinstance(extension, dict):
            raise ValidationError({'extension': '扩展字段必须是字典格式'})
        
        if len(extension) > 50:
            raise ValidationError({'extension': '扩展字段数量不能超过50个'})
    
    @classmethod
    def validate_all(cls, data):
        errors = {}
        
        try:
            cls.validate_requirement_id(data.get('requirement_id'))
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_origin(
                data.get('origin_name'),
                data.get('origin_code'),
                data.get('origin_type')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_destination_cities(data.get('destination_cities'))
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_trip_days(
                data.get('trip_days'),
                data.get('travel_start_date'),
                data.get('travel_end_date')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_group_size(
                data.get('group_adults', 0),
                data.get('group_children', 0),
                data.get('group_seniors', 0),
                data.get('group_total')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_travel_dates(
                data.get('travel_start_date'),
                data.get('travel_end_date'),
                data.get('travel_date_flexible', False)
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_transportation(
                data.get('transportation_type', ''),
                data.get('transportation_notes', '')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_accommodation(
                data.get('hotel_level', ''),
                data.get('hotel_requirements', '')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_itinerary(
                data.get('trip_rhythm', ''),
                data.get('preference_tags', []),
                data.get('must_visit_spots', []),
                data.get('avoid_activities', [])
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_budget(
                data.get('budget_level', ''),
                data.get('budget_currency', 'CNY'),
                data.get('budget_min'),
                data.get('budget_max'),
                data.get('budget_notes', '')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_metadata(
                data.get('source_type', 'NaturalLanguage'),
                data.get('status', 'PendingReview'),
                data.get('is_template', False),
                data.get('template_name', ''),
                data.get('template_category', '')
            )
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_assumptions(data.get('assumptions', []))
        except ValidationError as e:
            errors.update(e.message_dict)
        
        try:
            cls.validate_extension(data.get('extension', {}))
        except ValidationError as e:
            errors.update(e.message_dict)
        
        if errors:
            raise ValidationError(errors)
        
        return True
