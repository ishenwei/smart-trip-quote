# 旅游行程规划AI Workflow 规范文档

## 1. 需求分析

### 1.1 功能需求
1. **Webhook 接收**：通过 HTTP POST 接收旅游需求的 JSON 数据
2. **数据验证**：验证输入数据的完整性和有效性
3. **目的地处理**：根据 `destination_cities` 数组循环处理每个城市
4. **AI 过滤条件生成**：为每个城市生成景点、酒店、餐厅的过滤条件
5. **数据查询**：根据过滤条件查询各城市的景点、酒店、餐厅数据
6. **数据聚合**：汇总所有城市的旅游数据
7. **AI 行程规划**：基于用户需求和收集的数据生成详细的旅游行程
8. **响应返回**：返回完整的行程规划结果

### 1.2 非功能需求
1. **性能**：处理时间不超过 30 秒
2. **可靠性**：具备错误处理和异常捕获机制
3. **可扩展性**：支持添加新的数据源和处理步骤
4. **安全性**：保护用户数据和 API 调用

## 2. 系统架构

### 2.1 技术栈
- **n8n**：工作流引擎
- **OpenAI API**：AI 过滤条件生成和行程规划
- **Django API**：提供景点、酒店、餐厅数据
- **HTTP**：数据传输协议

### 2.2 工作流架构
```
Webhook Trigger → Extract Data → Validate Data → Check Validation
  ↓ (有效)                     ↓ (无效)
Split Cities → AI Filter Conditions → Parse Filter Conditions
  ↓
Get Attractions → Combine Data
Get Hotels     → Combine Data
Get Restaurants → Combine Data
  ↓
Aggregate City Data → AI Itinerary Planning → Prepare Response → Respond Success
  ↓
Error Handler → Respond Error
```

## 3. 详细设计

### 3.1 节点设计

#### 3.1.1 Webhook Trigger
- **类型**：n8n-nodes-base.webhook
- **配置**：
  - HTTP 方法：POST
  - 路径：/travel-planning-ai
  - 响应模式：responseNode
- **输入**：旅游需求 JSON 数据
- **输出**：原始请求数据

#### 3.1.2 Extract Data
- **类型**：n8n-nodes-base.set
- **配置**：
  - 提取 `requirementData`、`destinationCities`、`tripDays`、`budget`、`preferences`
- **输入**：Webhook 触发的请求数据
- **输出**：提取后的数据对象

#### 3.1.3 Validate Data
- **类型**：n8n-nodes-base.code
- **配置**：
  - 验证 `base_info` 中的必要字段
  - 验证 `destination_cities` 不为空
  - 验证 `trip_days` 大于 0
- **输入**：提取后的数据
- **输出**：包含验证结果的数据

#### 3.1.4 Check Validation
- **类型**：n8n-nodes-base.if
- **配置**：
  - 条件：`validationResult.isValid` 为 true
- **输入**：包含验证结果的数据
- **输出**：根据验证结果分流

#### 3.1.5 Split Cities
- **类型**：n8n-nodes-base.splitInBatches
- **配置**：
  - 批处理大小：1
- **输入**：验证通过的数据
- **输出**：按城市分批处理的数据

#### 3.1.6 AI Filter Conditions
- **类型**：n8n-nodes-base.openAI
- **配置**：
  - 模型：gpt-4
  - 温度：0.7
  - 最大 tokens：500
  - 系统提示：旅游专家角色
  - 用户提示：生成过滤条件
- **输入**：单个城市的数据
- **输出**：AI 生成的过滤条件

#### 3.1.7 Parse Filter Conditions
- **类型**：n8n-nodes-base.code
- **配置**：
  - 解析 AI 生成的 JSON 格式过滤条件
  - 处理解析失败的情况
- **输入**：AI 生成的过滤条件
- **输出**：解析后的过滤条件

#### 3.1.8 Get Attractions
- **类型**：n8n-nodes-base.httpRequest
- **配置**：
  - URL：http://localhost:7000/api/attractions
  - 方法：GET
  - 查询参数：city, filters
- **输入**：包含城市和过滤条件的数据
- **输出**：景点数据

#### 3.1.9 Get Hotels
- **类型**：n8n-nodes-base.httpRequest
- **配置**：
  - URL：http://localhost:7000/api/hotels
  - 方法：GET
  - 查询参数：city, filters
- **输入**：包含城市和过滤条件的数据
- **输出**：酒店数据

#### 3.1.10 Get Restaurants
- **类型**：n8n-nodes-base.httpRequest
- **配置**：
  - URL：http://localhost:7000/api/restaurants
  - 方法：GET
  - 查询参数：city, filters
- **输入**：包含城市和过滤条件的数据
- **输出**：餐厅数据

#### 3.1.11 Combine Data
- **类型**：n8n-nodes-base.merge
- **配置**：
  - 模式：combine
- **输入**：景点、酒店、餐厅数据
- **输出**：合并后的数据

#### 3.1.12 Aggregate City Data
- **类型**：n8n-nodes-base.code
- **配置**：
  - 聚合每个城市的景点、酒店、餐厅数据
- **输入**：合并后的数据
- **输出**：按城市聚合的数据

#### 3.1.13 AI Itinerary Planning
- **类型**：n8n-nodes-base.openAI
- **配置**：
  - 模型：gpt-4
  - 温度：0.7
  - 最大 tokens：2000
  - 系统提示：旅游行程规划师角色
  - 用户提示：生成详细行程
- **输入**：聚合后的城市数据
- **输出**：AI 生成的行程规划

#### 3.1.14 Prepare Response
- **类型**：n8n-nodes-base.set
- **配置**：
  - 构建成功响应对象
