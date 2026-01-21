# Smart Trip Quote

## 项目概述

### 项目背景
随着旅游业的快速发展，用户对个性化旅行规划和报价的需求日益增长。传统的旅行规划方式往往需要用户手动提供大量详细信息，过程繁琐且效率低下。为了解决这一问题，我们开发了Smart Trip Quote（智能旅行报价）系统，利用人工智能技术简化用户需求收集和分析过程，为用户提供快速、准确的旅行报价。

### 项目目标
- 简化用户旅行需求的提交和分析流程
- 利用LLM（大语言模型）技术自动提取和结构化用户需求
- 提供高效、准确的旅行报价服务
- 支持多渠道接入和扩展
- 构建可维护、可扩展的系统架构

### 主要功能
- **智能需求分析**：通过LLM技术自动分析用户的自然语言输入，提取关键旅行信息
- **多LLM提供商支持**：集成OpenAI、Gemini、DeepSeek等多种LLM提供商
- **旅行报价生成**：根据用户需求自动生成详细的旅行报价
- **行程规划**：基于用户需求生成合理的行程安排
- **管理后台**：提供完整的管理功能，包括行程管理、定价规则管理等
- **API接口**：提供RESTful API接口，支持第三方系统集成
- **前端应用**：基于Vue.js的现代化前端界面
- **缓存与性能优化**：实现智能缓存机制，提高系统响应速度
- **速率限制**：内置速率限制功能，防止系统过载
- **安全管理**：实现请求安全检查和处理

## 目录结构

