from django.core.management.base import BaseCommand

from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant


class Command(BaseCommand):
    help = '验证日本测试数据'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== 数据验证报告 ===\n'))

        self.stdout.write(self.style.SUCCESS('东京数据统计:'))
        tokyo_attractions = Attraction.objects.filter(city_name="东京").count()
        tokyo_hotels = Hotel.objects.filter(city_name="东京").count()
        tokyo_restaurants = Restaurant.objects.filter(city_name="东京").count()
        
        self.stdout.write(f'  景点数量: {tokyo_attractions}')
        self.stdout.write(f'  酒店数量: {tokyo_hotels}')
        self.stdout.write(f'  餐厅数量: {tokyo_restaurants}')

        self.stdout.write(self.style.SUCCESS('\n大阪数据统计:'))
        osaka_attractions = Attraction.objects.filter(city_name="大阪").count()
        osaka_hotels = Hotel.objects.filter(city_name="大阪").count()
        osaka_restaurants = Restaurant.objects.filter(city_name="大阪").count()
        
        self.stdout.write(f'  景点数量: {osaka_attractions}')
        self.stdout.write(f'  酒店数量: {osaka_hotels}')
        self.stdout.write(f'  餐厅数量: {osaka_restaurants}')

        self.stdout.write(self.style.SUCCESS('\n=== 东京景点列表 ==='))
        for attraction in Attraction.objects.filter(city_name="东京"):
            self.stdout.write(f'  - {attraction.attraction_name} | 评分: {attraction.popularity_score} | 评论数: {attraction.review_count}')

        self.stdout.write(self.style.SUCCESS('\n=== 东京酒店列表 ==='))
        for hotel in Hotel.objects.filter(city_name="东京"):
            self.stdout.write(f'  - {hotel.hotel_name} | 星级: {hotel.hotel_star} | 评分: {hotel.popularity_score} | 价格: {hotel.min_price}-{hotel.max_price}')

        self.stdout.write(self.style.SUCCESS('\n=== 东京餐厅列表 ==='))
        for restaurant in Restaurant.objects.filter(city_name="东京"):
            self.stdout.write(f'  - {restaurant.restaurant_name} | 菜系: {restaurant.cuisine_type} | 评分: {restaurant.popularity_score} | 人均: {restaurant.avg_price_per_person}')

        self.stdout.write(self.style.SUCCESS('\n=== 大阪景点列表 ==='))
        for attraction in Attraction.objects.filter(city_name="大阪"):
            self.stdout.write(f'  - {attraction.attraction_name} | 评分: {attraction.popularity_score} | 评论数: {attraction.review_count}')

        self.stdout.write(self.style.SUCCESS('\n=== 大阪酒店列表 ==='))
        for hotel in Hotel.objects.filter(city_name="大阪"):
            self.stdout.write(f'  - {hotel.hotel_name} | 星级: {hotel.hotel_star} | 评分: {hotel.popularity_score} | 价格: {hotel.min_price}-{hotel.max_price}')

        self.stdout.write(self.style.SUCCESS('\n=== 大阪餐厅列表 ==='))
        for restaurant in Restaurant.objects.filter(city_name="大阪"):
            self.stdout.write(f'  - {restaurant.restaurant_name} | 菜系: {restaurant.cuisine_type} | 评分: {restaurant.popularity_score} | 人均: {restaurant.avg_price_per_person}')

        self.stdout.write(self.style.SUCCESS('\n=== 验证完成 ==='))
        
        total = tokyo_attractions + tokyo_hotels + tokyo_restaurants + osaka_attractions + osaka_hotels + osaka_restaurants
        self.stdout.write(self.style.SUCCESS(f'\n总计创建 {total} 条测试数据'))
