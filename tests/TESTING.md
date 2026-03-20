# 测试目录结构与指南

## 目录结构

```
tests/
├── __init__.py              # 包初始化
├── conftest.py              # pytest 共享 fixtures
├── pytest.ini               # pytest 配置
├── TESTING.md              # 测试文档
│
├── unit/                    # 单元测试
│   └── test_models.py       # 模型 CRUD 测试
│
├── integration/             # 集成测试
│   └── test_webhook.py     # Webhook API 测试
│
├── admin/                   # Admin 功能测试
│   └── test_admin.py       # Django Admin 配置测试
│
├── fixtures/                # 测试数据 (Excel 文件)
│   ├── 餐厅集合信息.xlsx
│   ├── 景点集合信息.xlsx
│   ├── 酒店信息表.xlsx
│   └── ...
│
└── reports/                 # 测试报告
    └── *.json
```

---

## 运行测试

### 在 Docker 环境中运行测试（推荐）

所有测试必须在 Docker 环境中运行，以确保与生产环境一致。

```bash
# 进入项目目录
cd /Users/weishen/Git/smart-trip-quote

# 运行所有测试
docker-compose exec -T web pytest tests/ -v

# 运行所有测试（简洁输出）
docker-compose exec -T web pytest tests/

# 运行所有测试（带详细错误信息）
docker-compose exec -T web pytest tests/ -v --tb=short

# 运行所有测试（带覆盖率）
docker-compose exec -T web pytest tests/ --cov=apps --cov-report=html
```

### 分模块运行

```bash
# 单元测试
docker-compose exec -T web pytest tests/unit/ -v

# 集成测试
docker-compose exec -T web pytest tests/integration/ -v

# Admin 测试
docker-compose exec -T web pytest tests/admin/ -v
```

### 运行特定测试

```bash
# 运行特定测试文件
docker-compose exec -T web pytest tests/unit/test_models.py -v

# 运行特定测试类
docker-compose exec -T web pytest tests/unit/test_models.py::TestHotelModel -v

# 运行特定测试方法
docker-compose exec -T web pytest tests/unit/test_models.py::TestHotelModel::test_create_hotel -v

# 使用关键字过滤
docker-compose exec -T web pytest -k "test_create" -v
```

---

## 测试类型说明

### 1. 单元测试 (tests/unit/)

**目的**: 测试单个模型的功能

| 测试文件 | 测试内容 | 测试数量 |
|---------|---------|---------|
| `test_models.py` | 模型 CRUD 操作 | 19 |

**覆盖模型**:
- Hotel (酒店)
- Attraction (景点)
- Restaurant (餐厅)
- Itinerary (行程) + 关联模型 (TravelerStats, Destination, DailySchedule)

### 2. 集成测试 (tests/integration/)

**目的**: 测试组件间的协作

| 测试文件 | 测试内容 | 测试数量 |
|---------|---------|---------|
| `test_webhook.py` | Webhook API | 34 |

**覆盖范围**:
- Serializer 测试 (数据验证)
- Service 测试 (业务逻辑)
- Webhook 响应处理
- 日志脱敏与敏感数据过滤

### 3. Admin 测试 (tests/admin/)

**目的**: 测试 Django Admin 配置

| 测试文件 | 测试内容 | 测试数量 |
|---------|---------|---------|
| `test_admin.py` | Admin 配置验证 | 60 |

**覆盖 Admin**:
- Requirement Admin (需求管理)
- Attraction Admin (景点管理)
- Hotel Admin (酒店管理)
- Restaurant Admin (餐厅管理)
- Itinerary Admin (行程管理)

---

## 测试结果验证

### 成功标准

所有测试必须通过:
```
======================= 113 passed =======================
```

### 运行结果解读

```
# 全部通过
======================= 113 passed, 1 warning in 12.08s =======================

# 失败示例
======================= 100 passed, 13 failed =======================
```

### 查看详细错误

```bash
# 显示详细的失败信息
docker-compose exec -T web pytest tests/ -v --tb=long

# 只显示失败的测试
docker-compose exec -T web pytest tests/ -v --tb=short --lf
```

---

## 测试 Fixtures

### conftest.py 共享 fixtures

| Fixture | 用途 |
|---------|------|
| `django_db_setup` | 配置数据库测试环境 |
| `db` | 启用数据库访问 |
| `sample_requirement_data` | 样例需求数据 |
| `sample_itinerary_data` | 样例行程数据 |
| `fixtures_path` | fixtures 目录路径 |
| `excel_files` | Excel 测试数据文件列表 |

### 使用示例

```python
def test_example(db):
    """使用 db fixture 访问数据库"""
    hotel = Hotel.objects.create(name="测试酒店")
    assert hotel.id is not None
```

---

## pytest 配置

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
addopts = -v --tb=short
```

---

## 测试数据

### fixtures/ 目录

存放测试用的 Excel 数据文件:
- `景点集合信息.xlsx` - 景点数据
- `酒店信息表.xlsx` - 酒店数据
- `餐厅集合信息.xlsx` - 餐厅数据

### 数据加载方式

测试数据通过模型直接创建，不依赖 fixtures 文件加载。

---

## 注意事项

### ⚠️ 重要提醒

1. **必须在 Docker 中运行**: 所有测试必须在 Docker 容器中运行，以确保环境一致
2. **数据库**: 使用 Docker 中的 MariaDB，端口 3306
3. **依赖**: 所有测试依赖 Django 5.2 + pytest + pytest-django
4. **不要在本地运行**: 本地环境可能缺少依赖，导致测试失败

### 常见问题

#### Q: 本地运行测试失败
A: 必须使用 Docker 环境运行测试。详见上面的 "在 Docker 环境中运行测试" 部分。

#### Q: 数据库连接错误
A: 确保 Docker 服务正在运行: `docker-compose ps`

#### Q: 测试失败但代码未改动
A: 检查是否有未提交的代码迁移: `docker-compose exec -T web python manage.py migrate`

---

## 测试报告生成

### 生成 HTML 覆盖率报告

```bash
docker-compose exec -T web pytest tests/ --cov=apps --cov-report=html
# 报告生成在 htmlcov/ 目录
```

### 生成 JUnit XML 报告

```bash
docker-compose exec -T web pytest tests/ --junitxml=reports/pytest.xml
```

---

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec -T web pytest tests/
```

---

*Last updated: 2026-03-21*