```
smart_trip_quote/
├── apps/                  # Django应用目录
│   ├── admin/             # 管理后台应用
│   │   ├── __init__.py
│   │   ├── itinerary.py   # 行程管理相关功能
│   │   ├── pricing.py     # 定价相关功能
│   │   ├── pricing_rule.py # 定价规则管理
│   │   ├── prompt.py      # 提示词管理
│   │   ├── requirement.py # 需求管理
│   ├── admin_ext/         # 管理后台扩展
│   │   ├── __init__.py
│   │   ├── actions.py     # 管理后台动作
│   │   ├── filters.py     # 管理后台过滤器
│   │   ├── widgets.py     # 管理后台组件
│   ├── api/               # API接口应用
│   │   ├── serializers/   # 序列化器
│   │   │   ├── __init__.py
│   │   │   ├── llm_serializer.py # LLM相关序列化
│   │   │   ├── requirement_serializer.py # 需求序列化
│   │   ├── views/         # 视图
│   │   │   ├── __init__.py
│   │   │   ├── llm_views.py # LLM相关视图
│   │   │   ├── llm_views_simple.py # 简化版LLM视图
│   │   ├── __init__.py
│   │   ├── urls.py        # API路由配置
│   ├── migrations/        # 数据库迁移文件
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_requirement_created_by_and_more.py
│   │   ├── 0003_alter_requirement_travel_end_date_and_more.py
│   │   ├── __init__.py
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py        # 基础模型
│   │   ├── example_usage.py # 示例用法
│   │   ├── itinerary.py   # 行程模型
│   │   ├── pricing.py     # 定价模型
│   │   ├── requirement.py # 需求模型
│   │   ├── status_manager.py # 状态管理
│   │   ├── template_manager.py # 模板管理
│   │   ├── validators.py  # 验证器
│   ├── web/               # 前端应用
│   │   ├── public/        # 静态资源
│   │   │   ├── vite.svg
│   │   ├── src/           # 源代码
│   │   │   ├── assets/    # 资源文件
│   │   │   │   ├── vue.svg
│   │   │   ├── components/ # 组件
│   │   │   │   ├── HelloWorld.vue
│   │   │   ├── App.vue    # 主应用组件
│   │   │   ├── main.js    # 入口文件
│   │   │   ├── style.css  # 样式文件
│   │   ├── .gitignore
│   │   ├── README.md      # 前端应用说明
│   │   ├── index.html     # HTML入口
│   │   ├── package-lock.json
│   │   ├── package.json   # 前端依赖
│   │   ├── vite.config.js # Vite配置
│   ├── __init__.py
├── config/                # 项目配置
│   ├── __init__.py
│   ├── asgi.py            # ASGI配置
│   ├── llm_config.json    # LLM配置
│   ├── settings.py        # Django设置
│   ├── urls.py            # 项目路由
│   ├── wsgi.py            # WSGI配置
├── doc/                   # 文档目录
│   ├── LLM_SERVICE_ARCHITECTURE.md # LLM服务架构
│   ├── LLM_SERVICE_README.md # LLM服务说明
│   ├── LLM_SERVICE_SUMMARY.md # LLM服务总结
│   ├── LLM_SERVICE_USAGE.md # LLM服务使用
│   ├── LOCATION_EXCEPTION_HANDLER.md # 位置异常处理
│   ├── MARIADB_CONFIG.md  # MariaDB配置
│   ├── REQUIREMENT_MODEL_DESIGN.md # 需求模型设计
├── domain/                # 领域模型
│   ├── __init__.py
├── examples/              # 示例代码
│   ├── llm_service_example.py # LLM服务示例
├── infrastructure/        # 基础设施
│   ├── __init__.py
├── services/              # 服务层
│   ├── llm/               # LLM服务
│   │   ├── providers/     # LLM提供商实现
│   │   │   ├── __init__.py
│   │   │   ├── deepseek.py # DeepSeek实现
│   │   │   ├── gemini.py  # Gemini实现
│   │   │   ├── openai.py  # OpenAI实现
│   │   ├── __init__.py
│   │   ├── base.py        # 基础类
│   │   ├── cache.py       # 缓存管理
│   │   ├── config.py      # 配置管理
│   │   ├── conversation_manager.py # 会话管理
│   │   ├── extractor.py   # 数据提取
│   │   ├── factory.py     # 提供商工厂
│   │   ├── location_exception_handler.py # 位置异常处理
│   │   ├── location_validator.py # 位置验证
│   │   ├── logger.py      # 日志管理
│   │   ├── persistence.py # 持久化
│   │   ├── rate_limiter.py # 速率限制
│   │   ├── security.py    # 安全管理
│   │   ├── service.py     # LLM服务核心
│   ├── __init__.py
├── tests/                 # 测试目录
│   ├── reports/           # 测试报告
│   │   ├── llm_field_test_report_20260120_210155.txt
│   │   ├── llm_field_test_report_20260120_213012.txt
│   │   ├── llm_field_test_report_20260120_214732.txt
│   │   ├── llm_field_test_report_20260121_112118.txt
│   │   ├── web_requirement_test_report_20260121_115642.json
│   │   ├── web_requirement_test_report_20260121_115854.json
│   │   ├── web_requirement_test_report_20260121_115946.json
│   │   ├── web_requirement_test_report_20260121_120512.json
│   │   ├── web_requirement_test_report_20260121_120756.json
│   │   ├── web_requirement_test_report_20260121_121143.json
│   │   ├── web_requirement_test_report_20260121_121228.json
│   │   ├── web_requirement_test_report_20260121_121831.json
│   ├── __init__.py
│   ├── llm_field_test_cases.py # LLM字段测试用例
│   ├── llm_field_test_runner.py # LLM字段测试运行器
│   ├── llm_field_test_simple.py # 简化版LLM字段测试
│   ├── run_tests.py       # 测试运行脚本
│   ├── run_web_requirement_tests.py # Web需求测试运行脚本
│   ├── test_admin.py      # 管理后台测试
│   ├── test_db_connection.py # 数据库连接测试
│   ├── test_llm_end_to_end.py # LLM端到端测试
│   ├── test_llm_extractor.py # LLM提取器测试
│   ├── test_llm_providers.py # LLM提供商测试
│   ├── test_llm_rate_limiter.py # LLM速率限制测试
│   ├── test_llm_security.py # LLM安全测试
│   ├── test_llm_service.py # LLM服务测试
│   ├── test_location_validator.py # 位置验证器测试
│   ├── test_web_requirement_cases.py # Web需求测试用例
├── .env.llm.example       # LLM环境变量示例
├── .gitignore
├── Dockerfile             # Docker构建文件
├── README.md              # 项目说明（本文档）
├── docker-compose.yml     # Docker Compose配置
├── manage.py              # Django管理命令
├── nginx.conf             # Nginx配置
├── requirements.txt       # Python依赖
```

## 环境要求与安装步骤

