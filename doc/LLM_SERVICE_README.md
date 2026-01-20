# LLM旅游需求处理服务

一个功能完整的LLM调用接口程序，用于接收用户关于旅游需求的自然语言输入，通过精心设计的提示词工程调用LLM服务，并将LLM返回结果解析为符合预设requirement模型规范的结构化JSON数据。

## 功能特性

### 核心功能
- ✅ 自然语言输入处理
- ✅ 多LLM提供商支持（DeepSeek、Gemini、OpenAI）
- ✅ 结构化数据提取与验证
- ✅ 数据持久化到数据库
- ✅ 同步和异步API调用

### 配置管理
- ✅ 基于配置文件的LLM服务管理
- ✅ 环境变量支持
- ✅ 动态配置切换
- ✅ API请求超时配置
- ✅ 重试策略配置
- ✅ 缓存机制配置

### 性能与安全
- ✅ 请求限流机制（每分钟、每小时、突发）
- ✅ API密钥加密存储
- ✅ 敏感信息脱敏
- ✅ 响应缓存
- ✅ 完善的日志记录

### 测试覆盖
- ✅ LLM调用测试
- ✅ JSON返回测试
- ✅ 数据库操作测试
- ✅ 端到端流程测试
- ✅ 边界条件测试

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.llm.example .env
# 编辑 .env 文件，填写您的API密钥
```

### 3. 运行服务

```bash
python manage.py runserver
```

### 4. 测试API

```bash
curl -X POST http://localhost:8000/api/llm/process/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想从北京去上海旅游5天，2个成人，预算5000到10000元"
  }'
```

## 项目结构

```
smart_trip_quote/
├── services/llm/              # LLM服务核心模块
│   ├── base.py                # 基础类定义
│   ├── config.py              # 配置管理
│   ├── factory.py             # 提供商工厂
│   ├── extractor.py           # 数据提取与验证
│   ├── persistence.py         # 数据持久化
│   ├── rate_limiter.py        # 请求限流
│   ├── security.py            # 安全管理
│   ├── cache.py              # 缓存管理
│   ├── logger.py             # 日志管理
│   ├── service.py            # 主服务类
│   └── providers/           # LLM提供商适配层
│       ├── deepseek.py
│       ├── gemini.py
│       └── openai.py
├── apps/api/                 # API接口
│   ├── serializers/          # 序列化器
│   └── views/              # 视图
├── tests/                    # 测试用例
│   ├── test_llm_providers.py
│   ├── test_llm_extractor.py
│   ├── test_llm_rate_limiter.py
│   ├── test_llm_security.py
│   ├── test_llm_service.py
│   ├── test_llm_end_to_end.py
│   └── run_tests.py
├── doc/                      # 文档
│   ├── LLM_SERVICE_USAGE.md
│   └── LLM_SERVICE_ARCHITECTURE.md
├── config/
│   ├── llm_config.json       # LLM配置文件
│   └── settings.py
└── requirements.txt
```

## API文档

### 主要端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/llm/process/` | POST | 处理用户输入 |
| `/api/llm/provider-info/` | GET | 获取提供商信息 |
| `/api/llm/rate-limit-stats/` | GET | 获取限流统计 |
| `/api/llm/cache-stats/` | GET | 获取缓存统计 |
| `/api/llm/cache/clear/` | POST | 清除缓存 |
| `/api/llm/config/reload/` | POST | 重新加载配置 |
| `/api/llm/health/` | GET | 健康检查 |

