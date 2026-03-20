# webhook_views.py 代码改进计划

> **For Claude:** REQUIRED SUB-SKILL: Use `executing-plans` skill to implement this plan task-by-task.

**Goal:** 全面改进 webhook_views.py 的代码质量，修复严重bug，优化性能，增强安全性

**Architecture:** 
- 创建专门的 validator 层用于输入验证
- 创建 service 层封装业务逻辑和数据操作
- 添加日志脱敏工具函数
- 重构现有 View 为更小、更专注的组件
- 统一使用 DRF Serializer 进行数据验证

**Tech Stack:** Django REST Framework, drf-yasg, json, logging

---

## 📋 问题分析摘要

### 1. 🔴 静默失败 (CRITICAL BUG)
**位置:** 第 146-154 行
**问题:** 数据库操作失败却返回 HTTP 200 OK
```python
except Exception as db_error:
    logger.error(f'数据库操作失败: {db_error}', exc_info=True)
    return JsonResponse({
        'success': True,  # ❌ BUG: 应该是 False
        'message': '...',
    }, status=200)  # ❌ BUG: 应该是 500
```
**影响:** 调用方无法得知数据未保存，导致数据不一致

### 2. 🟡 长函数
**位置:** 
- `ItineraryWebhookView.post()` - 130+ 行
- `RequirementWebhookView.post()` - 200+ 行
- `create_daily_schedules()` - 75+ 行

**问题:** 单一方法承担了太多职责，难以测试和维护

### 3. 🟡 N+1 查询
**位置:** `create_daily_schedules()` 方法
```python
# 循环内查询目的地
for day_schedule in daily_schedules:
    destination = Destination.objects.filter(...).first()  # N+1
    
    for activity in activities:
        # 每个活动都单独查询
        if activity_type == ATTRACTION:
            attraction = Attraction.objects.get(...)  # N+1
        elif activity_type == MEAL:
            restaurant = Restaurant.objects.get(...)  # N+1
        elif activity_type == CHECK_IN/CHECK_OUT:
            hotel = Hotel.objects.get(...)  # N+1
```
**影响:** 假设有 10 天行程，每天 5 个活动 = 最多 51 次数据库查询

### 4. 🟠 输入验证缺失
**问题:**
- 只检查字段存在，不验证类型
- 无数据大小限制
- 无格式验证（如日期格式、ID格式）
- 无恶意数据检测

### 5. 🟠 日志敏感信息泄露
**位置:**
- 第 340 行: `json.dumps(data, ensure_ascii=False)[:500]`
- 第 585 行: `user_input[:100]` - 可能包含 PII
- 多处记录完整请求数据

---

## 📝 实施计划

### 阶段 1: 日志脱敏工具 (安全优先)

#### Task 1.1: 创建日志脱敏工具

**Files:**
- Create: `apps/api/utils/logging_utils.py`
- Modify: `apps/api/views/webhook_views.py` (导入使用)

**Step 1: 创建日志脱敏模块**