### 环境要求
- Python 3.8+
- Django 5.0+
- MySQL/MariaDB 10.0+
- Node.js 14.0+ (用于前端开发)
- npm 6.0+ (用于前端开发)
- 可选：Docker和Docker Compose (用于容器化部署)

### 依赖项列表

#### 后端依赖
```
Django>=5.0
python-dotenv>=1.0.0
mysqlclient>=2.2.0
djangorestframework>=3.14.0
aiohttp>=3.9.0
requests>=2.31.0
cryptography>=41.0.0
drf-yasg>=1.21.0
django-q2
pytest>=7.4.0
pytest-django>=4.5.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
```

#### 前端依赖
前端依赖位于 `apps/web/package.json` 文件中，主要包括：
- Vue.js 3
- Vite
- 其他前端库

### 安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd smart_trip_quote
```

#### 2. 配置环境变量
复制环境变量示例文件并根据实际情况修改：

```bash
# 复制LLM环境变量示例文件
cp .env.llm.example .env.llm

# 编辑环境变量文件，填写相应的值
# 例如：设置数据库连接信息、LLM API密钥等
```

#### 3. 安装后端依赖
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 安装前端依赖
```bash
cd apps/web
npm install
```

#### 5. 数据库配置与迁移
```bash
# 返回项目根目录
cd ../..

# 运行数据库迁移
python manage.py migrate

# 创建超级用户（用于管理后台）
python manage.py createsuperuser
```

#### 6. 启动开发服务器

##### 启动后端服务器
```bash
python manage.py runserver
```

##### 启动前端开发服务器
```bash
cd apps/web
npm run dev
```

启动成功后，前端应用通常会在 `http://localhost:5173` 或类似端口运行，具体地址会在终端输出中显示。

#### 访问前端应用
1. 确保后端服务器和前端开发服务器都已启动
2. 打开浏览器，访问前端应用地址（如 `http://localhost:5173`）
3. 在前端界面中，您可以：
   - 提交旅行需求
   - 查看需求分析结果
   - 获取旅行报价
   - 管理个人行程

## 使用指南

### 基本操作流程

1. **访问管理后台**：打开浏览器，访问 `http://localhost:8000/admin/`，使用超级用户账号登录
2. **配置LLM提供商**：在管理后台中配置LLM提供商的API密钥和其他参数
3. **提交旅行需求**：通过前端应用或API接口提交旅行需求
4. **查看分析结果**：系统会自动分析需求并生成结构化数据
5. **获取旅行报价**：基于分析结果生成旅行报价
6. **管理行程**：在管理后台中查看和管理生成的行程

### 核心功能使用示例

#### LLM服务使用示例

```python
from services.llm.service import LLMRequirementService

# 初始化LLM服务
llm_service = LLMRequirementService()

# 处理用户需求
user_input = "我想在明年3月份去日本东京旅行，为期5天，预算在5000元左右，希望能参观主要景点。"
result = llm_service.process_requirement_sync(user_input)

if result.success:
    print(f"处理成功，需求ID: {result.requirement_id}")
    print(f"结构化数据: {result.structured_data}")
else:
    print(f"处理失败: {result.error}")
    if result.warnings:
        print(f"警告: {result.warnings}")
```

#### API接口使用示例

```bash
# 提交旅行需求
curl -X POST http://localhost:8000/api/llm/process/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "我想在明年3月份去日本东京旅行，为期5天，预算在5000元左右，希望能参观主要景点。"
  }'
```

### 参数说明

#### LLM服务参数
- `user_input`：用户的自然语言输入，描述旅行需求
- `provider`：可选，指定使用的LLM提供商（OpenAI、Gemini、DeepSeek等）
- `client_id`：可选，客户端ID，用于速率限制和会话管理
- `save_to_db`：可选，是否将处理结果保存到数据库，默认为True

#### API接口参数
- `user_input`：用户的自然语言输入，描述旅行需求
- `provider`：可选，指定使用的LLM提供商
- `client_id`：可选，客户端ID

## API文档

### 主要API接口

#### 处理旅行需求

**接口URL**：`/api/llm/process/`

**请求方法**：POST

