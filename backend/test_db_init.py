"""测试数据库初始化功能"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_login():
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
        print(f"Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"Error: {resp.text}")
        return None

def test_init_status(token):
    """测试获取初始化状态"""
    print("\n" + "=" * 60)
    print("2. 获取数据库初始化状态")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{BASE_URL}/api/admin/database/init-status",
        headers=headers
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    return resp.status_code == 200

def test_init_database(token):
    """测试初始化数据库"""
    print("\n" + "=" * 60)
    print("3. 初始化数据库")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(
        f"{BASE_URL}/api/admin/database/init",
        headers=headers
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    return resp.status_code == 200

def test_init_status_after(token):
    """初始化后再次获取状态"""
    print("\n" + "=" * 60)
    print("4. 初始化后获取状态")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{BASE_URL}/api/admin/database/init-status",
        headers=headers
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    return resp.status_code == 200

if __name__ == "__main__":
    print("开始测试数据库初始化功能")
    print("=" * 60)
    
    # 1. 登录
    token = test_login()
    if not token:
        print("❌ 登录失败，终止测试")
        exit(1)
    print("✅ 登录成功")
    
    # 2. 获取初始状态
    if test_init_status(token):
        print("✅ 获取初始化状态成功")
    else:
        print("❌ 获取初始化状态失败")
    
    # 3. 初始化数据库
    if test_init_database(token):
        print("✅ 数据库初始化成功")
    else:
        print("❌ 数据库初始化失败")
    
    # 4. 再次获取状态
    if test_init_status_after(token):
        print("✅ 获取初始化状态成功")
    else:
        print("❌ 获取初始化状态失败")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