```python
# apps/api/utils/logging_utils.py
"""日志脱敏工具模块"""
import re
import logging
from typing import Any, Dict, List, Optional
from functools import wraps

# 敏感字段名模式
SENSITIVE_FIELD_PATTERNS = [
    'password', 'secret', 'token', 'api_key', 'apikey',
    'phone', 'mobile', 'tel', 'email', 'address',
    'id_card', 'idcard', 'passport', 'credit_card',
    'card_number', 'bank_account', 'ssn'
]

# 手机号正则 (中国)
PHONE_PATTERN = re.compile(r'1[3-9]\d{9}')
# 邮箱正则
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
# 身份证正则
ID_CARD_PATTERN = re.compile(r'\d{17}[\dXx]')


class LogSanitizer:
    """日志脱敏器"""
    
    @staticmethod
    def mask_phone(text: str) -> str:
        """脱敏手机号: 13812345678 -> 138****5678"""
        def replacer(match):
            phone = match.group()
            return phone[:3] + '****' + phone[-4:]
        return PHONE_PATTERN.sub(replacer, text)
    
    @staticmethod
    def mask_email(text: str) -> str:
        """脱敏邮箱: user@example.com -> u***@example.com"""
        def replacer(match):
            email = match.group()
            local = email.split('@')[0]
            domain = email.split('@')[1] if '@' in email else ''
            return f"{local[0]}***@{domain}"
        return EMAIL_PATTERN.sub(replacer, text)
    
    @staticmethod
    def mask_id_card(text: str) -> str:
        """脱敏身份证: 110101199001011234 -> 110101********1234"""
        def replacer(match):
            id_card = match.group()
            return id_card[:6] + '********' + id_card[-4:]
        return ID_CARD_PATTERN.sub(replacer, text)
    
    @classmethod
    def is_sensitive_field(cls, field_name: str) -> bool:
        """判断字段是否为敏感字段"""
        field_lower = field_name.lower()
        for pattern in SENSITIVE_FIELD_PATTERNS:
            if pattern in field_lower:
                return True
        return False
    
    @classmethod
    def sanitize_dict(cls, data: Any, depth: int = 0, max_depth: int = 10) -> Any:
        """递归脱敏字典中的敏感信息"""
        if depth > max_depth:
            return '[MAX_DEPTH_EXCEEDED]'
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if cls.is_sensitive_field(key):
                    if isinstance(value, str) and len(value) > 4:
                        result[key] = value[:2] + '***' + value[-2:]
                    else:
                        result[key] = '***'
                else:
                    result[key] = cls.sanitize_dict(value, depth + 1, max_depth)
            return result
        
        elif isinstance(data, list):
            return [cls.sanitize_dict(item, depth + 1, max_depth) for item in data]
        
        elif isinstance(data, str):
            text = cls.mask_phone(data)
            text = cls.mask_email(text)
            text = cls.mask_id_card(text)
            # 截断过长字符串
            if len(text) > 200:
                return text[:200] + '...[TRUNCATED]'
            return text
        
        return data
    
    @classmethod
    def sanitize_for_logging(cls, data: Any, include_fields: Optional[List[str]] = None) -> str:
        """
        将数据脱敏后转为日志字符串
        
        Args:
            data: 要脱敏的数据
            include_fields: 如果指定，只记录这些字段（用于白名单模式）
        """
        import json
        
        if include_fields:
            # 白名单模式
            if isinstance(data, dict):
                filtered = {k: v for k, v in data.items() if k in include_fields}
                data = filtered
            else:
                data = {}
        
        sanitized = cls.sanitize_dict(data)
        
        try:
            return json.dumps(sanitized, ensure_ascii=False, default=str)
        except Exception:
            return str(sanitized)


def log_webhook_call(logger: logging.Logger, data: Dict, message: str, 
                     include_fields: Optional[List[str]] = None,
                     max_length: int = 500):
    """
    记录 webhook 调用日志（自动脱敏）
    
    Args:
        logger: 日志记录器
        data: 请求数据
        message: 日志消息
        include_fields: 只记录的字段列表（可选）
        max_length: 最大日志长度
    """
    sanitized = LogSanitizer.sanitize_for_logging(data, include_fields)
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + '...[TRUNCATED]'
    logger.info(f"{message}: {sanitized}")
```

**Step 2: 验证模块存在性**

Run: `ls -la apps/api/utils/`
Expected: 目录存在或自动创建

---

### 阶段 2: 创建 Serializer 层 (输入验证)

#### Task 2.1: 创建 ItineraryWebhookSerializer

**Files:**
- Create: `apps/api/serializers/webhook_serializers.py`

**Step 1: 创建 Webhook 序列化器**

```python
# apps/api/serializers/webhook_serializers.py
"""Webhook API 专用序列化器"""
from rest_framework import serializers
from apps.models.requirement import Requirement
from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant


class ActivitySerializer(serializers.Serializer):
    """单个活动序列化器"""
    activity_title = serializers.CharField(max_length=200)
    activity_type = serializers.ChoiceField(choices=[
        'FLIGHT', 'TRAIN', 'ATTRACTION', 'MEAL', 
        'TRANSPORT', 'SHOPPING', 'FREE', 'CHECK_IN', 'CHECK_OUT', 'OTHER'
    ])
    start_time = serializers.TimeField(format='%H:%M:%S')
    end_time = serializers.TimeField(format='%H:%M:%S')
    activity_description = serializers.CharField(required=False, allow_blank=True)
    id_reference = serializers.CharField(required=False, allow_blank=True)


class DayScheduleSerializer(serializers.Serializer):
    """每日行程序列化器"""
    day = serializers.IntegerField(min_value=1)
    date = serializers.DateField()
    city = serializers.CharField(max_length=100)
    activities = ActivitySerializer(many=True)


class DestinationSerializer(serializers.Serializer):
    """目的地序列化器"""
    city_name = serializers.CharField(max_length=100)
    country_code = serializers.CharField(max_length=3, required=False, default='CN')
    destination_order = serializers.IntegerField(min_value=1)
    arrival_date = serializers.DateField()
    departure_date = serializers.DateField()


class TravelerStatsInputSerializer(serializers.Serializer):
    """旅行者统计输入序列化器"""
    adults = serializers.IntegerField(min_value=0, default=0)
    children = serializers.IntegerField(min_value=0, default=0)
    infants = serializers.IntegerField(min_value=0, default=0)
    seniors = serializers.IntegerField(min_value=0, default=0)


class ItineraryWebhookInputSerializer(serializers.Serializer):
    """Itinerary Webhook 输入序列化器"""
    requirement_id = serializers.CharField(max_length=100)
    itinerary_name = serializers.CharField(max_length=200)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    # 可选字段
    destinations = DestinationSerializer(many=True, required=False)
    traveler_stats = TravelerStatsInputSerializer(required=False)
    daily_schedules = DayScheduleSerializer(many=True, required=False)
    
    def validate(self, data):
        """交叉验证"""
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': '结束日期不能早于开始日期'
                })
        return data


class RequirementWebhookInputSerializer(serializers.Serializer):
    """Requirement Webhook 输入序列化器"""
    user_input = serializers.CharField(max_length=5000, required=False)
    structured_data = serializers.DictField(required=False)
    requirement_id = serializers.CharField(max_length=100, required=False)
    llm_info = serializers.DictField(required=False)
    output = serializers.DictField(required=False)
    
    def validate(self, data):
        """验证至少有一个有效数据源"""
        if not any([
            data.get('user_input'),
            data.get('structured_data'),
            data.get('requirement_id')
        ]):
            raise serializers.ValidationError(
                '至少需要提供 user_input, structured_data 或 requirement_id 之一'
            )
        return data
```

