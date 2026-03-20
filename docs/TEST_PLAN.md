# Smart Trip Quote Web 端测试计划

## 测试目标
验证 Web 端功能，包括用户登录、需求创建、行程管理等核心流程。

---

## 一、测试环境

| 项目 | 值 |
|------|-----|
| Web 地址 | http://192.168.3.189:8000 |
| Nginx 地址 | http://192.168.3.189:7777 |
| Admin 用户 | admin / admin123 |
| 数据库 | MariaDB (stq_db) |

---

## 二、测试用例

### 2.1 用户登录测试

| 用例ID | 测试项 | 预期结果 |
|--------|--------|----------|
| TC001 | 访问 Admin 登录页 | 页面正常显示样式 |
| TC002 | 使用正确凭据登录 | 登录成功，进入管理后台 |
| TC003 | 使用错误密码登录 | 提示用户名或密码错误 |
| TC004 | CSRF 防护验证 | 登录表单包含 csrf token |

### 2.2 旅行需求 (Requirement) 测试

| 用例ID | 测试项 | 预期结果 |
|--------|--------|----------|
| TC010 | 创建新需求 | 需求成功创建，返回需求ID |
| TC011 | 查看需求列表 | 显示所有需求记录 |
| TC012 | 查看需求详情 | 显示需求的完整信息 |
| TC013 | 更新需求状态 | 状态成功更新 |

### 2.3 行程 (Itinerary) 测试

| 用例ID | 测试项 | 预期结果 |
|--------|--------|----------|
| TC020 | 创建行程 | 行程成功创建 |
| TC021 | 行程关联目的地 | 目的地正确关联 |
| TC022 | 查看行程列表 | 显示所有行程 |

### 2.4 API 接口测试

| 用例ID | 接口 | 方法 | 预期结果 |
|--------|------|------|----------|
| TC030 | /api/requirements/ | GET | 返回需求列表 |
| TC031 | /api/requirements/ | POST | 创建新需求 |
| TC032 | /api/itineraries/ | GET | 返回行程列表 |
| TC033 | /api/webhook/requirement/ | POST | 处理 webhook 请求 |

### 2.5 Webhook 端点测试

| 用例ID | 测试项 | 预期结果 |
|--------|--------|----------|
| TC040 | n8n 触发需求创建 | 需求成功创建 |
| TC041 | n8n 触发行程优化 | 行程优化完成 |

---

## 三、测试数据准备

### 3.1 现有测试数据
- 需求: 3 条 (REQ_2026_001/002/003)
- 行程: 3 条 (ITN_2026_001/002/003)
- 目的地: 9 条

### 3.2 创建测试数据 (Django Shell)
```python
# 创建测试用户
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user('test', 'test@test.com', 'test123')
"

# 创建测试需求
python manage.py shell -c "
from apps.models import Requirement
from django.contrib.auth.models import User
user = User.objects.first()
Requirement.objects.create(
    requirement_id='TEST_001',
    origin_input='测试需求',
    group_total=2,
    destination_cities='上海;杭州',
    travel_start_date='2026-04-01',
    travel_end_date='2026-04-05',
    created_by=user
)
"
```

---

## 四、测试执行方式

### 4.1 手动测试
1. 打开浏览器访问 http://192.168.3.189:7777/admin/
2. 使用 admin/admin123 登录
3. 按测试用例逐项验证

### 4.2 自动化测试 (Django Test)
```bash
# 运行所有测试
docker compose exec web python manage.py test

# 运行特定测试
docker compose exec web python manage.py test tests.test_webhook_refactor -v 2
```

### 4.3 API 测试 (curl)
```bash
# 登录获取 CSRF token
curl -c cookies.txt http://192.168.3.189:8000/admin/login/
curl -b cookies.txt -X POST http://192.168.3.189:8000/admin/login/ \
  -d "username=admin&password=admin123&csrfmiddlewaretoken=xxx"

# 测试 API
curl http://192.168.3.189:8000/api/requirements/
```

---

## 五、缺陷跟踪

| 缺陷ID | 描述 | 状态 |
|--------|------|------|
| - | - | - |

---

## 六、注意事项

1. **CSRF 问题**: 通过 Nginx 访问时需配置 CSRF_TRUSTED_ORIGINS
2. **静态文件**: 确保 collectstatic 已执行
3. **数据库**: 测试数据可在测试环境预先准备
