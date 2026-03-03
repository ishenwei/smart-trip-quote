import requests
import json
from datetime import date

# 测试webhook URL
webhook_url = "http://localhost:8000/api/llm/webhook/itinerary/"

# 生成测试数据
test_data = {
    "output": {
        "requirement_id": "REQ_20260303_001",
        "itinerary_name": "上海三日游",
        "start_date": "2026-04-01",
        "end_date": "2026-04-03",
        "destinations": [
            {
                "destination_order": 1,
                "city_name": "上海",
                "country_code": "CN",
                "arrival_date": "2026-04-01",
                "departure_date": "2026-04-03"
            }
        ],
        "traveler_stats": {
            "total_travelers": 2,
            "adults": 2,
            "children": 0,
            "infants": 0,
            "seniors": 0
        },
        "daily_schedules": [
            {
                "day": 1,
                "date": "2026-04-01",
                "city": "上海",
                "activities": [
                    {
                        "activity_title": "抵达上海",
                        "activity_type": "FLIGHT",
                        "start_time": "09:00:00",
                        "end_time": "11:00:00",
                        "activity_description": "乘坐航班抵达上海浦东国际机场"
                    },
                    {
                        "activity_title": "酒店入住",
                        "activity_type": "CHECK_IN",
                        "start_time": "12:00:00",
                        "end_time": "13:00:00",
                        "activity_description": "办理酒店入住手续"
                    },
                    {
                        "activity_title": "外滩游览",
                        "activity_type": "ATTRACTION",
                        "start_time": "14:00:00",
                        "end_time": "16:00:00",
                        "activity_description": "游览上海外滩，欣赏黄浦江两岸风光"
                    },
                    {
                        "activity_title": "晚餐",
                        "activity_type": "MEAL",
                        "start_time": "18:00:00",
                        "end_time": "20:00:00",
                        "activity_description": "在上海老饭店享用晚餐"
                    }
                ]
            },
            {
                "day": 2,
                "date": "2026-04-02",
                "city": "上海",
                "activities": [
                    {
                        "activity_title": "豫园游览",
                        "activity_type": "ATTRACTION",
                        "start_time": "09:00:00",
                        "end_time": "11:00:00",
                        "activity_description": "游览豫园，感受上海传统文化"
                    },
                    {
                        "activity_title": "午餐",
                        "activity_type": "MEAL",
                        "start_time": "12:00:00",
                        "end_time": "13:30:00",
                        "activity_description": "在豫园附近品尝上海特色小吃"
                    },
                    {
                        "activity_title": "上海博物馆",
                        "activity_type": "ATTRACTION",
                        "start_time": "14:30:00",
                        "end_time": "16:30:00",
                        "activity_description": "参观上海博物馆，了解上海历史文化"
                    },
                    {
                        "activity_title": "晚餐",
                        "activity_type": "MEAL",
                        "start_time": "18:00:00",
                        "end_time": "20:00:00",
                        "activity_description": "在新天地享用晚餐"
                    }
                ]
            },
            {
                "day": 3,
                "date": "2026-04-03",
                "city": "上海",
                "activities": [
                    {
                        "activity_title": "上海科技馆",
                        "activity_type": "ATTRACTION",
                        "start_time": "09:00:00",
                        "end_time": "11:00:00",
                        "activity_description": "参观上海科技馆，体验科技魅力"
                    },
                    {
                        "activity_title": "午餐",
                        "activity_type": "MEAL",
                        "start_time": "12:00:00",
                        "end_time": "13:30:00",
                        "activity_description": "在科技馆附近享用午餐"
                    },
                    {
                        "activity_title": "酒店退房",
                        "activity_type": "CHECK_OUT",
                        "start_time": "14:00:00",
                        "end_time": "15:00:00",
                        "activity_description": "办理酒店退房手续"
                    },
                    {
                        "activity_title": "离开上海",
                        "activity_type": "FLIGHT",
                        "start_time": "16:00:00",
                        "end_time": "18:00:00",
                        "activity_description": "乘坐航班离开上海"
                    }
                ]
            }
        ]
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
        json=test_data,
        verify=False
    )
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    # 解析响应
    if response.status_code == 200:
        response_data = response.json()
        print(f"Success: {response_data.get('success')}")
        print(f"Itinerary ID: {response_data.get('itinerary_id')}")
        print(f"Itinerary Name: {response_data.get('itinerary_name')}")
    else:
        print("Error occurred")
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()