详细API文档请参考: [LLM_SERVICE_USAGE.md](file:///c:/project/smart_trip_quote/doc/LLM_SERVICE_USAGE.md)

## 使用示例

### Python代码示例

```python
from services.llm.service import LLMRequirementService
from services.llm.config import LLMProvider

# 创建服务实例
service = LLMRequirementService()

# 处理用户输入
result = service.process_requirement_sync(
    user_input="我想从北京去上海旅游5天，2个成人",
    provider=LLMProvider.DEEPSEEK,
    save_to_db=True
)

if result.success:
    print(f"需求ID: {result.requirement_id}")
    print(f"结构化数据: {result.structured_data}")
else:
    print(f"处理失败: {result.error}")
```

### cURL示例

```bash
curl -X POST http://localhost:8000/api/llm/process/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想从北京去上海旅游5天，2个成人，预算5000到10000元",
    "provider": "deepseek",
    "save_to_db": true
  }'
```

## 测试

运行所有测试：

```bash
python tests/run_tests.py
```

运行特定测试：

```bash
python tests/run_tests.py test_llm_providers
```

查看测试覆盖率：

```bash
python tests/run_tests.py --coverage
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API密钥 | - |
| GEMINI_API_KEY | Gemini API密钥 | - |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| LLM_REQUESTS_PER_MINUTE | 每分钟请求数限制 | 60 |
| LLM_REQUESTS_PER_HOUR | 每小时请求数限制 | 1000 |
| LLM_CACHE_ENABLED | 是否启用缓存 | true |

详细配置说明请参考: [LLM_SERVICE_USAGE.md](file:///c:/project/smart_trip_quote/doc/LLM_SERVICE_USAGE.md)

## 架构设计

详细的架构设计说明请参考: [LLM_SERVICE_ARCHITECTURE.md](file:///c:/project/smart_trip_quote/doc/LLM_SERVICE_ARCHITECTURE.md)

## 支持的LLM提供商

- **DeepSeek**: 深度求索的AI模型
- **Gemini**: Google的AI模型
- **OpenAI**: OpenAI的GPT系列模型

## 性能特性

- **缓存机制**: 相同输入直接返回缓存结果，减少API调用
- **异步支持**: 支持高并发异步处理
- **请求限流**: 多级限流保护，防止API滥用
- **连接池**: 复用HTTP连接，提高性能

## 安全特性

- **API密钥加密**: 使用Fernet加密存储API密钥
- **日志脱敏**: 自动清理日志中的敏感信息
- **输入验证**: 严格的数据验证，防止恶意输入
- **访问控制**: 支持客户端级别的访问控制

## 扩展性

### 添加新的LLM提供商

1. 在 `services/llm/providers/` 下创建新的提供商类
2. 继承 `BaseLLMProvider`
3. 实现 `generate` 和 `generate_sync` 方法
4. 在 `ProviderFactory` 中注册新提供商

### 自定义验证规则

修改 `RequirementExtractor` 中的验证方法，添加自定义验证逻辑。

### 自定义限流策略

继承 `RateLimiter` 类，重写限流逻辑。

## 依赖项

- Django >= 5.0
- djangorestframework >= 3.14.0
- aiohttp >= 3.9.0
- requests >= 2.31.0
- cryptography >= 41.0.0
- drf-yasg >= 1.21.0
- pytest >= 7.4.0

完整依赖列表请查看: [requirements.txt](file:///c:/project/smart_trip_quote/requirements.txt)

## 故障处理

系统实现了完善的错误处理机制：

- **API调用失败**: 自动重试，最多3次
- **验证失败**: 返回详细的错误信息
- **数据库错误**: 事务回滚，保证数据一致性
- **限流触发**: 返回429状态码和重试建议
- **超时处理**: 合理的超时设置，避免长时间等待

## 监控与日志

系统提供完善的监控和日志功能：

- **请求日志**: 记录所有LLM请求
- **响应日志**: 记录所有LLM响应
- **错误日志**: 记录所有错误信息
- **性能日志**: 记录响应时间和token使用量
- **限流统计**: 实时查看限流状态
- **缓存统计**: 实时查看缓存命中率

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。

---

**注意**: 请勿将API密钥提交到版本控制系统。使用 `.env.llm.example` 作为模板，创建自己的 `.env` 文件。
