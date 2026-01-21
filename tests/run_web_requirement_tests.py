#!/usr/bin/env python3
"""
执行旅游需求管理系统的Web测试用例

使用Selenium自动化测试Web页面操作，验证完整的旅游需求处理流程
"""

import json
import time
import unittest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 导入测试用例
from test_web_requirement_cases import TEST_CASES, validate_json_structure, validate_json_content

# 测试结果记录
TEST_RESULTS = []

class WebRequirementTests(unittest.TestCase):
    def setUp(self):
        """设置测试环境"""
        # 启动Chrome浏览器
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)  # 隐式等待
        
        # 访问Web页面
        self.driver.get("http://localhost:5173")
        
        # 等待页面加载完成
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "userInput"))
            )
            print("Web页面加载成功")
        except Exception as e:
            print(f"Web页面加载失败: {e}")
            # 打印当前页面内容，以便诊断问题
            try:
                print("当前页面内容:")
                print(self.driver.page_source[:1000])  # 只打印前1000个字符
            except:
                pass
            raise
    
    def tearDown(self):
        """清理测试环境"""
        if self.driver:
            self.driver.quit()
    
    def test_all_cases(self):
        """执行所有测试用例"""
        for test_case in TEST_CASES:
            print(f"\n=== 执行测试用例: {test_case['id']} - {test_case['description']} ===")
            
            # 记录测试开始时间
            start_time = time.time()
            
            # 步骤1: 输入自然语言旅游需求
            try:
                textarea = self.driver.find_element(By.ID, "userInput")
                textarea.clear()
                textarea.send_keys(test_case['input_text'])
                print(f"输入旅游需求: {test_case['input_text'][:100]}...")
            except Exception as e:
                print(f"输入旅游需求失败: {e}")
                TEST_RESULTS.append({
                    "test_case_id": test_case['id'],
                    "description": test_case['description'],
                    "status": "FAILED",
                    "error": f"输入旅游需求失败: {e}",
                    "response_time": time.time() - start_time
                })
                continue
            
            # 步骤2: 提交表单
            try:
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                print("提交表单成功")
                
                # 等待处理完成，最多等待60秒
                print("等待处理完成...")
                
                # 检查是否出现错误信息
                try:
                    error_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
                    )
                    error_message = error_element.text
                    print(f"出现错误信息: {error_message}")
                    TEST_RESULTS.append({
                        "test_case_id": test_case['id'],
                        "description": test_case['description'],
                        "status": "FAILED",
                        "error": f"提交失败: {error_message}",
                        "response_time": time.time() - start_time
                    })
                    continue
                except:
                    # 没有错误信息，继续等待成功页面
                    pass
                    
            except Exception as e:
                print(f"提交表单失败: {e}")
                # 打印当前页面内容，以便诊断问题
                try:
                    print("当前页面内容:")
                    print(self.driver.page_source[:1000])
                except:
                    pass
                TEST_RESULTS.append({
                    "test_case_id": test_case['id'],
                    "description": test_case['description'],
                    "status": "FAILED",
                    "error": f"提交表单失败: {e}",
                    "response_time": time.time() - start_time
                })
                continue
            
            # 步骤3: 等待处理完成并验证结果
            try:
                # 等待成功页面加载
                print("等待成功页面加载...")
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "success-card"))
                )
                print("处理完成，成功页面加载")
                
                # 等待结构化数据显示
                print("等待结构化数据显示...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "structured-data"))
                )
                print("结构化数据显示成功")
                
                # 获取结构化数据
                structured_data_element = self.driver.find_element(By.CLASS_NAME, "structured-data")
                structured_data_text = structured_data_element.find_element(By.TAG_NAME, "pre").text
                print(f"获取到的结构化数据: {structured_data_text[:100]}...")
                actual_json = json.loads(structured_data_text)
                print("解析结构化数据成功")
                
                # 验证JSON结构
                structure_valid, structure_errors = validate_json_structure(actual_json, test_case['expected_json'])
                
                # 验证JSON内容
                content_valid, content_errors = validate_json_content(actual_json, test_case['expected_json'])
                
                # 记录测试结果
                response_time = time.time() - start_time
                
                if structure_valid and content_valid:
                    print("测试用例执行成功")
                    TEST_RESULTS.append({
                        "test_case_id": test_case['id'],
                        "description": test_case['description'],
                        "status": "PASSED",
                        "response_time": response_time,
                        "actual_json": actual_json
                    })
                else:
                    print("测试用例执行失败")
                    errors = structure_errors + content_errors
                    for error in errors:
                        print(f"错误: {error}")
                    TEST_RESULTS.append({
                        "test_case_id": test_case['id'],
                        "description": test_case['description'],
                        "status": "FAILED",
                        "errors": errors,
                        "response_time": response_time,
                        "actual_json": actual_json,
                        "expected_json": test_case['expected_json']
                    })
                    
            except Exception as e:
                print(f"验证结果失败: {e}")
                import traceback
                traceback.print_exc()
                # 打印当前页面内容，以便诊断问题
                try:
                    print("当前页面内容:")
                    print(self.driver.page_source[:2000])  # 打印前2000个字符
                except:
                    pass
                TEST_RESULTS.append({
                    "test_case_id": test_case['id'],
                    "description": test_case['description'],
                    "status": "FAILED",
                    "error": f"验证结果失败: {e}",
                    "response_time": time.time() - start_time
                })
                continue
            
            # 步骤4: 重置表单，准备下一个测试用例
            try:
                reset_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '提交新需求')]")
                reset_button.click()
                # 等待输入页面重新加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "userInput"))
                )
                print("重置表单成功")
            except Exception as e:
                print(f"重置表单失败: {e}")

# 生成测试报告
def generate_test_report():
    """生成测试报告"""
    report_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/web_requirement_test_report_{report_time}.json"
    
    # 确保报告目录存在
    import os
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    # 统计测试结果
    total_cases = len(TEST_RESULTS)
    passed_cases = len([r for r in TEST_RESULTS if r['status'] == 'PASSED'])
    failed_cases = len([r for r in TEST_RESULTS if r['status'] == 'FAILED'])
    
    # 计算平均响应时间
    if TEST_RESULTS:
        avg_response_time = sum([r['response_time'] for r in TEST_RESULTS]) / len(TEST_RESULTS)
    else:
        avg_response_time = 0
    
    # 生成报告
    report = {
        "report_time": datetime.now().isoformat(),
        "test_summary": {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "pass_rate": (passed_cases / total_cases * 100) if total_cases > 0 else 0,
            "average_response_time": avg_response_time
        },
        "test_results": TEST_RESULTS
    }
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== 测试报告生成完成 ===")
    print(f"测试报告文件: {report_file}")
    print(f"总测试用例: {total_cases}")
    print(f"通过测试用例: {passed_cases}")
    print(f"失败测试用例: {failed_cases}")
    print(f"通过率: {report['test_summary']['pass_rate']:.2f}%")
    print(f"平均响应时间: {avg_response_time:.2f}秒")

if __name__ == "__main__":
    # 运行测试
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # 生成测试报告
    generate_test_report()
