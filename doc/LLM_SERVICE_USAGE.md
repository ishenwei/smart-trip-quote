# LLM服务使用文档

## 概述

LLM服务是一个功能完整的旅游需求处理系统，通过自然语言输入调用LLM服务，将用户需求转换为结构化的JSON数据并保存到数据库。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例配置文件并填写实际的API密钥：

```bash
cp .env.llm.example .env
```

编辑 `.env` 文件，填写您的API密钥：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

或者使用JSON配置文件 `config/llm_config.json`。

### 3. 运行Django服务器

```bash
python manage.py runserver
```

## API使用示例

### 1. 处理旅游需求

**请求：**

```bash
curl -X POST http://localhost:8000/api/llm/process/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想从北京去上海旅游5天，2个成人，预算5000到10000元，想住舒适型酒店，坐高铁去",
    "provider": "deepseek",
    "client_id": "user123",
    "save_to_db": true
  }'
```

**响应：**

```json
{
  "success": true,
  "requirement_id": "REQ-20240120-1234",
  "raw_response": "{...LLM原始响应...}",
  "structured_data": {
    "requirement_id": "REQ-20240120-1234",
    "base_info": {
      "origin": {
        "name": "北京",
        "code": "BJS",
        "type": "city"
      },
      "destination_cities": [
        {
          "name": "上海",
          "code": "SHA",
          "country": "中国"
        }
      ],
      "trip_days": 5,
      "group_size": {
        "adults": 2,
        "children": 0,
        "seniors": 0,
        "total": 2
      },
      "travel_date": {
        "start_date": null,
        "end_date": null,
        "is_flexible": false
      }
    },
    "preferences": {
      "transportation": {
        "type": "HighSpeedTrain",
        "notes": ""
      },
      "accommodation": {
        "level": "Comfort",
        "requirements": ""
      },
      "itinerary": {
        "rhythm": "Moderate",
        "tags": [],
        "special_constraints": {
          "must_visit_spots": [],
          "avoid_activities": []
        }
      }
    },
    "budget": {
      "level": "Comfort",
      "currency": "CNY",
      "range": {
        "min": 5000,
        "max": 10000
      },
      "budget_notes": ""
    },
    "metadata": {
      "source_type": "NaturalLanguage",
      "status": "PendingReview",
      "assumptions": []
    }
  },
  "validation_errors": null,
  "warnings": [],
  "error": null,
  "llm_info": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "tokens_used": 150,
    "response_time": 1.23
  }
}
```

### 2. 获取提供商信息

**请求：**

```bash
curl http://localhost:8000/api/llm/provider-info/?provider=deepseek
```

**响应：**

```json
{
  "provider": "deepseek",
  "model": "deepseek-chat",
  "api_url": "https://api.deepseek.com/v1/chat/completions"
}
```

### 3. 获取限流统计

**请求：**

```bash
curl http://localhost:8000/api/llm/rate-limit-stats/?client_id=user123
```

**响应：**

```json
{
  "enabled": true,
  "requests_per_minute": 60,
  "requests_per_hour": 1000,
  "burst_size": 10,
  "current_minute_requests": 5,
  "current_hour_requests": 45,
  "minute_remaining": 55,
  "hour_remaining": 955,
  "client_id": "user123",
  "client_minute_requests": 3,
  "client_hour_requests": 20,
  "client_minute_remaining": 57,
  "client_hour_remaining": 980
}
```

### 4. 获取缓存统计

**请求：**

```bash
curl http://localhost:8000/api/llm/cache-stats/
```

**响应：**

```json
{
  "total_entries": 25,
  "total_hits": 150,
  "cache_size_mb": 0.5
}
```

### 5. 清除缓存

**请求：**

```bash
curl -X POST http://localhost:8000/api/llm/cache/clear/
```

**响应：**

```json
{
  "message": "Cache cleared successfully"
}
```

### 6. 重新加载配置

**请求：**

```bash
curl -X POST http://localhost:8000/api/llm/config/reload/
```

**响应：**

```json
{
  "message": "Configuration reloaded successfully"
}
```

### 7. 健康检查

**请求：**

```bash
curl http://localhost:8000/api/llm/health/
```

**响应：**

```json
{
  "status": "healthy",
  "available_providers": ["deepseek", "gemini", "openai"],
  "default_provider": "deepseek"
}
```

## Python代码示例

### 同步调用

```python
from services.llm.service import LLMRequirementService
from services.llm.config import LLMProvider

# 创建服务实例
service = LLMRequirementService()

# 处理用户输入
result = service.process_requirement_sync(
    user_input="我想从北京去上海旅游5天，2个成人",
    provider=LLMProvider.DEEPSEEK,
    client_id="user123",
    save_to_db=True
)

if result.success:
    print(f"需求ID: {result.requirement_id}")
    print(f"结构化数据: {result.structured_data}")
    print(f"警告: {result.warnings}")
else:
    print(f"处理失败: {result.error}")
```

### 异步调用

```python
import asyncio
from services.llm.service import LLMRequirementService
from services.llm.config import LLMProvider

async def process_requirement():
    service = LLMRequirementService()
    
    result = await service.process_requirement_async(
        user_input="我想从北京去上海旅游5天，2个成人",
        provider=LLMProvider.DEEPSEEK,
        client_id="user123",
        save_to_db=True
    )
    
    if result.success:
        print(f"需求ID: {result.requirement_id}")
        print(f"结构化数据: {result.structured_data}")
    else:
        print(f"处理失败: {result.error}")

# 运行异步函数
asyncio.run(process_requirement())
```