---

### 阶段 3: 修复静默失败 Bug (关键修复)

#### Task 3.1: 修复数据库失败返回 200 的问题

**Files:**
- Modify: `apps/api/views/webhook_views.py:146-154`

**Step 1: 修改异常处理逻辑**

在 `ItineraryWebhookView.post()` 方法中，将:

```python
except Exception as db_error:
    logger.error(f'数据库操作失败: {db_error}', exc_info=True)
    # 即使数据库操作失败，也要返回成功的响应，因为JSON解析和验证已经成功
    return JsonResponse({
        'success': True,
        'message': 'JSON解析和验证成功，但数据库操作失败。这可能是因为数据库服务不可用。',
        'itinerary_name': data.get('itinerary_name'),
        'requirement_id': data.get('requirement_id')
    }, status=200)
```

替换为:

```python
except Exception as db_error:
    logger.error(f'数据库操作失败: {db_error}', exc_info=True)
    # 明确返回错误状态，让调用方知道数据未保存
    return JsonResponse({
        'success': False,
        'error': '数据库操作失败，数据未保存',
        'error_code': 'DB_OPERATION_FAILED',
        'itinerary_name': data.get('itinerary_name') if data else None,
        'requirement_id': data.get('requirement_id') if data else None
    }, status=500)
```

**Step 2: 添加错误响应结构化**

在文件顶部添加错误码常量:

```python
# 错误码定义
class WebhookErrorCode:
    INVALID_JSON = 'INVALID_JSON'
    MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    REQUIREMENT_NOT_FOUND = 'REQUIREMENT_NOT_FOUND'
    DB_OPERATION_FAILED = 'DB_OPERATION_FAILED'
    N8N_WEBHOOK_ERROR = 'N8N_WEBHOOK_ERROR'
    N8N_TIMEOUT = 'N8N_TIMEOUT'
    INTERNAL_ERROR = 'INTERNAL_ERROR'
```

---

### 阶段 4: 重构长函数 (代码结构)

#### Task 4.1: 提取数据处理服务

**Files:**
- Create: `apps/api/services/webhook_services.py`

**Step 1: 创建 Webhook 服务层**

