# 测试策略与用法文档

## 1. 测试架构

### 1.1 测试目录结构

```
tests/
├── __init__.py
├── run_tests.py                # 测试运行脚本
├── test_llm_service.py         # LLM服务测试
├── test_llm_providers.py       # LLM提供者测试
├── test_llm_extractor.py       # LLM提取器测试
├── test_llm_security.py        # LLM安全测试
├── test_llm_rate_limiter.py    # LLM速率限制测试
├── test_llm_end_to_end.py      # LLM端到端测试
├── test_api.py                 # API测试
├── test_iternary_parser.py     # 行程解析测试
├── test_location_validator.py  # 位置验证器测试
├── test_models.py              # 模型测试
├── test_origin_input.py        # 原始输入测试
├── test_webhook.py             # Webhook测试
├── test_admin.py               # 管理功能测试
├── test_db_connection.py       # 数据库连接测试
├── test_display.py             # 显示功能测试
├── test_daily_schedule_filter.py # 日程过滤测试
├── test_itinerary_import.py    # 行程导入测试
├── test_itinerary_webhook.py   # 行程Webhook测试
├── test_web_requirement_cases.py # Web需求测试
├── generate_test_data.py       # 测试数据生成
├── generate_test_data_simple.py # 简单测试数据生成
├── generate_test_data_for_iternary.py # 行程测试数据生成
├── llm_field_test_cases.py     # LLM字段测试用例
├── llm_field_test_runner.py    # LLM字段测试运行器
├── llm_field_test_simple.py    # 简单LLM字段测试
├── run_web_requirement_tests.py # Web需求测试运行器
├── check_db_records.py         # 数据库记录检查
├── check_requirements.py       # 需求检查
├── fix_test.py                 # 测试修复
├── validate_json.py            # JSON验证
├── verify_import.py            # 导入验证
├── verify_iternary_data.py     # 行程数据验证
├── test_iternary_data.json     # 行程测试数据
├── test_iternary_data2.json    # 行程测试数据2
├── test_itinerary_data.json    # 行程测试数据
└── TEST_ITERNARY_PARSER_README.md # 行程解析测试说明
```

## 2. 测试运行方式

### 2.1 运行所有测试

```bash
python tests/run_tests.py
```

### 2.2 运行特定测试文件

```bash
python tests/run_tests.py test_llm_providers
```

### 2.3 运行特定测试类

```bash
python tests/run_tests.py test_llm_providers::TestDeepSeekProvider
```

### 2.4 运行特定测试方法

```bash
python tests/run_tests.py test_llm_providers::TestDeepSeekProvider::test_validate_config
```

### 2.5 查看测试覆盖率

```bash
python tests/run_tests.py --coverage
```

### 2.6 详细输出模式

```bash
python tests/run_tests.py -v
```

## 3. 测试策略

### 3.1 LLM服务测试 (test_llm_service.py)

**测试目标**：测试 LLM 服务的核心功能和流程

**测试策略**：
- 测试同步处理需求的成功场景
- 测试速率限制超过的场景
- 测试 LLM 错误的场景
- 测试数据验证失败的场景
- 测试提供者信息获取
- 测试速率限制统计
- 测试缓存统计和清理
- 测试配置重载

**关键测试方法**：
- `test_process_requirement_sync_success`：测试成功处理需求
- `test_process_requirement_sync_rate_limit_exceeded`：测试速率限制
- `test_process_requirement_sync_llm_error`：测试 LLM 错误
- `test_process_requirement_sync_validation_failed`：测试验证失败

### 3.2 LLM提供者测试 (test_llm_providers.py)

**测试目标**：测试不同 LLM 服务提供者的集成

**测试策略**：
- 测试 DeepSeek 提供者
- 测试 Gemini 提供者
- 测试 OpenAI 提供者
- 测试提供者工厂
- 测试配置验证
- 测试同步生成成功场景
- 测试同步生成错误场景
- 测试超时场景

**关键测试方法**：
- `test_validate_config`：测试配置验证
- `test_generate_sync_success`：测试成功生成
- `test_generate_sync_error`：测试生成错误
- `test_create_provider`：测试提供者创建

### 3.3 LLM提取器测试 (test_llm_extractor.py)

**测试目标**：测试需求提取和验证功能

**测试策略**：
- 测试从响应中提取 JSON（带代码块）
- 测试从响应中提取 JSON（不带代码块）
- 测试无效 JSON 提取
- 测试有效数据验证
- 测试缺失必填字段的验证
- 测试无效行程天数的验证
- 测试无效团队大小的验证
- 测试无效日期格式的验证
- 测试无效日期范围的验证
- 测试无效交通类型的验证
- 测试无效预算范围的验证
- 测试数据规范化
- 测试需求 ID 生成

**关键测试方法**：
- `test_extract_json_from_response_with_code_blocks`：测试从代码块中提取 JSON
- `test_validate_requirement_data_valid`：测试有效数据验证
- `test_validate_requirement_data_missing_required_fields`：测试缺失字段验证
- `test_normalize_data`：测试数据规范化

### 3.4 LLM安全测试 (test_llm_security.py)

**测试目标**：测试安全相关功能

**测试策略**：
- 测试 API 密钥掩码
- 测试敏感数据哈希
- 测试 API 密钥格式验证
- 测试日志数据清理
- 测试 API 密钥缓存

**关键测试方法**：
- `test_mask_api_key`：测试 API 密钥掩码
- `test_hash_sensitive_data`：测试敏感数据哈希
- `test_validate_api_key_format`：测试 API 密钥格式验证
- `test_sanitize_log_data`：测试日志数据清理

