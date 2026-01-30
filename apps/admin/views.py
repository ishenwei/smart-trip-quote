from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from ..models import (
    Itinerary,
    TravelerStats,
    Destination,
    DailySchedule
)

@staff_member_required
def preview_itinerary(request, itinerary_id):
    """行程详情预览视图"""
    itinerary = get_object_or_404(Itinerary, itinerary_id=itinerary_id)
    
    # 获取相关数据
    traveler_stats = TravelerStats.objects.filter(itinerary=itinerary).first()
    destinations = Destination.objects.filter(itinerary=itinerary).order_by('destination_order')
    daily_schedules = DailySchedule.objects.filter(itinerary_id=itinerary).order_by('schedule_date', 'start_time')
    
    # 按日期分组每日行程
    grouped_schedules = {}
    for schedule in daily_schedules:
        date_key = schedule.schedule_date
        if date_key not in grouped_schedules:
            grouped_schedules[date_key] = []
        grouped_schedules[date_key].append(schedule)
    
    context = {
        'itinerary': itinerary,
        'traveler_stats': traveler_stats,
        'destinations': destinations,
        'grouped_schedules': grouped_schedules
    }
    
    return render(request, 'admin/preview_itinerary.html', context)