```python
# apps/api/services/webhook_services.py
"""Webhook 业务逻辑服务层"""
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date, time
import logging

from django.db import transaction
from django.db.models import Q

from apps.models.requirement import Requirement
from apps.models.itinerary import Itinerary
from apps.models.destinations import Destination
from apps.models.traveler_stats import TravelerStats
from apps.models.daily_schedule import DailySchedule
from apps.models.attraction import Attraction
from apps.models.hotel import Hotel
from apps.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class ItineraryWebhookService:
    """行程 Webhook 服务"""
    
    def __init__(self, validated_data: Dict):
        self.data = validated_data
        self.itinerary: Optional[Itinerary] = None
        self.destinations_cache: Dict[str, Destination] = {}
        self.attractions_cache: Dict[str, Attraction] = {}
        self.hotels_cache: Dict[str, Hotel] = {}
        self.restaurants_cache: Dict[str, Restaurant] = {}
    
    def process(self, requirement: Requirement) -> Tuple[bool, str, Optional[Itinerary]]:
        """
        处理行程数据
        
        Returns:
            Tuple[成功标志, 消息, 行程对象]
        """
        try:
            with transaction.atomic():
                # 1. 预加载关联数据 (解决 N+1 问题)
                self._preload_related_data()
                
                # 2. 创建行程主表
                self.itinerary = self._create_itinerary(requirement)
                
                # 3. 创建关联关系
                self._create_requirement_itinerary(requirement)
                
                # 4. 创建目的地
                self._create_destinations()
                
                # 5. 创建旅行者统计
                self._create_traveler_stats()
                
                # 6. 创建每日行程
                self._create_daily_schedules()
                
                return True, '行程数据处理成功', self.itinerary
                
        except Exception as e:
            logger.error(f'处理行程数据失败: {e}', exc_info=True)
            return False, str(e), None
    
    def _preload_related_data(self):
        """预加载所有关联数据以避免 N+1 查询"""
        requirement_id = self.data.get('requirement_id')
        
        # 预加载目的地
        destinations = self.data.get('destinations', [])
        destination_cities = [d.get('city_name') for d in destinations]
        if destination_cities:
            self.destinations_cache = {
                d.city_name: d for d in Destination.objects.filter(
                    itinerary=self.itinerary,
                    city_name__in=destination_cities
                )
            }
        
        # 预加载所有可能用到的景点
        attraction_ids = []
        hotel_ids = []
        restaurant_ids = []
        
        for day_schedule in self.data.get('daily_schedules', []):
            for activity in day_schedule.get('activities', []):
                ref_id = activity.get('id_reference')
                if activity.get('activity_type') == 'ATTRACTION':
                    attraction_ids.append(ref_id)
                elif activity.get('activity_type') in ['CHECK_IN', 'CHECK_OUT']:
                    hotel_ids.append(ref_id)
                elif activity.get('activity_type') == 'MEAL':
                    restaurant_ids.append(ref_id)
        
        if attraction_ids:
            self.attractions_cache = {
                a.attraction_id: a for a in Attraction.objects.filter(
                    attraction_id__in=attraction_ids
                )
            }
        if hotel_ids:
            self.hotels_cache = {
                h.hotel_id: h for h in Hotel.objects.filter(
                    hotel_id__in=hotel_ids
                )
            }
        if restaurant_ids:
            self.restaurants_cache = {
                r.restaurant_id: r for r in Restaurant.objects.filter(
                    restaurant_id__in=restaurant_ids
                )
            }
    
    def _create_itinerary(self, requirement: Requirement) -> Itinerary:
        """创建行程主表"""
        itinerary = Itinerary(
            itinerary_name=self.data.get('itinerary_name', '未命名行程'),
            start_date=self.data.get('start_date'),
            end_date=self.data.get('end_date'),
            travel_purpose=Itinerary.TravelPurpose.LEISURE,
            contact_person=requirement.contact_person or '测试用户',
            contact_phone=requirement.contact_phone or '13800138000',
            contact_company=requirement.contact_company,
            departure_city=requirement.origin_name or '上海',
            return_city=requirement.origin_name or '上海',
            current_status=Itinerary.CurrentStatus.DRAFT,
            created_by='webhook_user'
        )
        itinerary.save()
        return itinerary
    
    def _create_requirement_itinerary(self, requirement: Requirement):
        """创建需求与行程关联"""
        from apps.models.requirement_itinerary import RequirementItinerary
        
        requirement_itinerary = RequirementItinerary(
            requirement=requirement,
            itinerary=self.itinerary
        )
        requirement_itinerary.save()
        logger.info(
            f'创建需求与行程关联成功: '
            f'requirement_id={requirement.requirement_id}, '
            f'itinerary_id={self.itinerary.itinerary_id}'
        )
    
    def _create_destinations(self):
        """批量创建目的地"""
        destinations = self.data.get('destinations', [])
        
        for dest_data in destinations:
            destination = Destination(
                itinerary=self.itinerary,
                destination_order=dest_data.get('destination_order'),
                city_name=dest_data.get('city_name'),
                country_code=dest_data.get('country_code', 'CN'),
                arrival_date=dest_data.get('arrival_date'),
                departure_date=dest_data.get('departure_date')
            )
            destination.save()
            self.destinations_cache[dest_data.get('city_name')] = destination
    
    def _create_traveler_stats(self):
        """创建旅行者统计"""
        traveler_stats_info = self.data.get('traveler_stats', {})
        
        traveler_stats = TravelerStats(
            itinerary=self.itinerary,
            adult_count=traveler_stats_info.get('adults', 0),
            child_count=traveler_stats_info.get('children', 0),
            infant_count=traveler_stats_info.get('infants', 0),
            senior_count=traveler_stats_info.get('seniors', 0)
        )
        traveler_stats.save()
    
    def _create_daily_schedules(self):
        """批量创建每日行程 (使用预加载的数据)"""
        daily_schedules = self.data.get('daily_schedules', [])
        
        for day_schedule in daily_schedules:
            day_number = day_schedule.get('day')
            schedule_date = day_schedule.get('date')
            city = day_schedule.get('city')
            
            # 使用缓存的目的地
            destination = self.destinations_cache.get(city)
            
            # 批量处理活动
            activities = day_schedule.get('activities', [])
            for activity in activities:
                self._create_activity_schedule(
                    day_number, schedule_date, city, destination, activity
                )
    
    def _create_activity_schedule(
        self, day_number: int, schedule_date: date, city: str,
        destination: Optional[Destination], activity: Dict
    ):
        """创建单个活动记录"""
        activity_type = self._map_activity_type(activity.get('activity_type'))
        
        # 使用缓存的关联对象
        attraction = self.hotel = self.restaurant = None
        
        if activity_type == DailySchedule.ActivityType.ATTRACTION:
            attraction = self.attractions_cache.get(activity.get('id_reference'))
        elif activity_type in [DailySchedule.ActivityType.CHECK_IN, DailySchedule.ActivityType.CHECK_OUT]:
            self.hotel = self.hotels_cache.get(activity.get('id_reference'))
        elif activity_type == DailySchedule.ActivityType.MEAL:
            self.restaurant = self.restaurants_cache.get(activity.get('id_reference'))
        
        schedule = DailySchedule(
            itinerary_id=self.itinerary,
            day_number=day_number,
            schedule_date=schedule_date,
            destination_id=destination,
            activity_type=activity_type,
            activity_title=activity.get('activity_title'),
            activity_description=activity.get('activity_description', ''),
            start_time=activity.get('start_time'),
            end_time=activity.get('end_time'),
            attraction_id=attraction,
            hotel_id=self.hotel,
            restaurant_id=self.restaurant,
            booking_status=DailySchedule.BookingStatus.NOT_BOOKED
        )
        schedule.save()
    
    @staticmethod
    def _map_activity_type(activity_type_str: str) -> str:
        """映射活动类型"""
        mapping = {
            'FLIGHT': DailySchedule.ActivityType.FLIGHT,
            'TRAIN': DailySchedule.ActivityType.TRAIN,
            'ATTRACTION': DailySchedule.ActivityType.ATTRACTION,
            'MEAL': DailySchedule.ActivityType.MEAL,
            'TRANSPORT': DailySchedule.ActivityType.TRANSPORT,
            'SHOPPING': DailySchedule.ActivityType.SHOPPING,
            'FREE': DailySchedule.ActivityType.FREE,
            'CHECK_IN': DailySchedule.ActivityType.CHECK_IN,
            'CHECK_OUT': DailySchedule.ActivityType.CHECK_OUT,
            'OTHER': DailySchedule.ActivityType.OTHER
        }
        return mapping.get(activity_type_str, DailySchedule.ActivityType.OTHER)


class RequirementWebhookService:
    """需求 Webhook 服务"""
    
    def __init__(self, validated_data: Dict):
        self.data = validated_data
        self.requirement_id: Optional[str] = None
    
    def process(self) -> Tuple[bool, str, Optional[str], Optional[Requirement]]:
        """
        处理需求数据
        
        Returns:
            Tuple[成功标志, 消息, 需求ID, 需求对象]
        """
        try:
            # 提取数据
            requirement_data = self._extract_structured_data()
            
            # 生成需求ID
            self.requirement_id = self._generate_requirement_id()
            
            # 构建需求对象
            requirement = self._build_requirement(requirement_data)
            
            # 保存
            requirement.save()
            
            logger.info(f'需求保存成功，ID: {self.requirement_id}')
            return True, '需求处理成功', self.requirement_id, requirement
            
        except Exception as e:
            logger.error(f'处理需求失败: {e}', exc_info=True)
            return False, str(e), None, None
    
    def _extract_structured_data(self) -> Dict:
        """提取结构化数据"""
        # 优先使用 structured_data，否则使用原始数据
        if 'structured_data' in self.data:
            return self.data['structured_data']
        
        # 移除顶层元数据字段
        result = {k: v for k, v in self.data.items() 
                  if k not in ['user_input', 'requirement_id', 'llm_info', 'output']}
        return result
    
    def _generate_requirement_id(self) -> str:
        """生成唯一的 requirement_id"""
        import time
        
        max_attempts = 100
        for attempt in range(max_attempts):
            today = datetime.now().strftime('%Y%m%d')
            prefix = f'REQ_{today}_'
            
            # 获取当前最大序号
            max_seq = Requirement.objects.filter(
                requirement_id__startswith=prefix
            ).aggregate(
                max_seq=Max(
                    Cast(
                        Substr(F('requirement_id'), len(prefix) + 1),
                        output_field=IntegerField()
                    )
                )
            )['max_seq'] or 0
            
            new_id = f'{prefix}{max_seq + 1:03d}'
            
            if not Requirement.objects.filter(requirement_id=new_id).exists():
                return new_id
            
            time.sleep(0.01)
        
        raise ValueError('无法生成唯一的 requirement_id')
    
    def _build_requirement(self, data: Dict) -> Requirement:
        """构建 Requirement 对象"""
        base_info = data.get('base_info', {})
        preferences = data.get('preferences', {})
        budget = data.get('budget', {})
        metadata = data.get('metadata', {})
        
        # 解析日期
        travel_start = self._parse_date(
            base_info.get('travel_date', {}).get('start_date')
        )
        travel_end = self._parse_date(
            base_info.get('travel_date', {}).get('end_date')
        )
        
        # 解析预算
        budget_range = budget.get('range', {})
        budget_min = self._parse_decimal(budget_range.get('min'))
        budget_max = self._parse_decimal(budget_range.get('max'))
        
        return Requirement(
            requirement_id=self.requirement_id,
            origin_name=base_info.get('origin', {}).get('name', ''),
            origin_code=base_info.get('origin', {}).get('code', ''),
            origin_type=base_info.get('origin', {}).get('type', ''),
            destination_cities=base_info.get('destination_cities', []),
            trip_days=base_info.get('trip_days', 1),
            group_adults=base_info.get('group_size', {}).get('adults', 0),
            group_children=base_info.get('group_size', {}).get('children', 0),
            group_seniors=base_info.get('group_size', {}).get('seniors', 0),
            group_total=base_info.get('group_size', {}).get('total', 1),
            travel_start_date=travel_start,
            travel_end_date=travel_end,
            travel_date_flexible=base_info.get('travel_date', {}).get('is_flexible', False),
            transportation_type=preferences.get('transportation', {}).get('type', ''),
            transportation_notes=preferences.get('transportation', {}).get('notes', ''),
            hotel_level=preferences.get('accommodation', {}).get('level', ''),
            hotel_requirements=preferences.get('accommodation', {}).get('requirements', ''),
            trip_rhythm=preferences.get('itinerary', {}).get('rhythm', ''),
            preference_tags=preferences.get('itinerary', {}).get('tags', []),
            must_visit_spots=preferences.get('itinerary', {}).get('special_constraints', {}).get('must_visit_spots', []),
            avoid_activities=preferences.get('itinerary', {}).get('special_constraints', {}).get('avoid_activities', []),
            budget_level=budget.get('level', ''),
            budget_currency=budget.get('currency', 'CNY'),
            budget_min=budget_min,
            budget_max=budget_max,
            budget_notes=budget.get('budget_notes', ''),
            source_type=metadata.get('source_type', 'NaturalLanguage'),
            status=metadata.get('status', 'Confirmed'),
            assumptions=metadata.get('assumptions', []),
            is_template=metadata.get('is_template', False),
            template_name=metadata.get('template_info', {}).get('name', ''),
            template_category=metadata.get('template_info', {}).get('category', ''),
            extension=data.get('extension', {})
        )
    
    def _parse_date(self, value) -> Optional[date]:
        """解析日期"""
        if not value:
            return None
        if isinstance(value, date):
            return value
        try:
            return datetime.fromisoformat(str(value)).date()
        except (ValueError, TypeError):
            logger.warning(f'无法解析日期: {value}')
            return None
    
    def _parse_decimal(self, value) -> Optional[Decimal]:
        """解析 Decimal"""
        if not value:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            logger.warning(f'无法解析金额: {value}')
            return None
```

