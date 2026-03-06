from django.http import HttpResponse
from django.contrib.admin import AdminSite
from apps.admin.itinerary import ItineraryAdmin
from apps.models import Itinerary
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpRequest

# 创建测试用户
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_superuser('testuser', 'test@example.com', 'password123')

# 创建行程对象
obj = Itinerary(
    itinerary_name='测试行程',
    description='这是一个测试行程',
    travel_purpose='LEISURE',
    start_date=timezone.now().date(),
    end_date=timezone.now().date(),
    total_days=1,
    departure_city='北京',
    return_city='上海',
    contact_person='测试联系人',
    contact_phone='13800138000',
    total_budget=10000,
    budget_flexibility='MEDIUM',
    current_status='DRAFT'
)

# 模拟请求
request = HttpRequest()
request.user = user
request.method = 'POST'
request.POST = {}

# 模拟表单
class MockForm:
    pass

form = MockForm()

# 创建 ItineraryAdmin 实例
admin_site = AdminSite()
itinerary_admin = ItineraryAdmin(Itinerary, admin_site)

def test_itinerary_save_logs(request):
    """测试 save_model 方法的日志输出"""
    print("开始调用 save_model 方法...")
    itinerary_admin.save_model(request, obj, form, False)
    print("save_model 方法调用完成")
    return HttpResponse("测试完成")
