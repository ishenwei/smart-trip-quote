# LLM地理位置异常处理机制文档

## 概述

本文档描述了为基于LLM的旅游需求分析应用程序设计的稳健异常处理机制，专门用于检测和处理LLM未能从用户输入中识别起始位置和目的位置的情况。

## 架构组件

### 1. LocationValidator (位置验证器)

**文件**: `services/llm/location_validator.py`

**功能**:
- 验证LLM响应中的地理位置数据
- 检测缺失的出发地或目的地
- 生成用户友好的错误消息
- 提供输入建议和示例

**核心方法**:

```python
# 验证地理位置数据
result = LocationValidator.validate_locations(data)

# 生成用户友好消息
message = LocationValidator.generate_user_friendly_message(result, user_input)

# 获取输入示例
examples = LocationValidator.get_input_examples()

# 检查是否应该重试
should_retry = LocationValidator.should_retry(result, current_retry, max_retries=3)
```

**验证标准**:

1. **有效的城市名称**:
   - 长度: 2-20个字符
   - 不能是占位符（如"未指定"、"null"、"None"）
   - 必须是字符串类型

2. **有效的出发地**:
   - 必须包含有效的城市名称
   - 不能为null或空字符串

3. **有效的目的地**:
   - 至少包含一个有效的城市名称
   - 必须是列表类型
   - 每个目的地必须是字典类型

**验证状态枚举**:

```python
class LocationValidationStatus(Enum):
    VALID = "valid"                    # 验证通过
    MISSING_ORIGIN = "missing_origin"        # 缺少出发地
    MISSING_DESTINATION = "missing_destination"  # 缺少目的地
    MISSING_BOTH = "missing_both"          # 两者都缺少
    INVALID_FORMAT = "invalid_format"        # 格式错误
    AMBIGUOUS = "ambiguous"                # 信息模糊
```

### 2. ConversationManager (对话管理器)

**文件**: `services/llm/conversation_manager.py`

**功能**:
- 管理用户对话状态
- 跟踪重试次数
- 维护对话上下文
- 自动清理过期对话

**对话状态枚举**:

```python
class ConversationState(Enum):
    INITIAL = "initial"                          # 初始状态
    WAITING_FOR_ORIGIN = "waiting_for_origin"        # 等待出发地
    WAITING_FOR_DESTINATION = "waiting_for_destination"  # 等待目的地
    WAITING_FOR_BOTH = "waiting_for_both"            # 等待两者
    COMPLETED = "completed"                        # 已完成
    MAX_RETRIES_REACHED = "max_retries_reached"    # 达到最大重试次数
```

**核心方法**:

```python
# 创建新对话
context = manager.create_conversation(
    conversation_id="conv-123",
    user_id="user-456",
    original_input="用户输入",
    max_retries=3
)

# 获取对话
context = manager.get_conversation("conv-123")

# 更新对话状态
manager.update_conversation(
    conversation_id="conv-123",
    state=ConversationState.WAITING_FOR_ORIGIN,
    collected_data={'origin': '北京'}
)

# 增加重试次数
context = manager.increment_retry("conv-123")

# 检查是否可以重试
can_retry = context.can_retry()

# 清理过期对话
count = manager.cleanup_expired_conversations()
```

### 3. LocationExceptionHandler (位置异常处理器)

**文件**: `services/llm/location_exception_handler.py`

**功能**:
- 协调整个验证流程
- 生成增强的提示词
- 管理重试逻辑
- 记录验证结果

**核心方法**:

```python
handler = LocationExceptionHandler()

# 处理位置验证
result = handler.handle_location_validation(
    user_input="用户输入",
    llm_response_data=llm_data,
    conversation_id="conv-123",
    user_id="user-456"
)

# 获取对话上下文
context = handler.get_conversation_context("conv-123")

# 清理过期对话
count = handler.cleanup_expired_conversations()

# 获取统计信息
stats = handler.get_statistics()
```

**处理结果**:

