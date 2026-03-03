# 旅游行程规划AI Workflow 规范文档

## 1. 需求分析

### 1.1 功能需求
1. **Webhook 接收**：通过 HTTP POST 接收旅游需求的 JSON 数据
2. **数据验证**：验证输入数据的完整性和有效性
3. **目的地处理**：根据 `destination_cities` 数组循环处理每个城市
4. **AI SQL 查询生成**：为每个城市生成景点、酒店、餐厅的 SQL 查询语句
5. **数据库查询**：根据生成的 SQL 查询语句从 MySQL 数据库获取数据
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
- **DeepSeek API**：AI SQL 查询生成和行程规划
- **MySQL**：存储景点、酒店、餐厅数据
- **HTTP**：数据传输协议

### 2.2 工作流架构
```
Webhook Trigger → 解析旅游需求数据 → 校验旅游需求必要数据 → 检查数据校验是否成功
  ↓ (有效)                     ↓ (无效)
循环目的地城市 → 读取数据表结构文件 → 解析数据表数据 → AI SQL 查询生成 → 数据库查询
  ↓                                                                   ↓
景点列表 → Merge ← 酒店列表 ← 查询数据库2 ← 筛选目的地城市酒店 ← DeepSeek Chat Model1
  ↓                                                                   ↓
景点列表 → Merge ← 餐厅列表 ← 查询数据库3 ← 筛选目的地城市餐厅 ← DeepSeek Chat Model2
  ↓
旅游行程规划 → 准备旅游行程规划返回数据 → 数据返回成功
  ↓
错误处理 → 返回错误消息
```

## 3. 详细设计

### 3.1 节点设计

#### 3.1.1 获取旅游需求详细数据
- **类型**：n8n-nodes-base.webhook
- **配置**：
  - HTTP 方法：POST
  - 路径：/smart-trip-requirement
  - 响应模式：responseNode
- **输入**：旅游需求 JSON 数据
- **输出**：原始请求数据

#### 3.1.2 解析旅游需求数据1
- **类型**：n8n-nodes-base.set
- **配置**：
  - 提取 `destinationCities`：`={{ $json.body.requirement_json_data.base_info.destination_cities }}`
- **输入**：Webhook 触发的请求数据
- **输出**：包含目的地城市的数据对象

#### 3.1.3 解析旅游需求数据2
- **类型**：n8n-nodes-base.set
- **配置**：
  - 提取 `requirementData`：`={{ $json.body }}`
  - 提取 `destinationCities`：`={{ $json.body.requirement_json_data.base_info.destination_cities }}`
  - 提取 `tripDays`：`={{ $json.body.requirement_json_data.base_info.trip_days }}`
  - 提取 `budget`：`={{ $json.body.budget || {} }}`
  - 提取 `preferences`：`={{ $json.body.preferences || {} }}`
- **输入**：Webhook 触发的请求数据
- **输出**：提取后的数据对象

#### 3.1.4 校验旅游需求必要数据
- **类型**：n8n-nodes-base.code
- **配置**：
  - 验证 `base_info` 中的必要字段
  - 验证 `destination_cities` 不为空
  - 验证 `trip_days` 大于 0
- **输入**：提取后的数据
- **输出**：包含验证结果的数据

#### 3.1.5 检查数据校验是否成功
- **类型**：n8n-nodes-base.if
- **配置**：
  - 条件：`validationResult.isValid` 为 true
- **输入**：包含验证结果的数据
- **输出**：根据验证结果分流

#### 3.1.6 循环目的地城市
- **类型**：n8n-nodes-base.splitInBatches
- **配置**：
  - 批处理大小：1
- **输入**：验证通过的数据
- **输出**：按城市分批处理的数据

#### 3.1.7 读取数据表结构文件
- **类型**：n8n-nodes-base.readWriteFile
- **配置**：
  - 文件路径：/home/node/.n8n-files/db.txt
- **输入**：按城市分批处理的数据
- **输出**：数据表结构文件内容

#### 3.1.8 解析数据表数据
- **类型**：n8n-nodes-base.extractFromFile
- **配置**：
  - 操作：text
- **输入**：数据表结构文件内容
- **输出**：解析后的数据表结构

#### 3.1.9 筛选目的地城市景点
- **类型**：@n8n/n8n-nodes-langchain.agent
- **配置**：
  - 提示类型：define
  - 文本：AI SQL 查询生成提示
  - 输出解析器：是
