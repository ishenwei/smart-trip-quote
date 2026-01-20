"""
LLM服务测试运行脚本

运行所有测试：
    python tests/run_tests.py

运行特定测试文件：
    python tests/run_tests.py test_llm_providers

运行特定测试类：
    python tests/run_tests.py test_llm_providers::TestDeepSeekProvider

运行特定测试方法：
    python tests/run_tests.py test_llm_providers::TestDeepSeekProvider::test_validate_config

查看覆盖率：
    python tests/run_tests.py --coverage
"""

import sys
import os
import argparse
import subprocess


def run_tests(test_target: str = None, coverage: bool = False, verbose: bool = False):
    """
    运行测试
    
    Args:
        test_target: 测试目标（文件、类或方法）
        coverage: 是否生成覆盖率报告
        verbose: 是否显示详细输出
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"Warning: Django setup failed: {e}")
    
    pytest_args = []
    
    if coverage:
        pytest_args.extend([
            '--cov=services/llm',
            '--cov=apps/api',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    if verbose:
        pytest_args.append('-v')
    else:
        pytest_args.append('-q')
    
    if test_target:
        test_path = f'tests/{test_target}'
    else:
        test_path = 'tests/'
    
    pytest_args.append(test_path)
    
    print(f"Running tests: {test_path}")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest'] + pytest_args,
        cwd=base_dir
    )
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run LLM service tests')
    parser.add_argument(
        'target',
        nargs='?',
        help='Test target (file, class, or method)'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        test_target=args.target,
        coverage=args.coverage,
        verbose=args.verbose
    )
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
