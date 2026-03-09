"""
验证LLM代码移除后的系统功能测试
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def test_imports():
    """测试导入是否正常"""
    print("=" * 60)
    print("测试模块导入")
    print("=" * 60)
    
    try:
        from apps.api.views.webhook_views import (
            ItineraryWebhookView,
            RequirementWebhookView,
            ProcessRequirementViaN8nView
        )
        print("✅ webhook_views 导入成功")
    except ImportError as e:
        print(f"❌ webhook_views 导入失败: {e}")
    
    try:
        from apps.api import urls
        print("✅ API URLs 导入成功")
    except ImportError as e:
        print(f"❌ API URLs 导入失败: {e}")
    
    try:
        from config import settings
        print("✅ settings 导入成功")
    except ImportError as e:
        print(f"❌ settings 导入失败: {e}")


def test_removed_files():
    """测试已移除的文件"""
    print("\n" + "=" * 60)
    print("测试已移除的文件")
    print("=" * 60)
    
    removed_files = [
        'services/llm',
        'apps/api/views/llm_views.py',
        'apps/api/views/llm_views_simple.py',
        'apps/api/serializers/llm_serializer.py',
        'config/llm_config.json',
    ]
    
    for file_path in removed_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(full_path):
            print(f"✅ {file_path} 已移除")
        else:
            print(f"❌ {file_path} 仍存在")


def test_url_patterns():
    """测试URL配置"""
    print("\n" + "=" * 60)
    print("测试URL配置")
    print("=" * 60)
    
    try:
        from apps.api.urls import urlpatterns
        
        expected_patterns = [
            'webhook/itinerary/',
            'requirement/',
            'requirement/callback/',
        ]
        
        actual_patterns = [pattern.pattern.regex.pattern for pattern in urlpatterns]
        
        for expected in expected_patterns:
            found = any(expected in pattern for pattern in actual_patterns)
            if found:
                print(f"✅ {expected} 存在")
            else:
                print(f"❌ {expected} 不存在")
        
        removed_patterns = [
            'process/',
            'provider-info/',
            'rate-limit-stats/',
            'cache-stats/',
            'cache/clear/',
            'config/reload/',
            'health/',
        ]
        
        for removed in removed_patterns:
            found = any(removed in pattern for pattern in actual_patterns)
            if not found:
                print(f"✅ {removed} 已移除")
            else:
                print(f"❌ {removed} 仍存在")
                
    except Exception as e:
        print(f"❌ URL配置测试失败: {e}")


def test_settings():
    """测试settings配置"""
    print("\n" + "=" * 60)
    print("测试settings配置")
    print("=" * 60)
    
    try:
        from config.settings import LOGGING
        
        if 'llm_service' in LOGGING.get('loggers', {}):
            print("❌ llm_service logger 仍存在")
        else:
            print("✅ llm_service logger 已移除")
            
    except Exception as e:
        print(f"❌ settings配置测试失败: {e}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("LLM代码移除后的系统功能验证测试")
    print("=" * 60)
    
    test_imports()
    test_removed_files()
    test_url_patterns()
    test_settings()
    
    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()