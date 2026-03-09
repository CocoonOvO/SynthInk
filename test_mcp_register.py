"""
测试MCP注册接口
"""
import requests
import json

BASE_URL = "http://localhost:8002/api/mcp"

def test_register_user():
    """测试普通用户注册"""
    print("=" * 60)
    print("测试1: 普通用户注册")
    print("=" * 60)
    
    import time
    suffix = str(int(time.time()))[-4:]
    
    payload = {
        "username": f"testuser_{suffix}",
        "password": "TestPass123!",
        "email": f"testuser_{suffix}@example.com",
        "display_name": "测试用户",
        "bio": "这是一个测试用户账号"
    }
    
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/tools/register_user", json=payload)
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_register_agent():
    """测试Agent注册"""
    print("\n" + "=" * 60)
    print("测试2: Agent注册")
    print("=" * 60)
    
    import time
    suffix = str(int(time.time()))[-4:]
    
    payload = {
        "username": f"testagent_{suffix}",
        "password": "AgentPass123!",
        "email": f"agent_{suffix}@example.com",
        "display_name": "测试Agent",
        "bio": "这是一个AI测试代理",
        "agent_model": "kimi-k2.5",
        "agent_provider": "moonshot",
        "agent_config": {
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }
    
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/tools/register_agent", json=payload)
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_register_agent_missing_fields():
    """测试Agent注册缺少必填字段"""
    print("\n" + "=" * 60)
    print("测试3: Agent注册缺少必填字段(应失败)")
    print("=" * 60)
    
    payload = {
        "username": "testagent_002",
        "password": "AgentPass123!",
        "email": "agent2@example.com",
        "display_name": "测试Agent2",
        "bio": "这是一个AI测试代理",
        # 缺少 agent_model 和 agent_provider
    }
    
    print(f"请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/tools/register_agent", json=payload)
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 422  # 应该返回422错误（缺少必填字段）
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_mcp_docs():
    """测试MCP文档端点"""
    print("\n" + "=" * 60)
    print("测试4: MCP文档端点")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        # 查找注册相关工具
        register_tools = [t for t in data.get("tools", []) if "register" in t["name"]]
        print(f"\n注册相关工具:")
        for tool in register_tools:
            print(f"  - {tool['name']}: {tool['description']}")
            if tool.get('important_note'):
                print(f"    ⚠️ {tool['important_note']}")
        
        return len(register_tools) == 2
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "🧪 MCP注册接口测试开始".center(60, "=") + "\n")
    
    results = []
    
    # 运行测试
    results.append(("普通用户注册", test_register_user()))
    results.append(("Agent注册", test_register_agent()))
    results.append(("Agent注册验证", test_register_agent_missing_fields()))
    results.append(("MCP文档", test_mcp_docs()))
    
    # 打印结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 通过")
