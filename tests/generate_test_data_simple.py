import random
import uuid
from datetime import time
import os
import sys

# Add Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    import django
    django.setup()
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc

from django.db.utils import IntegrityError

# 从Django模型导入
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant

# 中国知名旅游城市列表
CHINESE_CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆", "西安", "厦门",
    "青岛", "大连", "三亚", "丽江", "大理", "昆明", "桂林", "阳朔", "张家界", "黄山"
]

# 各城市对应的知名景点
CITY_ATTRACTIONS = {
    "北京": ["故宫博物院", "长城", "颐和园", "天坛", "天安门广场"],
    "上海": ["外滩", "东方明珠", "迪士尼乐园", "南京路", "豫园"],
    "广州": ["白云山", "陈家祠", "广州塔", "越秀公园", "中山纪念堂"],
    "深圳": ["世界之窗", "欢乐谷", "东部华侨城", "大梅沙", "小梅沙"],
    "杭州": ["西湖", "灵隐寺", "千岛湖", "西溪湿地", "宋城"],
    "南京": ["中山陵", "明孝陵", "夫子庙", "总统府", "玄武湖"],
    "成都": ["大熊猫繁育研究基地", "都江堰", "青城山", "武侯祠", "锦里"],
    "重庆": ["洪崖洞", "解放碑", "长江索道", "武隆天坑", "大足石刻"],
    "西安": ["兵马俑", "大雁塔", "城墙", "华清池", "陕西历史博物馆"],
    "厦门": ["鼓浪屿", "厦门大学", "环岛路", "南普陀寺", "曾厝垵"]
}

# 生成景点数据
def generate_attractions():
    print("生成景点数据...")
    categories = ["NATURAL", "HISTORICAL", "CULTURAL", "RELIGIOUS", "MODERN"]
    
    for i in range(100):
        try:
            city = random.choice(CHINESE_CITIES)
            
            # 优先选择城市对应的知名景点
            if city in CITY_ATTRACTIONS:
                attraction_name = random.choice(CITY_ATTRACTIONS[city])
            else:
                attraction_name = f"{city}景点{i+1}"
            
            attraction = Attraction(
                attraction_id=uuid.uuid4(),
                attraction_code=f"ATTR_{city[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                attraction_name=attraction_name,
                country_code="CN",
                city_name=city,
                address=f"{city}市某某路{i+1}号",
                category=random.choice(categories),
                description=f"{attraction_name}是{city}的著名景点",
                ticket_price=round(random.uniform(0, 200), 2),
                currency="CNY",
                status="ACTIVE"
            )
            attraction.save()
            if (i+1) % 10 == 0:
                print(f"已生成{i+1}个景点")
        except IntegrityError:
            continue

# 生成酒店数据
def generate_hotels():
    print("生成酒店数据...")
    hotel_types = ["LUXURY", "BUSINESS", "RESORT", "BOUTIQUE", "HOMESTAY"]
    brands = ["万豪", "希尔顿", "洲际", "喜来登", "香格里拉"]
    
    for i in range(100):
        try:
            city = random.choice(CHINESE_CITIES)
            hotel_type = random.choice(hotel_types)
            
            if hotel_type == "LUXURY":
                hotel_name = f"{city}{random.choice(brands)}酒店"
            else:
                hotel_name = f"{city}{random.choice(['商务', '精品', '度假', '民宿'])}酒店{i+1}"
            
            min_price = round(random.uniform(100, 800), 2)
            
            hotel = Hotel(
                hotel_id=uuid.uuid4(),
                hotel_code=f"HOTEL_{city[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                hotel_name=hotel_name,
                country_code="CN",
                city_name=city,
                address=f"{city}市某某路{i+1}号",
                hotel_type=hotel_type,
                min_price=min_price,
                max_price=round(min_price + random.uniform(200, 1000), 2),
                currency="CNY",
                status="ACTIVE"
            )
            hotel.save()
            if (i+1) % 10 == 0:
                print(f"已生成{i+1}个酒店")
        except IntegrityError:
            continue

# 生成餐厅数据
def generate_restaurants():
    print("生成餐厅数据...")
    cuisines = ["川菜", "粤菜", "鲁菜", "苏菜", "浙菜", "闽菜", "湘菜", "徽菜", "西餐", "日料"]
    restaurant_types = ["FINE_DINING", "CASUAL", "FAST_FOOD", "CAFE", "BAR"]
    
    for i in range(100):
        try:
            city = random.choice(CHINESE_CITIES)
            cuisine = random.choice(cuisines)
            restaurant_type = random.choice(restaurant_types)
            
            restaurant_name = f"{city}{random.choice(['美食', '餐厅', '小馆', '饭店', '食堂'])}{i+1}"
            
            restaurant = Restaurant(
                restaurant_id=uuid.uuid4(),
                restaurant_code=f"REST_{city[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                restaurant_name=restaurant_name,
                country_code="CN",
                city_name=city,
                address=f"{city}市某某路{i+1}号",
                cuisine_type=cuisine,
                restaurant_type=restaurant_type,
                price_range=random.choice(["$", "$$", "$$$", "$$$$"]),
                avg_price_per_person=round(random.uniform(30, 300), 2),
                status="ACTIVE"
            )
            restaurant.save()
            if (i+1) % 10 == 0:
                print(f"已生成{i+1}个餐厅")
        except IntegrityError:
            continue

# 执行生成数据
if __name__ == "__main__":
    print("开始生成测试数据...")
    generate_attractions()
    generate_hotels()
    generate_restaurants()
    print("测试数据生成完成！")
