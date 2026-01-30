import os
import random
import uuid
from datetime import time
from django.db.utils import IntegrityError

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# 从Django模型导入
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant

# 中国知名旅游城市列表
CHINESE_CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "重庆", "西安", "厦门",
    "青岛", "大连", "三亚", "丽江", "大理", "昆明", "桂林", "阳朔", "张家界", "黄山",
    "庐山", "泰山", "衡山", "华山", "恒山", "嵩山", "五台山", "普陀山", "九华山", "峨眉山"
]

# 各城市对应的知名景点
CITY_ATTRACTIONS = {
    "北京": ["故宫博物院", "长城", "颐和园", "天坛", "天安门广场", "圆明园", "景山公园", "北海公园", "恭王府", "雍和宫"],
    "上海": ["外滩", "东方明珠", "迪士尼乐园", "南京路", "豫园", "静安寺", "陆家嘴", "世纪公园", "上海博物馆", "野生动物园"],
    "广州": ["白云山", "陈家祠", "广州塔", "越秀公园", "中山纪念堂", "黄埔军校", "华南植物园", "莲花山", "沙面", "北京路"],
    "深圳": ["世界之窗", "欢乐谷", "东部华侨城", "大梅沙", "小梅沙", "红树林", "莲花山", "深圳湾公园", "梧桐山", "仙湖植物园"],
    "杭州": ["西湖", "灵隐寺", "千岛湖", "西溪湿地", "宋城", "六和塔", "雷峰塔", "孤山", "九溪烟树", "龙井村"],
    "南京": ["中山陵", "明孝陵", "夫子庙", "总统府", "玄武湖", "鸡鸣寺", "雨花台", "栖霞山", "牛首山", "莫愁湖"],
    "成都": ["大熊猫繁育研究基地", "都江堰", "青城山", "武侯祠", "锦里", "宽窄巷子", "春熙路", "杜甫草堂", "青羊宫", "金沙遗址"],
    "重庆": ["洪崖洞", "解放碑", "长江索道", "武隆天坑", "大足石刻", "磁器口古镇", "南山一棵树", "鹅岭公园", "三峡博物馆", "人民大礼堂"],
    "西安": ["兵马俑", "大雁塔", "城墙", "华清池", "陕西历史博物馆", "回民街", "小雁塔", "大唐芙蓉园", "大明宫", "翠华山"],
    "厦门": ["鼓浪屿", "厦门大学", "环岛路", "南普陀寺", "曾厝垵", "胡里山炮台", "集美鳌园", "万石植物园", "中山路", "沙坡尾"],
    "青岛": ["栈桥", "崂山", "八大关", "五四广场", "奥帆中心", "海底世界", "极地海洋世界", "石老人海滩", "信号山", "小鱼山"],
    "大连": ["星海广场", "金石滩", "老虎滩海洋公园", "圣亚海洋世界", "棒棰岛", "付家庄海滩", "大连森林动物园", "旅顺军港", "大连博物馆", "劳动公园"],
    "三亚": ["亚龙湾", "蜈支洲岛", "天涯海角", "南山文化旅游区", "大小洞天", "鹿回头", "大东海", "三亚湾", "海棠湾", "西岛"],
    "丽江": ["丽江古城", "玉龙雪山", "束河古镇", "黑龙潭", "木府", "拉市海", "虎跳峡", "老君山", "白沙古镇", "蓝月谷"],
    "大理": ["大理古城", "洱海", "苍山", "崇圣寺三塔", "双廊", "喜洲古镇", "蝴蝶泉", "南诏风情岛", "天龙八部影视城", "鸡足山"],
    "昆明": ["滇池", "石林", "世博园", "金殿", "翠湖", "云南民族村", "西山", "圆通寺", "大观楼", "九乡溶洞"],
    "桂林": ["漓江", "象山", "七星公园", "叠彩山", "伏波山", "芦笛岩", "独秀峰·王城", "两江四湖", "银子岩", "世外桃源"],
    "阳朔": ["西街", "遇龙河", "十里画廊", "相公山", "兴坪古镇", "蝴蝶泉", "图腾古道", "聚龙潭", "大榕树", "月亮山"],
    "张家界": ["天门山", "武陵源", "大峡谷", "黄龙洞", "宝峰湖", "袁家界", "天子山", "黄石寨", "金鞭溪", "十里画廊"],
    "黄山": ["黄山风景区", "宏村", "西递", "呈坎", "唐模", "棠樾牌坊群", "鲍家花园", "徽州古城", "屯溪老街", "齐云山"]
}

