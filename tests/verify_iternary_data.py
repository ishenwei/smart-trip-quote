import os
import django

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule

# 验证数据
print("=== 行程测试数据验证 ===")
print(f"行程总数: {Itinerary.objects.count()}")
print(f"目的地总数: {Destination.objects.count()}")
print(f"旅行者统计总数: {TravelerStats.objects.count()}")
print(f"每日行程总数: {DailySchedule.objects.count()}")

# 查看最近创建的行程
if Itinerary.objects.exists():
    latest_itinerary = Itinerary.objects.latest('created_at')
    print(f"\n最近创建的行程:")
    print(f"行程ID: {latest_itinerary.itinerary_id}")
    print(f"行程名称: {latest_itinerary.itinerary_name}")
    print(f"开始日期: {latest_itinerary.start_date}")
    print(f"结束日期: {latest_itinerary.end_date}")
    
    # 查看关联的目的地
    destinations = Destination.objects.filter(itinerary=latest_itinerary)
    print(f"\n关联的目的地 ({destinations.count()}个):")
    for dest in destinations:
        print(f"- {dest.city_name} (顺序: {dest.destination_order})")
    
    # 查看关联的旅行者统计
    traveler_stats = TravelerStats.objects.filter(itinerary=latest_itinerary)
    if traveler_stats.exists():
        stats = traveler_stats.first()
        print(f"\n旅行者统计:")
        # 打印存在的字段
        if hasattr(stats, 'adults'):
            print(f"成人: {stats.adults}")
        if hasattr(stats, 'children'):
            print(f"儿童: {stats.children}")
        if hasattr(stats, 'infants'):
            print(f"婴儿: {stats.infants}")
        if hasattr(stats, 'seniors'):
            print(f"老人: {stats.seniors}")
    
    # 查看每日行程
    daily_schedules = DailySchedule.objects.filter(itinerary_id=latest_itinerary)
    print(f"\n每日行程安排 ({daily_schedules.count()}个活动):")
    # 按日期和时间排序
    sorted_schedules = daily_schedules.order_by('schedule_date', 'start_time')
    for schedule in sorted_schedules:
        print(f"- {schedule.schedule_date} {schedule.start_time}-{schedule.end_time}: {schedule.activity_title} ({schedule.activity_type})")
        # 打印关联的景点、酒店或餐厅
        if schedule.attraction_id:
            print(f"  关联景点: {schedule.attraction_id.attraction_name}")
        if schedule.hotel_id:
            print(f"  关联酒店: {schedule.hotel_id.hotel_name}")
        if schedule.restaurant_id:
            print(f"  关联餐厅: {schedule.restaurant_id.restaurant_name}")

print("\n=== 验证完成 ===")