> **注意:** 需要在 `_generate_requirement_id` 中添加必要的导入:
> ```python
> from django.db.models import Max, F
> from django.db.models.functions import Substr
> from django.db.models import IntegerField
> ```

---

### 阶段 5: 重构 View 层 (使用新服务)

#### Task 5.1: 重构 ItineraryWebhookView

**Files:**
- Modify: `apps/api/views/webhook_views.py`

**Step 1: 重构 ItineraryWebhookView**

```python
@method_decorator(csrf_exempt, name='dispatch')
class ItineraryWebhookView(View):
    """处理n8n webhook返回的行程数据"""
    
    def post(self, request, *args, **kwargs):
        """接收并处理webhook数据"""
        from apps.api.utils.logging_utils import log_webhook_call
        from apps.api.serializers.webhook_serializers import ItineraryWebhookInputSerializer
        
        try:
            # 1. 解析请求体
            content = request.body.decode('utf-8')
            raw_data = json.loads(content)
            
            # 2. 日志记录（脱敏后）
            log_webhook_call(
                logger, raw_data, 
                '接收到行程webhook请求',
                include_fields=['requirement_id', 'itinerary_name', 'start_date', 'end_date']
            )
            
            # 3. 处理 output 字段
            data = raw_data.get('output', raw_data)
            
            # 4. 输入验证
            serializer = ItineraryWebhookInputSerializer(data=data)
            if not serializer.is_valid():
                logger.warning(f'输入验证失败: {serializer.errors}')
                return JsonResponse({
                    'success': False,
                    'error': '输入验证失败',
                    'error_code': WebhookErrorCode.VALIDATION_FAILED,
                    'details': serializer.errors
                }, status=400)
            
            validated_data = serializer.validated_data
            
            # 5. 验证关联需求存在
            requirement_id = validated_data.get('requirement_id')
            try:
                requirement = Requirement.objects.get(requirement_id=requirement_id)
            except Requirement.DoesNotExist:
                logger.error(f'需求不存在: {requirement_id}')
                return JsonResponse({
                    'success': False,
                    'error': f'需求不存在: {requirement_id}',
                    'error_code': WebhookErrorCode.REQUIREMENT_NOT_FOUND
                }, status=404)
            
            # 6. 调用服务处理
            from apps.api.services.webhook_services import ItineraryWebhookService
            service = ItineraryWebhookService(validated_data)
            success, message, itinerary = service.process(requirement)
            
            if success:
                logger.info(f'行程创建成功: itinerary_id={itinerary.itinerary_id}')
                return JsonResponse({
                    'success': True,
                    'itinerary_id': itinerary.itinerary_id,
                    'itinerary_name': itinerary.itinerary_name
                }, status=200)
            else:
                logger.error(f'行程创建失败: {message}')
                return JsonResponse({
                    'success': False,
                    'error': message,
                    'error_code': WebhookErrorCode.DB_OPERATION_FAILED
                }, status=500)
                
        except json.JSONDecodeError as e:
            logger.error(f'JSON格式错误: {e}')
            return JsonResponse({
                'success': False,
                'error': f'JSON格式错误: {str(e)}',
                'error_code': WebhookErrorCode.INVALID_JSON
            }, status=400)
        except Exception as e:
            logger.error(f'处理行程数据失败: {e}', exc_info=True)
            return JsonResponse({
                'success': False,
                'error': f'处理数据失败: {str(e)}',
                'error_code': WebhookErrorCode.INTERNAL_ERROR
            }, status=500)
```

