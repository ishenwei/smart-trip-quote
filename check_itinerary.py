from apps.models import Itinerary, DailySchedule

# Get the itinerary
itinerary = Itinerary.objects.get(itinerary_id='ITI_20260305_012')
print(f'行程ID: {itinerary.itinerary_id}')
print(f'总天数: {itinerary.total_days}')
print(f'开始日期: {itinerary.start_date}')
print(f'结束日期: {itinerary.end_date}')

# Get the daily schedules
schedules = DailySchedule.objects.filter(itinerary_id=itinerary)
print(f'每日行程数量: {schedules.count()}')
for s in schedules:
    print(f'  第{s.day_number}天: {s.activity_title}')