```python
@dataclass
class LocationExceptionHandlerResult:
    success: bool                          # 是否成功
    should_continue: bool                    # 是否应该继续处理
    user_message: Optional[str]              # 用户友好消息
    enhanced_prompt: Optional[str]            # 增强的提示词
    conversation_id: Optional[str]            # 对话ID
    retry_count: int                        # 重试次数
    original_data: Optional[Dict[str, Any]]   # 原始数据
    error: Optional[str]                     # 错误信息
    suggestions: Optional[list]               # 建议
```

## 使用示例

### 基本使用流程

```python
from services.llm.service import LLMRequirementService

service = LLMRequirementService()

# 处理用户输入
result = service.process_requirement_sync(
    user_input="我想去旅游",
    client_id="user-123"
)

# 检查结果
if result.success:
    print("处理成功！")
    print(f"需求ID: {result.requirement_id}")
else:
    print("处理失败")
    print(f"错误: {result.error}")
    
    # 检查是否需要用户补充信息
    if result.conversation_id:
        print(f"对话ID: {result.conversation_id}")
        print(f"重试次数: {result.retry_count}")
        
        if result.suggestions:
            print("建议:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
```

### 处理缺失位置信息

```python
# 场景1: 缺少出发地和目的地
user_input = "我想去旅游"
result = service.process_requirement_sync(user_input, client_id="user-1")

# 返回的错误消息:
"""
抱歉，我无法从您的描述中识别出发地和目的地。

您的输入：我想去旅游

请同时提供这两个信息，例如：
• '从北京去上海旅游'
• '从广州出发，去成都玩5天'
• '我想从深圳去杭州'
"""

# 场景2: 缺少出发地
user_input = "去上海旅游5天"
result = service.process_requirement_sync(user_input, client_id="user-1")

# 返回的错误消息:
"""
抱歉，我无法从您的描述中识别出发地。

您的输入：去上海旅游5天

目的地已识别，但请告诉我您从哪个城市出发，例如：
• '从上海出发'
• '我在北京，想去上海'
"""

# 场景3: 缺少目的地
user_input = "从北京出发"
result = service.process_requirement_sync(user_input, client_id="user-1")

# 返回的错误消息:
"""
抱歉，我无法从您的描述中识别目的地。

您的输入：从北京出发

出发地已识别为'北京'，但请告诉我您想去哪个城市，例如：
• '从北京去上海'
• '从北京出发，去成都'
"""
```

### 重试机制

```python
# 第一次尝试
result = service.process_requirement_sync(
    user_input="我想去旅游",
    client_id="user-1"
)

# result.retry_count = 0
# result.conversation_id = "conv-123"
# result.should_continue = True

# 用户根据提示补充信息后，第二次尝试
result = service.process_requirement_sync(
    user_input="从北京出发",
    client_id="conv-123"  # 使用相同的conversation_id
)

# result.retry_count = 1
# result.should_continue = True

# 第三次尝试
result = service.process_requirement_sync(
    user_input="去上海",
    client_id="conv-123"
)

# result.retry_count = 2
# result.should_continue = True

# 第四次尝试（超过最大重试次数）
result = service.process_requirement_sync(
    user_input="还是不清楚",
    client_id="conv-123"
)

# result.retry_count = 3
# result.should_continue = False
# 返回最终错误消息:
"""
抱歉，经过3次尝试后，仍无法识别您的位置信息。

您的原始输入：我想去旅游

请参考以下示例重新描述您的需求：

1. 从北京去上海旅游5天
2. 从广州出发，去成都玩一周
3. 我想从深圳去杭州，3个人
4. 从上海出发去三亚，预算5000元
5. 北京到香港，2个成人，10天行程

或者您可以选择：
• 重新开始对话
• 联系客服获取帮助
"""
```

## API响应格式

### 成功响应

```json
{
  "success": true,
  "requirement_id": "REQ-20250120-0001",
  "raw_response": "{...}",
  "structured_data": {
    "base_info": {
      "origin": {
        "name": "北京",
        "code": "BJS",
        "type": "Domestic"
      },
      "destination_cities": [
        {
          "name": "上海",
          "code": "SHA",
          "country": "中国"
        }
      ],
      ...
    },
    ...
  },
  "validation_errors": [],
  "warnings": [],
  "error": null,
  "llm_info": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "tokens_used": 1234,
    "response_time": 12.5
  }
}
```

