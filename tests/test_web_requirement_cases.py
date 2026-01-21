#!/usr/bin/env python3
"""
旅游需求管理系统测试用例

本文件包含了针对旅游需求管理系统的测试用例，覆盖不同类型的旅游需求场景。
"""

import json
from datetime import datetime, timedelta

# 测试环境信息
TEST_ENVIRONMENT = {
    "web_url": "http://localhost:5173",  # 前端Web页面地址
    "api_url": "http://localhost:8000/api",  # 后端API地址
    "database": {
        "host": "localhost",
        "port": 3306,
        "name": "stq_db",
        "user": "stq_user",
        "password": "",
    },
    "llm_service": {
        "provider": "deepseek",  # 默认LLM提供商
        "model": "deepseek-chat",
    }
}

# 测试用例列表
TEST_CASES = [
    {
        "id": "TC001",
        "description": "基础旅游需求 - 明确目的地、时间和人数",
        "preconditions": [
            "前端Web页面可访问",
            "后端API服务正常运行",
            "数据库连接正常"
        ],
        "input_text": "我想在2026年5月1日到5月5日和家人去三亚旅游，2个大人1个小孩，共3人，住4晚，希望住海景房。",
        "expected_json": {
            "base_info": {
                "origin": {
                    "name": "未知",  # 输入中未明确出发地
                    "code": "",
                    "type": ""
                },
                "destination_cities": ["三亚"],
                "trip_days": 5,
                "group_size": {
                    "adults": 2,
                    "children": 1,
                    "seniors": 0,
                    "total": 3
                },
                "travel_date": {
                    "start_date": "2026-05-01",
                    "end_date": "2026-05-05",
                    "is_flexible": False
                }
            },
            "preferences": {
                "transportation": {
                    "type": "",
                    "notes": ""
                },
                "accommodation": {
                    "level": "",
                    "requirements": "希望住海景房"
                },
                "itinerary": {
                    "rhythm": "",
                    "tags": [],
                    "special_constraints": {
                        "must_visit_spots": [],
                        "avoid_activities": []
                    }
                }
            },
            "budget": {
                "level": "",
                "currency": "CNY",
                "range": {
                    "min": None,
                    "max": None
                },
                "budget_notes": ""
            }
        },
        "expected_db_result": {
            "origin_name": "未知",
            "destination_cities": ["三亚"],
            "trip_days": 5,
            "group_adults": 2,
            "group_children": 1,
            "group_seniors": 0,
            "group_total": 3,
            "travel_start_date": "2026-05-01",
            "travel_end_date": "2026-05-05",
            "travel_date_flexible": False,
            "hotel_requirements": "希望住海景房"
        }
    },
    {
        "id": "TC002",
        "description": "包含特定活动偏好的旅游需求",
        "preconditions": [
            "前端Web页面可访问",
            "后端API服务正常运行",
            "数据库连接正常"
        ],
        "input_text": "我计划在端午节期间和朋友去杭州玩3天，2个人，喜欢爬山和品尝当地美食，希望住西湖附近的酒店。",
        "expected_json": {
            "base_info": {
                "origin": {
                    "name": "未知",
                    "code": "",
                    "type": ""
                },
                "destination_cities": ["杭州"],
                "trip_days": 3,
                "group_size": {
                    "adults": 2,
                    "children": 0,
                    "seniors": 0,
                    "total": 2
                },
                "travel_date": {
                    "start_date": None,  # 输入中只提到端午节期间，未明确具体日期
                    "end_date": None,
                    "is_flexible": True
                }
            },
            "preferences": {
                "transportation": {
                    "type": "",
                    "notes": ""
                },
                "accommodation": {
                    "level": "",
                    "requirements": "希望住西湖附近的酒店"
                },
                "itinerary": {
                    "rhythm": "",
                    "tags": ["爬山", "美食"],
                    "special_constraints": {
                        "must_visit_spots": [],
                        "avoid_activities": []
                    }
                }
            },
            "budget": {
                "level": "",
                "currency": "CNY",
                "range": {
                    "min": None,
                    "max": None
                },
                "budget_notes": ""
            }
        },
        "expected_db_result": {
            "origin_name": "未知",
            "destination_cities": ["杭州"],
            "trip_days": 3,
            "group_adults": 2,
            "group_children": 0,
            "group_seniors": 0,
            "group_total": 2,
            "travel_date_flexible": True,
            "hotel_requirements": "希望住西湖附近的酒店",
            "preference_tags": ["爬山", "美食"]
        }
    },
    {
        "id": "TC003",
        "description": "包含预算限制的旅游需求",
        "preconditions": [
            "前端Web页面可访问",
            "后端API服务正常运行",
            "数据库连接正常"
        ],
        "input_text": "我想在国庆节期间和女朋友去成都旅游，2个人，住5天，预算8000元左右，希望住舒适型酒店，交通方便。",
        "expected_json": {
            "base_info": {
                "origin": {
                    "name": "未知",
                    "code": "",
                    "type": ""
                },
                "destination_cities": ["成都"],
                "trip_days": 5,
                "group_size": {
                    "adults": 2,
                    "children": 0,
                    "seniors": 0,
                    "total": 2
                },
                "travel_date": {
                    "start_date": None,  # 输入中只提到国庆节期间，未明确具体日期
                    "end_date": None,
                    "is_flexible": True
                }
            },
            "preferences": {
                "transportation": {
                    "type": "",
                    "notes": "交通方便"
                },
                "accommodation": {
                    "level": "Comfort",  # 舒适型酒店
                    "requirements": ""
                },
                "itinerary": {
                    "rhythm": "",
                    "tags": [],
                    "special_constraints": {
                        "must_visit_spots": [],
                        "avoid_activities": []
                    }
                }
            },
            "budget": {
                "level": "",
                "currency": "CNY",
                "range": {
                    "min": 7000,  # 预算8000元左右，设置合理范围
                    "max": 9000
                },
                "budget_notes": ""
            }
        },
        "expected_db_result": {
            "origin_name": "未知",
            "destination_cities": ["成都"],
            "trip_days": 5,
            "group_adults": 2,
            "group_children": 0,
            "group_seniors": 0,
            "group_total": 2,
            "travel_date_flexible": True,
            "transportation_notes": "交通方便",
            "hotel_level": "Comfort",
            "budget_currency": "CNY",
            "budget_min": 7000,
            "budget_max": 9000
        }
    },
    {
        "id": "TC004",
        "description": "包含特殊要求的旅游需求",
        "preconditions": [
            "前端Web页面可访问",
            "后端API服务正常运行",
            "数据库连接正常"
        ],
        "input_text": "我和父母计划在2026年10月1日到10月7日去北京旅游，3个人，父亲需要轮椅，有饮食禁忌不能吃辣，希望住有电梯的酒店，预算20000元。",
        "expected_json": {
            "base_info": {
                "origin": {
                    "name": "未知",
                    "code": "",
                    "type": ""
                },
                "destination_cities": ["北京"],
                "trip_days": 7,
                "group_size": {
                    "adults": 2,  # 父母和我
                    "children": 0,
                    "seniors": 1,  # 父母为老人
                    "total": 3
                },
                "travel_date": {
                    "start_date": "2026-10-01",
                    "end_date": "2026-10-07",
                    "is_flexible": False
                }
            },
            "preferences": {
                "transportation": {
                    "type": "",
                    "notes": ""
                },
                "accommodation": {
                    "level": "",
                    "requirements": "希望住有电梯的酒店"
                },
                "itinerary": {
                    "rhythm": "",
                    "tags": [],
                    "special_constraints": {
                        "must_visit_spots": [],
                        "avoid_activities": ["辣食"]
                    }
                }
            },
            "budget": {
                "level": "",
                "currency": "CNY",
                "range": {
                    "min": 18000,  # 预算20000元，设置合理范围
                    "max": 22000
                },
                "budget_notes": ""
            },
            "extension": {
                "special_needs": ["轮椅", "饮食禁忌"]
            }
        },
        "expected_db_result": {
            "origin_name": "未知",
            "destination_cities": ["北京"],
            "trip_days": 7,
            "group_adults": 2,
            "group_children": 0,
            "group_seniors": 1,
            "group_total": 3,
            "travel_start_date": "2026-10-01",
            "travel_end_date": "2026-10-07",
            "travel_date_flexible": False,
            "hotel_requirements": "希望住有电梯的酒店",
            "budget_currency": "CNY",
            "budget_min": 18000,
            "budget_max": 22000,
            "extension": {
                "special_needs": ["轮椅", "饮食禁忌"]
            }
        }
    }
]

