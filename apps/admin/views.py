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

@staff_member_required
async def generate_itinerary(request, requirement_id):
    """生成旅游行程规划，调用n8n webhook"""
    from django.conf import settings
    from ..models import Requirement
    import aiohttp
    import json
    import logging
    import asyncio
    from datetime import datetime
    
    # 配置日志
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '仅支持POST请求'}, status=405)
    
    try:
        # 获取需求对象
        requirement = get_object_or_404(Requirement, requirement_id=requirement_id)
        
        # 验证数据完整性
        if not requirement.destination_cities:
            return JsonResponse({'success': False, 'error': '目的地城市不能为空'}, status=400)
        
        if not requirement.trip_days:
            return JsonResponse({'success': False, 'error': '出行天数不能为空'}, status=400)
        
        if not requirement.group_total:
            return JsonResponse({'success': False, 'error': '总人数不能为空'}, status=400)
        
        # 准备webhook数据
        webhook_data = requirement.to_json()
        
        # 获取配置
        n8n_webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', '')
        n8n_api_key = getattr(settings, 'N8N_API_KEY', '')
        
        if not n8n_webhook_url:
            return JsonResponse({'success': False, 'error': 'n8n webhook URL未配置'}, status=500)
        
        if not n8n_api_key:
            return JsonResponse({'success': False, 'error': 'n8n API密钥未配置'}, status=500)
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 发送webhook请求（异步）
        async def send_webhook():
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': n8n_api_key,
                'X-Request-ID': request_id
            }
            
            timeout = aiohttp.ClientTimeout(total=30)  # 30秒超时
            retry_count = 0
            max_retries = 2
            
            while retry_count <= max_retries:
                try:
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.post(
                            n8n_webhook_url,
                            headers=headers,
                            json=webhook_data,
                            ssl=True  # 强制使用HTTPS
                        ) as response:
                            status_code = response.status
                            response_text = await response.text()
                            
                            logger.info(f"Webhook调用结果 - 时间戳: {datetime.now().isoformat()}, "
                                        f"请求ID: {request_id}, "
                                        f"状态码: {status_code}, "
                                        f"结果: {response_text[:100]}...")
                            
                            if status_code >= 200 and status_code < 300:
                                return True, status_code
                            else:
                                logger.warning(f"Webhook调用失败 - 状态码: {status_code}, "
                                              f"重试次数: {retry_count}")
                except Exception as e:
                    logger.error(f"Webhook调用异常 - 错误: {str(e)}, "
                                 f"重试次数: {retry_count}")
                
                retry_count += 1
                if retry_count <= max_retries:
                    await asyncio.sleep(2)  # 等待2秒后重试
            
            return False, None
        
        # 异步发送webhook
        success, status_code = await send_webhook()
        
        if success:
            logger.info(f"行程规划生成请求已发送 - 需求ID: {requirement.requirement_id}, "
                        f"请求ID: {request_id}")
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'webhook调用失败，请稍后重试'})
            
    except Exception as e:
        logger.error(f"生成行程规划异常 - 错误: {str(e)}")
        return JsonResponse({'success': False, 'error': f'服务器内部错误: {str(e)}'}, status=500)

