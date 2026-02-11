# 旅游需求模型设计文档

## 概述

旅游需求模型是一个标准化的数据模型，用于捕获和管理用户的旅游偏好信息。该模型支持自然语言解析与表单输入两种方式，生成结构化数据对象，并作为后续行程规划流程的唯一合法输入源。

## 模型架构

### 核心模型：Requirement

`Requirement` 模型是旅游需求的核心数据结构，包含以下主要部分：

1. **基本行程信息**
2. **交通偏好**
3. **住宿偏好**
4. **行程偏好**
5. **预算信息**
6. **系统管理字段**

## 字段详细说明

### 1. 基本行程信息

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| requirement_id | CharField(50) | 是 | 唯一，以"REQ-"开头 | 需求唯一标识 |
| origin_name | CharField(100) | 是 | 最大100字符 | 出发地名称 |
| origin_code | CharField(10) | 否 | 最大10字符 | 出发地代码（如BJS） |
| origin_type | CharField(20) | 否 | Domestic/International | 出发地类型 |
| destination_cities | JSONField | 是 | 列表格式 | 目的地城市列表 |
| trip_days | IntegerField | 是 | 1-365 | 出行天数 |
| group_adults | IntegerField | 否 | ≥0 | 成人数量 |
| group_children | IntegerField | 否 | ≥0 | 儿童数量 |
| group_seniors | IntegerField | 否 | ≥0 | 老人数量 |
| group_total | IntegerField | 是 | ≥1，等于各类型人数之和 | 总人数 |
| travel_start_date | DateField | 是 | 有效日期 | 出行开始日期 |
| travel_end_date | DateField | 是 | ≥开始日期，≤开始日期+365天 | 出行结束日期 |
| travel_date_flexible | BooleanField | 否 | 默认False | 日期是否灵活 |

**destination_cities 结构示例：**
```json
[
  {
    "name": "西安",
    "code": "SIA",
    "stay_days": 3
  },
  {
    "name": "成都",
    "code": "CTU",
    "stay_days": 2
  }
]
```

### 2. 交通偏好

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| transportation_type | CharField(20) | 否 | 枚举值 | 大交通方式 |
| transportation_notes | TextField | 否 | 最大500字符 | 交通偏好说明 |

**transportation_type 枚举值：**
- `RoundTripFlight` - 双飞
- `OneWayFlight` - 单飞
- `HighSpeedTrain` - 高铁
- `Train` - 火车
- `SelfDriving` - 自驾
- `Other` - 其他

### 3. 住宿偏好

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| hotel_level | CharField(20) | 否 | 枚举值 | 酒店等级 |
| hotel_requirements | TextField | 否 | 最大500字符 | 住宿特殊要求 |

**hotel_level 枚举值：**
- `Economy` - 经济型
- `Comfort` - 舒适型
- `Premium` - 高档型
- `Luxury` - 豪华型

### 4. 行程偏好

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| trip_rhythm | CharField(20) | 否 | 枚举值 | 行程节奏 |
| preference_tags | JSONField | 否 | 列表，最多20个 | 偏好标签 |
| must_visit_spots | JSONField | 否 | 列表，最多20个 | 必游景点 |
| avoid_activities | JSONField | 否 | 列表，最多10个 | 避免活动 |

**trip_rhythm 枚举值：**
- `Relaxed` - 悠闲
- `Moderate` - 适中
- `Intense` - 紧凑

**preference_tags 可选值：**
- `Culture` - 文化
- `CityScape` - 城市景观
- `Food` - 美食
- `History` - 历史
- `Nature` - 自然风光
- `Shopping` - 购物
- `Entertainment` - 娱乐
- `Other` - 其他

### 5. 预算信息

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| budget_level | CharField(20) | 否 | 枚举值 | 预算等级 |
| budget_currency | CharField(10) | 否 | 默认CNY，最大10字符 | 预算货币 |
| budget_min | DecimalField(10,2) | 否 | ≥0 | 最低预算 |
| budget_max | DecimalField(10,2) | 否 | ≥0，≥budget_min | 最高预算 |
| budget_notes | TextField | 否 | 最大500字符 | 预算说明 |

**budget_level 枚举值：**
- `Economy` - 经济
- `Comfort` - 舒适
- `HighEnd` - 高端
- `Luxury` - 奢华

### 6. 系统管理字段