#### Task 5.2: 重构 RequirementWebhookView

**Files:**
- Modify: `apps/api/views/webhook_views.py`

**Step 1: 简化 RequirementWebhookView.post 方法**

```python
@method_decorator(csrf_exempt, name='dispatch')
class RequirementWebhookView(APIView):
    """处理n8n webhook返回的旅游需求数据"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(...)
    def post(self, request, *args, **kwargs):
        from apps.api.utils.logging_utils import log_webhook_call
        from apps.api.serializers.webhook_serializers import RequirementWebhookInputSerializer
        from apps.api.services.webhook_services import RequirementWebhookService
        
        try:
            raw_data = request.data
            
            # 处理列表结构
            if isinstance(raw_data, list) and len(raw_data) > 0:
                raw_data = raw_data[0]
            
            # 处理 output 字段
            if 'output' in raw_data:
                raw_data = raw_data['output']
            
            # 日志记录（脱敏）
            log_webhook_call(
                logger, raw_data,
                '接收到需求webhook请求',
                include_fields=['requirement_id', 'source_type', 'status']
            )
            
            # 输入验证
            serializer = RequirementWebhookInputSerializer(data=raw_data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': '输入验证失败',
                    'error_code': WebhookErrorCode.VALIDATION_FAILED,
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 调用服务处理
            service = RequirementWebhookService(serializer.validated_data)
            success, message, requirement_id, requirement = service.process()
            
            if success:
                return Response({
                    'success': True,
                    'requirement_id': requirement_id,
                    'structured_data': serializer.validated_data.get('structured_data', {}),
                    'validation_errors': None,
                    'warnings': [],
                    'error': None
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': message,
                    'error_code': WebhookErrorCode.DB_OPERATION_FAILED
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f'处理需求解析数据失败: {e}', exc_info=True)
            return Response({
                'success': False,
                'error': f'处理数据失败: {str(e)}',
                'error_code': WebhookErrorCode.INTERNAL_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

### 阶段 6: 添加单元测试

#### Task 6.1: 创建 Webhook 测试文件

**Files:**
- Create: `tests/api/test_webhook_views.py`

**Step 1: 创建测试文件**

```python
"""Webhook API 测试"""
import json
from datetime import date, time
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.http import JsonResponse

