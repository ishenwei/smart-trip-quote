from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class LocationValidationStatus(Enum):
    VALID = "valid"
    MISSING_ORIGIN = "missing_origin"
    MISSING_DESTINATION = "missing_destination"
    MISSING_BOTH = "missing_both"
    INVALID_FORMAT = "invalid_format"
    AMBIGUOUS = "ambiguous"


@dataclass
class LocationValidationResult:
    status: LocationValidationStatus
    origin: Optional[Dict[str, Any]]
    destination: Optional[List[Dict[str, Any]]]
    is_valid: bool
    error_message: Optional[str] = None
    suggestions: Optional[List[str]] = None
    retry_count: int = 0
    
    def add_suggestion(self, suggestion: str):
        if self.suggestions is None:
            self.suggestions = []
        self.suggestions.append(suggestion)


class LocationValidator:
    VALID_ORIGIN_KEYWORDS = ['从', '出发', '起点', '始发', '离开', '在']
    VALID_DESTINATION_KEYWORDS = ['去', '到', '去往', '前往', '目的地', '旅游', '玩']
    
    MIN_CITY_NAME_LENGTH = 2
    MAX_CITY_NAME_LENGTH = 20
    
    DEFAULT_ORIGIN_PLACEHOLDER = '未指定'
    DEFAULT_DESTINATION_PLACEHOLDER = '未指定'
    
    @staticmethod
    def validate_locations(data: Dict[str, Any]) -> LocationValidationResult:
        if not isinstance(data, dict) or 'base_info' not in data:
            return LocationValidationResult(
                status=LocationValidationStatus.INVALID_FORMAT,
                origin=None,
                destination=None,
                is_valid=False,
                error_message="数据格式错误：缺少base_info字段"
            )
        
        base_info = data['base_info']
        
        if 'origin' not in base_info or 'destination_cities' not in base_info:
            return LocationValidationResult(
                status=LocationValidationStatus.INVALID_FORMAT,
                origin=None,
                destination=None,
                is_valid=False,
                error_message="数据格式错误：缺少origin或destination_cities字段"
            )
        
        origin = base_info['origin']
        destinations = base_info['destination_cities']
        
        if not isinstance(origin, dict):
            return LocationValidationResult(
                status=LocationValidationStatus.INVALID_FORMAT,
                origin=None,
                destination=None,
                is_valid=False,
                error_message="数据格式错误：origin必须是字典类型"
            )
        
        if not isinstance(destinations, list):
            return LocationValidationResult(
                status=LocationValidationStatus.INVALID_FORMAT,
                origin=None,
                destination=None,
                is_valid=False,
                error_message="数据格式错误：destination_cities必须是列表类型"
            )
        
        origin_name = origin.get('name')
        has_valid_origin = LocationValidator._is_valid_location_name(origin_name)
        
        has_valid_destination = False
        if destinations:
            for dest in destinations:
                if isinstance(dest, dict):
                    dest_name = dest.get('name')
                    if LocationValidator._is_valid_location_name(dest_name):
                        has_valid_destination = True
                        break
        
        if not has_valid_origin and not has_valid_destination:
            return LocationValidationResult(
                status=LocationValidationStatus.MISSING_BOTH,
                origin=origin,
                destination=destinations,
                is_valid=False,
                error_message="未能识别出发地和目的地信息",
                suggestions=[
                    "请同时提供出发地和目的地，例如：'从北京去上海'",
                    "或者分别说明：'出发地：北京，目的地：上海'"
                ]
            )
        
        if not has_valid_origin:
            return LocationValidationResult(
                status=LocationValidationStatus.MISSING_ORIGIN,
                origin=origin,
                destination=destinations,
                is_valid=False,
                error_message="未能识别出发地信息",
                suggestions=[
                    "请提供出发地，例如：'从北京出发'",
                    "或者在描述中说明您的出发城市"
                ]
            )
        
        if not has_valid_destination:
            return LocationValidationResult(
                status=LocationValidationStatus.MISSING_DESTINATION,
                origin=origin,
                destination=destinations,
                is_valid=False,
                error_message="未能识别目的地信息",
                suggestions=[
                    "请提供目的地，例如：'去上海旅游'",
                    "或者说明您想去哪个城市"
                ]
            )
        
        return LocationValidationResult(
            status=LocationValidationStatus.VALID,
            origin=origin,
            destination=destinations,
            is_valid=True
        )
    
    @staticmethod
    def _is_valid_location_name(name: Optional[str]) -> bool:
        if name is None:
            return False
        
        if not isinstance(name, str):
            return False
        
        name = name.strip()
        
        if len(name) < LocationValidator.MIN_CITY_NAME_LENGTH:
            return False
        
        if len(name) > LocationValidator.MAX_CITY_NAME_LENGTH:
            return False
        
        if name in [LocationValidator.DEFAULT_ORIGIN_PLACEHOLDER, LocationValidator.DEFAULT_DESTINATION_PLACEHOLDER]:
            return False
        
        if name in ['', 'null', 'None', '未明确', '不清楚']:
            return False
        
        return True
    
    @staticmethod
    def generate_user_friendly_message(result: LocationValidationResult, user_input: str) -> str:
        if result.is_valid:
            return ""
        
        messages = {
            LocationValidationStatus.MISSING_BOTH: f"抱歉，我无法从您的描述中识别出发地和目的地。\n\n您的输入：{user_input}\n\n请同时提供这两个信息，例如：\n• '从北京去上海旅游'\n• '从广州出发，去成都玩5天'\n• '我想从深圳去杭州'",
            
            LocationValidationStatus.MISSING_ORIGIN: f"抱歉，我无法从您的描述中识别出发地。\n\n您的输入：{user_input}\n\n目的地已识别，但请告诉我您从哪个城市出发，例如：\n• '从{LocationValidator._extract_destination_name(result.destination)}出发'\n• '我在北京，想去{LocationValidator._extract_destination_name(result.destination)}'",
            
            LocationValidationStatus.MISSING_DESTINATION: f"抱歉，我无法从您的描述中识别目的地。\n\n您的输入：{user_input}\n\n出发地已识别为'{result.origin.get('name', '')}'，但请告诉我您想去哪个城市，例如：\n• '从{result.origin.get('name', '')}去上海'\n• '从{result.origin.get('name', '')}出发，去成都'",
            
            LocationValidationStatus.INVALID_FORMAT: f"抱歉，数据处理出现错误：{result.error_message}\n\n请重新描述您的旅游需求。"
        }
        
        return messages.get(result.status, "抱歉，无法识别您的位置信息，请重新描述。")
    
    @staticmethod
    def _extract_destination_name(destinations: List[Dict[str, Any]]) -> str:
        if not destinations:
            return "目的地"
        
        for dest in destinations:
            if isinstance(dest, dict):
                name = dest.get('name')
                if name and LocationValidator._is_valid_location_name(name):
                    return name
        
        return "目的地"
    
    @staticmethod
    def get_input_examples() -> List[str]:
        return [
            "从北京去上海旅游5天",
            "从广州出发，去成都玩一周",
            "我想从深圳去杭州，3个人",
            "从上海出发去三亚，预算5000元",
            "北京到香港，2个成人，10天行程"
        ]
    
    @staticmethod
    def should_retry(result: LocationValidationResult, current_retry: int, max_retries: int = 3) -> bool:
        if result.is_valid:
            return False
        
        if current_retry >= max_retries:
            return False
        
        return True
