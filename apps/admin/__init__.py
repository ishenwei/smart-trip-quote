from django.contrib.admin import AdminSite
from django.conf import settings
from .requirement import RequirementAdmin
from .attraction import AttractionAdmin
from .hotel import HotelAdmin
from .restaurant import RestaurantAdmin
from .itinerary import ItineraryAdmin, DailyScheduleAdmin
from apps.models import Requirement
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant
from apps.models import Itinerary, DailySchedule


class SmartTripAdminSite(AdminSite):
    """自定义Admin站点类"""
    # 使用settings.py中的配置
    site_header = getattr(settings, 'ADMIN_SITE_HEADER', '智能旅游规划系统')
    site_title = getattr(settings, 'ADMIN_SITE_TITLE', '智能旅游规划系统')
    index_title = getattr(settings, 'ADMIN_INDEX_TITLE', '智能旅游规划系统管理')


# 创建自定义Admin站点实例
admin_site = SmartTripAdminSite(name='smart_trip_admin')

# 注册模型到自定义Admin站点
admin_site.register(Requirement, RequirementAdmin)
admin_site.register(Attraction, AttractionAdmin)
admin_site.register(Hotel, HotelAdmin)
admin_site.register(Restaurant, RestaurantAdmin)
admin_site.register(Itinerary, ItineraryAdmin)
admin_site.register(DailySchedule, DailyScheduleAdmin)

__all__ = ['RequirementAdmin', 'AttractionAdmin', 'HotelAdmin', 'RestaurantAdmin', 'ItineraryAdmin', 'DailyScheduleAdmin', 'admin_site']
