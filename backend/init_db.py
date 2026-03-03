"""执行数据库初始化"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001"

def login():
    """登录获取token"""
    print("=" * 60)
    print("1. 登录获取Token")
    print("=" * 60)
    
    resp = requests.post(
        f"{BASE_URL}/api/admin/login",
        json={"username": "admin", "password": "123456"}
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 登录成功")
        print(f"Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ 登录失败: {resp.text}")
        return None

def check_init_status(token):
    """检查初始化状态"""
    print("\n" + "=" * 60)
    print("2. 检查数据库初始化状态")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{BASE_URL}/api/admin/database/init-status",
        headers=headers
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get("ready"):
        print("✅ 数据库已就绪，无需初始化")
        return True
    else:
        print("⚠️ 数据库未就绪，需要初始化")
        return False

def init_database(token):
    """初始化数据库"""
    print("\n" + "=" * 60)
    print("3. 执行数据库初始化")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{BASE_URL}/api/admin/database/init",
        headers=headers
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get("success") and data.get("ready"):
        print("✅ 数据库初始化成功")
        return True
    else:
        print(f"❌ 数据库初始化失败: {data.get('error', 'Unknown error')}")
        return False

def verify_tables():
    """验证数据库表"""
    print("\n" + "=" * 60)
    print("4. 验证数据库表结构")
    print("=" * 60)
    
    # 使用MCP查询PostgreSQL
    print("请查看PostgreSQL中的表结构")
    print("预期表: users, posts, tags, groups, post_tags")

if __name__ == "__main__":
    print("开始数据库初始化流程")
    print("=" * 60)
    
    # 1. 登录
    token = login()
    if not token:
        sys.exit(1)
    
    # 2. 检查状态
    if check_init_status(token):
        print("\n✅ 数据库已初始化完成")
        sys.exit(0)
    
    # 3. 初始化
    if init_database(token):
        print("\n✅ 数据库初始化完成")
        
        # 4. 再次检查状态
        print("\n" + "=" * 60)
        print("5. 验证初始化结果")
        print("=" * 60)
        check_init_status(token)
    else:
        print("\n❌ 数据库初始化失败")
        sys.exit(1)