- **输入**：解析后的数据表结构和城市数据
- **输出**：AI 生成的景点 SQL 查询

#### 3.1.10 筛选目的地城市酒店
- **类型**：@n8n/n8n-nodes-langchain.agent
- **配置**：
  - 提示类型：define
  - 文本：AI SQL 查询生成提示
  - 输出解析器：是
- **输入**：解析后的数据表结构和城市数据
- **输出**：AI 生成的酒店 SQL 查询

#### 3.1.11 筛选目的地城市餐厅
- **类型**：@n8n/n8n-nodes-langchain.agent
- **配置**：
  - 提示类型：define
  - 文本：AI SQL 查询生成提示
  - 输出解析器：是
- **输入**：解析后的数据表结构和城市数据
- **输出**：AI 生成的餐厅 SQL 查询

#### 3.1.12 查询数据库1
- **类型**：n8n-nodes-base.mySql
- **配置**：
  - 操作：executeQuery
  - 查询：`{{ $json.output.sql }}`
- **输入**：AI 生成的景点 SQL 查询
- **输出**：景点数据

#### 3.1.13 查询数据库2
- **类型**：n8n-nodes-base.mySql
- **配置**：
  - 操作：executeQuery
  - 查询：`{{ $json.output.sql }}`
- **输入**：AI 生成的酒店 SQL 查询
- **输出**：酒店数据

#### 3.1.14 查询数据库3
- **类型**：n8n-nodes-base.mySql
- **配置**：
  - 操作：executeQuery
  - 查询：`{{ $json.output.sql }}`
- **输入**：AI 生成的餐厅 SQL 查询
- **输出**：餐厅数据

#### 3.1.15 景点列表
- **类型**：n8n-nodes-base.code
- **配置**：
  - 处理查询结果，提取景点数据
- **输入**：景点数据
- **输出**：格式化的景点列表

#### 3.1.16 酒店列表
- **类型**：n8n-nodes-base.code
- **配置**：
  - 处理查询结果，提取酒店数据
- **输入**：酒店数据
- **输出**：格式化的酒店列表

#### 3.1.17 餐厅列表
- **类型**：n8n-nodes-base.code
- **配置**：
  - 处理查询结果，提取餐厅数据
- **输入**：餐厅数据
- **输出**：格式化的餐厅列表

#### 3.1.18 Merge
- **类型**：n8n-nodes-base.merge
- **配置**：
  - 模式：combine
  - 合并方式：combineByPosition
  - 输入数量：4
- **输入**：景点列表、酒店列表、餐厅列表、需求数据
- **输出**：合并后的数据

#### 3.1.19 旅游行程规划
- **类型**：@n8n/n8n-nodes-langchain.agent
- **配置**：
  - 提示类型：define
  - 文本：旅游行程规划提示
  - 输出解析器：是
- **输入**：合并后的数据
- **输出**：AI 生成的行程规划

#### 3.1.20 准备旅游行程规划返回数据
- **类型**：n8n-nodes-base.set
- **配置**：
  - 构建成功响应对象
- **输入**：AI 生成的行程规划
- **输出**：格式化的响应数据

#### 3.1.21 数据返回成功
- **类型**：n8n-nodes-base.respondToWebhook
- **配置**：
  - 响应格式：json
  - 响应体：`={{ JSON.stringify($json.itineraryResult) }}`
- **输入**：格式化的响应数据
- **输出**：HTTP 响应

#### 3.1.22 错误处理
- **类型**：n8n-nodes-base.set
- **配置**：
  - 构建错误响应对象
- **输入**：验证失败的数据
- **输出**：错误响应数据

#### 3.1.23 返回错误消息
- **类型**：n8n-nodes-base.respondToWebhook
- **配置**：
  - 响应格式：json
  - 响应体：`={{ JSON.stringify($json.errorResponse) }}`
- **输入**：错误响应数据
- **输出**：HTTP 错误响应

#### 3.1.24 DeepSeek Chat Model
- **类型**：@n8n/n8n-nodes-langchain.lmChatDeepSeek
- **配置**：
  - 凭证：DeepSeek account
- **输入**：无
- **输出**：AI 语言模型

#### 3.1.25 DeepSeek Chat Model1
- **类型**：@n8n/n8n-nodes-langchain.lmChatDeepSeek
- **配置**：
  - 凭证：DeepSeek account
- **输入**：无
- **输出**：AI 语言模型