# 验证函数
def validate_json_structure(actual_json, expected_json):
    """
    验证JSON数据结构是否符合预期
    
    Args:
        actual_json (dict): 实际生成的JSON数据
        expected_json (dict): 预期的JSON数据
    
    Returns:
        bool: 验证是否通过
        list: 验证失败的原因
    """
    errors = []
    
    # 检查必要的顶级字段
    required_fields = ["base_info", "preferences", "budget"]
    for field in required_fields:
        if field not in actual_json:
            errors.append(f"缺少必要字段: {field}")
    
    # 检查base_info字段
    if "base_info" in actual_json:
        base_info = actual_json["base_info"]
        if "destination_cities" not in base_info:
            errors.append("缺少destination_cities字段")
        if "trip_days" not in base_info:
            errors.append("缺少trip_days字段")
        if "group_size" not in base_info:
            errors.append("缺少group_size字段")
        elif "total" not in base_info["group_size"]:
            errors.append("缺少group_size.total字段")
    
    # 检查preferences字段
    if "preferences" in actual_json:
        preferences = actual_json["preferences"]
        if "accommodation" not in preferences:
            errors.append("缺少preferences.accommodation字段")
        if "itinerary" not in preferences:
            errors.append("缺少preferences.itinerary字段")
    
    # 检查budget字段
    if "budget" in actual_json:
        budget = actual_json["budget"]
        if "currency" not in budget:
            errors.append("缺少budget.currency字段")
        if "range" not in budget:
            errors.append("缺少budget.range字段")
    
    return len(errors) == 0, errors