# 景点类别
ATTRACTION_CATEGORIES = ["NATURAL", "HISTORICAL", "CULTURAL", "RELIGIOUS", "MODERN", "ENTERTAINMENT", "SHOPPING", "OUTDOOR", "INDOOR"]

# 酒店类型
HOTEL_TYPES = ["LUXURY", "BUSINESS", "RESORT", "BOUTIQUE", "HOSTEL", "APARTMENT", "HOMESTAY"]

# 酒店品牌
HOTEL_BRANDS = ["万豪", "希尔顿", "洲际", "喜来登", "香格里拉", "凯悦", "威斯汀", "铂尔曼", "皇冠假日", "雅高"]

# 菜系类型
CUISINE_TYPES = ["川菜", "粤菜", "鲁菜", "苏菜", "浙菜", "闽菜", "湘菜", "徽菜", "东北菜", "西北菜", "云南菜", "贵州菜", "广西菜", "海南菜", "清真菜", "西餐", "日料", "韩料", "泰料", "东南亚菜"]

# 餐厅类型
RESTAURANT_TYPES = ["FINE_DINING", "CASUAL", "FAST_FOOD", "CAFE", "BAR", "STREET_FOOD", "BUFFET"]

# 价格范围
PRICE_RANGES = ["$", "$$", "$$$", "$$$$"]

# 生成景点数据
def generate_attraction_data():
    print("开始生成景点数据...")
    count = 0
    while count < 100:
        try:
            # 随机选择城市
            city = random.choice(CHINESE_CITIES)
            
            # 随机选择景点名称，如果城市在CITY_ATTRACTIONS中，优先选择对应景点
            if city in CITY_ATTRACTIONS and CITY_ATTRACTIONS[city]:
                attraction_name = random.choice(CITY_ATTRACTIONS[city])
            else:
                # 生成随机景点名称
                attraction_name = f"{city}{random.choice(['公园', '博物馆', '风景区', '文化村', '古镇', '山', '湖', '寺', '塔', '广场'])}"
            
            # 生成景点代码
            attraction_code = f"ATTR_{city[:2].upper()}_{str(uuid.uuid4())[:8].upper()}"
            
            # 随机生成其他字段
            category = random.choice(ATTRACTION_CATEGORIES)
            ticket_price = round(random.uniform(0, 300), 2)
            recommended_duration = random.randint(60, 360)
            popularity_score = round(random.uniform(3.0, 5.0), 2)
            visitor_rating = round(random.uniform(3.0, 5.0), 2)
            review_count = random.randint(0, 10000)
            
            # 创建景点对象
            attraction = Attraction(
                attraction_id=uuid.uuid4(),
                attraction_code=attraction_code,
                attraction_name=attraction_name,
                country_code="CN",
                city_name=city,
                region=random.choice(["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区", "门头沟区", "房山区", "通州区", "顺义区"]) if city == "北京" else "",
                address=f"{city}{random.choice(['市', '区'])}{random.choice(['街道', '路', '大道'])} {random.randint(1, 999)}号",
                category=category,
                tags=[category, random.choice(["热门", "推荐", "必游", "打卡", "网红"])],
                description=f"{attraction_name}是{city}著名的{dict(Attraction.ATTRACTION_CATEGORY_CHOICES)[category]}景点，吸引了大量游客前来观光。",
                recommended_duration=recommended_duration,
                opening_hours={"周一至周五": "09:00-17:00", "周六至周日": "08:30-17:30"},
                best_season=["春季", "秋季" if category == "NATURAL" else "全年"],
                ticket_price=ticket_price,
                currency="CNY",
                booking_required=random.choice([True, False]),
                popularity_score=popularity_score,
                visitor_rating=visitor_rating,
                review_count=review_count,
                status="ACTIVE"
            )
            
            attraction.save()
            count += 1
            if count % 10 == 0:
                print(f"已生成{count}条景点数据")
                
        except IntegrityError:
            # 处理唯一约束冲突
            continue

