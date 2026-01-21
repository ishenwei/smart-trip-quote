import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.llm.location_validator import LocationValidator, LocationValidationStatus


def test_location_validator():
    print("=== 测试位置验证器 ===\n")
    
    test_cases = [
        {
            'name': '测试1：缺少出发地和目的地',
            'data': {
                'base_info': {
                    'origin': {'name': '未指定', 'code': None, 'type': None},
                    'destination_cities': [{'name': '未指定', 'code': None, 'country': None}],
                    'trip_days': 5,
                    'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                    'travel_date': {'start_date': None, 'end_date': None, 'is_flexible': True}
                },
                'preferences': {},
                'budget': {},
                'metadata': {}
            }
        },
        {
            'name': '测试2：缺少出发地',
            'data': {
                'base_info': {
                    'origin': {'name': '未指定', 'code': None, 'type': None},
                    'destination_cities': [{'name': '上海', 'code': 'SHA', 'country': '中国'}],
                    'trip_days': 5,
                    'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                    'travel_date': {'start_date': None, 'end_date': None, 'is_flexible': True}
                },
                'preferences': {},
                'budget': {},
                'metadata': {}
            }
        },
        {
            'name': '测试3：缺少目的地',
            'data': {
                'base_info': {
                    'origin': {'name': '北京', 'code': 'BJS', 'type': 'Domestic'},
                    'destination_cities': [{'name': '未指定', 'code': None, 'country': None}],
                    'trip_days': 5,
                    'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                    'travel_date': {'start_date': None, 'end_date': None, 'is_flexible': True}
                },
                'preferences': {},
                'budget': {},
                'metadata': {}
            }
        },
        {
            'name': '测试4：有效的出发地和目的地',
            'data': {
                'base_info': {
                    'origin': {'name': '北京', 'code': 'BJS', 'type': 'Domestic'},
                    'destination_cities': [{'name': '上海', 'code': 'SHA', 'country': '中国'}],
                    'trip_days': 5,
                    'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
                    'travel_date': {'start_date': None, 'end_date': None, 'is_flexible': True}
                },
                'preferences': {},
                'budget': {},
                'metadata': {}
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print("-" * 50)
        
        result = LocationValidator.validate_locations(test_case['data'])
        
        print(f"状态: {result.status.value}")
        print(f"是否有效: {result.is_valid}")
        print(f"出发地: {result.origin}")
        print(f"目的地: {result.destination}")
        
        if result.error_message:
            print(f"错误信息: {result.error_message}")
        
        if result.suggestions:
            print("建议:")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"  {i}. {suggestion}")
        
        print("\n用户友好消息:")
        user_message = LocationValidator.generate_user_friendly_message(result, "测试输入")
        print(user_message)
        print("=" * 50)
    
    print("\n=== 测试输入示例 ===")
    examples = LocationValidator.get_input_examples()
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n=== 测试重试逻辑 ===")
    test_data = {
        'base_info': {
            'origin': {'name': '未指定', 'code': None, 'type': None},
            'destination_cities': [{'name': '未指定', 'code': None, 'country': None}],
            'trip_days': 5,
            'group_size': {'adults': 2, 'children': 0, 'seniors': 0, 'total': 2},
            'travel_date': {'start_date': None, 'end_date': None, 'is_flexible': True}
        },
        'preferences': {},
        'budget': {},
        'metadata': {}
    }
    
    result = LocationValidator.validate_locations(test_data)
    
    for retry in range(5):
        should_retry = LocationValidator.should_retry(result, retry, max_retries=3)
        print(f"重试次数 {retry}: 是否应该重试 = {should_retry}")
        if not should_retry:
            print("达到最大重试次数，停止重试")
            break


if __name__ == '__main__':
    test_location_validator()