from apps.api.views.webhook_views import (
    ItineraryWebhookView, 
    RequirementWebhookView,
    WebhookErrorCode
)
from apps.api.serializers.webhook_serializers import (
    ItineraryWebhookInputSerializer,
    RequirementWebhookInputSerializer
)


class ItineraryWebhookSerializerTest(TestCase):
    """ItineraryWebhookInputSerializer 测试"""
    
    def test_valid_data(self):
        """测试有效数据"""
        data = {
            'requirement_id': 'REQ_20240101_001',
            'itinerary_name': '测试行程',
            'start_date': '2024-03-01',
            'end_date': '2024-03-05'
        }
        serializer = ItineraryWebhookInputSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_missing_required_field(self):
        """测试缺少必需字段"""
        data = {
            'requirement_id': 'REQ_20240101_001'
            # 缺少 itinerary_name
        }
        serializer = ItineraryWebhookInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('itinerary_name', serializer.errors)
    
    def test_end_date_before_start_date(self):
        """测试结束日期早于开始日期"""
        data = {
            'requirement_id': 'REQ_20240101_001',
            'itinerary_name': '测试行程',
            'start_date': '2024-03-05',
            'end_date': '2024-03-01'  # 早于开始日期
        }
        serializer = ItineraryWebhookInputSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', str(serializer.errors))


