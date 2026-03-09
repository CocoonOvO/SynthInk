import requests

resp = requests.get('http://localhost:8002/api/openapi.json')
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"路径数量: {len(data.get('paths', {}))}")
    
    # 查找所有包含posts的路径
    for path, methods in data.get('paths', {}).items():
        if 'posts' in path:
            print(f"\n路径: {path}")
            for method, info in methods.items():
                print(f"  方法: {method.upper()}")
                print(f"  摘要: {info.get('summary', 'N/A')}")
else:
    print(f"错误: {resp.text[:200]}")
