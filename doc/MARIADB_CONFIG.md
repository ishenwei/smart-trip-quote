# MariaDB 数据库配置说明

## 概述

本项目已成功配置并连接到 MariaDB 数据库。所有数据库迁移已成功应用，系统功能正常运行。

## 配置详情

### 1. 数据库配置文件

**文件位置**: `config/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME', 'stq_db'),
        'USER': os.getenv('DATABASE_USER', 'stq_user'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 2. 环境变量配置

**文件位置**: `.env`

```bash
# Database Configuration (MariaDB)
MYSQL_ROOT_PASSWORD=!Abcde12345
MYSQL_DATABASE=stq_db
MYSQL_USER=stq_user
MYSQL_PASSWORD=!Abcde12345
MYSQL_HOST=mariadb
MYSQL_PORT=3306

# Application Database Settings
# For local development: use localhost:3306 (requires Docker to be running)
# For Docker container: use mariadb (Docker service name)
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=stq_db
DATABASE_USER=stq_user
DATABASE_PASSWORD=!Abcde12345
```

### 3. Docker Compose 配置

**文件位置**: `docker-compose.yml`

```yaml
mariadb:
  container_name: stq_mariadb
  image: mariadb:10.11
  environment:
    - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    - MYSQL_DATABASE=${MYSQL_DATABASE}
    - MYSQL_USER=${MYSQL_USER}
    - MYSQL_PASSWORD=${MYSQL_PASSWORD}
  volumes:
    - mariadb_data:/var/lib/mysql
  ports:
    - "${MYSQL_PORT}:${MYSQL_PORT}"
  networks:
    - stq_network
