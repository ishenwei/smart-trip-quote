import json

# 读取JSON文件
with open('n8n_workflows/travel_planning_ai_workflow.json', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    # 尝试解析JSON
    data = json.loads(content)
    print("JSON is valid")
    print(f"Workflow name: {data.get('name')}")
    print(f"Number of nodes: {len(data.get('nodes', []))}")
except json.JSONDecodeError as e:
    print(f"JSON is invalid: {e}")
