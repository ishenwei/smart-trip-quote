# 行程规划数据解析测试文档

## JSON文件修改说明

### 主要变更

1. **移除iternary顶层结构**
   - 原来的JSON包含`iternary`顶层结构
   - 现在直接在顶层包含所有字段，更符合n8n返回的格式

2. **添加requirement_id字段**
   - 新增`requirement_id`字段，用于关联原始的旅游需求
   - n8n返回的JSON不包含itinerary_id，只包含requirement_id
   - itinerary_id在保存到数据库时自动生成

3. **destination结构变更**
   - 原来的`destination`对象改为`destinations`数组
   - 每个目的地作为一个独立的item，包含：
     - `destination_order`: 目的地顺序
     - `city_name`: 城市名称
     - `country_code`: 国家代码
     - `arrival_date`: 抵达日期
     - `departure_date`: 离开日期

4. **daily_schedules结构变更**
   - 将原来的`attractions`、`hotel`、`restaurants`、`flights`、`transportation`统一改为`activities`数组
   - 每个活动按照时间顺序排列
   - 每个活动包含：
     - `activity_type`: 活动类型（FLIGHT、TRAIN、ATTRACTION、MEAL、TRANSPORT、SHOPPING、FREE、CHECK_IN、CHECK_OUT、OTHER）
     - `activity_title`: 活动标题
     - `activity_description`: 活动描述
     - `start_time`: 开始时间
     - `end_time`: 结束时间
     - 根据活动类型可能包含额外的字段：
       - `attraction_id`: 景点ID（ATTRACTION类型）
       - `hotel_id`: 酒店ID（CHECK_IN、CHECK_OUT类型）
       - `restaurant_id`: 餐厅ID（MEAL类型）
       - `flight_number`: 航班号（FLIGHT类型）
       - `transport_mode`: 交通方式（TRANSPORT类型）
       - `route`: 路线（TRANSPORT类型）

### 示例数据

JSON文件包含5天的行程数据，涵盖以下活动类型：
- FLIGHT: 航班活动
- TRANSPORT: 交通活动
- ATTRACTION: 景点游览
- MEAL: 餐饮活动
- CHECK_IN: 酒店入住
- CHECK_OUT: 酒店退房
- FREE: 自由活动

## 测试脚本修改说明

### 主要功能

1. **JSON解析**
   - 正确解析新的JSON格式
   - 验证必需字段（requirement_id、itinerary_name）
   - 处理JSON格式错误和数据缺失情况

2. **数据库操作**
   - 创建itinerary（行程主表）
   - 创建destination（目的地信息表）
   - 创建traveler_stats（旅行者统计信息表）
   - 创建daily_schedule（每日行程安排表）

3. **错误处理**
   - 使用数据库事务确保数据一致性
   - 捕获并显示详细的错误信息
   - 提供清晰的错误提示

### 核心方法

1. **create_itinerary**
   - 创建行程主表记录
   - 自动生成itinerary_id
   - 设置默认值（联系人、电话、城市等）

2. **create_destinations**
   - 根据destinations数组创建多个目的地记录
   - 每个目的地包含顺序、城市、国家、抵达和离开日期

3. **create_traveler_stats**
   - 创建旅行者统计信息
   - 包含成人、儿童、婴儿、老人数量

4. **create_daily_schedules**
   - 根据daily_schedules数组创建每日行程安排
   - 每个活动根据类型映射到相应的数据库字段
   - 自动关联对应的目的地ID

5. **get_activity_type**
   - 将字符串转换为活动类型枚举
   - 支持所有活动类型

## 使用说明

### 运行测试脚本

```bash
python test_iternary_parser.py test_iternary_data.json
```

### 预期输出

```
行程数据解析并保存成功
行程ID: ITI_20241001_001
行程名称: 日本东京大阪5日游
关联需求ID: REQ-2024-001
```

## 数据验证

### UUID格式

JSON中使用的UUID格式示例：
- Attraction ID: `550e8400-e29b-41d4-a716-446655440001`
- Hotel ID: `550e8400-e29b-41d4-a716-446655440021`
- Restaurant ID: `550e8400-e29b-41d4-a716-446655440011`

注意：在实际使用时，这些UUID应该对应数据库中实际存在的记录。

### 活动类型映射

| JSON类型 | 数据库枚举 | 说明 |
|---------|-----------|------|
| FLIGHT | FLIGHT | 航班 |
| TRAIN | TRAIN | 火车 |
| ATTRACTION | ATTRACTION | 景点 |
| MEAL | MEAL | 餐饮 |
| TRANSPORT | TRANSPORT | 交通 |
| SHOPPING | SHOPPING | 购物 |
| FREE | FREE | 自由活动 |
| CHECK_IN | CHECK_IN | 入住 |
| CHECK_OUT | CHECK_OUT | 退房 |
| OTHER | OTHER | 其他 |

## 注意事项

1. **数据库连接**
   - 确保数据库连接配置正确
   - 确保数据库中存在对应的attraction、hotel、restaurant记录

2. **数据完整性**
   - 所有UUID必须对应数据库中实际存在的记录
   - 日期格式必须为YYYY-MM-DD
   - 时间格式必须为HH:MM

3. **事务处理**
   - 使用数据库事务确保数据一致性
   - 如果任何步骤失败，所有操作都会回滚

4. **错误处理**
   - 脚本会捕获并显示详细的错误信息
   - 包括JSON格式错误、数据缺失、数据库操作错误等
