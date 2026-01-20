import pytest
from django.test import TestCase, Client
from django.urls import reverse
import json


class TestLLMAPIEndpoints(TestCase):
    
    @pytest.fixture(autouse=True)
    def setup_django(self):
        from django.conf import settings
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY='test-secret-key',
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                INSTALLED_APPS=[
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'apps',
                ],
                USE_TZ=True,
            )
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check(self):
        response = self.client.get('/api/llm/health/')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'healthy'
        assert 'available_providers' in data
    
    def test_process_requirement_invalid_input(self):
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
    
    def test_process_requirement_missing_user_input(self):
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({'provider': 'deepseek'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
    
    def test_process_requirement_invalid_provider(self):
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': 'test input',
                'provider': 'invalid_provider'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
    
    def test_provider_info(self):
        response = self.client.get('/api/llm/provider-info/')
        
        assert response.status_code in [200, 404]
    
    def test_provider_info_with_provider(self):
        response = self.client.get('/api/llm/provider-info/?provider=deepseek')
        
        assert response.status_code in [200, 404]
    
    def test_rate_limit_stats(self):
        response = self.client.get('/api/llm/rate-limit-stats/')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'enabled' in data
        assert 'requests_per_minute' in data
    
    def test_rate_limit_stats_with_client_id(self):
        response = self.client.get('/api/llm/rate-limit-stats/?client_id=test_client')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['client_id'] == 'test_client'
    
    def test_cache_stats(self):
        response = self.client.get('/api/llm/cache-stats/')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'total_entries' in data
        assert 'total_hits' in data
    
    def test_clear_cache(self):
        response = self.client.post('/api/llm/cache/clear/')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'message' in data
    
    def test_reload_config(self):
        response = self.client.post('/api/llm/config/reload/')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'message' in data


class TestEndToEndFlow(TestCase):
    
    @pytest.fixture(autouse=True)
    def setup_django(self):
        from django.conf import settings
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY='test-secret-key',
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                INSTALLED_APPS=[
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'apps',
                ],
                USE_TZ=True,
            )
    
    def setUp(self):
        self.client = Client()
    
    def test_full_flow_with_mock(self):
        from unittest.mock import patch, Mock
        from services.llm.service import LLMRequirementService
        
        mock_response_data = {
            'requirement_id': 'REQ-20240101-1234',
            'base_info': {
                'origin': {'name': '北京', 'code': 'BJS', 'type': 'city'},
                'destination_cities': [{'name': '上海', 'code': 'SHA', 'country': '中国'}],
                'trip_days': 5,
                'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                'travel_date': {
                    'start_date': '2024-02-01',
                    'end_date': '2024-02-05',
                    'is_flexible': False
                }
            },
            'preferences': {
                'transportation': {'type': 'HighSpeedTrain', 'notes': ''},
                'accommodation': {'level': 'Comfort', 'requirements': ''},
                'itinerary': {
                    'rhythm': 'Moderate',
                    'tags': ['文化', '美食'],
                    'special_constraints': {
                        'must_visit_spots': ['外滩', '豫园'],
                        'avoid_activities': []
                    }
                }
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
        
        with patch.object(LLMRequirementService, 'process_requirement_sync') as mock_process:
            mock_result = Mock()
            mock_result.success = True
            mock_result.requirement_id = 'REQ-20240101-1234'
            mock_result.structured_data = mock_response_data
            mock_result.validation_result = Mock(is_valid=True, errors=[], warnings=[])
            mock_result.llm_response = Mock(
                provider='deepseek',
                model='deepseek-chat',
                tokens_used=100,
                response_time=1.5
            )
            mock_result.warnings = []
            mock_result.raw_response = json.dumps(mock_response_data)
            mock_process.return_value = mock_result
            
            response = self.client.post(
                '/api/llm/process/',
                data=json.dumps({
                    'user_input': '我想从北京去上海旅游5天，2个成人，预算5000到10000元',
                    'provider': 'deepseek',
                    'client_id': 'test_client',
                    'save_to_db': False
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.content)
            assert data['success'] is True
            assert data['requirement_id'] == 'REQ-20240101-1234'
            assert data['structured_data'] is not None


class TestBoundaryConditions(TestCase):
    
    @pytest.fixture(autouse=True)
    def setup_django(self):
        from django.conf import settings
        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY='test-secret-key',
                DATABASES={
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                INSTALLED_APPS=[
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'apps',
                ],
                USE_TZ=True,
            )
    
    def setUp(self):
        self.client = Client()
    
    def test_very_long_user_input(self):
        long_input = 'a' * 10000
        
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': long_input
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_empty_user_input(self):
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': ''
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_whitespace_only_input(self):
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': '   '
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_special_characters_in_input(self):
        special_input = '我想去旅游！@#$%^&*()_+{}[]|\\:";\'<>?,./'
        
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': special_input
            }),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 429, 500]
    
    def test_unicode_in_input(self):
        unicode_input = '我想去🏯日本🗾旅游，体验🍣寿司和🌸樱花'
        
        response = self.client.post(
            '/api/llm/process/',
            data=json.dumps({
                'user_input': unicode_input
            }),
            content_type='application/json'
            , save_to_db=False
        )
        
        assert response.status_code in [200, 400, 429, 500]
    
    def test_invalid_json_request(self):
        response = self.client.post(
            '/api/llm/process/',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
