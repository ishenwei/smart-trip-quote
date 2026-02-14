# 旅游行程规划n8n工作流设计文档

## 概述

本文档描述了为旅游行程规划系统设计的n8n工作流，该工作流通过webhook接收旅游需求详情页的"旅游行程规划"按钮触发的数据，进行数据验证、处理和结果返回。

## 工作流架构

### 工作流名称
`Travel Itinerary Planning Workflow`

### 触发方式
- **触发器**: Webhook
- **HTTP方法**: POST
- **路径**: `/travel-itinerary-planning`
- **认证方式**: Header Authentication

### 数据流程图

```
Webhook Trigger → Data Validation → Validate Schema → Check Validation
                                                          ↓
                                              ┌─────────────┴─────────────┐
                                              ↓                           ↓
                                        Process Itinerary          Error Handler
                                              ↓                           ↓
                                        HTTP Request            Set Error Response
                                              ↓                           ↓
                                        Log Processing              Respond Error
                                              ↓
                                        Set Success Response
                                              ↓
                                        Respond Success
```

## 节点详细说明

### 1. Webhook Trigger（触发器）
- **类型**: `n8n-nodes-base.webhook`
- **功能**: 接收来自旅游需求详情页的POST请求
- **配置**:
  - HTTP Method: POST
  - Path: `travel-itinerary-planning`
  - Response Mode: responseNode
  - Authentication: headerAuth

### 2. Data Validation（数据验证准备）
- **类型**: `n8n-nodes-base.set`
- **功能**: 提取和准备验证所需的数据
- **输出字段**:
  - `validationResult`: 初始化验证结果对象
  - `requirement_id`: 从请求体中提取的需求ID
  - `requirement_json_data`: 从请求体中提取的JSON数据

### 3. Validate Schema（模式验证）
- **类型**: `n8n-nodes-base.code`
- **功能**: 执行JavaScript代码验证数据结构
- **验证规则**:

#### 必填字段验证（errors）
- `requirement_id`: 必须存在
- `requirement_json_data`: 必须存在
- `base_info`: 必须存在
- `base_info.origin`: 必须存在
- `base_info.destination_cities`: 必须非空数组
- `base_info.trip_days`: 必须大于等于1

#### 可选字段验证（warnings）
- `base_info.travel_date`: 缺失时发出警告
- `preferences`: 缺失时发出警告
- `budget`: 缺失时发出警告

**验证结果结构**:
```javascript
{
  isValid: boolean,
  errors: string[],
  warnings: string[]
}
```

### 4. Check Validation（条件分支）
- **类型**: `n8n-nodes-base.if`
- **功能**: 根据验证结果路由到不同的处理分支
- **条件**: `validationResult.isValid === true`
- **分支**:
  - **True分支**: Process Itinerary → 正常处理流程
  - **False分支**: Error Handler → 错误处理流程

### 5. Process Itinerary（处理行程）
- **类型**: `n8n-nodes-base.set`
- **功能**: 设置处理状态和时间戳
- **输出字段**:
  - `processStatus`: "processing"
  - `timestamp`: ISO格式时间戳

### 6. HTTP Request（模拟API调用）
- **类型**: `n8n-nodes-base.set`
- **功能**: 模拟第三方服务调用（实际使用时可替换为真实的HTTP请求节点）
- **输出字段**:
  - `apiResponse`: API响应对象
  - `itinerary_id`: 生成的行程ID

### 7. Log Processing（日志记录）
- **类型**: `n8n-nodes-base.set`
- **功能**: 记录处理日志
- **输出字段**:
  - `logEntry`: 包含requirement_id、status、timestamp和validation信息的日志对象

### 8. Set Success Response（设置成功响应）
- **类型**: `n8n-nodes-base.set`
- **功能**: 构建成功的JSON响应
- **响应格式**:
```json
{
  "success": true,
  "message": "旅游行程规划已成功启动",
  "data": {
    "requirement_id": "REQ-xxx",
    "status": "processing",
    "timestamp": "2026-02-14T00:00:00.000Z"
  }
}
```

### 9. Respond Success（返回成功响应）
- **类型**: `n8n-nodes-base.respondToWebhook`
- **功能**: 向webhook调用方返回成功响应
- **配置**:
  - Respond With: json
  - Response Body: JSON格式的响应数据

### 10. Error Handler（错误处理器）
- **类型**: `n8n-nodes-base.set`
- **功能**: 准备错误信息
- **输出字段**:
  - `errorMessage`: "数据验证失败"
  - `errorDetails`: 验证错误列表

