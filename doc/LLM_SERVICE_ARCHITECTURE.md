# LLM服务架构说明

## 项目结构

```
smart_trip_quote/
├── apps/
│   ├── api/
│   │   ├── serializers/
│   │   │   └── llm_serializer.py          # API序列化器
│   │   ├── views/
│   │   │   └── llm_views.py               # API视图
│   │   └── urls.py                        # API路由
│   └── models/
│       └── requirement.py                  # Requirement数据模型
├── config/
│   ├── llm_config.json                     # LLM配置文件
│   ├── settings.py                        # Django设置
│   └── urls.py                           # 主路由
├── services/
│   └── llm/
│       ├── __init__.py
│       ├── base.py                         # 基础类定义
│       ├── config.py                       # 配置管理
│       ├── factory.py                      # 提供商工厂
│       ├── extractor.py                    # 数据提取与验证
│       ├── persistence.py                  # 数据持久化
│       ├── rate_limiter.py                # 请求限流
│       ├── security.py                     # 安全管理
│       ├── cache.py                        # 缓存管理
│       ├── logger.py                       # 日志管理
│       ├── service.py                      # 主服务类
│       └── providers/
│           ├── __init__.py
│           ├── deepseek.py                # DeepSeek提供商
│           ├── gemini.py                  # Gemini提供商
│           └── openai.py                 # OpenAI提供商
├── tests/
│   ├── test_llm_providers.py              # 提供商测试
│   ├── test_llm_extractor.py              # 提取器测试
│   ├── test_llm_rate_limiter.py          # 限流测试
│   ├── test_llm_security.py              # 安全测试
│   ├── test_llm_service.py               # 服务测试
│   ├── test_llm_end_to_end.py            # 端到端测试
│   └── run_tests.py                     # 测试运行脚本
├── doc/
│   └── LLM_SERVICE_USAGE.md              # 使用文档
├── requirements.txt                       # Python依赖
└── .env.llm.example                     # 环境变量示例
```

## 核心模块说明

### 1. 配置管理 (config.py)

**功能：**
- 管理LLM提供商配置
- 支持JSON配置文件和环境变量
- 单例模式确保配置一致性

**主要类：**
- `LLMConfig`: LLM配置数据类
- `RateLimitConfig`: 限流配置数据类
- `LoggingConfig`: 日志配置数据类
- `ConfigManager`: 配置管理器（单例）

### 2. 基础类 (base.py)

**功能：**
- 定义LLM请求和响应的数据结构
- 提供提供商基类接口

**主要类：**
- `LLMRequest`: LLM请求数据类
- `LLMResponse`: LLM响应数据类
- `BaseLLMProvider`: 提供商基类（抽象类）

### 3. 提供商适配层 (providers/)

**功能：**
- 实现不同LLM提供商的API调用
- 统一的接口，支持同步和异步调用

**主要类：**
- `DeepSeekProvider`: DeepSeek API适配器
- `GeminiProvider`: Gemini API适配器
- `OpenAIProvider`: OpenAI API适配器

### 4. 提供商工厂 (factory.py)

**功能：**
- 根据配置创建对应的提供商实例
- 支持动态注册新的提供商

**主要类：**
- `ProviderFactory`: 提供商工厂类

### 5. 数据提取与验证 (extractor.py)

**功能：**
- 从LLM响应中提取JSON数据
- 验证数据符合Requirement模型规范
- 数据标准化处理

**主要类：**
- `RequirementExtractor`: 需求提取器
- `ValidationResult`: 验证结果数据类

### 6. 数据持久化 (persistence.py)

**功能：**
- 将结构化数据保存到数据库
- 提供CRUD操作接口

**主要类：**
- `RequirementService`: 需求服务类

### 7. 请求限流 (rate_limiter.py)

**功能：**
- 实现多级限流（每分钟、每小时、突发）
- 支持客户端级别的限流
- 提供统计信息

**主要类：**
- `RateLimiter`: 限流器类

