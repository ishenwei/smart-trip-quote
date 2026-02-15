import os
import django
import uuid

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant

# 生成测试数据
def generate_test_data():
    print("开始生成测试数据...")
    
    # 生成景点数据
    attractions = [
        {"id": "550e8400-e29b-41d4-a716-446655440001", "name": "浅草寺", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440002", "name": "东京塔", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440003", "name": "明治神宫", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440004", "name": "涩谷十字路口", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440005", "name": "大阪城", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440006", "name": "环球影城", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440007", "name": "道顿堀", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440008", "name": "心斋桥", "city": "大阪"},
    ]
    
    for attr in attractions:
        try:
            attraction = Attraction(
                attraction_id=uuid.UUID(attr["id"]),
                attraction_code=f"ATTR_{attr['city'][:2].upper()}_{attr['id'][-8:]}",
                attraction_name=attr["name"],
                country_code="JP",
                city_name=attr["city"],
                address=f"{attr['city']}市{attr['name']}附近",
                category="CULTURAL",
                status="ACTIVE"
            )
            attraction.save()
            print(f"创建景点: {attr['name']}")
        except Exception as e:
            print(f"创建景点失败 {attr['name']}: {e}")
    
    # 生成酒店数据
    hotels = [
        {"id": "550e8400-e29b-41d4-a716-446655440021", "name": "东京丽思卡尔顿酒店", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440022", "name": "大阪威斯汀酒店", "city": "大阪"},
    ]
    
    for hotel in hotels:
        try:
            hotel_obj = Hotel(
                hotel_id=uuid.UUID(hotel["id"]),
                hotel_code=f"HOTEL_{hotel['city'][:2].upper()}_{hotel['id'][-8:]}",
                hotel_name=hotel["name"],
                country_code="JP",
                city_name=hotel["city"],
                address=f"{hotel['city']}市{hotel['name']}附近",
                hotel_star=5,
                hotel_type="LUXURY",
                status="ACTIVE"
            )
            hotel_obj.save()
            print(f"创建酒店: {hotel['name']}")
        except Exception as e:
            print(f"创建酒店失败 {hotel['name']}: {e}")
    
    # 生成餐厅数据
    restaurants = [
        {"id": "550e8400-e29b-41d4-a716-446655440011", "name": "寿司大", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440012", "name": "六本木寿司", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440013", "name": "筑地市场", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440014", "name": "新宿烤肉", "city": "东京"},
        {"id": "550e8400-e29b-41d4-a716-446655440015", "name": "大阪烧名店", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440016", "name": "环球影城餐厅", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440017", "name": "道顿堀美食街", "city": "大阪"},
        {"id": "550e8400-e29b-41d4-a716-446655440018", "name": "心斋桥餐厅", "city": "大阪"},
    ]
    
    for restaurant in restaurants:
        try:
            restaurant_obj = Restaurant(
                restaurant_id=uuid.UUID(restaurant["id"]),
                restaurant_code=f"REST_{restaurant['city'][:2].upper()}_{restaurant['id'][-8:]}",
                restaurant_name=restaurant["name"],
                country_code="JP",
                city_name=restaurant["city"],
                address=f"{restaurant['city']}市{restaurant['name']}附近",
                cuisine_type="日料",
                restaurant_type="CASUAL",
                status="ACTIVE"
            )
            restaurant_obj.save()
            print(f"创建餐厅: {restaurant['name']}")
        except Exception as e:
            print(f"创建餐厅失败 {restaurant['name']}: {e}")
    
    print("测试数据生成完成！")

if __name__ == "__main__":
    generate_test_data()
