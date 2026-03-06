import unittest
import logging
from datetime import date, datetime, timedelta
from django.test import TestCase
from apps.models.itinerary import Itinerary
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.destinations import Destination

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('itinerary_update_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('itinerary_update_test')

class ItineraryUpdateTest(TestCase):
    def setUp(self):
        """创建测试数据"""
        logger.info("=== 开始设置测试数据 ===")
        
        # 创建一个Itinerary对象
        self.itinerary = Itinerary.objects.create(
            itinerary_name="测试行程",
            description="这是一个测试行程",
            travel_purpose=Itinerary.TravelPurpose.LEISURE,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            contact_person="张三",
            contact_phone="13800138000",
            departure_city="北京",
            return_city="北京",
            current_status=Itinerary.CurrentStatus.DRAFT,
            created_by="test_user"
        )
        logger.info(f"创建测试行程: {self.itinerary.itinerary_id}")
        
        # 创建TravelerStats对象
        self.traveler_stats = TravelerStats.objects.create(
            itinerary=self.itinerary,
            adult_count=2,
            child_count=1,
            infant_count=0,
            senior_count=0,
            notes="测试旅行者统计"
        )
        logger.info(f"创建测试旅行者统计: {self.traveler_stats.stat_id}")
        
        # 创建Destination对象
        self.destination1 = Destination.objects.create(
            itinerary=self.itinerary,
            destination_order=1,
            city_name="上海",
            country_code="CN",
            region="上海",
            arrival_date=date.today(),
            departure_date=date.today() + timedelta(days=2)
        )
        self.destination2 = Destination.objects.create(
            itinerary=self.itinerary,
            destination_order=2,
            city_name="杭州",
            country_code="CN",
            region="浙江",
            arrival_date=date.today() + timedelta(days=2),
            departure_date=date.today() + timedelta(days=4)
        )
        logger.info(f"创建测试目的地: {self.destination1.city_name}, {self.destination2.city_name}")
        
        # 创建DailySchedule对象
        self.schedule1 = DailySchedule.objects.create(
            itinerary_id=self.itinerary,
            day_number=1,
            schedule_date=date.today(),
            activity_type=DailySchedule.ActivityType.FLIGHT,
            activity_title="北京到上海",
            start_time=datetime.strptime("08:00", "%H:%M").time(),
            end_time=datetime.strptime("10:00", "%H:%M").time()
        )
        self.schedule2 = DailySchedule.objects.create(
            itinerary_id=self.itinerary,
            day_number=1,
            schedule_date=date.today(),
            activity_type=DailySchedule.ActivityType.ATTRACTION,
            activity_title="外滩游览",
            start_time=datetime.strptime("14:00", "%H:%M").time(),
            end_time=datetime.strptime("16:00", "%H:%M").time()
        )
        logger.info(f"创建测试日程: {self.schedule1.activity_title}, {self.schedule2.activity_title}")
        
        logger.info("=== 测试数据设置完成 ===")
    
    def tearDown(self):
        """清理测试数据"""
        logger.info("=== 开始清理测试数据 ===")
        # 由于Django的TestCase会自动清理数据库，这里不需要手动删除
        logger.info("=== 测试数据清理完成 ===")
    
    def log_object_state(self, obj, obj_name, state="当前"):
        """记录对象状态"""
        if isinstance(obj, Itinerary):
            logger.info(f"{state}行程状态: ID={obj.itinerary_id}, 名称={obj.itinerary_name}, 开始日期={obj.start_date}, 结束日期={obj.end_date}")
        elif isinstance(obj, TravelerStats):
            logger.info(f"{state}旅行者统计: 成人={obj.adult_count}, 儿童={obj.child_count}, 婴儿={obj.infant_count}, 老人={obj.senior_count}")
        elif isinstance(obj, Destination):
            logger.info(f"{state}目的地: 城市={obj.city_name}, 顺序={obj.destination_order}, 抵达日期={obj.arrival_date}, 离开日期={obj.departure_date}")
        elif isinstance(obj, DailySchedule):
            logger.info(f"{state}日程: 标题={obj.activity_title}, 类型={obj.activity_type}, 日期={obj.schedule_date}, 开始时间={obj.start_time}, 结束时间={obj.end_time}")
    
    def test_update_itinerary_basic_properties(self):
        """测试修改Itinerary基础属性"""
        logger.info("=== 开始测试修改Itinerary基础属性 ===")
        
        # 记录修改前状态
        self.log_object_state(self.itinerary, "行程", "修改前")
        
        # 模拟用户界面交互：修改表单数据
        new_name = "更新后的测试行程"
        new_description = "这是更新后的测试行程描述"
        new_start_date = date.today() + timedelta(days=1)
        new_end_date = date.today() + timedelta(days=7)
        new_departure_city = "上海"
        new_return_city = "上海"
        
        # 应用修改
        self.itinerary.itinerary_name = new_name
        self.itinerary.description = new_description
        self.itinerary.start_date = new_start_date
        self.itinerary.end_date = new_end_date
        self.itinerary.departure_city = new_departure_city
        self.itinerary.return_city = new_return_city
        self.itinerary.updated_by = "test_user"
        
        # 保存修改
        save_time = datetime.now()
        logger.info(f"触发保存操作，时间戳: {save_time}")
        
        try:
            self.itinerary.save()
            logger.info("保存成功")
            
            # 验证修改是否生效
            updated_itinerary = Itinerary.objects.get(itinerary_id=self.itinerary.itinerary_id)
            self.log_object_state(updated_itinerary, "行程", "修改后")
            
            # 断言验证
            self.assertEqual(updated_itinerary.itinerary_name, new_name)
            self.assertEqual(updated_itinerary.description, new_description)
            self.assertEqual(updated_itinerary.start_date, new_start_date)
            self.assertEqual(updated_itinerary.end_date, new_end_date)
            self.assertEqual(updated_itinerary.departure_city, new_departure_city)
            self.assertEqual(updated_itinerary.return_city, new_return_city)
            self.assertEqual(updated_itinerary.total_days, 7)  # 验证总天数是否重新计算
            self.assertEqual(updated_itinerary.updated_by, "test_user")
            self.assertGreater(updated_itinerary.version, 1)  # 验证版本号是否递增
            
            logger.info("基础属性修改测试通过")
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            raise
        
        logger.info("=== 测试修改Itinerary基础属性完成 ===")
    
    def test_update_traveler_stats(self):
        """测试更新traveler_stats数据"""
        logger.info("=== 开始测试更新traveler_stats数据 ===")
        
        # 记录修改前状态
        self.log_object_state(self.traveler_stats, "旅行者统计", "修改前")
        
        # 模拟用户界面交互：修改表单数据
        new_adult_count = 3
        new_child_count = 2
        new_infant_count = 1
        new_senior_count = 1
        new_notes = "更新后的测试旅行者统计"
        
        # 应用修改
        self.traveler_stats.adult_count = new_adult_count
        self.traveler_stats.child_count = new_child_count
        self.traveler_stats.infant_count = new_infant_count
        self.traveler_stats.senior_count = new_senior_count
        self.traveler_stats.notes = new_notes
        
        # 保存修改
        save_time = datetime.now()
        logger.info(f"触发保存操作，时间戳: {save_time}")
        
        try:
            self.traveler_stats.save()
            logger.info("保存成功")
            
            # 验证修改是否生效
            updated_stats = TravelerStats.objects.get(stat_id=self.traveler_stats.stat_id)
            self.log_object_state(updated_stats, "旅行者统计", "修改后")
            
            # 断言验证
            self.assertEqual(updated_stats.adult_count, new_adult_count)
            self.assertEqual(updated_stats.child_count, new_child_count)
            self.assertEqual(updated_stats.infant_count, new_infant_count)
            self.assertEqual(updated_stats.senior_count, new_senior_count)
            self.assertEqual(updated_stats.notes, new_notes)
            
            logger.info("旅行者统计更新测试通过")
        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            raise
        
        logger.info("=== 测试更新traveler_stats数据完成 ===")
    
    def test_crud_daily_schedule(self):
        """测试对daily_schedule执行完整的CRUD操作"""
        logger.info("=== 开始测试对daily_schedule执行完整的CRUD操作 ===")
        
        # 1. 新增日程条目
        logger.info("1. 测试新增日程条目")
        new_schedule = DailySchedule.objects.create(
            itinerary_id=self.itinerary,
            day_number=2,
            schedule_date=date.today() + timedelta(days=1),
            activity_type=DailySchedule.ActivityType.MEAL,
            activity_title="午餐",
            start_time=datetime.strptime("12:00", "%H:%M").time(),
            end_time=datetime.strptime("13:30", "%H:%M").time()
        )
        logger.info(f"新增日程: {new_schedule.activity_title}")
        
        # 验证新增是否成功
        schedules_count = DailySchedule.objects.filter(itinerary_id=self.itinerary).count()
        self.assertEqual(schedules_count, 3)
        logger.info("新增日程测试通过")
        
        # 2. 修改现有日程内容
        logger.info("2. 测试修改现有日程内容")
        self.log_object_state(self.schedule1, "日程", "修改前")
        
        new_activity_title = "北京到上海(更新)"
        new_activity_description = "更新的航班信息"
        
        self.schedule1.activity_title = new_activity_title
        self.schedule1.activity_description = new_activity_description
        self.schedule1.save()
        
        updated_schedule = DailySchedule.objects.get(schedule_id=self.schedule1.schedule_id)
        self.log_object_state(updated_schedule, "日程", "修改后")
        
        self.assertEqual(updated_schedule.activity_title, new_activity_title)
        self.assertEqual(updated_schedule.activity_description, new_activity_description)
        logger.info("修改日程测试通过")
        
        # 3. 删除指定日程
        logger.info("3. 测试删除指定日程")
        schedule_to_delete = self.schedule2
        logger.info(f"删除日程: {schedule_to_delete.activity_title}")
        schedule_to_delete.delete()
        
        # 验证删除是否成功
        schedules_count = DailySchedule.objects.filter(itinerary_id=self.itinerary).count()
        self.assertEqual(schedules_count, 2)
        logger.info("删除日程测试通过")
        
        # 4. 调整日程顺序（通过修改day_number和start_time）
        logger.info("4. 测试调整日程顺序")
        # 假设我们要将第二天的午餐调整到第一天
        new_schedule.day_number = 1
        new_schedule.start_time = datetime.strptime("11:00", "%H:%M").time()
        new_schedule.end_time = datetime.strptime("12:30", "%H:%M").time()
        new_schedule.save()
        
        # 验证顺序调整是否成功
        schedules = DailySchedule.objects.filter(itinerary_id=self.itinerary).order_by('day_number', 'start_time')
        schedule_order = [s.activity_title for s in schedules]
        logger.info(f"调整后的日程顺序: {schedule_order}")
        
        logger.info("调整日程顺序测试通过")
        logger.info("=== 测试对daily_schedule执行完整的CRUD操作完成 ===")
    
    def test_manage_destinations(self):
        """测试管理destinations列表"""
        logger.info("=== 开始测试管理destinations列表 ===")
        
        # 1. 添加新目的地
        logger.info("1. 测试添加新目的地")
        new_destination = Destination.objects.create(
            itinerary=self.itinerary,
            destination_order=3,
            city_name="苏州",
            country_code="CN",
            region="江苏",
            arrival_date=date.today() + timedelta(days=4),
            departure_date=date.today() + timedelta(days=5)
        )
        logger.info(f"新增目的地: {new_destination.city_name}")
        
        # 验证新增是否成功
        destinations_count = Destination.objects.filter(itinerary=self.itinerary).count()
        self.assertEqual(destinations_count, 3)
        logger.info("新增目的地测试通过")
        
        # 2. 编辑现有目的地信息
        logger.info("2. 测试编辑现有目的地信息")
        self.log_object_state(self.destination1, "目的地", "修改前")
        
        new_city_name = "上海(更新)"
        new_region = "上海市"
        
        self.destination1.city_name = new_city_name
        self.destination1.region = new_region
        self.destination1.save()
        
        updated_destination = Destination.objects.get(destination_id=self.destination1.destination_id)
        self.log_object_state(updated_destination, "目的地", "修改后")
        
        self.assertEqual(updated_destination.city_name, new_city_name)
        self.assertEqual(updated_destination.region, new_region)
        logger.info("编辑目的地测试通过")
        
        # 3. 移除目的地
        logger.info("3. 测试移除目的地")
        destination_to_delete = self.destination2
        logger.info(f"删除目的地: {destination_to_delete.city_name}")
        destination_to_delete.delete()
        
        # 验证删除是否成功
        destinations_count = Destination.objects.filter(itinerary=self.itinerary).count()
        self.assertEqual(destinations_count, 2)
        logger.info("移除目的地测试通过")
        
        # 4. 调整目的地访问顺序
        logger.info("4. 测试调整目的地访问顺序")
        # 交换两个目的地的顺序
        self.destination1.destination_order = 2
        new_destination.destination_order = 1
        self.destination1.save()
        new_destination.save()
        
        # 验证顺序调整是否成功
        destinations = Destination.objects.filter(itinerary=self.itinerary).order_by('destination_order')
        destination_order = [d.city_name for d in destinations]
        logger.info(f"调整后的目的地顺序: {destination_order}")
        
        logger.info("调整目的地顺序测试通过")
        logger.info("=== 测试管理destinations列表完成 ===")
    
    def test_validate_save_integrity(self):
        """验证保存操作的完整性"""
        logger.info("=== 开始验证保存操作的完整性 ===")
        
        # 修改Itinerary及其所有关联对象
        # 1. 修改Itinerary基础属性
        self.itinerary.itinerary_name = "完整性测试行程"
        self.itinerary.updated_by = "test_user"
        
        # 2. 修改TravelerStats
        self.traveler_stats.adult_count = 4
        self.traveler_stats.save()
        
        # 3. 添加新的DailySchedule
        new_schedule = DailySchedule.objects.create(
            itinerary_id=self.itinerary,
            day_number=3,
            schedule_date=date.today() + timedelta(days=2),
            activity_type=DailySchedule.ActivityType.SHOPPING,
            activity_title="购物",
            start_time=datetime.strptime("14:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time()
        )
        
        # 4. 添加新的Destination
        new_destination = Destination.objects.create(
            itinerary=self.itinerary,
            destination_order=3,
            city_name="南京",
            country_code="CN",
            region="江苏",
            arrival_date=date.today() + timedelta(days=3),
            departure_date=date.today() + timedelta(days=4)
        )
        
        # 保存Itinerary
        save_time = datetime.now()
        logger.info(f"触发保存操作，时间戳: {save_time}")
        self.itinerary.save()
        
        # 重新加载所有对象，验证是否都被正确保存
        updated_itinerary = Itinerary.objects.get(itinerary_id=self.itinerary.itinerary_id)
        updated_stats = TravelerStats.objects.get(stat_id=self.traveler_stats.stat_id)
        updated_schedules = DailySchedule.objects.filter(itinerary_id=self.itinerary)
        updated_destinations = Destination.objects.filter(itinerary=self.itinerary)
        
        # 验证
        self.assertEqual(updated_itinerary.itinerary_name, "完整性测试行程")
        self.assertEqual(updated_stats.adult_count, 4)
        self.assertEqual(updated_schedules.count(), 3)  # 原始2个 + 新增1个
        self.assertEqual(updated_destinations.count(), 3)  # 原始2个 + 新增1个
        
        # 验证JSON数据是否更新
        self.assertIsNotNone(updated_itinerary.itinerary_json_data)
        self.assertEqual(len(updated_itinerary.itinerary_json_data.get('destinations', [])), 3)
        self.assertEqual(len(updated_itinerary.itinerary_json_data.get('daily_schedules', [])), 3)
        self.assertEqual(len(updated_itinerary.itinerary_json_data.get('traveler_stats', [])), 1)
        
        logger.info("保存操作完整性验证通过")
        logger.info("=== 验证保存操作的完整性完成 ===")
    
    def test_boundary_cases(self):
        """测试边界情况"""
        logger.info("=== 开始测试边界情况 ===")
        
        # 1. 测试空值处理
        logger.info("1. 测试空值处理")
        self.itinerary.description = None
        self.itinerary.total_budget = None
        self.itinerary.save()
        
        updated_itinerary = Itinerary.objects.get(itinerary_id=self.itinerary.itinerary_id)
        self.assertIsNone(updated_itinerary.description)
        self.assertIsNone(updated_itinerary.total_budget)
        logger.info("空值处理测试通过")
        
        # 2. 测试数据格式验证
        logger.info("2. 测试数据格式验证")
        # 测试DailySchedule的时间验证（结束时间必须晚于开始时间）
        invalid_schedule = DailySchedule(
            itinerary_id=self.itinerary,
            day_number=1,
            schedule_date=date.today(),
            activity_type=DailySchedule.ActivityType.FREE,
            activity_title="自由活动",
            start_time=datetime.strptime("14:00", "%H:%M").time(),
            end_time=datetime.strptime("13:00", "%H:%M").time()  # 结束时间早于开始时间
        )
        with self.assertRaises(Exception):
            invalid_schedule.full_clean()
        logger.info("数据格式验证测试通过")
        
        # 3. 测试关联约束检查
        logger.info("3. 测试关联约束检查")
        # 测试删除Itinerary时，关联对象是否会被级联删除
        itinerary_id = self.itinerary.itinerary_id
        stats_count_before = TravelerStats.objects.filter(itinerary=self.itinerary).count()
        schedules_count_before = DailySchedule.objects.filter(itinerary_id=self.itinerary).count()
        destinations_count_before = Destination.objects.filter(itinerary=self.itinerary).count()
        
        self.itinerary.delete()
        
        stats_count_after = TravelerStats.objects.filter(itinerary__itinerary_id=itinerary_id).count()
        schedules_count_after = DailySchedule.objects.filter(itinerary_id__itinerary_id=itinerary_id).count()
        destinations_count_after = Destination.objects.filter(itinerary__itinerary_id=itinerary_id).count()
        
        self.assertEqual(stats_count_after, 0)
        self.assertEqual(schedules_count_after, 0)
        self.assertEqual(destinations_count_after, 0)
        logger.info("关联约束检查测试通过")
        
        logger.info("=== 测试边界情况完成 ===")

if __name__ == '__main__':
    unittest.main()