class ItineraryWebhookViewTest(TestCase):
    """ItineraryWebhookView 测试"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.view = ItineraryWebhookView.as_view()
    
    @patch('apps.api.views.webhook_views.Requirement.objects')
    def test_db_failure_returns_500(self, mock_requirement):
        """测试数据库失败时返回 500 而非 200"""
        # 模拟数据库失败
        mock_requirement.get.side_effect = Exception('Database connection failed')
        
        request = self.factory.post(
            '/api/webhook/itinerary/',
            data=json.dumps({
                'requirement_id': 'REQ_20240101_001',
                'itinerary_name': '测试',
                'start_date': '2024-03-01',
                'end_date': '2024-03-05'
            }),
            content_type='application/json'
        )
        
        response = self.view(request)
        
        # 关键断言：数据库失败应返回 500
        self.assertEqual(response.status_code, 500)
        
        response_data = json.loads(response.content)
        self.assertFalse(response_data.get('success'))
        self.assertEqual(
            response_data.get('error_code'), 
            WebhookErrorCode.DB_OPERATION_FAILED
        )


class LogSanitizerTest(TestCase):
    """日志脱敏工具测试"""
    
    def test_mask_phone(self):
        """测试手机号脱敏"""
        from apps.api.utils.logging_utils import LogSanitizer
        
        text = "联系电话: 13812345678"
        result = LogSanitizer.sanitize_dict({'phone': '13812345678'})
        self.assertEqual(result['phone'], '13***5678')
    
    def test_mask_email(self):
        """测试邮箱脱敏"""
        from apps.api.utils.logging_utils import LogSanitizer
        
        result = LogSanitizer.sanitize_dict({'email': 'user@example.com'})
        self.assertEqual(result['email'], 'u***@example.com')
    
    def test_sensitive_field_masking(self):
        """测试敏感字段自动脱敏"""
        from apps.api.utils.logging_utils import LogSanitizer
        
        data = {
            'password': 'secret123',
            'api_key': 'sk-abc123xyz',
            'username': 'john_doe'  # 非敏感字段
        }
        
        result = LogSanitizer.sanitize_dict(data)
        
        self.assertEqual(result['password'], 'se***23')
        self.assertEqual(result['api_key'], 'sk***yz')
        self.assertEqual(result['username'], 'john_doe')  # 保持原样
```

**Step 2: 运行测试验证**

Run: `python manage.py test tests.api.test_webhook_views -v 2`
Expected: 所有测试通过

---

## 📊 预期改进效果

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| **静默失败 Bug** | 存在 | ✅ 修复 |
| **post() 方法行数** | 130+ / 200+ | ~40 行 |
| **N+1 查询次数** | 最多 51 次 | 最多 4 次 |
| **输入验证** | 基础检查 | 完整 Schema 验证 |
| **敏感信息泄露** | 存在 | ✅ 已脱敏 |

---

## 🚀 实施顺序建议

1. **Task 1.1** - 创建日志脱敏工具 (安全基础)
2. **Task 3.1** - 修复静默失败 Bug (关键修复)
3. **Task 2.1** - 创建 Serializer 层 (验证基础)
4. **Task 4.1** - 创建服务层 (重构核心)
5. **Task 5.1/5.2** - 重构 View 层 (使用新代码)
6. **Task 6.1** - 添加单元测试 (质量保证)

---

**Plan complete and saved to `docs/plans/webhook-views-improvement-plan.md`**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
