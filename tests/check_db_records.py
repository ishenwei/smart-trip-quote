#!/usr/bin/env python
"""
检查数据库中最近创建的需求记录，验证origin_input和requirement_json_data字段是否正确保存
"""

import os
import sys
import json
from datetime import datetime

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.models import Requirement


def check_recent_records():
    """检查最近创建的需求记录"""
    print("开始检查数据库中的需求记录...")
    
    # 获取最近创建的10条记录
    recent_requirements = Requirement.objects.order_by('-created_at')[:10]
    
    print(f"找到最近的 {recent_requirements.count()} 条需求记录\n")
    
    for i, requirement in enumerate(recent_requirements, 1):
        print(f"=== 记录 #{i}: {requirement.requirement_id} ===")
        print(f"创建时间: {requirement.created_at}")
        
        # 检查origin_input字段
        print(f"\norigin_input:")
        if requirement.origin_input:
            print(f"  长度: {len(requirement.origin_input)} 字符")
            print(f"  内容前50字符: '{requirement.origin_input[:50]}...'")
        else:
            print(f"  为空")
        
        # 检查requirement_json_data字段
        print(f"\nrequirement_json_data:")
        if requirement.requirement_json_data:
            print(f"  类型: {type(requirement.requirement_json_data).__name__}")
            if isinstance(requirement.requirement_json_data, dict):
                print(f"  包含的键: {list(requirement.requirement_json_data.keys())}")
                # 检查是否包含origin_input
                if 'origin_input' in requirement.requirement_json_data:
                    print(f"  包含origin_input: 是")
                    origin_input_in_json = requirement.requirement_json_data.get('origin_input')
                    if origin_input_in_json:
                        print(f"  origin_input长度: {len(origin_input_in_json)} 字符")
                    else:
                        print(f"  origin_input为空")
                else:
                    print(f"  包含origin_input: 否")
        else:
            print(f"  为空")
        
        print("-" * 50)
    
    # 统计信息
    total_records = Requirement.objects.count()
    records_with_origin_input = Requirement.objects.exclude(origin_input='').count()
    records_with_json_data = Requirement.objects.exclude(requirement_json_data=None).count()
    
    print(f"\n=== 统计信息 ===")
    print(f"总记录数: {total_records}")
    print(f"包含origin_input的记录数: {records_with_origin_input} ({records_with_origin_input/total_records*100:.1f}%)")
    print(f"包含requirement_json_data的记录数: {records_with_json_data} ({records_with_json_data/total_records*100:.1f}%)")


if __name__ == '__main__':
    check_recent_records()