- **输入**：AI 生成的行程规划
- **输出**：格式化的响应数据

#### 3.1.15 Respond Success
- **类型**：n8n-nodes-base.respondToWebhook
- **配置**：
  - 响应格式：JSON
- **输入**：格式化的响应数据
- **输出**：HTTP 响应

#### 3.1.16 Error Handler
- **类型**：n8n-nodes-base.set
- **配置**：
  - 构建错误响应对象
- **输入**：验证失败的数据
- **输出**：错误响应数据

#### 3.1.17 Respond Error
- **类型**：n8n-nodes-base.respondToWebhook
- **配置**：
  - 响应格式：JSON
- **输入**：错误响应数据
- **输出**：HTTP 错误响应

### 3.2 数据结构

#### 3.2.1 输入数据结构
```json
{
  "base_info": {
    "origin": "北京",
    "destination_cities": ["上海", "杭州"],
    "trip_days": 5,
    "travel_date": "2026-05-01"
  },
  "preferences": {
    "attraction_types": ["历史古迹", "自然景观"],
    "hotel_star": 4,
    "food_types": ["中餐", "西餐"]
  },
  "budget": {
    "total": 10000,
    "per_day": 2000
  }
}
```

#### 3.2.2 输出数据结构
```json
{
  "success": true,
  "message": "旅游行程规划完成",
  "data": {
    "requirement": {...}, // 原始需求数据
    "itinerary": "...", // AI 生成的详细行程
    "cityData": {
      "上海": {
        "attractions": [...],
        "hotels": [...],
        "restaurants": [...]
      },
      "杭州": {
        "attractions": [...],
        "hotels": [...],
        "restaurants": [...]
      }
    },
    "generatedAt": "2026-03-02T00:00:00.000Z"
  }
}
```

## 4. 实现细节

### 4.1 API 接口设计

#### 4.1.1 景点 API
- **URL**：http://localhost:7000/api/attractions
- **方法**：GET
- **参数**：
  - city：城市名称
  - filters：过滤条件（JSON 字符串）
- **返回**：景点列表

#### 4.1.2 酒店 API
- **URL**：http://localhost:7000/api/hotels
- **方法**：GET
- **参数**：
  - city：城市名称
  - filters：过滤条件（JSON 字符串）
- **返回**：酒店列表

#### 4.1.3 餐厅 API
- **URL**：http://localhost:7000/api/restaurants
- **方法**：GET
- **参数**：
  - city：城市名称
  - filters：过滤条件（JSON 字符串）
- **返回**：餐厅列表

### 4.2 AI 提示设计

#### 4.2.1 过滤条件生成提示
```
你是一个旅游专家，负责为每个目的地城市生成合适的景点、酒店和餐厅的过滤条件。根据用户的旅行偏好和预算，为每个城市生成具体的过滤条件。

请为城市 {{ city }} 生成旅游相关的过滤条件。

用户偏好：{{ preferences }}
预算：{{ budget }}
旅行天数：{{ tripDays }}

请生成：
1. 景点过滤条件（类型、价格、特色等）
2. 酒店过滤条件（星级、价格、设施等）
3. 餐厅过滤条件（菜系、价格、特色等）

返回JSON格式。
```

#### 4.2.2 行程规划提示
```
你是一个专业的旅游行程规划师，负责根据用户的需求和收集到的目的地数据，制定详细的旅游行程计划。

请根据以下信息制定详细的旅游行程计划：

用户需求：{{ requirementData }}

目的地数据：{{ cityData }}

请生成：
1. 详细的每日行程安排
2. 交通建议
3. 住宿安排
4. 餐饮推荐
5. 预算估算

返回详细的行程计划。
```

## 5. 部署与集成

### 5.1 环境配置
1. **n8n 配置**：
   - 安装 n8n：`npm install -g n8n`
   - 启动 n8n：`n8n start`
   - 导入 workflow：通过 n8n UI 导入 JSON 文件

2. **OpenAI 配置**：
   - 设置环境变量：`OPENAI_API_KEY=your_api_key`

3. **Django API 配置**：
   - 启动 Django 服务器：`python manage.py runserver 0.0.0.0:7000`

### 5.2 集成测试
1. **测试数据**：准备完整的旅游需求 JSON 数据
2. **API 测试**：验证景点、酒店、餐厅 API 的可用性
3. **Workflow 测试**：通过 Postman 发送 POST 请求到 webhook 端点
4. **结果验证**：检查返回的行程规划是否符合预期

## 6. 监控与维护

### 6.1 日志记录
- n8n 工作流执行日志
- OpenAI API 调用日志
- Django API 访问日志

### 6.2 错误处理
- 数据验证错误
- API 调用失败
- AI 生成错误
- 网络超时

### 6.3 性能优化
- 缓存 AI 生成的过滤条件
- 批量处理 API 请求
- 优化 AI 提示词，减少 token 使用

## 7. 扩展可能性

### 7.1 功能扩展
- 添加天气数据集成
- 支持多语言行程生成
- 集成机票和交通预订
- 添加用户反馈机制

### 7.2 技术扩展
- 支持更多 AI 模型
- 集成更多数据源
- 添加实时数据更新
- 支持个性化推荐

## 8. 总结

本 workflow 设计实现了一个完整的旅游行程规划系统，通过以下步骤实现：
1. 接收并验证旅游需求数据
2. 为每个目的地城市生成 AI 过滤条件
3. 查询各城市的景点、酒店、餐厅数据
4. 聚合数据并生成详细的旅游行程
5. 返回完整的行程规划结果

系统采用了模块化设计，具有良好的可扩展性和可维护性，能够满足不同用户的旅游规划需求。