```

### 4. 依赖包

**文件位置**: `requirements.txt`

```
Django>=5.0
python-dotenv>=1.0.0
mysqlclient>=2.2.0
djangorestframework>=3.14.0
```

## 数据库信息

### 连接信息

- **数据库类型**: MariaDB 10.11
- **主机地址**: localhost (本地开发) / mariadb (Docker 容器)
- **端口**: 3306
- **数据库名**: stq_db
- **用户名**: stq_user
- **密码**: !Abcde12345

### 数据库表

已创建的表结构：

| 表名 | 说明 |
|------|------|
| requirements | 旅游需求表（核心业务表） |
| auth_group | Django 用户组表 |
| auth_group_permissions | 用户组权限表 |
| auth_permission | Django 权限表 |
| auth_user | Django 用户表 |
| auth_user_groups | 用户组关联表 |
| auth_user_user_permissions | 用户权限关联表 |
| django_admin_log | Django 管理日志表 |
| django_content_type | Django 内容类型表 |
| django_migrations | Django 迁移记录表 |
| django_session | Django 会话表 |

### requirements 表结构

| 字段名 | 类型 | 说明 |
|---------|------|------|
| id | bigint(20) | 主键，自增 |
| requirement_id | varchar(50) | 需求唯一标识 |
| origin_name | varchar(100) | 出发地名称 |
| origin_code | varchar(10) | 出发地代码 |
| origin_type | varchar(20) | 出发地类型 |
| destination_cities | longtext | 目的地城市列表（JSON） |
| trip_days | int(11) | 出行天数 |
| group_adults | int(11) | 成人数量 |
| group_children | int(11) | 儿童数量 |
| group_seniors | int(11) | 老人数量 |
| group_total | int(11) | 总人数 |
| travel_start_date | date | 出行开始日期 |
| travel_end_date | date | 出行结束日期 |
| travel_date_flexible | tinyint(1) | 日期是否灵活 |
| transportation_type | varchar(20) | 交通方式 |
| transportation_notes | longtext | 交通偏好说明 |
| hotel_level | varchar(20) | 酒店等级 |
| hotel_requirements | longtext | 住宿特殊要求 |
| trip_rhythm | varchar(20) | 行程节奏 |
| preference_tags | longtext | 偏好标签（JSON） |
| must_visit_spots | longtext | 必游景点（JSON） |
| avoid_activities | longtext | 避免活动（JSON） |
| budget_level | varchar(20) | 预算等级 |
| budget_currency | varchar(10) | 预算货币 |
| budget_min | decimal(10,2) | 最低预算 |
| budget_max | decimal(10,2) | 最高预算 |
| budget_notes | longtext | 预算说明 |
| source_type | varchar(20) | 需求来源 |
| status | varchar(20) | 需求状态 |
| assumptions | longtext | 系统推断说明（JSON） |
| created_by | varchar(100) | 创建人 |
| reviewed_by | varchar(100) | 审核人 |
| is_template | tinyint(1) | 是否模板 |
| template_name | varchar(200) | 模板名称 |
| template_category | varchar(100) | 模板分类 |
| expires_at | datetime(6) | 过期时间 |
| created_at | datetime(6) | 创建时间 |
| updated_at | datetime(6) | 更新时间 |
| extension | longtext | 扩展字段（JSON） |

### 数据库索引

已创建的索引：

- `requirement_require_d528d1_idx` - requirement_id（唯一索引）
- `requirement_status_b8bfb6_idx` - status
- `requirement_created_d3ee3d_idx` - created_by
- `requirement_is_temp_d1d097_idx` - is_template
- `requirement_created_0ede4d_idx` - created_at（降序）

## 迁移历史

### 已应用的迁移

1. **0001_initial.py** - 创建 Requirement 模型
   - 创建 requirements 表
   - 创建所有字段和索引

2. **0002_alter_requirement_created_by_and_more.py** - 修改字段允许 NULL
   - created_by 字段允许 NULL
   - reviewed_by 字段允许 NULL

3. **0003_alter_requirement_travel_end_date_and_more.py** - 修改日期字段允许 NULL
   - travel_start_date 字段允许 NULL
   - travel_end_date 字段允许 NULL

## 使用说明

### 启动 MariaDB 容器

```bash
docker-compose up -d mariadb
```

### 停止 MariaDB 容器

```bash
docker-compose stop mariadb
```

### 查看容器状态

```bash
docker ps --filter "name=stq_mariadb"
```

### 连接到数据库

```bash
docker exec -it stq_mariadb mysql -u stq_user -p!Abcde12345 stq_db
```

### 执行数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 测试数据库连接

```bash
python test_db_connection.py
```

## 环境配置

### 本地开发环境

使用 localhost 连接数据库：

```bash
DATABASE_HOST=localhost
DATABASE_PORT=3306
```

**注意**: 需要先启动 MariaDB Docker 容器。

### Docker 容器环境

使用 Docker 服务名连接数据库：

```bash
DATABASE_HOST=mariadb
DATABASE_PORT=3306
```

## 故障排查

### 连接失败

1. 检查 MariaDB 容器是否运行：
   ```bash
   docker ps | grep stq_mariadb
   ```

2. 检查端口是否正确：
   ```bash
   docker ps --filter "name=stq_mariadb" --format "table {{.Names}}\t{{.Ports}}"
   ```

3. 检查环境变量是否正确：
   ```bash
   cat .env | grep DATABASE_
   ```

### 迁移失败

1. 检查数据库连接：
   ```bash
   python manage.py dbshell
   ```

2. 查看迁移状态：
   ```bash
   python manage.py showmigrations
   ```

3. 回滚迁移（如需要）：
   ```bash
   python manage.py migrate apps 0002
   ```

### 权限问题

如果遇到权限错误，检查数据库用户权限：

```sql
GRANT ALL PRIVILEGES ON stq_db.* TO 'stq_user'@'%';
FLUSH PRIVILEGES;
```

## 性能优化建议

1. **索引优化**
   - 已为常用查询字段创建索引
   - 根据实际查询模式添加更多索引

2. **查询优化**
   - 使用 select_related 和 prefetch_related 减少查询次数
   - 使用 only() 和 defer() 只查询需要的字段

3. **连接池**
   - 考虑使用连接池（如 django-db-geventpool）
   - 配置合适的连接池大小

4. **缓存**
   - 使用 Redis 缓存常用查询结果
   - 缓存模板和配置数据

## 安全建议

1. **密码管理**
   - 不要在代码中硬编码密码
   - 使用环境变量或密钥管理服务
   - 定期更换数据库密码

2. **网络访问**
   - 生产环境中不要暴露数据库端口
   - 使用防火墙限制访问
   - 只允许应用服务器访问

3. **数据备份**
   - 定期备份数据库
   - 测试备份恢复流程
   - 保留多个版本的备份

4. **日志监控**
   - 监控数据库连接数
   - 监控慢查询
   - 设置告警机制

## 维护建议

1. **定期维护**
   - 定期优化表：`OPTIMIZE TABLE requirements`
   - 定期分析表：`ANALYZE TABLE requirements`
   - 清理过期数据

2. **监控**
   - 监控磁盘空间使用
   - 监控数据库性能指标
   - 监控慢查询日志

3. **更新**
   - 定期更新 MariaDB 版本
   - 定期更新依赖包
   - 应用安全补丁

## 测试验证

所有功能已通过测试：

✓ 数据库连接正常  
✓ 模型功能正常  
✓ 状态管理正常  
✓ 模板管理正常  
✓ JSON 导出功能正常  
✓ 数据验证功能正常  

## 相关文档

- [Django 数据库文档](https://docs.djangoproject.com/en/5.2/ref/databases/)
- [MariaDB 文档](https://mariadb.com/kb/en/documentation/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [项目设计文档](REQUIREMENT_MODEL_DESIGN.md)
