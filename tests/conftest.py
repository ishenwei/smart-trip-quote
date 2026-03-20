"""
pytest 配置文件
提供共享的 fixtures 和配置
"""
import os
import sys
import pytest
from datetime import date, time

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


@pytest.fixture(scope='session')
def django_db_setup(django_db_blocker):
    """配置数据库测试环境"""
    pass


@pytest.fixture
def db(django_db_blocker):
    """启用数据库访问"""
    with django_db_blocker.unblock():
        yield


@pytest.fixture
def sample_requirement_data():
    """样例需求数据"""
    return {
        "requirement_id": "TEST_REQ_001",
        "origin": {
            "name": "北京",
            "code": "BJS",
            "type": "city"
        },
        "destination_cities": [
            {"name": "上海", "code": "SHA", "type": "city"}
        ],
        "trip_days": 3,
        "group_size": {
            "adults": 2,
            "children": 1,
            "seniors": 0,
            "total": 3
        },
        "travel_date": {
            "start_date": "2026-04-01",
            "end_date": "2026-04-03",
            "is_flexible": False
        }
    }


@pytest.fixture
def sample_itinerary_data():
    """样例行程数据"""
    return {
        "requirement_id": "TEST_REQ_001",
        "itinerary_name": "测试行程",
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
            "total_travelers": 3,
            "adults": 2,
            "children": 1,
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
                        "activity_description": "乘坐航班抵达上海"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def fixtures_path():
    """返回 fixtures 目录路径"""
    return os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def excel_files(fixtures_path):
    """返回所有 Excel 测试数据文件"""
    excel_dir = fixtures_path
    if not os.path.exists(excel_dir):
        return []
    return [f for f in os.listdir(excel_dir) if f.endswith('.xlsx')]