#### 3.1.26 DeepSeek Chat Model2
- **类型**：@n8n/n8n-nodes-langchain.lmChatDeepSeek
- **配置**：
  - 凭证：DeepSeek account
- **输入**：无
- **输出**：AI 语言模型

#### 3.1.27 DeepSeek Chat Model3
- **类型**：@n8n/n8n-nodes-langchain.lmChatDeepSeek
- **配置**：
  - 凭证：DeepSeek account
- **输入**：无
- **输出**：AI 语言模型

#### 3.1.28 Structured Output Parser
- **类型**：@n8n/n8n-nodes-langchain.outputParserStructured
- **配置**：
  - JSON Schema 示例：SQL 查询输出格式
- **输入**：无
- **输出**：结构化输出解析器

#### 3.1.29 Structured Output Parser1
- **类型**：@n8n/n8n-nodes-langchain.outputParserStructured
- **配置**：
  - JSON Schema 示例：SQL 查询输出格式
- **输入**：无
- **输出**：结构化输出解析器

#### 3.1.30 Structured Output Parser2
- **类型**：@n8n/n8n-nodes-langchain.outputParserStructured
- **配置**：
  - JSON Schema 示例：SQL 查询输出格式
- **输入**：无
- **输出**：结构化输出解析器

#### 3.1.31 旅游行程规划结构化输出
- **类型**：@n8n/n8n-nodes-langchain.outputParserStructured
- **配置**：
  - JSON Schema 示例：行程规划输出格式
- **输入**：无
- **输出**：结构化输出解析器

### 3.2 数据结构

#### 3.2.1 输入数据结构
```json
{
  "body": {
    "requirement_json_data": {
      "base_info": {
        "origin": "北京",
        "destination_cities": ["上海", "杭州"],
        "trip_days": 5,
        "travel_date": "2026-05-01"
      }
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
}
```

#### 3.2.2 输出数据结构
```json
{
  "success": true,
  "message": "旅游行程规划完成",
  "data": {
    "requirement": {...}, // 原始需求数据
    "itinerary": {...}, // AI 生成的详细行程（JSON格式）
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

### 4.1 数据库设计

#### 4.1.1 景点表 (attractions)
- **字段**：attraction_id, attraction_name, city_name, ...

#### 4.1.2 酒店表 (hotels)
- **字段**：hotel_id, hotel_name, city_name, ...

#### 4.1.3 餐厅表 (restaurants)
- **字段**：restaurant_id, restaurant_name, city_name, ...

### 4.2 AI 提示设计

#### 4.2.1 SQL 查询生成提示
```
You are a senior database query assistant.

Your task is to follow pre-defined data structure, then convert user natural language and follow requests into safe, optimized, and syntactically correct SQL queries.

#User Natural Input:
查询{{ $('循环目的地城市').item.json.destinationCities[0].name }}的景点，返回景点ID, 景点名称

## DATABASE DATA STRUCTURE
{{ $json.data }}

You MUST follow these rules strictly
## GENERAL RULES
1. Only generate SQL.
2. Do NOT include explanations unless explicitly requested.
3. Always assume the database is MySQL 8+ compatible.
4. Use readable formatting and indentation.
5. Use explicit column names (never SELECT *).
6. Use table aliases when helpful.
## SECURITY RULES (CRITICAL)
❌ NEVER generate:
- DELETE
- UPDATE
- INSERT
- DROP
- TRUNCATE
- ALTER
- GRANT
- REVOKE
❌ NEVER modify data.
Only generate SELECT queries.
## QUERY SAFETY
✔ Always include LIMIT when result size may be large.
✔ Use ORDER BY when user implies ranking or recency.
✔ Use WHERE filters whenever possible.
✔ If date range is unclear, assume last 30 days.
## AMBIGUITY HANDLING
If the request is ambiguous:
- choose the most logical interpretation
- add reasonable filters
- keep results useful and concise
## OUTPUT FORMAT
Return output in JSON format, output SQL as a single-line query without line breaks.

{
  "sql": "SQL query here",
  "description": "short explanation"
}
```

#### 4.2.2 行程规划提示
```
## Role
你是一个专业且严谨的“高级旅游行程规划专家”Agent。你的核心任务是根据用户提供的结构化旅游需求数据，以及严格限定的候选资源列表（景点、酒店、餐厅），生成一份精确到小时的每日行程规划。

