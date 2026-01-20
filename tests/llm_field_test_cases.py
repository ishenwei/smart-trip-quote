"""
全面的LLM字段识别测试用例
用于系统地验证所有字段的识别功能
"""

TEST_CASES = {
    "base_info": {
        "origin": [
            {
                "name": "标准格式-明确出发地",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "上海"}],
                        "trip_days": 5
                    }
                },
                "description": "用户明确指定出发地为北京"
            },
            {
                "name": "边界值-多个出发地关键词",
                "input": "从广州出发去深圳",
                "expected": {
                    "base_info": {
                        "origin": {"name": "广州", "type": "Domestic"},
                        "destination_cities": [{"name": "深圳"}]
                    }
                },
                "description": "包含多个出发地关键词"
            },
            {
                "name": "错误格式-缺少出发地",
                "input": "去上海旅游5天",
                "expected": {
                    "base_info": {
                        "origin": {"name": "未指定"},
                        "destination_cities": [{"name": "上海"}],
                        "trip_days": 5
                    }
                },
                "description": "缺少出发地信息"
            },
            {
                "name": "特殊字符-包含标点符号",
                "input": "从北京、上海去广州",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "广州"}]
                    }
                },
                "description": "包含中文标点符号"
            },
            {
                "name": "空值-未指定出发地",
                "input": "我想去旅游",
                "expected": {
                    "base_info": {
                        "origin": {"name": "未指定"},
                        "destination_cities": [{"name": "未指定"}]
                    }
                },
                "description": "未指定出发地和目的地"
            }
        ],
        "destination_cities": [
            {
                "name": "标准格式-明确目的地",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "上海"}],
                        "trip_days": 5
                    }
                },
                "description": "用户明确指定目的地为上海"
            },
            {
                "name": "边界值-多个目的地",
                "input": "从北京去上海、杭州、苏州旅游",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [
                            {"name": "上海"},
                            {"name": "杭州"},
                            {"name": "苏州"}
                        ]
                    }
                },
                "description": "用户指定多个目的地"
            },
            {
                "name": "错误格式-缺少目的地",
                "input": "从北京出发旅游5天",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "未指定"}],
                        "trip_days": 5
                    }
                },
                "description": "缺少目的地信息"
            },
            {
                "name": "特殊字符-包含省份",
                "input": "从北京去云南旅游",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "云南"}]
                    }
                },
                "description": "目的地为省份"
            },
            {
                "name": "空值-未指定目的地",
                "input": "从北京出发旅游",
                "expected": {
                    "base_info": {
                        "origin": {"name": "北京", "type": "Domestic"},
                        "destination_cities": [{"name": "未指定"}]
                    }
                },
                "description": "未指定目的地"
            }
        ],
        "trip_days": [
            {
                "name": "标准格式-明确天数",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "base_info": {
                        "trip_days": 5
                    }
                },
                "description": "用户明确指定5天"
            },
            {
                "name": "边界值-最小天数",
                "input": "从北京去上海旅游1天",
                "expected": {
                    "base_info": {
                        "trip_days": 1
                    }
                },
                "description": "最小有效天数"
            },
            {
                "name": "边界值-最大天数",
                "input": "从北京去上海旅游365天",
                "expected": {
                    "base_info": {
                        "trip_days": 365
                    }
                },
                "description": "最大有效天数"
            },
            {
                "name": "错误格式-超出范围",
                "input": "从北京去上海旅游400天",
                "expected": {
                    "error": "trip_days必须是1-365之间的整数"
                },
                "description": "天数超出有效范围"
            },
            {
                "name": "特殊格式-使用日",
                "input": "从北京去上海旅游7日",
                "expected": {
                    "base_info": {
                        "trip_days": 7
                    }
                },
                "description": "使用'日'代替'天'"
            },
            {
                "name": "空值-未指定天数",
                "input": "从北京去上海旅游",
                "expected": {
                    "error": "Error: 抱歉，您必须提供旅行的天数"
                },
                "description": "未指定旅行天数"
            },
            {
                "name": "边界值-天数为0",
                "input": "从北京去上海旅游0天",
                "expected": {
                    "error": "trip_days必须是1-365之间的整数"
                },
                "description": "天数为0"
            }
        ],
        "group_size": [
            {
                "name": "标准格式-明确人数",
                "input": "从北京去上海旅游5天，2个成人",
                "expected": {
                    "base_info": {
                        "group_size": {"adults": 2, "children": 0, "seniors": 0, "total": 2}
                    }
                },
                "description": "用户明确指定2个成人"
            },
            {
                "name": "边界值-包含儿童和老人",
                "input": "从北京去上海旅游5天，2个成人，1个儿童，1个老人",
                "expected": {
                    "base_info": {
                        "group_size": {"adults": 2, "children": 1, "seniors": 1, "total": 4}
                    }
                },
                "description": "包含不同年龄段的人数"
            },
            {
                "name": "错误格式-人数为0",
                "input": "从北京去上海旅游5天，0个人",
                "expected": {
                    "error": "group_size.total必须是>=1的整数"
                },
                "description": "总人数为0"
            },
            {
                "name": "特殊格式-使用人",
                "input": "从北京去上海旅游5天，3个人",
                "expected": {
                    "base_info": {
                        "group_size": {"total": 3}
                    }
                },
                "description": "使用'人'代替具体年龄段"
            },
            {
                "name": "空值-未指定人数",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "base_info": {
                        "group_size": {"total": 1}
                    }
                },
                "description": "未指定人数，默认为1"
            }
        ],
        "travel_date": [
            {
                "name": "标准格式-明确日期",
                "input": "从北京去上海旅游5天，2025-03-20出发",
                "expected": {
                    "base_info": {
                        "travel_date": {"start_date": "2025-03-20", "is_flexible": False}
                    }
                },
                "description": "用户明确指定出发日期"
            },
            {
                "name": "边界值-日期范围",
                "input": "从北京去上海旅游5天，2025-03-20到2025-03-25",
                "expected": {
                    "base_info": {
                        "travel_date": {"start_date": "2025-03-20", "end_date": "2025-03-25", "is_flexible": False}
                    }
                },
                "description": "用户指定日期范围"
            },
            {
                "name": "错误格式-日期格式错误",
                "input": "从北京去上海旅游5天，2025年3月20日出发",
                "expected": {
                    "base_info": {
                        "travel_date": {"start_date": None, "is_flexible": True}
                    }
                },
                "description": "日期格式不标准"
            },
            {
                "name": "特殊格式-灵活日期",
                "input": "从北京去上海旅游5天，时间灵活",
                "expected": {
                    "base_info": {
                        "travel_date": {"start_date": None, "end_date": None, "is_flexible": True}
                    }
                },
                "description": "用户表示日期灵活"
            },
            {
                "name": "空值-未指定日期",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "base_info": {
                        "travel_date": {"start_date": None, "end_date": None, "is_flexible": True}
                    }
                },
                "description": "未指定日期，默认灵活"
            }
        ]
    },
    "preferences": {
        "transportation": [
            {
                "name": "标准格式-飞机",
                "input": "从北京去上海旅游5天，坐飞机",
                "expected": {
                    "preferences": {
                        "transportation": {"type": "RoundTripFlight"}
                    }
                },
                "description": "用户指定飞机出行"
            },
            {
                "name": "边界值-高铁",
                "input": "从北京去上海旅游5天，坐高铁",
                "expected": {
                    "preferences": {
                        "transportation": {"type": "HighSpeedTrain"}
                    }
                },
                "description": "用户指定高铁出行"
            },
            {
                "name": "错误格式-无效交通方式",
                "input": "从北京去上海旅游5天，坐火箭",
                "expected": {
                    "preferences": {
                        "transportation": {"type": None}
                    }
                },
                "description": "指定了无效的交通方式"
            },
            {
                "name": "特殊格式-自驾",
                "input": "从北京去上海旅游5天，自驾",
                "expected": {
                    "preferences": {
                        "transportation": {"type": "SelfDriving"}
                    }
                },
                "description": "用户指定自驾"
            },
            {
                "name": "空值-未指定交通方式",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "preferences": {
                        "transportation": {"type": None}
                    }
                },
                "description": "未指定交通方式"
            }
        ],
        "accommodation": [
            {
                "name": "标准格式-舒适型",
                "input": "从北京去上海旅游5天，舒适型酒店",
                "expected": {
                    "preferences": {
                        "accommodation": {"level": "Comfort"}
                    }
                },
                "description": "用户指定舒适型酒店"
            },
            {
                "name": "边界值-豪华型",
                "input": "从北京去上海旅游5天，豪华酒店",
                "expected": {
                    "preferences": {
                        "accommodation": {"level": "Luxury"}
                    }
                },
                "description": "用户指定豪华型酒店"
            },
            {
                "name": "错误格式-无效等级",
                "input": "从北京去上海旅游5天，超级豪华酒店",
                "expected": {
                    "preferences": {
                        "accommodation": {"level": None}
                    }
                },
                "description": "指定了无效的酒店等级"
            },
            {
                "name": "特殊格式-经济型",
                "input": "从北京去上海旅游5天，经济型酒店",
                "expected": {
                    "preferences": {
                        "accommodation": {"level": "Economy"}
                    }
                },
                "description": "用户指定经济型酒店"
            },
            {
                "name": "空值-未指定酒店等级",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "preferences": {
                        "accommodation": {"level": "Comfort"}
                    }
                },
                "description": "未指定酒店等级，默认为Comfort"
            }
        ],
        "itinerary": [
            {
                "name": "标准格式-适中节奏",
                "input": "从北京去上海旅游5天，行程适中",
                "expected": {
                    "preferences": {
                        "itinerary": {"rhythm": "Moderate"}
                    }
                },
                "description": "用户指定适中节奏"
            },
            {
                "name": "边界值-轻松节奏",
                "input": "从北京去上海旅游5天，行程轻松",
                "expected": {
                    "preferences": {
                        "itinerary": {"rhythm": "Relaxed"}
                    }
                },
                "description": "用户指定轻松节奏"
            },
            {
                "name": "错误格式-无效节奏",
                "input": "从北京去上海旅游5天，行程超级快",
                "expected": {
                    "preferences": {
                        "itinerary": {"rhythm": None}
                    }
                },
                "description": "指定了无效的行程节奏"
            },
            {
                "name": "特殊格式-紧凑节奏",
                "input": "从北京去上海旅游5天，行程紧凑",
                "expected": {
                    "preferences": {
                        "itinerary": {"rhythm": "Intense"}
                    }
                },
                "description": "用户指定紧凑节奏"
            },
            {
                "name": "空值-未指定节奏",
                "input": "从北京去上海旅游5天",
                "expected": {
                    "preferences": {
                        "itinerary": {"rhythm": "Moderate"}
                    }
                },
                "description": "未指定行程节奏，默认为Moderate"
            }
        ]
    },
    "budget": [
        {
            "name": "标准格式-预算范围",
            "input": "从北京去上海旅游5天，预算5000到10000元",
            "expected": {
                "budget": {"level": "Comfort", "currency": "CNY", "range": {"min": 5000, "max": 10000}}
            },
            "description": "用户指定预算范围"
        },
        {
            "name": "边界值-低预算",
            "input": "从北京去上海旅游5天，预算1500元",
            "expected": {
                "budget": {"level": "Economy", "currency": "CNY", "range": {"min": None, "max": 1500}}
            },
            "description": "预算低于2000元，推断为Economy"
        },
        {
            "name": "边界值-高预算",
            "input": "从北京去上海旅游5天，预算15000元",
            "expected": {
                "budget": {"level": "Luxury", "currency": "CNY", "range": {"min": None, "max": 15000}}
            },
            "description": "预算高于10000元，推断为Luxury"
        },
        {
            "name": "错误格式-无效货币",
            "input": "从北京去上海旅游5天，预算5000美元",
            "expected": {
                "budget": {"level": "Comfort", "currency": "USD", "range": {"min": None, "max": 5000}}
            },
            "description": "使用美元作为货币"
        },
        {
            "name": "特殊格式-预算等级",
            "input": "从北京去上海旅游5天，预算高一些",
            "expected": {
                "budget": {"level": "HighEnd", "currency": "CNY"}
            },
            "description": "用户指定预算等级"
        },
        {
            "name": "空值-未指定预算",
            "input": "从北京去上海旅游5天",
            "expected": {
                "budget": {"level": "Comfort", "currency": "CNY"}
            },
            "description": "未指定预算，默认为Comfort"
        }
    ],
    "combined": [
        {
            "name": "完整场景-所有字段",
            "input": "从北京去上海旅游5天，2个成人，坐飞机，舒适型酒店，行程适中，预算5000到10000元",
            "expected": {
                "base_info": {
                    "origin": {"name": "北京", "type": "Domestic"},
                    "destination_cities": [{"name": "上海"}],
                    "trip_days": 5,
                    "group_size": {"adults": 2, "children": 0, "seniors": 0, "total": 2},
                    "travel_date": {"start_date": None, "is_flexible": True}
                },
                "preferences": {
                    "transportation": {"type": "RoundTripFlight"},
                    "accommodation": {"level": "Comfort"},
                    "itinerary": {"rhythm": "Moderate"}
                },
                "budget": {"level": "Comfort", "currency": "CNY", "range": {"min": 5000, "max": 10000}}
            },
            "description": "用户指定所有字段"
        },
        {
            "name": "复杂场景-多目的地多人数",
            "input": "从广州出发去上海、杭州、苏州旅游7天，3个成人，2个儿童，1个老人，高铁，豪华酒店，行程轻松，预算20000元",
            "expected": {
                "base_info": {
                    "origin": {"name": "广州", "type": "Domestic"},
                    "destination_cities": [
                        {"name": "上海"},
                        {"name": "杭州"},
                        {"name": "苏州"}
                    ],
                    "trip_days": 7,
                    "group_size": {"adults": 3, "children": 2, "seniors": 1, "total": 6}
                },
                "preferences": {
                    "transportation": {"type": "HighSpeedTrain"},
                    "accommodation": {"level": "Luxury"},
                    "itinerary": {"rhythm": "Relaxed"}
                },
                "budget": {"level": "Luxury", "currency": "CNY", "range": {"min": None, "max": 20000}}
            },
            "description": "复杂场景包含多个目的地和人数"
        },
        {
            "name": "边界场景-最小有效输入",
            "input": "从北京去上海旅游1天",
            "expected": {
                "base_info": {
                    "origin": {"name": "北京", "type": "Domestic"},
                    "destination_cities": [{"name": "上海"}],
                    "trip_days": 1,
                    "group_size": {"total": 1},
                    "travel_date": {"start_date": None, "is_flexible": True}
                },
                "preferences": {
                    "accommodation": {"level": "Comfort"},
                    "itinerary": {"rhythm": "Moderate"}
                },
                "budget": {"level": "Comfort", "currency": "CNY"}
            },
            "description": "最小有效输入"
        }
    ]
}

PASS_CRITERIA = {
    "success": "测试成功，结果符合预期",
    "partial": "部分成功，部分字段符合预期",
    "failed": "测试失败，结果不符合预期"
}

ERROR_TYPES = {
    "extraction_error": "数据提取错误",
    "validation_error": "数据验证错误",
    "normalization_error": "数据规范化错误",
    "parsing_error": "数据解析错误",
    "default_value_error": "默认值应用错误"
}
