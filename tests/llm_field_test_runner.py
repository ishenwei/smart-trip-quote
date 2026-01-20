"""
LLM字段识别自动化测试脚本
用于系统地验证所有字段的识别功能
"""

import os
import sys
import json
import time
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from services.llm.service import LLMRequirementService
from tests.llm_field_test_cases import TEST_CASES, PASS_CRITERIA, ERROR_TYPES


class FieldRecognitionTester:
    def __init__(self):
        self.service = LLMRequirementService()
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'partial': 0,
            'errors': {},
            'field_stats': {},
            'error_stats': {}
        }
    
    def run_test_case(self, category: str, field: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        test_name = test_case['name']
        user_input = test_case['input']
        expected = test_case['expected']
        description = test_case['description']
        
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"类别: {category} - {field}")
        print(f"描述: {description}")
        print(f"输入: {user_input}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            result = self.service.process_requirement_sync(
                user_input=user_input,
                save_to_db=False
            )
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            
            print(f"\n处理时间: {elapsed_time:.2f}秒")
            print(f"成功: {result.success}")
            
            if not result.success:
                print(f"错误: {result.error}")
                if 'error' in expected:
                    expected_error = expected['error']
                    if expected_error in result.error:
                        status = PASS_CRITERIA['success']
                        self.results['passed'] += 1
                    else:
                        status = PASS_CRITERIA['failed']
                        self.results['failed'] += 1
                        self.results['errors'][test_name] = {
                            'expected': expected_error,
                            'actual': result.error,
                            'category': category,
                            'field': field
                        }
                else:
                    status = PASS_CRITERIA['failed']
                    self.results['failed'] += 1
                    self.results['errors'][test_name] = {
                        'expected': 'Success',
                        'actual': result.error,
                        'category': category,
                        'field': field
                    }
            else:
                actual = result.structured_data
                match_result = self._compare_with_expected(actual, expected)
                
                if match_result['matched']:
                    status = PASS_CRITERIA['success']
                    self.results['passed'] += 1
                    print(f"✓ 测试通过")
                elif match_result['partial']:
                    status = PASS_CRITERIA['partial']
                    self.results['partial'] += 1
                    print(f"⚠ 部分通过")
                    print(f"不匹配的字段: {match_result['mismatched_fields']}")
                    self.results['errors'][test_name] = {
                        'expected': expected,
                        'actual': actual,
                        'mismatched_fields': match_result['mismatched_fields'],
                        'category': category,
                        'field': field
                    }
                else:
                    status = PASS_CRITERIA['failed']
                    self.results['failed'] += 1
                    print(f"✗ 测试失败")
                    print(f"不匹配的字段: {match_result['mismatched_fields']}")
                    self.results['errors'][test_name] = {
                        'expected': expected,
                        'actual': actual,
                        'mismatched_fields': match_result['mismatched_fields'],
                        'category': category,
                        'field': field
                    }
            
            self.results['total_tests'] += 1
            
            return {
                'test_name': test_name,
                'status': status,
                'elapsed_time': elapsed_time,
                'expected': expected,
                'actual': result.structured_data if result.success else {'error': result.error},
                'category': category,
                'field': field,
                'description': description
            }
            
        except Exception as e:
            print(f"✗ 测试异常: {str(e)}")
            self.results['total_tests'] += 1
            self.results['failed'] += 1
            self.results['errors'][test_name] = {
                'exception': str(e),
                'category': category,
                'field': field
            }
            
            return {
                'test_name': test_name,
                'status': PASS_CRITERIA['failed'],
                'elapsed_time': 0,
                'expected': expected,
                'actual': {'exception': str(e)},
                'category': category,
                'field': field,
                'description': description
            }
    
    def _compare_with_expected(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """比较实际结果与预期结果"""
        matched = True
        partial = False
        mismatched_fields = []
        
        def extract_value(data: Dict[str, Any], path: str):
            """从嵌套字典中提取值"""
            keys = path.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        
        def compare_values(actual_value: Any, expected_value: Any, path: str):
            """递归比较值"""
            nonlocal matched, partial, mismatched_fields
            
            if isinstance(expected_value, dict):
                if isinstance(actual_value, dict):
                    for key, exp_val in expected_value.items():
                        if key in actual_value:
                            compare_values(actual_value[key], exp_val, f"{path}.{key}")
                        else:
                            matched = False
                            mismatched_fields.append(f"{path}.{key}: Missing field")
                else:
                    matched = False
                    mismatched_fields.append(f"{path}: Expected dict, got {type(actual_value).__name__}")
            elif isinstance(expected_value, list):
                if isinstance(actual_value, list):
                    if len(expected_value) != len(actual_value):
                        matched = False
                        mismatched_fields.append(f"{path}: Expected {len(expected_value)} items, got {len(actual_value)}")
                    else:
                        for i, (exp_item, act_item) in enumerate(zip(expected_value, actual_value)):
                            if isinstance(exp_item, dict):
                                compare_values(act_item, exp_item, f"{path}[{i}]")
                            elif exp_item != act_item:
                                matched = False
                                mismatched_fields.append(f"{path}[{i}]: Expected {exp_item}, got {act_item}")
                else:
                    matched = False
                    mismatched_fields.append(f"{path}: Expected list, got {type(actual_value).__name__}")
            elif expected_value != actual_value:
                matched = False
                mismatched_fields.append(f"{path}: Expected {expected_value}, got {actual_value}")
        
        for key, expected_value in expected.items():
            if key not in actual:
                matched = False
                mismatched_fields.append(f"Missing field: {key}")
                continue
            
            actual_value = actual[key]
            compare_values(actual_value, expected_value, key)
        
        return {
            'matched': matched,
            'partial': partial,
            'mismatched_fields': mismatched_fields
        }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """运行所有测试用例"""
        print("\n" + "="*80)
        print("开始运行LLM字段识别测试")
        print("="*80)
        
        all_results = []
        
        for category, fields in TEST_CASES.items():
            print(f"\n{'='*80}")
            print(f"测试类别: {category}")
            print(f"{'='*80}")
            
            if isinstance(fields, list):
                for test_case in fields:
                    field = "combined" if category == "combined" else category
                    print(f"\n字段: {field}")
                    print(f"{'-'*80}")
                    
                    field_key = f"{category}.{field}"
                    self.results['field_stats'][field_key] = {
                        'total': 1,
                        'passed': 0,
                        'failed': 0,
                        'partial': 0
                    }
                    
                    result = self.run_test_case(category, field, test_case)
                    all_results.append(result)
                    
                    if result['status'] == PASS_CRITERIA['success']:
                        self.results['field_stats'][field_key]['passed'] += 1
                    elif result['status'] == PASS_CRITERIA['partial']:
                        self.results['field_stats'][field_key]['partial'] += 1
                    else:
                        self.results['field_stats'][field_key]['failed'] += 1
            else:
                for field, test_cases in fields.items():
                    print(f"\n字段: {field}")
                    print(f"{'-'*80}")
                    
                    field_key = f"{category}.{field}"
                    self.results['field_stats'][field_key] = {
                        'total': len(test_cases),
                        'passed': 0,
                        'failed': 0,
                        'partial': 0
                    }
                    
                    for test_case in test_cases:
                        result = self.run_test_case(category, field, test_case)
                        all_results.append(result)
                        
                        if result['status'] == PASS_CRITERIA['success']:
                            self.results['field_stats'][field_key]['passed'] += 1
                        elif result['status'] == PASS_CRITERIA['partial']:
                            self.results['field_stats'][field_key]['partial'] += 1
                        else:
                            self.results['field_stats'][field_key]['failed'] += 1
        
        return all_results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """生成测试报告"""
        report_lines = []
        
        report_lines.append("\n" + "="*80)
        report_lines.append("LLM字段识别测试报告")
        report_lines.append("="*80)
        
        report_lines.append(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"总测试数: {self.results['total_tests']}")
        report_lines.append(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total_tests']*100:.1f}%)")
        report_lines.append(f"部分通过: {self.results['partial']} ({self.results['partial']/self.results['total_tests']*100:.1f}%)")
        report_lines.append(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total_tests']*100:.1f}%)")
        
        report_lines.append("\n" + "-"*80)
        report_lines.append("字段识别准确率统计")
        report_lines.append("-"*80)
        
        for field_key, stats in self.results['field_stats'].items():
            total = stats['total']
            passed = stats['passed']
            accuracy = (passed / total * 100) if total > 0 else 0
            report_lines.append(f"\n{field_key}:")
            report_lines.append(f"  总数: {total}")
            report_lines.append(f"  通过: {passed}")
            report_lines.append(f"  失败: {stats['failed']}")
            report_lines.append(f"  准确率: {accuracy:.1f}%")
        
        report_lines.append("\n" + "-"*80)
        report_lines.append("失败测试详情")
        report_lines.append("-"*80)
        
        for test_name, error_info in self.results['errors'].items():
            report_lines.append(f"\n{test_name}:")
            report_lines.append(f"  类别: {error_info.get('category', 'N/A')}")
            report_lines.append(f"  字段: {error_info.get('field', 'N/A')}")
            
            if 'expected' in error_info:
                report_lines.append(f"  预期: {json.dumps(error_info['expected'], ensure_ascii=False, indent=2)}")
            if 'actual' in error_info:
                report_lines.append(f"  实际: {json.dumps(error_info['actual'], ensure_ascii=False, indent=2)}")
            if 'mismatched_fields' in error_info:
                report_lines.append(f"  不匹配字段: {', '.join(error_info['mismatched_fields'])}")
            if 'exception' in error_info:
                report_lines.append(f"  异常: {error_info['exception']}")
        
        report_lines.append("\n" + "-"*80)
        report_lines.append("改进建议")
        report_lines.append("-"*80)
        
        suggestions = self._generate_suggestions()
        for i, suggestion in enumerate(suggestions, 1):
            report_lines.append(f"\n{i}. {suggestion}")
        
        report_lines.append("\n" + "="*80)
        
        return "\n".join(report_lines)
    
    def _generate_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        for field_key, stats in self.results['field_stats'].items():
            total = stats['total']
            passed = stats['passed']
            accuracy = (passed / total * 100) if total > 0 else 0
            
            if accuracy < 80:
                category, field = field_key.split('.', 1)
                suggestions.append(
                    f"字段'{field}'的识别准确率较低({accuracy:.1f}%)，建议优化LLM提示词，"
                    f"增加该字段的识别规则和示例"
                )
        
        if self.results['failed'] > self.results['total_tests'] * 0.2:
            suggestions.append(
                "整体失败率较高，建议检查数据验证逻辑，确保验证规则与实际需求一致"
            )
        
        if any('exception' in error for error in self.results['errors'].values()):
            suggestions.append(
                "存在测试异常，建议检查系统稳定性和错误处理机制"
            )
        
        if not suggestions:
            suggestions.append("所有测试表现良好，建议持续监控并定期更新测试用例")
        
        return suggestions
    
    def save_report(self, report: str):
        """保存测试报告到文件"""
        report_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(report_dir, f'llm_field_test_report_{timestamp}.txt')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n测试报告已保存到: {report_file}")


def main():
    """主函数"""
    tester = FieldRecognitionTester()
    
    results = tester.run_all_tests()
    report = tester.generate_report(results)
    
    print(report)
    tester.save_report(report)


if __name__ == '__main__':
    main()