| 字段名 | 数据类型 | 必填 | 约束条件 | 说明 |
|--------|----------|------|----------|------|
| source_type | CharField(20) | 否 | 枚举值 | 需求来源 |
| status | CharField(20) | 否 | 枚举值，默认PendingReview | 需求状态 |
| assumptions | JSONField | 否 | 列表格式 | 系统推断说明 |
| created_by | CharField(100) | 否 | 最大100字符 | 创建人 |
| reviewed_by | CharField(100) | 否 | 最大100字符 | 审核人 |
| is_template | BooleanField | 否 | 默认False | 是否模板 |
| template_name | CharField(200) | 否 | 模板时必填，最大200字符 | 模板名称 |
| template_category | CharField(100) | 否 | 最大100字符 | 模板分类 |
| expires_at | DateTimeField | 否 | 有效时间 | 过期时间 |
| created_at | DateTimeField | 是 | 自动生成 | 创建时间 |
| updated_at | DateTimeField | 是 | 自动更新 | 更新时间 |
| extension | JSONField | 否 | 字典，最多50个字段 | 扩展字段 |

**source_type 枚举值：**
- `NaturalLanguage` - 自然语言输入
- `FormInput` - 表单输入

**status 枚举值：**
- `PendingReview` - 待审核
- `Confirmed` - 已确认
- `Expired` - 已过期

**assumptions 结构示例：**
```json
[
  {
    "field": "transportation.type",
    "inferred_value": "HighSpeedTrain",
    "reason": "用户提到"坐火车快一点"，推断为高铁"
  }
]
```

## 数据验证规则

### RequirementValidator 类

`RequirementValidator` 提供了完整的数据验证功能：

#### 验证方法

1. **validate_requirement_id** - 验证需求ID格式
   - 不能为空
   - 长度不超过20字符
   - 必须以"REQ_"开头
   - 格式为"REQ_YYYYMMDD_XXX"，其中YYYYMMDD为创建日期，XXX为当日序号（从001开始）

2. **validate_origin** - 验证出发地信息
   - 名称不能为空
   - 名称长度不超过100字符
   - 代码长度不超过10字符
   - 类型必须是Domestic或International

3. **validate_destination_cities** - 验证目的地城市
   - 不能为空
   - 必须是列表格式
   - 每个城市必须包含name字段
   - 停留天数必须在1-365天之间

4. **validate_trip_days** - 验证出行天数
   - 必须是正整数
   - 不能超过365天
   - 与日期范围必须一致

5. **validate_group_size** - 验证出行人数
   - 总人数必须是正整数
   - 不能超过100人
   - 总人数必须等于各类型人数之和
   - 各类型人数不能为负数

6. **validate_travel_dates** - 验证出行日期
   - 开始日期和结束日期不能为空
   - 结束日期不能早于开始日期
   - 开始日期不能超过2年后
   - 日期范围不能超过365天

7. **validate_transportation** - 验证交通偏好
   - 交通类型必须是有效枚举值
   - 偏好说明长度不超过500字符

8. **validate_accommodation** - 验证住宿偏好
   - 酒店等级必须是有效枚举值
   - 特殊要求长度不超过500字符

9. **validate_itinerary** - 验证行程偏好
   - 行程节奏必须是有效枚举值
   - 偏好标签必须是有效值
   - 必游景点数量不超过20个
   - 避免活动数量不超过10个

10. **validate_budget** - 验证预算信息
    - 预算等级必须是有效枚举值
    - 货币代码长度不超过10字符
    - 预算金额不能为负数
    - 最低预算不能高于最高预算
    - 预算说明长度不超过500字符

11. **validate_metadata** - 验证元数据
    - 需求来源必须是有效枚举值
    - 需求状态必须是有效枚举值
    - 模板必须包含模板名称
    - 模板名称长度不超过200字符
    - 模板分类长度不超过100字符

12. **validate_assumptions** - 验证系统推断
    - 必须是列表格式
    - 每个推断必须是字典格式
    - 必须包含field、inferred_value、reason字段

13. **validate_extension** - 验证扩展字段
    - 必须是字典格式
    - 字段数量不能超过50个

14. **validate_all** - 综合验证
    - 执行所有验证规则
    - 返回统一的错误信息

## 状态流转机制

### RequirementStatusManager 类

`RequirementStatusManager` 管理需求对象的状态流转：

#### 状态转换规则

```
待审核 (PendingReview)
    ├──→ 已确认 (Confirmed) [需运营人员确认]
    └──→ 已过期 (Expired) [超过设定时间未审核]

已确认 (Confirmed)
    └──→ 已过期 (Expired) [超过有效期未使用]

已过期 (Expired)
    └──→ [不可转换]
```

