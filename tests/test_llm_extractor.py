import pytest
from services.llm.extractor import RequirementExtractor, ValidationResult


class TestRequirementExtractor:
    
    def test_extract_json_from_response_with_code_blocks(self):
        response_text = '''```json
{
  "requirement_id": "REQ-20240101-1234",
  "base_info": {
    "origin": {"name": "北京"},
    "destination_cities": [{"name": "上海"}],
    "trip_days": 5,
    "group_size": {"adults": 2, "children": 0, "seniors": 0, "total": 2},
    "travel_date": {"start_date": "2024-02-01", "end_date": "2024-02-05", "is_flexible": false}
  },
  "preferences": {
    "transportation": {"type": "HighSpeedTrain", "notes": ""},
    "accommodation": {"level": "Comfort", "requirements": ""},
    "itinerary": {"rhythm": "Moderate", "tags": [], "special_constraints": {"must_visit_spots": [], "avoid_activities": []}}
  },
  "budget": {
    "level": "Comfort",
    "currency": "CNY",
    "range": {"min": 5000, "max": 10000},
    "budget_notes": ""
  },
  "metadata": {
    "source_type": "NaturalLanguage",
    "status": "PendingReview",
    "assumptions": []
  }
}
```'''
        
        data = RequirementExtractor.extract_json_from_response(response_text)
        
        assert data is not None
        assert data['requirement_id'] == 'REQ-20240101-1234'
        assert data['base_info']['origin']['name'] == '北京'
    
    def test_extract_json_from_response_without_code_blocks(self):
        response_text = '''{
  "requirement_id": "REQ-20240101-1234",
  "base_info": {
    "origin": {"name": "北京"}
  }
}'''
        
        data = RequirementExtractor.extract_json_from_response(response_text)
        
        assert data is not None
        assert data['requirement_id'] == 'REQ-20240101-1234'
    
    def test_extract_json_from_response_invalid_json(self):
        response_text = 'This is not valid JSON'
        
        data = RequirementExtractor.extract_json_from_response(response_text)
        
        assert data is None
    
    def test_validate_requirement_data_valid(self):
        data = {
            'requirement_id': 'REQ-20240101-1234',
            'base_info': {
                'origin': {'name': '北京', 'code': 'BJS', 'type': 'city'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {
                'transportation': {'type': 'HighSpeedTrain', 'notes': ''},
                'accommodation': {'level': 'Comfort', 'requirements': ''},
                'itinerary': {'rhythm': 'Moderate', 'tags': [], 'special_constraints': {'must_visit_spots': [], 'avoid_activities': []}}
            },
            'budget': {
                'level': 'Comfort',
                'currency': 'CNY',
                'range': {'min': 5000, 'max': 10000},
                'budget_notes': ''
            },
            'metadata': {
                'source_type': 'NaturalLanguage',
                'status': 'PendingReview',
                'assumptions': []
            }
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_requirement_data_missing_required_fields(self):
        data = {
            'base_info': {},
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_validate_requirement_data_invalid_trip_days(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 0,
                'group_size': {'adults': 1, 'children': 0, 'seniors': 0, 'total': 1},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('trip_days' in error for error in result.errors)
    
    def test_validate_requirement_data_invalid_group_size(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 3},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('不一致' in error for error in result.errors)
    
    def test_validate_requirement_data_invalid_date_format(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 1, 'children': 0, 'seniors': 0, 'total': 1},
                'travel_date': {'start_date': '2024/02/01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('格式错误' in error for error in result.errors)
    
    def test_validate_requirement_data_invalid_date_range(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 1, 'children': 0, 'seniors': 0, 'total': 1},
                'travel_date': {'start_date': '2024-02-05', 'end_date': '2024-02-01', 'is_flexible': False}
            },
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('不能早于' in error for error in result.errors)
    
    def test_validate_requirement_data_invalid_transportation_type(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 1, 'children': 0, 'seniors': 0, 'total': 1},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {
                'transportation': {'type': 'InvalidType', 'notes': ''},
                'accommodation': {},
                'itinerary': {}
            },
            'budget': {},
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('transportation.type' in error for error in result.errors)
    
    def test_validate_requirement_data_invalid_budget_range(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 1, 'children': 0, 'seniors': 0, 'total': 1},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05', 'is_flexible': False}
            },
            'preferences': {},
            'budget': {
                'level': 'Comfort',
                'currency': 'CNY',
                'range': {'min': 10000, 'max': 5000},
                'budget_notes': ''
            },
            'metadata': {}
        }
        
        result = RequirementExtractor.validate_requirement_data(data)
        
        assert result.is_valid is False
        assert any('min不能大于max' in error for error in result.errors)
    
    def test_normalize_data(self):
        data = {
            'base_info': {
                'origin': {'name': '北京'},
                'destination_cities': [{'name': '上海'}],
                'trip_days': 5,
                'group_size': {'adults': 2, 'children': 0},
                'travel_date': {'start_date': '2024-02-01', 'end_date': '2024-02-05'}
            },
            'preferences': {},
            'budget': {},
            'metadata': {}
        }
        
        normalized = RequirementExtractor.normalize_data(data)
        
        assert 'requirement_id' in normalized
        assert normalized['base_info']['group_size']['total'] == 2
        assert normalized['base_info']['group_size']['seniors'] == 0
        assert normalized['base_info']['travel_date']['is_flexible'] is False
        assert normalized['metadata']['source_type'] == 'NaturalLanguage'
        assert normalized['metadata']['status'] == 'PendingReview'
    
    def test_generate_requirement_id(self):
        requirement_id = RequirementExtractor.generate_requirement_id()
        
        assert requirement_id.startswith('REQ-')
        assert len(requirement_id) == 17
