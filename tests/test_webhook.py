import requests
import json

# 测试webhook URL
webhook_url = "http://127.0.0.1:62000/webhook-test/smart-trip-requirement"

# 简单的JSON数据
json_data = {
    "requirement_id": "TEST_20260302_001",
    "requirement_json_data": {
        "base_info": {
            "origin": {
                "name": "北京",
                "code": "BJS",
                "type": "city"
            },
            "destination_cities": [
                {
                    "name": "上海",
                    "code": "SHA",
                    "type": "city"
                }
            ],
            "trip_days": 3,
            "group_size": {
                "adults": 2,
                "children": 0,
                "seniors": 0,
                "total": 2
            },
            "travel_date": {
                "start_date": "2026-04-01",
                "end_date": "2026-04-03",
                "is_flexible": False
            }
        },
        "preferences": {
            "transportation": {
                "type": "RoundTripFlight",
                "notes": "希望乘坐早上的航班"
            },
            "accommodation": {
                "level": "Comfort",
                "requirements": "靠近市中心"
            },
            "itinerary": {
                "rhythm": "Moderate",
                "tags": ["文化", "美食"],
                "special_constraints": {
                    "must_visit_spots": ["外滩", "豫园"],
                    "avoid_activities": ["购物"]
                }
            }
        },
        "budget": {
            "level": "Comfort",
            "currency": "CNY",
            "range": {
                "min": 5000,
                "max": 8000
            },
            "budget_notes": "包含往返机票"
        }
    }
}

# 发送POST请求
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "test-api-key"
}

try:
    response = requests.post(
        webhook_url,
        headers=headers,
        json=json_data,
        verify=False
    )
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"Error: {str(e)}")