**请求参数**：
| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| user_input | string | 是 | 用户的自然语言输入，描述旅行需求 |
| provider | string | 否 | 指定使用的LLM提供商（openai、gemini、deepseek） |
| client_id | string | 否 | 客户端ID，用于速率限制和会话管理 |

**响应格式**：
```json
{
  "success": true,
  "requirement_id": "REQ-2026-0001",
  "structured_data": {
    "destination": "东京",
    "country": "日本",
    "travel_start_date": "2027-03-01",
    "travel_end_date": "2027-03-05",
    "duration_days": 5,
    "budget": 5000,
    "budget_currency": "CNY",
    "travelers": 1,
    "interests": ["观光", "购物"]
  },
  "warnings": []
}
```

#### 获取LLM提供商信息

**接口URL**：`/api/llm/provider-info/`

**请求方法**：GET

**响应格式**：
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "version": "1.0"
}
```

## 开发指南

### 开发环境搭建
1. 按照上述安装步骤设置开发环境
2. 配置IDE（如VS Code、PyCharm等）以支持Python和Django开发
3. 安装必要的开发工具和插件

### 代码规范
- 遵循PEP 8代码风格指南
- 使用4个空格进行缩进
- 类名使用驼峰命名法（如`LLMRequirementService`）
- 函数和变量名使用下划线命名法（如`process_requirement_sync`）
- 为关键函数和类添加文档字符串
- 编写单元测试和集成测试

### 贡献流程
1. Fork项目仓库
2. 创建功能分支
3. 实现功能或修复bug
4. 运行测试确保代码质量
5. 提交Pull Request
6. 代码审查和合并

## 测试说明

### 测试环境配置
1. 确保已安装所有测试依赖（`pytest`及其相关插件）
2. 配置测试数据库连接
3. 准备测试数据

### 测试用例
项目包含以下主要测试用例：
- `test_llm_service.py`：测试LLM服务的核心功能
- `test_llm_providers.py`：测试不同LLM提供商的集成
- `test_llm_extractor.py`：测试LLM数据提取功能
- `test_location_validator.py`：测试位置验证功能
- `test_web_requirement_cases.py`：测试Web端需求处理

### 执行测试

#### 运行所有测试
```bash
python -m pytest
```

#### 运行特定测试文件
```bash
python -m pytest tests/test_llm_service.py
```

#### 运行测试并生成覆盖率报告
```bash
python -m pytest --cov=services/llm tests/
```

## 常见问题解答

### Q1: 如何配置LLM提供商？

**A1**: 在 `.env.llm` 文件中配置相应的API密钥和参数，例如：

```
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Gemini配置
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=geminipro

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
```

### Q2: 系统支持哪些LLM提供商？

**A2**: 目前系统支持以下LLM提供商：
- OpenAI (GPT系列模型)
- Google Gemini
- DeepSeek

### Q3: 如何处理API速率限制？

**A3**: 系统内置了速率限制功能，可在配置文件中调整速率限制参数。当请求超过限制时，系统会返回相应的错误信息，建议客户端实现重试机制。

### Q4: 如何部署到生产环境？

**A4**: 推荐使用Docker和Docker Compose进行部署，步骤如下：

1. 配置环境变量
2. 构建Docker镜像
3. 使用Docker Compose启动服务

```bash
docker-compose up -d
```

### Q5: 系统如何处理用户隐私？

**A5**: 系统实现了安全管理功能，包括：
- 敏感信息加密存储
- 请求安全检查
- 数据访问控制
- 符合数据保护法规的处理流程

## 版本历史和更新日志

### v1.0.0 (2026-01-21)
- 初始版本发布
- 实现核心LLM服务功能
- 支持多LLM提供商集成
- 实现基本的需求分析和处理
- 提供管理后台和API接口
- 集成前端应用

## 许可证信息

本项目采用MIT许可证。详情请参阅LICENSE文件。

## 联系方式

### 项目维护者
- 姓名：[维护者姓名]
- 邮箱：[维护者邮箱]
- GitHub：[GitHub账号]

### 问题反馈
- 提交Issue：[GitHub Issue链接]
- 联系邮箱：[项目邮箱]

### 贡献
欢迎通过Pull Request的方式贡献代码，或通过Issue提出建议和反馈。

---

**Smart Trip Quote** - 让旅行规划更智能、更简单！