### 8. 安全管理 (security.py)

**功能：**
- API密钥加密存储
- 敏感数据脱敏
- 日志数据清理

**主要类：**
- `SecurityManager`: 安全管理器（单例）

### 9. 缓存管理 (cache.py)

**功能：**
- LLM响应缓存
- 基于请求内容生成缓存键
- 自动清理过期缓存

**主要类：**
- `CacheManager`: 缓存管理器（单例）

### 10. 日志管理 (logger.py)

**功能：**
- 结构化日志记录
- 支持不同日志级别
- 请求和响应日志

**主要类：**
- `LLMLogger`: LLM日志记录器（单例）

### 11. 主服务类 (service.py)

**功能：**
- 整合所有组件
- 提供统一的处理接口
- 支持同步和异步调用

**主要类：**
- `LLMRequirementService`: LLM需求服务（单例）
- `ProcessResult`: 处理结果数据类

## 数据流程

### 同步处理流程

```
用户输入
    ↓
限流检查
    ↓
缓存查询
    ↓ (缓存未命中)
LLM API调用
    ↓
JSON提取
    ↓
数据验证
    ↓
数据标准化
    ↓
数据库保存
    ↓
返回结果
```

### 异步处理流程

```
用户输入
    ↓
限流检查
    ↓
缓存查询
    ↓ (缓存未命中)
异步LLM API调用
    ↓
JSON提取
    ↓
数据验证
    ↓
数据标准化
    ↓
数据库保存
    ↓
返回结果
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/llm/process/` | POST | 处理用户输入 |
| `/api/llm/provider-info/` | GET | 获取提供商信息 |
| `/api/llm/rate-limit-stats/` | GET | 获取限流统计 |
| `/api/llm/cache-stats/` | GET | 获取缓存统计 |
| `/api/llm/cache/clear/` | POST | 清除缓存 |
| `/api/llm/config/reload/` | POST | 重新加载配置 |
| `/api/llm/health/` | GET | 健康检查 |

## 配置优先级

1. JSON配置文件 (`config/llm_config.json`)
2. 环境变量 (`.env`)
3. 默认值

## 性能优化

1. **缓存机制**: 相同输入直接返回缓存结果
2. **异步支持**: 高并发场景使用异步API
3. **连接池**: 复用HTTP连接
4. **请求批处理**: 支持批量处理

## 安全特性

1. **API密钥加密**: 使用Fernet加密存储
2. **日志脱敏**: 自动清理敏感信息
3. **请求限流**: 防止滥用
4. **输入验证**: 严格的数据验证

## 扩展性

### 添加新的LLM提供商

1. 在 `services/llm/providers/` 下创建新的提供商类
2. 继承 `BaseLLMProvider`
3. 实现 `generate` 和 `generate_sync` 方法
4. 在 `ProviderFactory` 中注册新提供商

### 自定义验证规则

1. 修改 `RequirementExtractor` 中的验证方法
2. 添加新的验证逻辑
3. 返回详细的错误信息

### 自定义限流策略

1. 继承 `RateLimiter` 类
2. 重写限流逻辑
3. 在 `ConfigManager` 中配置新的限流器

## 测试覆盖

- 单元测试: 各个模块的独立测试
- 集成测试: 模块间协作测试
- 端到端测试: 完整流程测试
- 边界测试: 异常情况测试

## 监控指标

- 请求成功率
- 平均响应时间
- 缓存命中率
- 限流触发次数
- 错误类型分布

## 故障处理

1. **API调用失败**: 自动重试机制
2. **验证失败**: 返回详细错误信息
3. **数据库错误**: 事务回滚
4. **限流触发**: 返回429状态码
5. **超时处理**: 合理的超时设置

## 部署建议

1. **环境隔离**: 开发、测试、生产环境分离
2. **配置管理**: 使用环境变量或配置中心
3. **日志收集**: 集中化日志管理
4. **监控告警**: 实时监控和告警
5. **负载均衡**: 多实例部署