# 生成酒店数据
def generate_hotel_data():
    print("开始生成酒店数据...")
    count = 0
    while count < 100:
        try:
            # 随机选择城市
            city = random.choice(CHINESE_CITIES)
            
            # 随机选择酒店类型
            hotel_type = random.choice(HOTEL_TYPES)
            
            # 生成酒店名称
            if hotel_type == "LUXURY":
                brand = random.choice(HOTEL_BRANDS)
                hotel_name = f"{city}{brand}酒店"
            elif hotel_type == "BUSINESS":
                hotel_name = f"{city}{random.choice(['商务', '快捷', '精品'])}{random.choice(['酒店', '饭店'])}"
            elif hotel_type == "RESORT":
                hotel_name = f"{city}{random.choice(['海景', '山景', '湖景'])}{random.choice(['度假酒店', '度假村'])}"
            elif hotel_type == "BOUTIQUE":
                hotel_name = f"{city}{random.choice(['艺术', '设计', '精品', '特色'])}{random.choice(['酒店', '客栈'])}"
            elif hotel_type == "HOSTEL":
                hotel_name = f"{city}{random.choice(['青年', '背包客', '大学生'])}{random.choice(['旅舍', ' hostel'])}"
            elif hotel_type == "APARTMENT":
                hotel_name = f"{city}{random.choice(['服务式', '精品', '豪华'])}{random.choice(['公寓', '酒店公寓'])}"
            else:  # HOMESTAY
                hotel_name = f"{city}{random.choice(['民宿', '客栈', '雅居', '居舍'])}"
            
            # 生成酒店代码
            hotel_code = f"HOTEL_{city[:2].upper()}_{str(uuid.uuid4())[:8].upper()}"
            
            # 随机生成其他字段
            hotel_star = random.randint(1, 5) if hotel_type in ["LUXURY", "BUSINESS", "RESORT"] else None
            min_price = round(random.uniform(100, 1000), 2)
            max_price = round(min_price + random.uniform(100, 2000), 2)
            price_range = f"{min_price}-{max_price}元"
            popularity_score = round(random.uniform(3.0, 5.0), 2)
            guest_rating = round(random.uniform(3.0, 5.0), 2)
            review_count = random.randint(0, 5000)
            
            # 创建酒店对象
            hotel = Hotel(
                hotel_id=uuid.uuid4(),
                hotel_code=hotel_code,
                hotel_name=hotel_name,
                brand_name=random.choice(HOTEL_BRANDS) if hotel_type == "LUXURY" else "",
                country_code="CN",
                city_name=city,
                district=random.choice(["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区", "门头沟区", "房山区", "通州区", "顺义区"]) if city == "北京" else "",
                address=f"{city}{random.choice(['市', '区'])}{random.choice(['街道', '路', '大道'])} {random.randint(1, 999)}号",
                hotel_star=hotel_star,
                hotel_type=hotel_type,
                tags={"设施": ["免费WiFi", "停车场", "餐厅", "健身房", "游泳池"], "服务": ["24小时前台", "行李寄存", "叫醒服务"]},
                description=f"{hotel_name}是一家位于{city}的{dict(Hotel.HotelType.choices)[hotel_type]}，提供舒适的住宿环境和优质的服务。",
                check_in_time=time(14, 0),
                check_out_time=time(12, 0),
                contact_phone=f"0{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                amenities={"公共设施": ["WiFi", "停车场", "电梯", "会议室", "商务中心"], "休闲设施": ["健身房", "游泳池", "SPA", "酒吧"]},
                room_facilities={"基本设施": ["空调", "电视", "冰箱", "保险箱"], "卫浴设施": ["淋浴", "浴缸", "免费洗漱用品"]},
                room_types={"标准间": min_price, "豪华间": min_price + 200, "套房": min_price + 500},
                price_range=price_range,
                currency="CNY",
                min_price=min_price,
                max_price=max_price,
                popularity_score=popularity_score,
                guest_rating=guest_rating,
                review_count=review_count,
                status="ACTIVE"
            )
            
            hotel.save()
            count += 1
            if count % 10 == 0:
                print(f"已生成{count}条酒店数据")
                
        except IntegrityError:
            # 处理唯一约束冲突
            continue

