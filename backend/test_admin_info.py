#!/usr/bin/env python3
"""
测试获取管理员信息
"""
import http.client
import json

HOST = "localhost"
PORT = 8002

print("=" * 60)
print("测试获取管理员信息")
print("=" * 60)

# 读取token
try:
    with open('admin_token.txt', 'r') as f:
        token = f.read().strip()
    print(f"\n使用Token: {token[:50]}...")
except FileNotFoundError:
    print("❌ 未找到token文件，请先运行登录测试")
    exit(1)

# 测试获取管理员信息
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

print(f"\n请求: GET /api/admin/me")

conn.request("GET", "/api/admin/me", headers=headers)
response = conn.getresponse()

print(f"\n状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")

data = response.read().decode('utf-8')
print(f"\n响应内容:")
print("-" * 60)
try:
    json_data = json.loads(data)
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
    if response.status == 200:
        print("\n✅ 获取管理员信息成功!")
        print(f"管理员ID: {json_data.get('id')}")
        print(f"用户名: {json_data.get('username')}")
        print(f"角色: {json_data.get('role')}")
    else:
        print(f"\n❌ 获取信息失败: {json_data.get('detail', '未知错误')}")
except:
    print(data)

conn.close()

print("\n" + "=" * 60)