#### 主要方法

1. **confirm_requirement(requirement_id, reviewer=None)**
   - 确认需求
   - 将状态从待审核转换为已确认
   - 记录审核人信息

2. **expire_requirement(requirement_id)**
   - 过期需求
   - 将状态转换为已过期

3. **check_and_expire_pending_requirements(pending_hours=72)**
   - 检查并过期待审核需求
   - 默认72小时未审核自动过期

4. **check_and_expire_confirmed_requirements(validity_hours=168)**
   - 检查并过期已确认需求
   - 默认168小时（7天）未使用自动过期

5. **check_all_expired_requirements(pending_hours=72, confirmed_hours=168)**
   - 检查所有过期需求
   - 返回过期统计信息

6. **get_requirements_by_status(status)**
   - 按状态查询需求

7. **get_pending_requirements()**
   - 获取待审核需求列表

8. **get_confirmed_requirements()**
   - 获取已确认需求列表

9. **get_expired_requirements()**
   - 获取已过期需求列表

10. **get_requirements_near_expiry(hours_threshold=24)**
    - 获取即将过期的需求

11. **set_expiry_time(requirement_id, hours)**
    - 设置需求过期时间

12. **get_status_statistics()**
    - 获取状态统计信息

13. **validate_status_transition(current_status, new_status)**
    - 验证状态转换是否合法

## 模板功能支持

### TemplateManager 类

`TemplateManager` 提供需求模板的创建、管理和使用功能：

#### 主要方法

1. **create_template(source_requirement_id, template_name, template_category, created_by=None, clear_sensitive_data=True)**
   - 从现有需求创建模板
   - 自动清除敏感数据（如具体日期、人数、预算金额）
   - 设置模板标识和分类

2. **update_template(template_id, template_name=None, template_category=None, update_data=None)**
   - 更新模板信息
   - 支持更新模板名称、分类及其他字段

3. **delete_template(template_id)**
   - 删除模板

4. **get_template(template_id)**
   - 获取模板详情

5. **list_templates(category=None, search_keyword=None, page=1, page_size=20)**
   - 列出所有模板
   - 支持按分类筛选
   - 支持关键词搜索
   - 支持分页

6. **get_template_categories()**
   - 获取所有模板分类

7. **use_template(template_id, new_requirement_id, created_by=None)**
   - 使用模板创建新需求
   - 复制模板的偏好设置
   - 记录模板来源信息

8. **duplicate_template(template_id, new_requirement_id, new_template_name, created_by=None)**
   - 复制模板
   - 创建新的模板副本

#### 模板特点

- 模板状态固定为已确认
- 模板不包含敏感数据（具体日期、人数、预算金额）
- 模板可以按分类管理
- 支持模板搜索和检索
- 可以从模板快速创建新需求

## JSON 输出格式

### to_json() 方法

`Requirement` 模型提供 `to_json()` 方法，将需求对象转换为标准 JSON 格式：

```json
{
  "requirement_id": "REQ-20260120-001",
  "base_info": {
    "origin": {
      "name": "北京",
      "code": "BJS",
      "type": "International"
    },
    "destination_cities": [
      {
        "name": "西安",
        "code": "SIA",
        "stay_days": 3
      },
      {
        "name": "成都",
        "code": "CTU",
        "stay_days": 2
      }
    ],
    "trip_days": 5,
    "group_size": {
      "adults": 2,
      "children": 1,
      "seniors": 0,
      "total": 3
    },
    "travel_date": {
      "start_date": "2026-05-01",
      "end_date": "2026-05-05",
      "is_flexible": false
    }
  },
  "preferences": {
    "transportation": {
      "type": "HighSpeedTrain",
      "notes": "优先选二等座，希望在上午出发"
    },
    "accommodation": {
      "level": "Comfort",
      "requirements": "需要一间家庭房，最好靠近地铁站，带早餐"
    },
    "itinerary": {
      "rhythm": "Moderate",
      "tags": ["History", "Food", "CityScape"],
      "special_constraints": {
        "must_visit_spots": ["秦始皇兵马俑博物馆", "大唐不夜城"],
        "avoid_activities": ["徒步登山"]
      }
    }
  },
  "budget": {
    "level": "Comfort",
    "currency": "CNY",
    "range": {
      "min": 5000,
      "max": 8000
    },
    "budget_notes": "包含大交通，不含购物支出"
  },
  "metadata": {
    "source_type": "NaturalLanguage",
    "status": "PendingReview",
    "assumptions": [
      {
        "field": "transportation.type",
        "inferred_value": "HighSpeedTrain",
        "reason": "用户提到"坐火车快一点"，推断为高铁"
      }
    ],
    "is_template": false,
    "template_info": {
      "name": "西安成都亲子五日游",
      "category": "FamilyTour"
    },
    "audit_trail": {
      "created_at": "2026-01-20T10:00:00Z",
      "updated_at": "2026-01-20T10:15:00Z",
      "created_by": "user_12345",
      "reviewed_by": null
    }
  },
  "extension": {}
}
```

