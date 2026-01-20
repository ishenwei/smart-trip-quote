import pytest
from unittest.mock import Mock, patch
from services.llm.service import LLMRequirementService, ProcessResult
from services.llm.config import LLMProvider
from services.llm.base import LLMResponse


class TestLLMRequirementService:
    
    @pytest.fixture
    def service(self):
        return LLMRequirementService()
    
    @pytest.fixture
    def mock_llm_response(self):
        return LLMResponse(
            content='{"requirement_id": "REQ-20240101-1234", "base_info": {"origin": {"name": "北京"}, "destination_cities": [{"name": "上海"}], "trip_days": 5, "group_size": {"adults": 2, "children": 0, "seniors": 0, "total": 2}, "travel_date": {"start_date": "2024-02-01", "end_date": "2024-02-05", "is_flexible": false}}, "preferences": {"transportation": {"type": "HighSpeedTrain", "notes": ""}, "accommodation": {"level": "Comfort", "requirements": ""}, "itinerary": {"rhythm": "Moderate", "tags": [], "special_constraints": {"must_visit_spots": [], "avoid_activities": []}}}, "budget": {"level": "Comfort", "currency": "CNY", "range": {"min": 5000, "max": 10000}, "budget_notes": ""}, "metadata": {"source_type": "NaturalLanguage", "status": "PendingReview", "assumptions": []}}',
            model='deepseek-chat',
            provider='deepseek',
            tokens_used=100,
            response_time=1.5
        )
    
    @patch('services.llm.service.RequirementService.create_requirement_from_json')
    @patch('services.llm.service.RequirementExtractor.extract_json_from_response')
    @patch('services.llm.service.RequirementExtractor.validate_requirement_data')
    @patch('services.llm.service.RequirementExtractor.normalize_data')
    def test_process_requirement_sync_success(
        self,
        mock_normalize,
        mock_validate,
        mock_extract,
        mock_create,
        service,
        mock_llm_response
    ):
        mock_requirement = Mock()
        mock_requirement.requirement_id = 'REQ-20240101-1234'
        mock_create.return_value = mock_requirement
        
        mock_extract.return_value = {'test': 'data'}
        mock_normalize.return_value = {'test': 'normalized'}
        mock_validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
        
        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_model_info.return_value = {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'api_url': 'https://api.deepseek.com'
            }
            mock_provider.config.enable_cache = False
            mock_provider.generate_sync.return_value = mock_llm_response
            mock_get_provider.return_value = mock_provider
            
            result = service.process_requirement_sync(
                user_input='我想从北京去上海旅游5天',
                save_to_db=True
            )
        
        assert result.success is True
        assert result.requirement_id == 'REQ-20240101-1234'
        assert result.structured_data is not None
    
    @patch('services.llm.service.RequirementExtractor.extract_json_from_response')
    def test_process_requirement_sync_rate_limit_exceeded(
        self,
        mock_extract,
        service
    ):
        with patch.object(service, '_check_rate_limit') as mock_check:
            mock_check.return_value = (False, 'Rate limit exceeded')
            
            result = service.process_requirement_sync(
                user_input='test input'
            )
        
        assert result.success is False
        assert 'Rate limit exceeded' in result.error
    
    @patch('services.llm.service.RequirementExtractor.extract_json_from_response')
    def test_process_requirement_sync_llm_error(
        self,
        mock_extract,
        service
    ):
        mock_extract.return_value = None
        
        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_model_info.return_value = {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'api_url': 'https://api.deepseek.com'
            }
            mock_provider.config.enable_cache = False
            mock_provider.generate_sync.return_value = LLMResponse(
                content='',
                model='deepseek-chat',
                provider='deepseek',
                error='API Error'
            )
            mock_get_provider.return_value = mock_provider
            
            result = service.process_requirement_sync(
                user_input='test input'
            )
        
        assert result.success is False
        assert 'API Error' in result.error
    
    @patch('services.llm.service.RequirementExtractor.extract_json_from_response')
    def test_process_requirement_sync_validation_failed(
        self,
        mock_extract,
        service
    ):
        mock_extract.return_value = {'test': 'data'}
        
        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_model_info.return_value = {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'api_url': 'https://api.deepseek.com'
            }
            mock_provider.config.enable_cache = False
            mock_provider.generate_sync.return_value = LLMResponse(
                content='{"test": "data"}',
                model='deepseek-chat',
                provider='deepseek'
            )
            mock_get_provider.return_value = mock_provider
            
            with patch('services.llm.service.RequirementExtractor.validate_requirement_data') as mock_validate:
                mock_validate.return_value = Mock(
                    is_valid=False,
                    errors=['Invalid data'],
                    warnings=[]
                )
                
                result = service.process_requirement_sync(
                    user_input='test input'
                )
        
        assert result.success is False
        assert 'Validation failed' in result.error
    
    def test_get_provider_info(self, service):
        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = Mock()
            mock_provider.get_model_info.return_value = {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'api_url': 'https://api.deepseek.com'
            }
            mock_get_provider.return_value = mock_provider
            
            info = service.get_provider_info()
        
        assert info['provider'] == 'deepseek'
        assert info['model'] == 'deepseek-chat'
    
    def test_get_rate_limit_stats(self, service):
        stats = service.get_rate_limit_stats()
        
        assert 'enabled' in stats
        assert 'requests_per_minute' in stats
        assert 'current_minute_requests' in stats
    
    def test_get_rate_limit_stats_with_client_id(self, service):
        stats = service.get_rate_limit_stats(client_id='test_client')
        
        assert 'client_id' in stats
        assert stats['client_id'] == 'test_client'
    
    def test_get_cache_stats(self, service):
        stats = service.get_cache_stats()
        
        assert 'total_entries' in stats
        assert 'total_hits' in stats
        assert 'cache_size_mb' in stats
    
    def test_clear_cache(self, service):
        service.clear_cache()
        
        stats = service.get_cache_stats()
        assert stats['total_entries'] == 0
    
    def test_reload_configs(self, service):
        with patch.object(service.config_manager, 'reload_configs') as mock_reload:
            service.reload_configs()
            mock_reload.assert_called_once()
