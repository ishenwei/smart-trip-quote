import uuid
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from ..models import (
    Itinerary,
    TravelerStats,
    Destination,
    DailySchedule,
    Attraction,
    Restaurant,
    Hotel
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

@staff_member_required
def get_filtered_resources(request):
    """根据destination获取过滤后的资源数据"""
    destination_id = request.GET.get('destination_id')
    
    if not destination_id:
        return JsonResponse({
            'attractions': [],
            'restaurants': [],
            'hotels': []
        })
    
    # 验证destination_id是否为有效的UUID格式
    try:
        uuid.UUID(destination_id)
    except ValueError:
        # 如果不是有效的UUID格式，返回空结果
        return JsonResponse({
            'attractions': [],
            'restaurants': [],
            'hotels': []
        })
    
    try:
        # 获取选中的destination
        destination = Destination.objects.get(destination_id=destination_id)
        city_name = destination.city_name
        
        # 根据city_name过滤资源
        attractions = Attraction.objects.filter(city_name=city_name).values('attraction_id', 'attraction_name')
        restaurants = Restaurant.objects.filter(city_name=city_name).values('restaurant_id', 'restaurant_name')
        hotels = Hotel.objects.filter(city_name=city_name).values('hotel_id', 'hotel_name')
        
        # 转换为列表格式
        attraction_list = list(attractions)
        restaurant_list = list(restaurants)
        hotel_list = list(hotels)
        
        return JsonResponse({
            'city_name': city_name,
            'attractions': attraction_list,
            'restaurants': restaurant_list,
            'hotels': hotel_list
        })
    except Destination.DoesNotExist:
        # 如果destination不存在，返回空结果
        return JsonResponse({
            'attractions': [],
            'restaurants': [],
            'hotels': []
        })