### 3.5 行程解析测试 (test_iternary_parser.py)

**测试目标**：测试行程数据解析和导入功能

**测试策略**：
- 测试 JSON 格式验证
- 测试行程数据结构验证
- 测试数据库操作
- 测试目的地信息创建
- 测试旅行者统计信息创建
- 测试每日行程安排创建

**使用方法**：
```bash
python tests/test_iternary_parser.py <json_file>
```

### 3.6 API测试 (test_api.py)

**测试目标**：测试 API 接口功能

**测试策略**：
- 测试 LLM 处理 API
- 测试请求和响应格式

**使用方法**：
```bash
python tests/test_api.py
```

### 3.7 其他测试

- **test_location_validator.py**：测试位置验证功能
- **test_models.py**：测试数据模型功能
- **test_origin_input.py**：测试原始输入处理
- **test_webhook.py**：测试 Webhook 功能
- **test_admin.py**：测试管理功能
- **test_db_connection.py**：测试数据库连接
- **test_display.py**：测试显示功能
- **test_daily_schedule_filter.py**：测试日程过滤功能
- **test_itinerary_import.py**：测试行程导入功能
- **test_itinerary_webhook.py**：测试行程 Webhook 功能
- **test_web_requirement_cases.py**：测试 Web 需求功能

## 4. 测试数据生成

### 4.1 测试数据生成工具

- **generate_test_data.py**：生成通用测试数据
- **generate_test_data_simple.py**：生成简单测试数据
- **generate_test_data_for_iternary.py**：生行程测试数据

### 4.2 测试数据文件

- **test_iternary_data.json**：行程测试数据
- **test_iternary_data2.json**：行程测试数据 2
- **test_itinerary_data.json**：行程测试数据

## 5. 测试最佳实践

### 5.1 编写测试用例

1. **使用 pytest 框架**：遵循 pytest 测试规范
2. **使用模拟**：对外部依赖使用 unittest.mock 进行模拟
3. **测试边界情况**：测试各种边界情况和异常场景
4. **测试覆盖率**：确保测试覆盖率达到预期水平
5. **测试命名**：使用清晰的测试命名，描述测试场景

### 5.2 运行测试

1. **定期运行测试**：在代码变更后运行测试
2. **运行完整测试套件**：确保所有测试通过
3. **检查测试覆盖率**：确保代码覆盖率达到预期
4. **分析测试失败**：及时分析和修复测试失败

### 5.3 测试维护

1. **更新测试数据**：定期更新测试数据以反映业务变化
2. **修复测试用例**：及时修复因代码变更导致的测试失败
3. **添加新测试**：为新功能添加相应的测试用例
4. **优化测试性能**：优化测试执行速度

## 6. 测试环境配置

### 6.1 依赖项

- pytest：测试框架
- unittest：测试工具
- requests：HTTP 客户端（用于 API 测试）
- Django：Web 框架（用于集成测试）

### 6.2 环境变量

- `DJANGO_SETTINGS_MODULE`：Django 设置模块，默认为 `config.settings`

## 7. 常见问题与解决方案

### 7.1 测试失败

**问题**：测试失败

**解决方案**：
1. 查看测试错误信息
2. 分析失败原因
3. 修复代码或测试用例
4. 重新运行测试

### 7.2 测试覆盖率低

**问题**：测试覆盖率低

**解决方案**：
1. 运行 `python tests/run_tests.py --coverage` 查看覆盖率报告
2. 识别未覆盖的代码
3. 添加相应的测试用例
4. 重新运行测试查看覆盖率变化

### 7.3 测试运行缓慢

**问题**：测试运行缓慢

**解决方案**：
1. 识别耗时较长的测试
2. 优化测试代码
3. 使用测试缓存
4. 并行运行测试

## 8. 测试自动化

### 8.1 CI/CD 集成

可以将测试集成到 CI/CD 流程中，确保每次代码变更都能通过测试。

### 8.2 定时测试

可以设置定时任务，定期运行测试套件，确保系统稳定性。

## 9. 总结

本项目采用了全面的测试策略，覆盖了 LLM 服务、API、行程解析等核心功能。通过 pytest 框架和模拟技术，确保了测试的可靠性和效率。测试套件不仅验证了功能的正确性，还测试了各种边界情况和异常场景，为系统的稳定性和可靠性提供了保障。

定期运行测试套件、监控测试覆盖率、及时修复测试失败，是确保系统质量的重要措施。通过持续的测试维护和优化，可以不断提高系统的稳定性和可靠性。


docker compose exec web python manage.py import_excel_data --attractions tests/景点集合信息.xlsx --restaurants tests/餐厅集合信息.xlsx

docker compose exec web python manage.py import_excel_data --hotels "/app/tests/上冰雪世界皇冠酒店信息表.xlsx"
docker compose exec web python manage.py import_excel_data --hotels "/app/tests/上海卓越铂尔曼酒店信息表_完整版.xlsx"
docker compose exec web python manage.py import_excel_data --hotels "/app/tests/上海南汇百思特酒店信息表.xlsx"
docker compose exec web python manage.py import_excel_data --hotels "/app/tests/松江凯悦酒店单独信息表.xlsx" 
docker compose exec web python manage.py import_excel_data --hotels "/app/tests/松江开元酒店信息.xlsx"
docker compose exec web python manage.py import_excel_data --hotels "/app/tests/金山皇冠假日单独信息表.xlsx" 

docker exec stq_web python manage.py generate_japan_test_data'