### 位置验证失败响应（可重试）

```json
{
  "success": false,
  "requirement_id": null,
  "raw_response": "{...}",
  "structured_data": {
    "base_info": {
      "origin": {
        "name": "未指定",
        "code": null,
        "type": null
      },
      "destination_cities": [
        {
          "name": "未指定",
          "code": null,
          "country": null
        }
      ],
      ...
    },
    ...
  },
  "validation_errors": [],
  "warnings": [],
  "error": "抱歉，我无法从您的描述中识别出发地和目的地。\n\n您的输入：我想去旅游\n\n请同时提供这两个信息，例如：\n• '从北京去上海旅游'\n• '从广州出发，去成都玩5天'\n• '我想从深圳去杭州'",
  "conversation_id": "conv-123",
  "retry_count": 1,
  "suggestions": [
    "请同时提供出发地和目的地，例如：'从北京去上海'",
    "或者分别说明：'出发地：北京，目的地：上海'"
  ],
  "llm_info": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "tokens_used": 1234,
    "response_time": 12.5
  }
}
```

### 达到最大重试次数响应

```json
{
  "success": false,
  "requirement_id": null,
  "raw_response": "{...}",
  "structured_data": null,
  "validation_errors": null,
  "warnings": null,
  "error": "抱歉，经过3次尝试后，仍无法识别您的位置信息。\n\n您的原始输入：我想去旅游\n\n请参考以下示例重新描述您的需求：\n\n1. 从北京去上海旅游5天\n2. 从广州出发，去成都玩一周\n3. 我想从深圳去杭州，3个人\n4. 从上海出发去三亚，预算5000元\n5. 北京到香港，2个成人，10天行程\n\n或者您可以选择：\n• 重新开始对话\n• 联系客服获取帮助",
  "conversation_id": "conv-123",
  "retry_count": 3,
  "suggestions": null,
  "llm_info": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "tokens_used": 1234,
    "response_time": 12.5
  }
}
```

## 日志记录

### 验证成功日志

```json
{
  "timestamp": "2025-01-20T19:00:00.000000",
  "event": "location_validation_success",
  "conversation_id": "conv-123",
  "user_input": "从北京去上海",
  "validation_status": "valid",
  "origin": {
    "name": "北京",
    "code": "BJS",
    "type": "Domestic"
  },
  "destination": [
    {
      "name": "上海",
      "code": "SHA",
      "country": "中国"
    }
  ]
}
```

### 验证失败日志

```json
{
  "timestamp": "2025-01-20T19:00:00.000000",
  "event": "location_validation_failed",
  "conversation_id": "conv-123",
  "user_input": "我想去旅游",
  "validation_status": "missing_both",
  "error_message": "未能识别出发地和目的地信息",
  "origin": {
    "name": "未指定",
    "code": null,
    "type": null
  },
  "destination": [
    {
      "name": "未指定",
      "code": null,
      "country": null
    }
  ],
  "retry_count": 1
}
```

### 达到最大重试次数日志

```json
{
  "timestamp": "2025-01-20T19:00:00.000000",
  "event": "max_retries_reached",
  "conversation_id": "conv-123",
  "user_input": "还是不清楚",
  "retry_count": 3,
  "max_retries": 3
}
```

## 统计信息

### 获取对话统计

```python
from services.llm.location_exception_handler import LocationExceptionHandler

handler = LocationExceptionHandler()
stats = handler.get_statistics()

print(f"总对话数: {stats['total_conversations']}")
print(f"活跃对话数: {stats['active_conversations']}")
print(f"已完成对话数: {stats['completed_conversations']}")
print(f"失败对话数: {stats['failed_conversations']}")
print(f"成功率: {stats['success_rate']}%")
```

## 配置选项

### 最大重试次数

默认值: 3

可以在`LocationExceptionHandler`中修改:

```python
class LocationExceptionHandler:
    def _initialize(self):
        self.conversation_manager = ConversationManager()
        self.logger = LLMLogger()
        self.max_retries = 3  # 修改这里
```

### 对话过期时间

- **已完成对话**: 24小时
- **达到最大重试次数**: 1小时
- **活跃对话**: 不过期

可以在`ConversationContext.update_state()`中修改:

```python
def update_state(self, new_state: ConversationState):
    self.state = new_state
    self.updated_at = datetime.now()
    
    if new_state == ConversationState.COMPLETED:
        self.expires_at = datetime.now() + timedelta(hours=24)
    elif new_state == ConversationState.MAX_RETRIES_REACHED:
        self.expires_at = datetime.now() + timedelta(hours=1)
```

## 最佳实践

### 1. 始终使用conversation_id

```python
# 好的做法
result1 = service.process_requirement_sync(
    user_input="我想去旅游",
    client_id="user-123"
)

conversation_id = result1.conversation_id

result2 = service.process_requirement_sync(
    user_input="从北京出发",
    client_id=conversation_id  # 使用相同的conversation_id
)

# 不好的做法
result1 = service.process_requirement_sync(
    user_input="我想去旅游",
    client_id="user-123"
)

result2 = service.process_requirement_sync(
    user_input="从北京出发",
    client_id="user-123"  # 每次都是新的对话
)
```

### 2. 定期清理过期对话

```python
import schedule
import time

from services.llm.location_exception_handler import LocationExceptionHandler

handler = LocationExceptionHandler()

def cleanup():
    count = handler.cleanup_expired_conversations()
    print(f"清理了 {count} 个过期对话")

# 每小时清理一次
schedule.every().hour.do(cleanup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 3. 监控统计信息

```python
import time

from services.llm.location_exception_handler import LocationExceptionHandler

handler = LocationExceptionHandler()

while True:
    stats = handler.get_statistics()
    
    # 发送到监控系统
    send_to_monitoring(stats)
    
    # 检查成功率
    if stats['success_rate'] < 80:
        send_alert("成功率低于80%")
    
    time.sleep(300)  # 每5分钟检查一次
```

### 4. 提供清晰的输入示例

在用户界面中显示示例，帮助用户正确输入:

```html
<div class="input-examples">
  <h3>输入示例</h3>
  <ul>
    <li>从北京去上海旅游5天</li>
    <li>从广州出发，去成都玩一周</li>
    <li>我想从深圳去杭州，3个人</li>
    <li>从上海出发去三亚，预算5000元</li>
    <li>北京到香港，2个成人，10天行程</li>
  </ul>
</div>
```

## 测试

运行测试脚本验证功能:

```bash
python test_location_validator.py
```

测试覆盖:
- ✅ 缺少出发地和目的地
- ✅ 缺少出发地
- ✅ 缺少目的地
- ✅ 有效的出发地和目的地
- ✅ 用户友好消息生成
- ✅ 重试逻辑
- ✅ 输入示例

## 故障排除

### 问题1: 对话ID不工作

**症状**: 每次请求都创建新的对话

**解决方案**: 确保在后续请求中使用相同的`client_id`或`conversation_id`

### 问题2: 重试次数不增加

**症状**: `retry_count`始终为0

**解决方案**: 检查`LocationExceptionHandler`是否正确初始化

### 问题3: 对话不清理

**症状**: 内存使用持续增长

**解决方案**: 定期调用`cleanup_expired_conversations()`

## 总结

该异常处理机制提供了:

1. ✅ **验证逻辑**: 检查LLM响应中的出发地和目的地
2. ✅ **用户友好提示**: 清晰的错误消息和建议
3. ✅ **验证标准**: 明确的地理位置验证规则
4. ✅ **重试限制**: 最大3次重试，防止无限循环
5. ✅ **日志记录**: 详细的验证和重试日志
6. ✅ **对话上下文**: 维护对话状态和历史
7. ✅ **统计分析**: 成功率和对话统计

通过使用这个机制，应用程序可以优雅地处理LLM识别失败的情况，提供良好的用户体验，并收集数据用于模型改进。