def validate_json_content(actual_json, expected_json):
    """
    验证JSON数据内容是否符合预期
    
    Args:
        actual_json (dict): 实际生成的JSON数据
        expected_json (dict): 预期的JSON数据
    
    Returns:
        bool: 验证是否通过
        list: 验证失败的原因
    """
    errors = []
    
    # 检查destination_cities
    if "base_info" in actual_json and "destination_cities" in actual_json["base_info"]:
        actual_cities = actual_json["base_info"]["destination_cities"]
        expected_cities = expected_json["base_info"]["destination_cities"]
        
        # 提取城市名称进行比较
        if isinstance(actual_cities, list) and isinstance(expected_cities, list):
            # 处理实际数据可能是字典列表的情况
            actual_city_names = []
            for city in actual_cities:
                if isinstance(city, dict) and "name" in city:
                    actual_city_names.append(city["name"])
                elif isinstance(city, str):
                    actual_city_names.append(city)
            
            # 处理预期数据可能是字符串列表的情况
            expected_city_names = []
            for city in expected_cities:
                if isinstance(city, str):
                    expected_city_names.append(city)
            
            if not set(actual_city_names).issubset(set(expected_city_names)):
                errors.append(f"目的地城市不匹配: 实际={actual_city_names}, 预期={expected_city_names}")
    
    # 检查trip_days
    if "base_info" in actual_json and "trip_days" in actual_json["base_info"]:
        actual_days = actual_json["base_info"]["trip_days"]
        expected_days = expected_json["base_info"]["trip_days"]
        if actual_days != expected_days:
            errors.append(f"出行天数不匹配: 实际={actual_days}, 预期={expected_days}")
    
    # 检查group_size.total
    if "base_info" in actual_json and "group_size" in actual_json["base_info"] and "total" in actual_json["base_info"]["group_size"]:
        actual_total = actual_json["base_info"]["group_size"]["total"]
        expected_total = expected_json["base_info"]["group_size"]["total"]
        if actual_total != expected_total:
            errors.append(f"总人数不匹配: 实际={actual_total}, 预期={expected_total}")
    
    # 检查特殊要求
    if "extension" in actual_json and "special_needs" in actual_json["extension"]:
        actual_needs = actual_json["extension"]["special_needs"]
        if "extension" in expected_json and "special_needs" in expected_json["extension"]:
            expected_needs = expected_json["extension"]["special_needs"]
            for need in expected_needs:
                if need not in actual_needs:
                    errors.append(f"缺少特殊要求: {need}")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    # 打印测试环境信息
    print("\n=== 测试环境信息 ===")
    print(json.dumps(TEST_ENVIRONMENT, indent=2, ensure_ascii=False))
    
    # 打印测试用例
    print("\n=== 测试用例 ===")
    for test_case in TEST_CASES:
        print(f"\n测试用例ID: {test_case['id']}")
        print(f"描述: {test_case['description']}")
        print(f"输入文本: {test_case['input_text']}")
        print(f"预期JSON: {json.dumps(test_case['expected_json'], indent=2, ensure_ascii=False)}")
