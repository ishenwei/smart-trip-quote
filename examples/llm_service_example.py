"""
LLM服务使用示例

本脚本展示了如何使用LLM服务处理旅游需求
"""

import os
import sys
import django

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from services.llm.service import LLMRequirementService
from services.llm.config import LLMProvider


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    user_input = "我想从北京去上海旅游5天，2个成人，预算5000到10000元"
    
    print(f"用户输入: {user_input}\n")
    
    result = service.process_requirement_sync(
        user_input=user_input,
        save_to_db=False  # 不保存到数据库
    )
    
    if result.success:
        print("✓ 处理成功!")
        print(f"需求ID: {result.requirement_id}")
        print(f"LLM提供商: {result.llm_response.provider}")
        print(f"使用模型: {result.llm_response.model}")
        print(f"响应时间: {result.llm_response.response_time:.2f}秒")
        print(f"使用Token: {result.llm_response.tokens_used}")
        print(f"\n结构化数据:")
        import json
        print(json.dumps(result.structured_data, indent=2, ensure_ascii=False))
    else:
        print(f"✗ 处理失败: {result.error}")
    
    print()


def example_2_with_provider():
    """示例2: 指定LLM提供商"""
    print("=" * 60)
    print("示例2: 指定LLM提供商")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    user_input = "我想从广州去成都旅游3天，1个成人1个儿童，想住豪华型酒店"
    
    print(f"用户输入: {user_input}")
    print(f"使用提供商: {LLMProvider.DEEPSEEK.value}\n")
    
    result = service.process_requirement_sync(
        user_input=user_input,
        provider=LLMProvider.DEEPSEEK,
        save_to_db=False
    )
    
    if result.success:
        print("✓ 处理成功!")
        print(f"需求ID: {result.requirement_id}")
        print(f"目的地: {result.structured_data['base_info']['destination_cities'][0]['name']}")
        print(f"出行天数: {result.structured_data['base_info']['trip_days']}")
        print(f"总人数: {result.structured_data['base_info']['group_size']['total']}")
        print(f"酒店等级: {result.structured_data['preferences']['accommodation']['level']}")
    else:
        print(f"✗ 处理失败: {result.error}")
    
    print()


def example_3_with_client_id():
    """示例3: 使用客户端ID进行限流追踪"""
    print("=" * 60)
    print("示例3: 使用客户端ID进行限流追踪")
    print("=" * 60)
    
    service = LLMRequirementService()
    client_id = "user_12345"
    
    user_input = "我想从深圳去杭州旅游4天，3个成人，喜欢美食"
    
    print(f"用户输入: {user_input}")
    print(f"客户端ID: {client_id}\n")
    
    result = service.process_requirement_sync(
        user_input=user_input,
        client_id=client_id,
        save_to_db=False
    )
    
    if result.success:
        print("✓ 处理成功!")
        print(f"需求ID: {result.requirement_id}")
        
        # 获取限流统计
        stats = service.get_rate_limit_stats(client_id)
        print(f"\n限流统计:")
        print(f"  当前分钟请求数: {stats['client_minute_requests']}")
        print(f"  当前小时请求数: {stats['client_hour_requests']}")
        print(f"  每分钟剩余: {stats['client_minute_remaining']}")
        print(f"  每小时剩余: {stats['client_hour_remaining']}")
    else:
        print(f"✗ 处理失败: {result.error}")
    
    print()


