import os
import django

# 配置Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule

# 检查行程记录
print("=== 行程记录 ===")
itineraries = Itinerary.objects.all()
print(f"共有 {itineraries.count()} 条行程记录")
for itinerary in itineraries:
    print(f"行程ID: {itinerary.itinerary_id}")
    print(f"行程名称: {itinerary.itinerary_name}")
    print(f"开始日期: {itinerary.start_date}")
    print(f"结束日期: {itinerary.end_date}")
    print()

# 检查目的地记录
print("=== 目的地记录 ===")
destinations = Destination.objects.all()
print(f"共有 {destinations.count()} 条目的地记录")
for destination in destinations:
    print(f"目的地: {destination.city_name}")
    print(f"所属行程: {destination.itinerary.itinerary_name}")
    print(f"到达日期: {destination.arrival_date}")
    print(f"离开日期: {destination.departure_date}")
    print()

# 检查旅行者统计记录
print("=== 旅行者统计记录 ===")
traveler_stats = TravelerStats.objects.all()
print(f"共有 {traveler_stats.count()} 条旅行者统计记录")
for stats in traveler_stats:
    print(f"所属行程: {stats.itinerary.itinerary_name}")
    print(f"成人: {stats.adult_count}")
    print(f"儿童: {stats.child_count}")
    print(f"婴儿: {stats.infant_count}")
    print(f"老人: {stats.senior_count}")
    print()

# 检查每日行程记录
print("=== 每日行程记录 ===")
daily_schedules = DailySchedule.objects.all()
print(f"共有 {daily_schedules.count()} 条每日行程记录")
for schedule in daily_schedules:
    print(f"所属行程: {schedule.itinerary_id.itinerary_name}")
    print(f"第 {schedule.day_number} 天")
    print(f"日期: {schedule.schedule_date}")
    print(f"活动: {schedule.activity_title}")
    print(f"活动类型: {schedule.activity_type}")
    print()
