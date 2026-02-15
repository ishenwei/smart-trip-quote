#!/usr/bin/env python
"""
测试原始用户输入是否被正确保存到origin_input字段
"""

import os
import sys

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from services.llm.service import LLMRequirementService

def test_origin_input_saving():
    """测试原始用户输入是否被正确保存"""
    print("开始测试原始用户输入保存功能...")
    
    # 测试用例1: 短文本输入
    test_input = '我想从北京去上海玩3天，希望住舒适型酒店，预算5000-8000元，包含往返机票。'
    
    print(f"测试输入: {test_input}")
    print(f"输入长度: {len(test_input)} 字符")
    
    # 创建LLMRequirementService实例
    service = LLMRequirementService()
    
    # 处理需求（保存到数据库）
    result = service.process_requirement_sync(
        user_input=test_input,
        save_to_db=True
    )
    
    if result.success:
        print(f"✓ 需求处理成功！ID: {result.requirement_id}")
        
        # 从数据库获取需求
        from apps.models import Requirement
        requirement = Requirement.objects.get(requirement_id=result.requirement_id)
        
        # 验证origin_input字段
        origin_input = requirement.origin_input
        print(f"数据库中保存的原始输入长度: {len(origin_input)} 字符")
        
        if origin_input == test_input:
            print(f"✓ 原始输入保存成功！")
            print(f"保存的内容前50个字符: '{origin_input[:50]}...'")
        else:
            print(f"✗ 原始输入保存失败！")
            print(f"预期前50个字符: '{test_input[:50]}...'")
            print(f"实际前50个字符: '{origin_input[:50]}...'")
    else:
        print(f"✗ 需求处理失败: {result.error}")
    
    print("测试完成！")

if __name__ == '__main__':
    test_origin_input_saving()