# 生成餐厅数据
def generate_restaurant_data():
    print("开始生成餐厅数据...")
    count = 0
    while count < 100:
        try:
            # 随机选择城市
            city = random.choice(CHINESE_CITIES)
            
            # 随机选择菜系
            cuisine_type = random.choice(CUISINE_TYPES)
            
            # 随机选择餐厅类型
            restaurant_type = random.choice(RESTAURANT_TYPES)
            
            # 生成餐厅名称
            if restaurant_type == "FINE_DINING":
                restaurant_name = f"{city}{random.choice(['御品', '尊享', '豪华', '精品'])}{random.choice(['餐厅', '酒楼', '食府'])}"
            elif restaurant_type == "CASUAL":
                restaurant_name = f"{city}{random.choice(['小馆', '食堂', '餐厅', '饭店'])}"
            elif restaurant_type == "FAST_FOOD":
                restaurant_name = f"{city}{random.choice(['快餐', '速食', '简餐'])}{random.choice(['店', '餐厅'])}"
            elif restaurant_type == "CAFE":
                restaurant_name = f"{city}{random.choice(['咖啡', '饮品', '休闲'])}{random.choice(['馆', '店', '吧'])}"
            elif restaurant_type == "BAR":
                restaurant_name = f"{city}{random.choice(['酒吧', '酒廊', '酒馆'])}"
            elif restaurant_type == "STREET_FOOD":
                restaurant_name = f"{city}{random.choice(['小吃', '美食', '街头'])}{random.choice(['摊', '店', '坊'])}"
            else:  # BUFFET
                restaurant_name = f"{city}{random.choice(['自助', '海鲜', '烤肉'])}{random.choice(['餐厅', ' buffet'])}"
            
            # 生成餐厅代码
            restaurant_code = f"REST_{city[:2].upper()}_{str(uuid.uuid4())[:8].upper()}"
            
            # 随机生成其他字段
            price_range = random.choice(PRICE_RANGES)
            avg_price_per_person = round(random.uniform(20, 500), 2)
            popularity_score = round(random.uniform(3.0, 5.0), 2)
            food_rating = round(random.uniform(3.0, 5.0), 2)
            service_rating = round(random.uniform(3.0, 5.0), 2)
            review_count = random.randint(0, 5000)
            
            # 创建餐厅对象
            restaurant = Restaurant(
                restaurant_id=uuid.uuid4(),
                restaurant_code=restaurant_code,
                restaurant_name=restaurant_name,
                country_code="CN",
                city_name=city,
                district=random.choice(["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区", "门头沟区", "房山区", "通州区", "顺义区"]) if city == "北京" else "",
                address=f"{city}{random.choice(['市', '区'])}{random.choice(['街道', '路', '大道'])} {random.randint(1, 999)}号",
                cuisine_type=cuisine_type,
                sub_cuisine_types=[cuisine_type, random.choice(CUISINE_TYPES)] if random.choice([True, False]) else [cuisine_type],
                restaurant_type=restaurant_type,
                tags={"特色": [random.choice(["环境优雅", "服务周到", "菜品丰富", "性价比高"]), random.choice(["免费WiFi", "停车位", "包厢", "外卖"])]},
                description=f"{restaurant_name}是一家位于{city}的{dict(Restaurant.RestaurantType.choices)[restaurant_type]}，主打{dict(Restaurant.PriceRange.choices)[price_range]}价位的{cuisine_type}。",
                signature_dishes={"招牌菜1": f"{cuisine_type}特色菜1", "招牌菜2": f"{cuisine_type}特色菜2", "招牌菜3": f"{cuisine_type}特色菜3"},
                opening_hours={"周一至周五": "10:00-22:00", "周六至周日": "09:00-23:00"},
                contact_phone=f"0{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                reservation_required=random.choice([True, False]),
                price_range=price_range,
                avg_price_per_person=avg_price_per_person,
                amenities={"设施": ["WiFi", "停车场", "空调", "电视"]},  
                seating_capacity=random.randint(20, 500),
                private_rooms_available=random.choice([True, False]),
                dietary_options={"选项": ["vegetarian", "vegan", "gluten-free"]},
                alcohol_served=random.choice([True, False]),
                popularity_score=popularity_score,
                food_rating=food_rating,
                service_rating=service_rating,
                review_count=review_count,
                status="ACTIVE"
            )
            
            restaurant.save()
            count += 1
            if count % 10 == 0:
                print(f"已生成{count}条餐厅数据")
                
        except IntegrityError:
            # 处理唯一约束冲突
            continue

if __name__ == "__main__":
    print("开始生成测试数据...")
    
    # 生成景点数据
    generate_attraction_data()
    print("景点数据生成完成！")
    
    # 生成酒店数据
    generate_hotel_data()
    print("酒店数据生成完成！")
    
    # 生成餐厅数据
    generate_restaurant_data()
    print("餐厅数据生成完成！")
    
    print("所有测试数据生成完成！")