## Input Data
在每次请求中，你将接收到以下四份数据：
- Requirements (JSON): 包含基础信息、出行人统计、偏好（交通、住宿、节奏）和预算等。
Requirements: {{ JSON.stringify($json.requirementData) }}
- Attractions List (JSON/Array): 经过筛选的候选景点列表，包含景点ID、名称。
Attractions List：{{ JSON.stringify($json.attractions) }}
- Hotels List (JSON/Array): 经过筛选的候选酒店列表，包含酒店ID、名称等。
Hotels List：{{ JSON.stringify($json.hotels) }}
- Restaurants List (JSON/Array): 经过筛选的候选餐厅列表，包含餐厅ID、名称、餐饮类型等。
Restaurants List：{{ JSON.stringify($json.restaurants) }}


## Strict Rules & Constraints
你必须绝对遵守以下规则，任何违反都将导致任务失败：
- 绝对数据边界 (Zero Hallucination): - 行程中出现的所有 Attraction(景点), Hotel(酒店), 和 Restaurant(餐厅) 必须且只能从提供的 Input Data (候选资源列表) 中选取。
- 严禁自行捏造、假设或引入任何不在列表中的地点、实体或 ID。

## 严格响应需求 (Requirement Fidelity):
- 必须完全按照 User Requirements 规划行程。例如：如果 transportation.type 包含 "RoundTripFlight"，你必须在行程的第一天安排去程航班 (FLIGHT) 和接机 (TRANSPORT)，在最后一天安排送机 (TRANSPORT) 和回程航班 (FLIGHT)。
- 严格遵守 travel_date 的天数限制和 destination_cities 的城市顺序。
- 必须根据 itinerary.rhythm (如 Moderate) 合理安排每天的活动密度，禁止天马行空或物理上无法实现的紧凑安排。

## 行程逻辑连续性 (Logical Flow):
- 每天的活动必须遵循时间顺序（start_time 到 end_time），不能出现时间重叠。
- 必须包含必要的后勤节点：到达当天的 CHECK_IN，离开当天的 CHECK_OUT，以及每日的三餐 (MEAL，除非明确标注为自由活动)。
- 跨城市移动时，必须安排相应的 TRANSPORT 或 FLIGHT / TRAIN 活动。

## 强制 JSON 输出格式 (Output Formatting):
你的唯一输出必须是一个合法的、可解析的 JSON 对象。
严禁在 JSON 前后输出任何解释性文本、寒暄或 Markdown 代码块标记（除非你的环境要求使用 json  进行包裹，但内部必须纯净）。

必须完全匹配提供的目标 JSON Schema。
```

## 5. 部署与集成

### 5.1 环境配置
1. **n8n 配置**：
   - 安装 n8n：`npm install -g n8n`
   - 启动 n8n：`n8n start`
   - 导入 workflow：通过 n8n UI 导入 JSON 文件

2. **DeepSeek 配置**：
   - 设置 DeepSeek API 凭证

3. **MySQL 配置**：
   - 配置 MySQL 数据库连接
   - 准备景点、酒店、餐厅数据表

4. **文件系统配置**：
   - 创建 /home/node/.n8n-files/ 目录
   - 准备 db.txt 文件，包含数据表结构信息

### 5.2 集成测试
1. **测试数据**：准备完整的旅游需求 JSON 数据
2. **数据库测试**：验证 MySQL 数据库连接和数据表结构
3. **Workflow 测试**：通过 Postman 发送 POST 请求到 webhook 端点
4. **结果验证**：检查返回的行程规划是否符合预期

## 6. 监控与维护

### 6.1 日志记录
- n8n 工作流执行日志
- DeepSeek API 调用日志
- MySQL 数据库查询日志

### 6.2 错误处理
- 数据验证错误
- 数据库连接失败
- SQL 查询错误
- AI 生成错误
- 网络超时

### 6.3 性能优化
- 缓存数据表结构信息
- 优化 SQL 查询语句
- 批量处理数据库请求
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
2. 循环处理每个目的地城市
3. 读取数据表结构并生成 AI SQL 查询
4. 从 MySQL 数据库查询景点、酒店、餐厅数据
5. 合并数据并生成详细的旅游行程
6. 返回完整的行程规划结果

系统采用了模块化设计，具有良好的可扩展性和可维护性，能够满足不同用户的旅游规划需求。通过使用 DeepSeek AI 模型生成 SQL 查询和行程规划，系统能够根据用户的具体需求提供个性化的旅游行程建议。