### 11. Set Error Response（设置错误响应）
- **类型**: `n8n-nodes-base.set`
- **功能**: 构建错误的JSON响应
- **响应格式**:
```json
{
  "success": false,
  "message": "数据验证失败",
  "errors": ["error1", "error2"],
  "timestamp": "2026-02-14T00:00:00.000Z"
}
```

### 12. Respond Error（返回错误响应）
- **类型**: `n8n-nodes-base.respondToWebhook`
- **功能**: 向webhook调用方返回错误响应
- **配置**:
  - Respond With: json
  - Response Body: JSON格式的错误响应

## 数据格式规范

### 请求格式（POST /travel-itinerary-planning）

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <your-token>
```

**Body**:
```json
{
  "requirement_id": "REQ-20260214-001",
  "requirement_json_data": {
    "requirement_id": "REQ-20260214-001",
    "base_info": {
      "origin": {
        "name": "北京",
        "code": "BJS",
        "type": "Domestic"
      },
      "destination_cities": ["上海", "杭州", "苏州"],
      "trip_days": 5,
      "group_size": {
        "adults": 2,
        "children": 1,
        "seniors": 0,
        "total": 3
      },
      "travel_date": {
        "start_date": "2026-03-01",
        "end_date": "2026-03-05",
        "is_flexible": true
      }
    },
    "preferences": {
      "transportation": {
        "type": "high_speed_rail",
        "notes": "希望乘坐高铁"
      },
      "accommodation": {
        "level": "4_star",
        "requirements": "需要家庭房"
      },
      "itinerary": {
        "rhythm": "moderate",
        "tags": ["历史文化", "美食体验", "自然风光"],
        "special_constraints": {
          "must_visit_spots": ["外滩", "西湖"],
          "avoid_activities": ["爬山", "潜水"]
        }
      }
    },
    "budget": {
      "level": "medium",
      "currency": "CNY",
      "range": {
        "min": 10000,
        "max": 15000
      },
      "budget_notes": "预算可适当浮动"
    },
    "metadata": {
      "source_type": "form",
      "status": "pending",
      "assumptions": [],
      "is_template": false,
      "template_info": {
        "name": null,
        "category": null
      },
      "audit_trail": {
        "created_at": "2026-02-14T00:00:00Z",
        "updated_at": "2026-02-14T00:00:00Z",
        "created_by": "admin",
        "reviewed_by": null
      }
    },
    "extension": {}
  }
}
```

### 成功响应格式

**Status**: 200 OK

```json
{
  "success": true,
  "message": "旅游行程规划已成功启动",
  "data": {
    "requirement_id": "REQ-20260214-001",
    "status": "processing",
    "timestamp": "2026-02-14T00:00:00.000Z"
  }
}
```

### 错误响应格式

**Status**: 400 Bad Request

```json
{
  "success": false,
  "message": "数据验证失败",
  "errors": [
    "requirement_id is missing",
    "destination_cities is empty",
    "trip_days must be at least 1"
  ],
  "timestamp": "2026-02-14T00:00:00.000Z"
}
```

## 前端集成

### 前端代码示例

在旅游需求详情页的JavaScript中添加以下代码：

```javascript
document.addEventListener("DOMContentLoaded", function() {
    const btn = document.getElementById("itinerary-plan-btn");
    const messageDiv = document.getElementById("itinerary-plan-message");
    let isSubmitting = false;

    btn.addEventListener("click", async function() {
        if (isSubmitting) return;
        isSubmitting = true;
        btn.disabled = true;
        btn.style.opacity = "0.6";
        btn.innerHTML = "处理中...";
        messageDiv.style.display = "none";

        const requirementId = btn.dataset.requirementId;

        try {
            // 获取requirement_json_data
            const response = await fetch(`/admin/apps/requirement/${requirementId}/get-json-data/`, {
                method: "GET",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                }
            });

            const data = await response.json();

            // 发送到n8n工作流
            const n8nResponse = await fetch('https://n8n.ishenwei.online/webhook/travel-itinerary-planning', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_AUTH_TOKEN'
                },
                body: JSON.stringify({
                    requirement_id: requirementId,
                    requirement_json_data: data.requirement_json_data
                })
            });

            const result = await n8nResponse.json();

            if (result.success) {
                messageDiv.style.backgroundColor = "#d4edda";
                messageDiv.style.color = "#155724";
                messageDiv.style.border = "1px solid #c3e6cb";
                messageDiv.innerHTML = result.message;
            } else {
                messageDiv.style.backgroundColor = "#f8d7da";
                messageDiv.style.color = "#721c24";
                messageDiv.style.border = "1px solid #f5c6cb";
                messageDiv.innerHTML = "错误: " + (result.message || "生成行程规划失败");
            }
            messageDiv.style.display = "block";
        } catch (error) {
            messageDiv.style.backgroundColor = "#f8d7da";
            messageDiv.style.color = "#721c24";
            messageDiv.style.border = "1px solid #f5c6cb";
            messageDiv.innerHTML = "网络错误: 请稍后重试";
            messageDiv.style.display = "block";
        } finally {
            isSubmitting = false;
            btn.disabled = false;
            btn.style.opacity = "1";
            btn.innerHTML = "旅游行程规划";
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
```

## 安全性考虑

### 1. 认证
- 使用Header Authentication保护webhook端点
- 前端请求必须包含有效的Authorization token

### 2. 数据验证
- 严格的输入验证
- 防止SQL注入和XSS攻击
- 验证所有必填字段

### 3. 错误处理
- 不暴露敏感的系统信息
- 提供用户友好的错误消息
- 记录详细的错误日志用于调试

### 4. 速率限制
- 建议在n8n中配置速率限制
- 防止滥用和DDoS攻击

## 扩展性设计

### 1. 第三方服务集成
工作流中的"HTTP Request"节点可以替换为实际的第三方服务调用：
- AI行程规划服务
- 地图和路线规划API
- 酒店预订API
- 景点信息API

### 2. 数据持久化
可以添加节点将处理结果保存到数据库：
- PostgreSQL节点
- MySQL节点
- MongoDB节点

### 3. 通知功能
可以添加通知节点：
- Email节点
- Slack节点
- 短信节点

### 4. 异步处理
对于长时间运行的行程规划，可以：
- 使用队列系统
- 添加状态检查端点
- 实现进度回调

## 监控和日志

### 关键指标
- 请求成功率
- 平均响应时间
- 验证失败率
- 错误类型分布

### 日志记录
- 所有请求的验证结果
- 处理时间戳
- 错误详情
- API调用响应

## 部署步骤

### 1. 导入工作流
1. 登录n8n实例
2. 点击"Import from File"
3. 选择`travel_itinerary_planning_workflow.json`
4. 保存工作流

### 2. 配置认证
1. 在Webhook Trigger节点配置认证方式
2. 生成或配置认证token
3. 将token提供给前端开发团队

### 3. 测试工作流
1. 激活工作流
2. 使用Postman或curl测试webhook端点
3. 验证成功和错误场景
4. 检查响应格式

### 4. 前端集成
1. 更新前端代码以调用新的webhook端点
2. 配置认证token
3. 测试完整的用户流程

### 5. 监控设置
1. 配置n8n执行日志
2. 设置错误通知
3. 建立监控仪表板

## 测试用例

### 测试用例1：正常请求
```bash
curl -X POST https://n8n.ishenwei.online/webhook/travel-itinerary-planning \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d @valid_request.json
```

**预期结果**: 返回200 OK和成功响应

### 测试用例2：缺少必填字段
```bash
curl -X POST https://n8n.ishenwei.online/webhook/travel-itinerary-planning \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"requirement_id": "REQ-001"}'
```

**预期结果**: 返回400 Bad Request和错误详情

### 测试用例3：无效的JSON数据
```bash
curl -X POST https://n8n.ishenwei.online/webhook/travel-itinerary-planning \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"requirement_id": "REQ-001", "requirement_json_data": {}}'
```

**预期结果**: 返回400 Bad Request和验证错误列表

## 故障排查

### 常见问题

1. **工作流未触发**
   - 检查工作流是否已激活
   - 验证webhook URL是否正确
   - 确认认证token是否有效

2. **验证总是失败**
   - 检查请求体格式是否正确
   - 验证所有必填字段是否存在
   - 查看n8n执行日志获取详细错误信息

3. **响应超时**
   - 检查网络连接
   - 增加HTTP请求超时设置
   - 优化处理逻辑减少执行时间

4. **认证失败**
   - 验证Authorization header格式
   - 检查token是否过期
   - 确认认证配置正确

## 性能优化建议

1. **缓存验证结果**
   - 对相同的需求ID缓存验证结果
   - 减少重复验证的开销

2. **异步处理**
   - 将长时间运行的行程规划放入队列
   - 立即返回处理状态
   - 提供状态查询端点

3. **批量处理**
   - 支持批量处理多个需求
   - 减少API调用次数

4. **负载均衡**
   - 在多个n8n实例间分发请求
   - 使用负载均衡器

## 总结

本n8n工作流提供了一个完整、安全、可扩展的旅游行程规划解决方案。通过严格的数据验证、清晰的错误处理和灵活的架构设计，确保了系统的稳定性和可维护性。工作流可以轻松集成到现有的旅游需求详情页，并为未来的功能扩展提供了良好的基础。
