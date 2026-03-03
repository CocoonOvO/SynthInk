#!/usr/bin/env python3
"""
测试主人账号登录 - Cocoon
"""
import http.client
import json

HOST = "localhost"
PORT = 8002

print("=" * 60)
print("测试主人账号登录")
print("=" * 60)

# 测试用户登录（不是admin，是普通用户认证接口）
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)

# 准备登录数据 - 使用主人账号
login_data = {
    "username": "Cocoon",
    "password": "heat1423"
}

# 发送POST请求
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

# 编码表单数据
from urllib.parse import urlencode
body = urlencode(login_data)

print(f"\n请求: POST /api/auth/token")
print(f"账号: {login_data['username']}")

conn.request("POST", "/api/auth/token", body=body, headers=headers)
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
        print("\n✅ 主人登录成功!")
        print(f"Token: {json_data['access_token'][:50]}...")
        
        # 保存token到文件
        with open('cocoon_token.txt', 'w') as f:
            f.write(json_data['access_token'])
        print("Token已保存到 cocoon_token.txt")
    else:
        print("\n❌ 登录失败，未获取到token")
        print(f"错误: {json_data.get('detail', '未知错误')}")
except:
    print(data)

conn.close()

print("\n" + "=" * 60)
