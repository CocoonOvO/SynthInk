#!/usr/bin/env python3
"""
测试管理员登录
"""
import http.client
import json

HOST = "localhost"
PORT = 8002

print("=" * 60)
print("测试管理员登录")
print("=" * 60)

# 测试管理员登录
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)

# 准备登录数据
login_data = {
    "username": "admin",
    "password": "123456"
}

# 发送POST请求
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

body = json.dumps(login_data)

print(f"\n请求: POST /api/admin/login")
print(f"数据: {login_data}")

conn.request("POST", "/api/admin/login", body=body, headers=headers)
response = conn.getresponse()

print(f"\n状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")

data = response.read().decode('utf-8')
print(f"\n响应内容:")
print("-" * 60)
try:
    json_data = json.loads(data)
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
    # 保存token
    if 'access_token' in json_data:
        print("\n✅ 登录成功!")
        print(f"Token: {json_data['access_token'][:50]}...")
        
        # 保存token到文件
        with open('admin_token.txt', 'w') as f:
            f.write(json_data['access_token'])
        print("Token已保存到 admin_token.txt")
    else:
        print("\n❌ 登录失败，未获取到token")
        print(f"错误: {json_data.get('detail', '未知错误')}")
except:
    print(data)

conn.close()

print("\n" + "=" * 60)