### 批量处理

```python
from services.llm.service import LLMRequirementService
from services.llm.config import LLMProvider

service = LLMRequirementService()

user_inputs = [
    "我想从北京去上海旅游5天，2个成人",
    "我想从广州去成都旅游3天，1个成人1个儿童",
    "我想从深圳去杭州旅游4天，3个成人"
]

results = []
for user_input in user_inputs:
    result = service.process_requirement_sync(
        user_input=user_input,
        provider=LLMProvider.DEEPSEEK,
        save_to_db=True
    )
    results.append(result)

# 统计成功和失败
success_count = sum(1 for r in results if r.success)
failure_count = len(results) - success_count

print(f"成功: {success_count}, 失败: {failure_count}")
```

### 获取统计信息

```python
from services.llm.service import LLMRequirementService

service = LLMRequirementService()

# 获取限流统计
rate_stats = service.get_rate_limit_stats(client_id="user123")
print(f"每分钟剩余: {rate_stats['minute_remaining']}")
print(f"每小时剩余: {rate_stats['hour_remaining']}")

# 获取缓存统计
cache_stats = service.get_cache_stats()
print(f"缓存条目: {cache_stats['total_entries']}")
print(f"缓存命中: {cache_stats['total_hits']}")
```

## 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API密钥 | - |
| DEEPSEEK_API_URL | DeepSeek API地址 | https://api.deepseek.com/v1/chat/completions |
| DEEPSEEK_MODEL | DeepSeek模型名称 | deepseek-chat |
| GEMINI_API_KEY | Gemini API密钥 | - |
| GEMINI_API_URL | Gemini API地址 | https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent |
| GEMINI_MODEL | Gemini模型名称 | gemini-pro |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| OPENAI_API_URL | OpenAI API地址 | https://api.openai.com/v1/chat/completions |
| OPENAI_MODEL | OpenAI模型名称 | gpt-4 |
| ENCRYPTION_KEY | 加密密钥 | - |
| LLM_LOG_LEVEL | 日志级别 | INFO |
| LLM_LOG_FILE | 日志文件路径 | logs/llm_service.log |
| LLM_REQUESTS_PER_MINUTE | 每分钟请求数限制 | 60 |
| LLM_REQUESTS_PER_HOUR | 每小时请求数限制 | 1000 |
| LLM_BURST_SIZE | 突发请求数限制 | 10 |
| LLM_RATE_LIMIT_ENABLED | 是否启用限流 | true |
| LLM_CACHE_ENABLED | 是否启用缓存 | true |
| LLM_CACHE_TTL | 缓存过期时间（秒） | 3600 |

### JSON配置文件

`config/llm_config.json` 提供了更详细的配置选项：

```json
{
  "providers": {
    "deepseek": {
      "api_key": "your_api_key",
      "api_url": "https://api.deepseek.com/v1/chat/completions",
      "model": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 2000,
      "timeout": 30,
      "max_retries": 3,
      "retry_delay": 1.0,
      "enable_cache": true,
      "cache_ttl": 3600
    }
  },
  "rate_limit": {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "burst_size": 10,
    "enabled": true
  },
  "logging": {
    "level": "INFO",
    "log_file": "logs/llm_service.log",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "enable_request_logging": true,
    "enable_response_logging": true
  }
}
```

## 错误处理

### 常见错误及解决方案

1. **API密钥未配置**
   - 错误信息: `No configuration found for provider`
   - 解决: 检查 `.env` 或 `llm_config.json` 中的API密钥配置

2. **限流触发**
   - 错误信息: `Rate limit exceeded`
   - 解决: 减少请求频率或增加限流配置

3. **验证失败**
   - 错误信息: `Validation failed`
   - 解决: 检查LLM返回的数据格式是否符合要求

4. **数据库保存失败**
   - 错误信息: `Failed to save to database`
   - 解决: 检查数据库连接和数据完整性

## 测试

运行所有测试：

```bash
python tests/run_tests.py
```

运行特定测试文件：

```bash
python tests/run_tests.py test_llm_providers
```

查看测试覆盖率：

```bash
python tests/run_tests.py --coverage
```

## 性能优化建议

1. **启用缓存**: 对于重复的输入，缓存可以显著减少API调用
2. **调整限流**: 根据实际使用情况调整限流参数
3. **选择合适的模型**: 根据需求选择不同性能的模型
4. **异步处理**: 对于高并发场景，使用异步API

## 安全建议

1. **保护API密钥**: 不要将API密钥提交到版本控制系统
2. **使用加密**: 启用API密钥加密存储
3. **日志脱敏**: 确保日志中不包含敏感信息
4. **访问控制**: 在生产环境中添加适当的访问控制

## 支持的LLM提供商

- **DeepSeek**: 深度求索的AI模型
- **Gemini**: Google的AI模型
- **OpenAI**: OpenAI的GPT系列模型

## 数据模型

完整的Requirement模型定义请参考: [apps/models/requirement.py](file:///c:/project/smart_trip_quote/apps/models/requirement.py)

## API文档

启动服务后，访问以下地址查看Swagger API文档：

```
http://localhost:8000/swagger/
```

## 联系方式

如有问题，请提交Issue或联系开发团队。