## 序列化器

### RequirementSerializer

完整的模型序列化器，包含所有字段。

### RequirementDetailSerializer

详细视图序列化器，将数据组织为嵌套结构：
- base_info
- preferences
- budget
- metadata

### RequirementCreateSerializer

创建需求时的序列化器，包含所有可写字段。

### RequirementUpdateSerializer

更新需求时的序列化器，排除只读字段。

### RequirementListSerializer

列表视图序列化器，只包含关键字段。

### TemplateSerializer

模板序列化器，专门用于模板数据的展示。

### TemplateCreateSerializer

创建模板的序列化器。

### RequirementStatusSerializer

状态更新序列化器，用于状态流转操作。

## 数据库索引

模型包含以下索引以优化查询性能：

- `requirement_id` - 需求ID索引
- `status` - 状态索引
- `created_by` - 创建人索引
- `is_template` - 模板标识索引
- `-created_at` - 创建时间降序索引

## 扩展性设计

### extension 字段

`extension` 字段是一个 JSON 字段，用于存储扩展信息：

- 支持最多50个自定义字段
- 字段值可以是任意 JSON 兼容类型
- 不影响核心模型结构

### 未来扩展方向

1. **新增需求类型**
   - 商务出行
   - 研学旅行
   - 康养旅游

2. **新增偏好维度**
   - 餐饮偏好
   - 购物偏好
   - 娱乐偏好

3. **新增预算维度**
   - 按项目预算分配
   - 多货币支持

4. **新增协作功能**
   - 需求分享
   - 多人协作编辑

5. **新增分析功能**
   - 需求统计分析
   - 偏好趋势分析

## 使用示例

### 创建需求

```python
from apps.models import Requirement, RequirementValidator

data = {
    'requirement_id': 'REQ-20260120-001',
    'origin_name': '北京',
    'destination_cities': [...],
    'trip_days': 5,
    # ... 其他字段
}

RequirementValidator.validate_all(data)
requirement = Requirement.objects.create(**data)
```

### 确认需求

```python
from apps.models import RequirementStatusManager

requirement = RequirementStatusManager.confirm_requirement(
    'REQ-20260120-001',
    reviewer='admin_001'
)
```

### 创建模板

```python
from apps.models import TemplateManager

template = TemplateManager.create_template(
    'REQ-20260120-001',
    template_name='西安成都亲子五日游',
    template_category='FamilyTour',
    created_by='admin_001'
)
```

### 使用模板

```python
requirement = TemplateManager.use_template(
    'TPL-REQ-20260120-001',
    new_requirement_id='REQ-20260120-002',
    created_by='user_67890'
)
```

### 导出 JSON

```python
requirement = Requirement.objects.get(requirement_id='REQ-20260120-001')
json_data = requirement.to_json()
```

## 最佳实践

1. **数据验证**
   - 创建或更新需求前，始终使用 `RequirementValidator.validate_all()` 进行验证

2. **状态管理**
   - 使用 `RequirementStatusManager` 管理状态流转
   - 定期检查并过期超期需求

3. **模板使用**
   - 将常用需求保存为模板
   - 使用模板快速创建相似需求
   - 定期清理不使用的模板

4. **扩展字段**
   - 使用 `extension` 字段存储临时或特定场景的数据
   - 避免频繁修改核心模型结构

5. **性能优化**
   - 利用索引优化查询
   - 使用分页查询大量数据
   - 避免不必要的关联查询

## 总结

旅游需求模型提供了完整、灵活、可扩展的数据结构，能够满足各种旅游场景的需求。通过完善的验证机制、状态流转和模板功能，确保数据的质量和可用性，为后续的行程规划流程提供可靠的数据基础。