def example_4_cache_usage():
    """示例4: 缓存使用"""
    print("=" * 60)
    print("示例4: 缓存使用")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    user_input = "我想从北京去上海旅游5天，2个成人"
    
    print(f"用户输入: {user_input}\n")
    
    # 第一次请求
    print("第一次请求（无缓存）:")
    result1 = service.process_requirement_sync(
        user_input=user_input,
        save_to_db=False
    )
    
    if result1.success:
        print(f"✓ 处理成功，响应时间: {result1.llm_response.response_time:.2f}秒")
    
    # 第二次请求（使用缓存）
    print("\n第二次请求（使用缓存）:")
    result2 = service.process_requirement_sync(
        user_input=user_input,
        save_to_db=False
    )
    
    if result2.success:
        print(f"✓ 处理成功，响应时间: {result2.llm_response.response_time:.2f}秒")
        print(f"缓存加速: {result1.llm_response.response_time / result2.llm_response.response_time:.2f}x")
    
    # 查看缓存统计
    cache_stats = service.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  缓存条目: {cache_stats['total_entries']}")
    print(f"  缓存命中: {cache_stats['total_hits']}")
    
    print()


def example_5_batch_processing():
    """示例5: 批量处理"""
    print("=" * 60)
    print("示例5: 批量处理")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    user_inputs = [
        "我想从北京去上海旅游5天，2个成人",
        "我想从广州去成都旅游3天，1个成人1个儿童",
        "我想从深圳去杭州旅游4天，3个成人"
    ]
    
    print(f"批量处理 {len(user_inputs)} 个请求\n")
    
    results = []
    for i, user_input in enumerate(user_inputs, 1):
        print(f"处理请求 {i}/{len(user_inputs)}: {user_input[:30]}...")
        
        result = service.process_requirement_sync(
            user_input=user_input,
            save_to_db=False
        )
        results.append(result)
    
    # 统计结果
    success_count = sum(1 for r in results if r.success)
    failure_count = len(results) - success_count
    
    print(f"\n处理完成:")
    print(f"  成功: {success_count}")
    print(f"  失败: {failure_count}")
    
    if success_count > 0:
        avg_time = sum(r.llm_response.response_time for r in results if r.success) / success_count
        print(f"  平均响应时间: {avg_time:.2f}秒")
    
    print()


def example_6_error_handling():
    """示例6: 错误处理"""
    print("=" * 60)
    print("示例6: 错误处理")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    # 测试空输入
    print("测试1: 空输入")
    result = service.process_requirement_sync(user_input="")
    print(f"结果: {'✓ 成功' if result.success else '✗ 失败'}")
    if not result.success:
        print(f"错误: {result.error}")
    print()
    
    # 测试无效的提供商
    print("测试2: 无效的提供商")
    try:
        result = service.process_requirement_sync(
            user_input="test",
            provider="invalid_provider"
        )
    except Exception as e:
        print(f"✗ 捕获异常: {e}")
    print()
    
    # 测试限流
    print("测试3: 查看限流状态")
    stats = service.get_rate_limit_stats()
    print(f"限流启用: {stats['enabled']}")
    print(f"每分钟限制: {stats['requests_per_minute']}")
    print(f"每小时限制: {stats['requests_per_hour']}")
    print(f"突发限制: {stats['burst_size']}")
    
    print()


def example_7_get_provider_info():
    """示例7: 获取提供商信息"""
    print("=" * 60)
    print("示例7: 获取提供商信息")
    print("=" * 60)
    
    service = LLMRequirementService()
    
    # 获取默认提供商信息
    print("默认提供商信息:")
    info = service.get_provider_info()
    print(f"  提供商: {info['provider']}")
    print(f"  模型: {info['model']}")
    print(f"  API地址: {info['api_url']}")
    print()
    
    # 获取特定提供商信息
    print("DeepSeek提供商信息:")
    try:
        info = service.get_provider_info(LLMProvider.DEEPSEEK)
        print(f"  提供商: {info['provider']}")
        print(f"  模型: {info['model']}")
        print(f"  API地址: {info['api_url']}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("LLM服务使用示例")
    print("=" * 60 + "\n")
    
    try:
        example_1_basic_usage()
        example_2_with_provider()
        example_3_with_client_id()
        example_4_cache_usage()
        example_5_batch_processing()
        example_6_error_handling()
        example_7_get_provider_info()
        
        print("=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
