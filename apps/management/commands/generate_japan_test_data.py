from django.core.management.base import BaseCommand
import uuid
from django.db.utils import IntegrityError

from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant


class Command(BaseCommand):
    help = '生成东京和大阪的测试数据（景点、酒店、餐厅各10条）'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('开始生成东京和大阪的测试数据...'))
        
        self.generate_tokyo_data()
        self.generate_osaka_data()
        
        self.stdout.write(self.style.SUCCESS('测试数据生成完成！'))

    def generate_tokyo_data(self):
        self.stdout.write(self.style.SUCCESS('正在生成东京数据...'))
        
        # 东京景点数据
        tokyo_attractions = [
            {
                'name': '东京塔',
                'address': '東京都港区芝公園4-2-8',
                'category': 'MODERN',
                'description': '东京塔是东京的地标性建筑，高333米，是日本最高的自立式铁塔。游客可以登上展望台俯瞰东京全景，夜晚的灯光秀更是美不胜收。',
                'ticket_price': 1200.00,
                'popularity_score': 4.8,
                'visitor_rating': 4.7,
                'review_count': 15230,
                'recommended_duration': 90,
                'tags': ['地标', '夜景', '拍照', '必游']
            },
            {
                'name': '浅草寺',
                'address': '東京都台東区浅草2-3-1',
                'category': 'RELIGIOUS',
                'description': '浅草寺是东京最古老的寺庙，建于公元628年。雷门的大红灯笼是其标志性建筑，仲见世商店街是购买传统小吃的绝佳去处。',
                'ticket_price': 0.00,
                'popularity_score': 4.9,
                'visitor_rating': 4.8,
                'review_count': 28450,
                'recommended_duration': 120,
                'tags': ['历史', '文化', '免费', '购物']
            },
            {
                'name': '皇居',
                'address': '東京都千代田区千代田1-1',
                'category': 'HISTORICAL',
                'description': '皇居是日本天皇的居住地，原为江户城。游客可以参观皇居东御苑，欣赏美丽的日式庭园和历史建筑。',
                'ticket_price': 0.00,
                'popularity_score': 4.6,
                'visitor_rating': 4.5,
                'review_count': 8760,
                'recommended_duration': 60,
                'tags': ['历史', '免费', '庭园', '皇室']
            },
            {
                'name': '东京迪士尼乐园',
                'address': '千葉県浦安市舞浜1-1',
                'category': 'ENTERTAINMENT',
                'description': '东京迪士尼乐园是亚洲首座迪士尼主题乐园，拥有七大主题园区，是家庭游客和迪士尼粉丝的必游之地。',
                'ticket_price': 8200.00,
                'popularity_score': 4.9,
                'visitor_rating': 4.8,
                'review_count': 45620,
                'recommended_duration': 480,
                'tags': ['亲子', '娱乐', '必游', '主题乐园']
            },
            {
                'name': '涩谷十字路口',
                'address': '東京都渋谷区道玄坂',
                'category': 'MODERN',
                'description': '涩谷十字路口被称为世界上最繁忙的十字路口，每次绿灯亮起时，成千上万的人同时穿过马路，场面壮观。',
                'ticket_price': 0.00,
                'popularity_score': 4.7,
                'visitor_rating': 4.6,
                'review_count': 12340,
                'recommended_duration': 30,
                'tags': ['免费', '都市', '拍照', '购物']
            },
            {
                'name': '新宿御苑',
                'address': '東京都新宿区内藤町11',
                'category': 'NATURAL',
                'description': '新宿御苑是东京最大的公园之一，融合了日式、英式和法式庭园风格，是赏樱和休闲放松的好去处。',
                'ticket_price': 500.00,
                'popularity_score': 4.5,
                'visitor_rating': 4.4,
                'review_count': 6780,
                'recommended_duration': 90,
                'tags': ['自然', '庭园', '赏樱', '休闲']
            },
            {
                'name': '明治神宫',
                'address': '東京都渋谷区代々木神園町1-1',
                'category': 'RELIGIOUS',
                'description': '明治神宫是供奉明治天皇和昭宪皇太后的神社，位于东京市中心的一片森林中，是感受日本神道文化的绝佳场所。',
                'ticket_price': 0.00,
                'popularity_score': 4.6,
                'visitor_rating': 4.5,
                'review_count': 9870,
                'recommended_duration': 60,
                'tags': ['宗教', '文化', '免费', '森林']
            },
            {
                'name': '上野公园',
                'address': '東京都台東区上野公園',
                'category': 'NATURAL',
                'description': '上野公园是东京最著名的赏樱胜地，园内还有国立博物馆、动物园和美术馆，是文化休闲的好地方。',
                'ticket_price': 0.00,
                'popularity_score': 4.4,
                'visitor_rating': 4.3,
                'review_count': 11200,
                'recommended_duration': 120,
                'tags': ['自然', '赏樱', '博物馆', '免费']
            },
            {
                'name': '筑地场外市场',
                'address': '東京都中央区築地5-2-1',
                'category': 'SHOPPING',
                'description': '筑地场外市场是东京最大的海鲜市场，游客可以品尝新鲜的海鲜料理，购买各种食材和厨具。',
                'ticket_price': 0.00,
                'popularity_score': 4.5,
                'visitor_rating': 4.4,
                'review_count': 15670,
                'recommended_duration': 90,
                'tags': ['美食', '海鲜', '购物', '市场']
            },
            {
                'name': '六本木新城',
                'address': '東京都港区六本木6-10-1',
                'category': 'MODERN',
                'description': '六本木新城是东京最时尚的综合体，集购物、餐饮、艺术和娱乐于一体，顶层的展望台可欣赏东京夜景。',
                'ticket_price': 1800.00,
                'popularity_score': 4.3,
                'visitor_rating': 4.2,
                'review_count': 7650,
                'recommended_duration': 120,
                'tags': ['购物', '艺术', '夜景', '时尚']
            }
        ]

        # 东京酒店数据
        tokyo_hotels = [
            {
                'name': '帝国饭店东京',
                'brand': '帝国饭店',
                'address': '東京都千代田区内幸町1-1-1',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '帝国饭店是东京最著名的豪华酒店之一，拥有百年历史，位于皇居附近，服务一流，设施完善。',
                'min_price': 45000.00,
                'max_price': 85000.00,
                'popularity_score': 4.8,
                'guest_rating': 4.7,
                'review_count': 5420,
                'tags': {'商务': True, '奢华': True, '历史': True}
            },
            {
                'name': '东京君悦酒店',
                'brand': '凯悦',
                'address': '東京都港区六本木6-10-3',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '东京君悦酒店位于六本木新城，拥有豪华的客房和世界级的设施，是商务和休闲旅客的理想选择。',
                'min_price': 42000.00,
                'max_price': 78000.00,
                'popularity_score': 4.7,
                'guest_rating': 4.6,
                'review_count': 4890,
                'tags': {'商务': True, '奢华': True, '现代': True}
            },
            {
                'name': '东京半岛酒店',
                'brand': '半岛酒店',
                'address': '東京都千代田区有楽町1-8-1',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '东京半岛酒店是半岛酒店集团在日本的首家酒店，位于银座附近，提供极致的奢华体验。',
                'min_price': 55000.00,
                'max_price': 95000.00,
                'popularity_score': 4.9,
                'guest_rating': 4.8,
                'review_count': 3210,
                'tags': {'奢华': True, '商务': True, '购物': True}
            },
            {
                'name': '新宿格拉斯丽酒店',
                'brand': '格拉斯丽',
                'address': '東京都新宿区歌舞伎町1-19-1',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '新宿格拉斯丽酒店位于歌舞伎町中心，交通便利，是商务和观光旅客的经济实惠选择。',
                'min_price': 12000.00,
                'max_price': 25000.00,
                'popularity_score': 4.3,
                'guest_rating': 4.2,
                'review_count': 8760,
                'tags': {'商务': True, '经济': True, '便利': True}
            },
            {
                'name': '东京湾希尔顿酒店',
                'brand': '希尔顿',
                'address': '東京都港区台場2-6-1',
                'hotel_type': 'RESORT',
                'hotel_star': 4,
                'description': '东京湾希尔顿酒店位于台场，拥有美丽的海景，是家庭度假的理想选择。',
                'min_price': 28000.00,
                'max_price': 52000.00,
                'popularity_score': 4.5,
                'guest_rating': 4.4,
                'review_count': 6540,
                'tags': {'度假': True, '海景': True, '家庭': True}
            },
            {
                'name': '涩谷Excel酒店东急',
                'brand': '东急',
                'address': '東京都渋谷区道玄坂2-23-1',
                'hotel_type': 'BUSINESS',
                'hotel_star': 3,
                'description': '涩谷Excel酒店东急位于涩谷中心，地理位置优越，价格合理，是年轻旅客的热门选择。',
                'min_price': 8000.00,
                'max_price': 18000.00,
                'popularity_score': 4.2,
                'guest_rating': 4.1,
                'review_count': 12340,
                'tags': {'经济': True, '便利': True, '年轻': True}
            },
            {
                'name': '东京安达仕酒店',
                'brand': '安达仕',
                'address': '東京都港区虎ノ門1-23-4',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '东京安达仕酒店是现代奢华酒店的典范，设计独特，服务个性化，是追求品质旅客的首选。',
                'min_price': 48000.00,
                'max_price': 88000.00,
                'popularity_score': 4.6,
                'guest_rating': 4.5,
                'review_count': 2870,
                'tags': {'奢华': True, '设计': True, '商务': True}
            },
            {
                'name': '东京王子大饭店',
                'brand': '王子大饭店',
                'address': '東京都港区芝公園1-3-1',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '东京王子大饭店位于东京塔附近，历史悠久，是商务和观光旅客的经典选择。',
                'min_price': 18000.00,
                'max_price': 38000.00,
                'popularity_score': 4.4,
                'guest_rating': 4.3,
                'review_count': 7650,
                'tags': {'商务': True, '历史': True, '便利': True}
            },
            {
                'name': '浅草豪景酒店',
                'brand': '豪景',
                'address': '東京都台東区浅草2-16-2',
                'hotel_type': 'BOUTIQUE',
                'hotel_star': 3,
                'description': '浅草豪景酒店位于浅草寺附近，装修风格独特，是体验传统东京文化的理想住宿选择。',
                'min_price': 10000.00,
                'max_price': 22000.00,
                'popularity_score': 4.1,
                'guest_rating': 4.0,
                'review_count': 5430,
                'tags': {'精品': True, '传统': True, '文化': True}
            },
            {
                'name': '品川王子大饭店',
                'brand': '王子大饭店',
                'address': '東京都港区高輪4-10-30',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '品川王子大饭店靠近品川站，交通便利，设施完善，是商务旅客的热门选择。',
                'min_price': 15000.00,
                'max_price': 32000.00,
                'popularity_score': 4.3,
                'guest_rating': 4.2,
                'review_count': 9120,
                'tags': {'商务': True, '便利': True, '交通': True}
            }
        ]

        # 东京餐厅数据
        tokyo_restaurants = [
            {
                'name': '数寄屋桥次郎',
                'address': '東京都中央区銀座4-2-15',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '数寄屋桥次郎是世界上最著名的寿司店之一，由寿司之神小野二郎经营，提供极致的寿司体验。',
                'chef_name': '小野二郎',
                'year_established': 1965,
                'price_range': '$$$$',
                'avg_price_per_person': 40000.00,
                'popularity_score': 4.9,
                'food_rating': 5.0,
                'service_rating': 4.8,
                'review_count': 2340,
                'tags': {'米其林': True, '寿司': True, '高端': True}
            },
            {
                'name': '龙吟',
                'address': '東京都港区六本木7-15-17',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '龙吟是东京最著名的怀石料理餐厅之一，主厨山本征治将传统怀石料理与现代创意完美结合。',
                'chef_name': '山本征治',
                'year_established': 2003,
                'price_range': '$$$$',
                'avg_price_per_person': 35000.00,
                'popularity_score': 4.8,
                'food_rating': 4.9,
                'service_rating': 4.8,
                'review_count': 1870,
                'tags': {'米其林': True, '怀石料理': True, '创意': True}
            },
            {
                'name': '一兰拉面',
                'address': '東京都渋谷区道玄坂2-29-7',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '一兰拉面是日本最著名的拉面连锁店之一，以豚骨拉面闻名，提供独特的单人隔间用餐体验。',
                'year_established': 1960,
                'price_range': '$',
                'avg_price_per_person': 1200.00,
                'popularity_score': 4.5,
                'food_rating': 4.4,
                'service_rating': 4.3,
                'review_count': 45670,
                'tags': {'拉面': True, '经济': True, '连锁': True}
            },
            {
                'name': '筑地寿司大',
                'address': '東京都中央区築地5-2-1',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '筑地寿司大是筑地市场最著名的寿司店之一，提供新鲜的海鲜寿司，是体验东京美食文化的必去之地。',
                'year_established': 1965,
                'price_range': '$$',
                'avg_price_per_person': 4000.00,
                'popularity_score': 4.6,
                'food_rating': 4.7,
                'service_rating': 4.2,
                'review_count': 23450,
                'tags': {'寿司': True, '新鲜': True, '市场': True}
            },
            {
                'name': '鸟贵族',
                'address': '東京都新宿区歌舞伎町1-16-2',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '鸟贵族是日本最大的烤鸟连锁店之一，以平价的烤串和轻松的氛围深受年轻人喜爱。',
                'year_established': 1985,
                'price_range': '$',
                'avg_price_per_person': 2500.00,
                'popularity_score': 4.4,
                'food_rating': 4.3,
                'service_rating': 4.2,
                'review_count': 34560,
                'tags': {'烤串': True, '经济': True, '居酒屋': True}
            },
            {
                'name': '银座久兵卫',
                'address': '東京都中央区銀座8-7-6',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '银座久兵卫是银座最著名的江户前寿司店之一，拥有百年历史，提供传统正宗的寿司体验。',
                'chef_name': '久兵卫',
                'year_established': 1935,
                'price_range': '$$$$',
                'avg_price_per_person': 30000.00,
                'popularity_score': 4.7,
                'food_rating': 4.8,
                'service_rating': 4.6,
                'review_count': 3210,
                'tags': {'米其林': True, '寿司': True, '传统': True}
            },
            {
                'name': '一风堂',
                'address': '東京都渋谷区神宮前3-27-15',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '一风堂是日本著名的拉面连锁店，以博多豚骨拉面闻名，汤头浓郁，面条劲道。',
                'year_established': 1985,
                'price_range': '$$',
                'avg_price_per_person': 1500.00,
                'popularity_score': 4.5,
                'food_rating': 4.4,
                'service_rating': 4.3,
                'review_count': 28760,
                'tags': {'拉面': True, '博多': True, '连锁': True}
            },
            {
                'name': '吉野家',
                'address': '東京都千代田区丸の内1-9-1',
                'cuisine_type': '日料',
                'restaurant_type': 'FAST_FOOD',
                'description': '吉野家是日本最著名的牛肉饭连锁店，以快速、便宜、美味著称，是上班族的最爱。',
                'year_established': 1899,
                'price_range': '$',
                'avg_price_per_person': 500.00,
                'popularity_score': 4.2,
                'food_rating': 4.1,
                'service_rating': 4.0,
                'review_count': 67890,
                'tags': {'牛肉饭': True, '经济': True, '快餐': True}
            },
            {
                'name': '天妇罗近藤',
                'address': '東京都港区新橋1-5-5',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '天妇罗近藤是东京最著名的天妇罗店之一，主厨近藤文夫将天妇罗艺术发挥到极致。',
                'chef_name': '近藤文夫',
                'year_established': 1991,
                'price_range': '$$$$',
                'avg_price_per_person': 28000.00,
                'popularity_score': 4.8,
                'food_rating': 4.9,
                'service_rating': 4.7,
                'review_count': 1890,
                'tags': {'米其林': True, '天妇罗': True, '高端': True}
            },
            {
                'name': '松阪牛烧肉M',
                'address': '東京都港区六本木7-14-15',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '松阪牛烧肉M是东京著名的烧肉店，提供顶级的松阪牛肉，肉质鲜嫩，口感绝佳。',
                'year_established': 2005,
                'price_range': '$$$',
                'avg_price_per_person': 12000.00,
                'popularity_score': 4.6,
                'food_rating': 4.7,
                'service_rating': 4.4,
                'review_count': 8760,
                'tags': {'烧肉': True, '松阪牛': True, '和牛': True}
            }
        ]

        self.create_attractions('东京', tokyo_attractions)
        self.create_hotels('东京', tokyo_hotels)
        self.create_restaurants('东京', tokyo_restaurants)
        
        self.stdout.write(self.style.SUCCESS('东京数据生成完成！'))

    def generate_osaka_data(self):
        self.stdout.write(self.style.SUCCESS('正在生成大阪数据...'))
        
        # 大阪景点数据
        osaka_attractions = [
            {
                'name': '大阪城',
                'address': '大阪府大阪市中央区大阪城1-1',
                'category': 'HISTORICAL',
                'description': '大阪城是日本三大名城之一，由丰臣秀吉建造，是大阪的标志性建筑。城内有大阪城公园和天守阁。',
                'ticket_price': 600.00,
                'popularity_score': 4.7,
                'visitor_rating': 4.6,
                'review_count': 23450,
                'recommended_duration': 120,
                'tags': ['历史', '城堡', '公园', '必游']
            },
            {
                'name': '道顿堀',
                'address': '大阪府大阪市中央区道頓堀1-1-10',
                'category': 'MODERN',
                'description': '道顿堀是大阪最著名的美食和娱乐区，以霓虹灯招牌和美食闻名，是大阪夜生活的中心。',
                'ticket_price': 0.00,
                'popularity_score': 4.6,
                'visitor_rating': 4.5,
                'review_count': 34560,
                'recommended_duration': 90,
                'tags': ['美食', '夜景', '购物', '免费']
            },
            {
                'name': '日本环球影城',
                'address': '大阪府大阪市此花区桜島2-1-33',
                'category': 'ENTERTAINMENT',
                'description': '日本环球影城是世界著名的主题乐园，拥有哈利波特、小黄人等热门主题区，是家庭游客的必游之地。',
                'ticket_price': 8600.00,
                'popularity_score': 4.8,
                'visitor_rating': 4.7,
                'review_count': 56780,
                'recommended_duration': 480,
                'tags': ['亲子', '娱乐', '主题乐园', '必游']
            },
            {
                'name': '通天阁',
                'address': '大阪府大阪市浪速区恵美須東1-18-6',
                'category': 'MODERN',
                'description': '通天阁是大阪的地标性建筑，高103米，展望台可俯瞰大阪全景。周边的新世界地区充满复古风情。',
                'ticket_price': 900.00,
                'popularity_score': 4.3,
                'visitor_rating': 4.2,
                'review_count': 12340,
                'recommended_duration': 60,
                'tags': ['地标', '展望台', '复古', '拍照']
            },
            {
                'name': '四天王寺',
                'address': '大阪府大阪市天王寺区四天王寺1-11-18',
                'category': 'RELIGIOUS',
                'description': '四天王寺是日本最古老的佛教寺院之一，由圣德太子建造，是佛教文化的重要遗产。',
                'ticket_price': 300.00,
                'popularity_score': 4.4,
                'visitor_rating': 4.3,
                'review_count': 8760,
                'recommended_duration': 90,
                'tags': ['历史', '宗教', '文化', '古寺']
            },
            {
                'name': '大阪海游馆',
                'address': '大阪府大阪市港区海岸通1-1-10',
                'category': 'INDOOR',
                'description': '大阪海游馆是日本最大的水族馆之一，拥有巨大的水槽展示鲸鲨，是亲子游的热门目的地。',
                'ticket_price': 2550.00,
                'popularity_score': 4.5,
                'visitor_rating': 4.4,
                'review_count': 18760,
                'recommended_duration': 150,
                'tags': ['室内', '亲子', '水族馆', '海洋']
            },
            {
                'name': '心斋桥',
                'address': '大阪府大阪市中央区心斎橋筋1-1',
                'category': 'SHOPPING',
                'description': '心斋桥是大阪最著名的购物区，拥有众多百货商店、品牌店和药妆店，是购物爱好者的天堂。',
                'ticket_price': 0.00,
                'popularity_score': 4.6,
                'visitor_rating': 4.5,
                'review_count': 45670,
                'recommended_duration': 180,
                'tags': ['购物', '免费', '商业', '时尚']
            },
            {
                'name': '住吉大社',
                'address': '大阪府大阪市住吉区住吉2-9-89',
                'category': 'RELIGIOUS',
                'description': '住吉大社是日本最古老的神社之一，以美丽的太鼓桥和传统的建筑风格闻名。',
                'ticket_price': 0.00,
                'popularity_score': 4.5,
                'visitor_rating': 4.4,
                'review_count': 7650,
                'recommended_duration': 60,
                'tags': ['宗教', '文化', '免费', '传统']
            },
            {
                'name': '箕面瀑布',
                'address': '大阪府箕面市箕面公園',
                'category': 'NATURAL',
                'description': '箕面瀑布是大阪著名的自然景点，高33米，周围是美丽的山林，是徒步和亲近自然的好去处。',
                'ticket_price': 0.00,
                'popularity_score': 4.2,
                'visitor_rating': 4.1,
                'review_count': 5430,
                'recommended_duration': 120,
                'tags': ['自然', '瀑布', '徒步', '免费']
            },
            {
                'name': '天守阁',
                'address': '大阪府大阪市中央区大阪城1-1',
                'category': 'HISTORICAL',
                'description': '天守阁是大阪城的主体建筑，内部是历史博物馆，展示了大阪城的历史和文物。',
                'ticket_price': 600.00,
                'popularity_score': 4.6,
                'visitor_rating': 4.5,
                'review_count': 18920,
                'recommended_duration': 60,
                'tags': ['历史', '博物馆', '城堡', '文化']
            }
        ]

        # 大阪酒店数据
        osaka_hotels = [
            {
                'name': '大阪丽思卡尔顿酒店',
                'brand': '丽思卡尔顿',
                'address': '大阪府大阪市北区梅田2-5-25',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '大阪丽思卡尔顿酒店是梅田地区最奢华的酒店，提供世界级的服务和设施，是商务和休闲旅客的首选。',
                'min_price': 45000.00,
                'max_price': 85000.00,
                'popularity_score': 4.8,
                'guest_rating': 4.7,
                'review_count': 3210,
                'tags': {'奢华': True, '商务': True, '梅田': True}
            },
            {
                'name': '大阪康莱德酒店',
                'brand': '康莱德',
                'address': '大阪府大阪市西区靱本町1-8-16',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '大阪康莱德酒店位于本町，拥有豪华的客房和顶级的设施，是追求品质旅客的理想选择。',
                'min_price': 40000.00,
                'max_price': 78000.00,
                'popularity_score': 4.7,
                'guest_rating': 4.6,
                'review_count': 2870,
                'tags': {'奢华': True, '商务': True, '现代': True}
            },
            {
                'name': '大阪日航酒店',
                'brand': '日航',
                'address': '大阪府大阪市中央区西心斎橋1-3-3',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '大阪日航酒店位于心斋桥附近，交通便利，是商务和观光旅客的热门选择。',
                'min_price': 15000.00,
                'max_price': 32000.00,
                'popularity_score': 4.4,
                'guest_rating': 4.3,
                'review_count': 7650,
                'tags': {'商务': True, '便利': True, '心斋桥': True}
            },
            {
                'name': '大阪瑞士南海酒店',
                'brand': '瑞士南海',
                'address': '大阪府大阪市浪速区難波中2-10-70',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '大阪瑞士南海酒店靠近难波站，交通便利，设施完善，是商务旅客的热门选择。',
                'min_price': 12000.00,
                'max_price': 28000.00,
                'popularity_score': 4.3,
                'guest_rating': 4.2,
                'review_count': 9870,
                'tags': {'商务': True, '便利': True, '难波': True}
            },
            {
                'name': '大阪万豪酒店',
                'brand': '万豪',
                'address': '大阪府大阪市中央区大阪城1-3-3',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '大阪万豪酒店位于大阪城公园附近，拥有美丽的城景，是度假和商务旅客的理想选择。',
                'min_price': 35000.00,
                'max_price': 65000.00,
                'popularity_score': 4.6,
                'guest_rating': 4.5,
                'review_count': 4320,
                'tags': {'奢华': True, '度假': True, '大阪城': True}
            },
            {
                'name': '大阪希尔顿酒店',
                'brand': '希尔顿',
                'address': '大阪府大阪市北区梅田1-3-3',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '大阪希尔顿酒店位于梅田中心，交通便利，是商务旅客的热门选择。',
                'min_price': 18000.00,
                'max_price': 38000.00,
                'popularity_score': 4.4,
                'guest_rating': 4.3,
                'review_count': 6540,
                'tags': {'商务': True, '便利': True, '梅田': True}
            },
            {
                'name': '大阪凯悦酒店',
                'brand': '凯悦',
                'address': '大阪府大阪市天王寺区上本町6-2-10',
                'hotel_type': 'LUXURY',
                'hotel_star': 5,
                'description': '大阪凯悦酒店位于天王寺，拥有豪华的设施和优质的服务，是高端旅客的首选。',
                'min_price': 32000.00,
                'max_price': 60000.00,
                'popularity_score': 4.5,
                'guest_rating': 4.4,
                'review_count': 3870,
                'tags': {'奢华': True, '商务': True, '天王寺': True}
            },
            {
                'name': '大阪东横酒店',
                'brand': '东横',
                'address': '大阪府大阪市北区梅田2-11-6',
                'hotel_type': 'BUSINESS',
                'hotel_star': 3,
                'description': '大阪东横酒店位于梅田，价格合理，设施齐全，是经济型旅客的热门选择。',
                'min_price': 8000.00,
                'max_price': 18000.00,
                'popularity_score': 4.2,
                'guest_rating': 4.1,
                'review_count': 11230,
                'tags': {'经济': True, '便利': True, '梅田': True}
            },
            {
                'name': '大阪维纳斯酒店',
                'brand': '维纳斯',
                'address': '大阪府大阪市西区靱本町1-4-12',
                'hotel_type': 'BOUTIQUE',
                'hotel_star': 3,
                'description': '大阪维纳斯酒店是女性专用酒店，装修温馨，设施贴心，是女性旅客的理想选择。',
                'min_price': 10000.00,
                'max_price': 22000.00,
                'popularity_score': 4.3,
                'guest_rating': 4.2,
                'review_count': 5430,
                'tags': {'精品': True, '女性': True, '温馨': True}
            },
            {
                'name': '大阪京阪酒店',
                'brand': '京阪',
                'address': '大阪府大阪市中央区大手前1-7-18',
                'hotel_type': 'BUSINESS',
                'hotel_star': 4,
                'description': '大阪京阪酒店靠近大阪城，交通便利，是商务和观光旅客的热门选择。',
                'min_price': 14000.00,
                'max_price': 30000.00,
                'popularity_score': 4.3,
                'guest_rating': 4.2,
                'review_count': 7650,
                'tags': {'商务': True, '便利': True, '大阪城': True}
            }
        ]

        # 大阪餐厅数据
        osaka_restaurants = [
            {
                'name': '鹤桥',
                'address': '大阪府大阪市天王寺区下味原2-5-19',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '鹤桥是大阪最著名的烤肉街，聚集了众多烤肉店，提供各种优质的和牛，是肉食爱好者的天堂。',
                'year_established': 1970,
                'price_range': '$$$',
                'avg_price_per_person': 8000.00,
                'popularity_score': 4.6,
                'food_rating': 4.7,
                'service_rating': 4.3,
                'review_count': 23450,
                'tags': {'烤肉': True, '和牛': True, '鹤桥': True}
            },
            {
                'name': '千房',
                'address': '大阪府大阪市中央区道頓堀1-5-10',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '千房是大阪最著名的章鱼烧店，以外酥内嫩的章鱼烧闻名，是大阪必吃的美食。',
                'year_established': 1975,
                'price_range': '$',
                'avg_price_per_person': 800.00,
                'popularity_score': 4.5,
                'food_rating': 4.6,
                'service_rating': 4.2,
                'review_count': 45670,
                'tags': {'章鱼烧': True, '大阪': True, '小吃': True}
            },
            {
                'name': '本家',
                'address': '大阪府大阪市中央区道頓堀1-7-6',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '本家是大阪最著名的大阪烧店，提供正宗的大阪烧，口感丰富，是体验大阪美食文化的必去之地。',
                'year_established': 1965,
                'price_range': '$$',
                'avg_price_per_person': 2000.00,
                'popularity_score': 4.4,
                'food_rating': 4.5,
                'service_rating': 4.1,
                'review_count': 34560,
                'tags': {'大阪烧': True, '大阪': True, '铁板烧': True}
            },
            {
                'name': '串カツ田中',
                'address': '大阪府大阪市中央区宗右衛門町1-7-26',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '串カツ田中是大阪著名的串炸店，以酥脆的炸串和独特的酱汁闻名，是居酒文化的代表。',
                'year_established': 1970,
                'price_range': '$$',
                'avg_price_per_person': 2500.00,
                'popularity_score': 4.5,
                'food_rating': 4.6,
                'service_rating': 4.3,
                'review_count': 28760,
                'tags': {'串炸': True, '居酒屋': True, '大阪': True}
            },
            {
                'name': '吉兆',
                'address': '大阪府大阪市北区中之島3-1-15',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '吉兆是大阪最著名的怀石料理餐厅之一，拥有米其林三星，提供极致的怀石料理体验。',
                'chef_name': '德冈邦夫',
                'year_established': 1930,
                'price_range': '$$$$',
                'avg_price_per_person': 35000.00,
                'popularity_score': 4.9,
                'food_rating': 5.0,
                'service_rating': 4.8,
                'review_count': 1890,
                'tags': {'米其林': True, '怀石料理': True, '高端': True}
            },
            {
                'name': '太',
                'address': '大阪府大阪市中央区宗右衛門町1-7-15',
                'cuisine_type': '日料',
                'restaurant_type': 'FINE_DINING',
                'description': '太是大阪著名的寿司店，提供新鲜的江户前寿司，是寿司爱好者的必去之地。',
                'chef_name': '太',
                'year_established': 1985,
                'price_range': '$$$$',
                'avg_price_per_person': 28000.00,
                'popularity_score': 4.7,
                'food_rating': 4.8,
                'service_rating': 4.6,
                'review_count': 2340,
                'tags': {'米其林': True, '寿司': True, '高端': True}
            },
            {
                'name': '道顿堀今川烧',
                'address': '大阪府大阪市中央区道頓堀1-7-8',
                'cuisine_type': '日料',
                'restaurant_type': 'FAST_FOOD',
                'description': '道顿堀今川烧是大阪著名的今川烧店，以热腾腾的红豆馅今川烧闻名，是道顿堀的标志性小吃。',
                'year_established': 1950,
                'price_range': '$',
                'avg_price_per_person': 300.00,
                'popularity_score': 4.3,
                'food_rating': 4.4,
                'service_rating': 4.0,
                'review_count': 56780,
                'tags': {'今川烧': True, '小吃': True, '道顿堀': True}
            },
            {
                'name': '法善寺横丁',
                'address': '大阪府大阪市中央区難波1-2-16',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '法善寺横丁是大阪著名的美食街，聚集了众多传统小吃店和居酒屋，是体验大阪美食文化的绝佳场所。',
                'year_established': 1960,
                'price_range': '$$',
                'avg_price_per_person': 3000.00,
                'popularity_score': 4.4,
                'food_rating': 4.5,
                'service_rating': 4.2,
                'review_count': 34560,
                'tags': {'美食街': True, '传统': True, '居酒屋': True}
            },
            {
                'name': '松阪牛烧肉M大阪',
                'address': '大阪府大阪市中央区西心斎橋1-7-15',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': '松阪牛烧肉M大阪是大阪著名的烧肉店，提供顶级的松阪牛肉，肉质鲜嫩，口感绝佳。',
                'year_established': 2008,
                'price_range': '$$$',
                'avg_price_per_person': 10000.00,
                'popularity_score': 4.6,
                'food_rating': 4.7,
                'service_rating': 4.4,
                'review_count': 7650,
                'tags': {'烧肉': True, '松阪牛': True, '和牛': True}
            },
            {
                'name': 'お好み焼ききく',
                'address': '大阪府大阪市中央区道頓堀1-6-18',
                'cuisine_type': '日料',
                'restaurant_type': 'CASUAL',
                'description': 'お好み焼ききく是大阪著名的大阪烧店，提供正宗的大阪烧，口感丰富，是体验大阪美食文化的必去之地。',
                'year_established': 1970,
                'price_range': '$$',
                'avg_price_per_person': 1800.00,
                'popularity_score': 4.3,
                'food_rating': 4.4,
                'service_rating': 4.1,
                'review_count': 23450,
                'tags': {'大阪烧': True, '大阪': True, '铁板烧': True}
            }
        ]

        self.create_attractions('大阪', osaka_attractions)
        self.create_hotels('大阪', osaka_hotels)
        self.create_restaurants('大阪', osaka_restaurants)
        
        self.stdout.write(self.style.SUCCESS('大阪数据生成完成！'))

    def create_attractions(self, city_name, attractions_data):
        self.stdout.write(self.style.SUCCESS(f'正在生成{city_name}的景点数据...'))
        
        for idx, data in enumerate(attractions_data, 1):
            try:
                attraction = Attraction(
                    attraction_id=uuid.uuid4(),
                    attraction_code=f"ATTR_{city_name[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                    attraction_name=data['name'],
                    country_code='JP',
                    city_name=city_name,
                    address=data['address'],
                    category=data['category'],
                    description=data['description'],
                    ticket_price=data['ticket_price'],
                    currency='JPY',
                    popularity_score=data['popularity_score'],
                    visitor_rating=data['visitor_rating'],
                    review_count=data['review_count'],
                    recommended_duration=data['recommended_duration'],
                    tags=data['tags'],
                    status='ACTIVE'
                )
                attraction.save()
                self.stdout.write(self.style.SUCCESS(f'  已创建景点: {data["name"]}'))
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'  创建景点失败: {data["name"]} - {e}'))

    def create_hotels(self, city_name, hotels_data):
        self.stdout.write(self.style.SUCCESS(f'正在生成{city_name}的酒店数据...'))
        
        for idx, data in enumerate(hotels_data, 1):
            try:
                hotel = Hotel(
                    hotel_id=uuid.uuid4(),
                    hotel_code=f"HOTEL_{city_name[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                    hotel_name=data['name'],
                    brand_name=data['brand'],
                    country_code='JP',
                    city_name=city_name,
                    address=data['address'],
                    hotel_type=data['hotel_type'],
                    hotel_star=data['hotel_star'],
                    description=data['description'],
                    min_price=data['min_price'],
                    max_price=data['max_price'],
                    currency='JPY',
                    popularity_score=data['popularity_score'],
                    guest_rating=data['guest_rating'],
                    review_count=data['review_count'],
                    tags=data['tags'],
                    status='ACTIVE'
                )
                hotel.save()
                self.stdout.write(self.style.SUCCESS(f'  已创建酒店: {data["name"]}'))
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'  创建酒店失败: {data["name"]} - {e}'))

    def create_restaurants(self, city_name, restaurants_data):
        self.stdout.write(self.style.SUCCESS(f'正在生成{city_name}的餐厅数据...'))
        
        for idx, data in enumerate(restaurants_data, 1):
            try:
                restaurant = Restaurant(
                    restaurant_id=uuid.uuid4(),
                    restaurant_code=f"REST_{city_name[:2].upper()}_{str(uuid.uuid4())[:6].upper()}",
                    restaurant_name=data['name'],
                    country_code='JP',
                    city_name=city_name,
                    address=data['address'],
                    cuisine_type=data['cuisine_type'],
                    restaurant_type=data['restaurant_type'],
                    description=data['description'],
                    chef_name=data.get('chef_name', ''),
                    year_established=data.get('year_established'),
                    price_range=data['price_range'],
                    avg_price_per_person=data['avg_price_per_person'],
                    popularity_score=data['popularity_score'],
                    food_rating=data['food_rating'],
                    service_rating=data['service_rating'],
                    review_count=data['review_count'],
                    tags=data['tags'],
                    status='ACTIVE'
                )
                restaurant.save()
                self.stdout.write(self.style.SUCCESS(f'  已创建餐厅: {data["name"]}'))
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f'  创建餐厅失败: {data["name"]} - {e}'))
