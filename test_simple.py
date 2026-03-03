#!/usr/bin/env python3
"""
简单测试后端API
"""
import http.client
import json

HOST = "localhost"
PORT = 8000

def test_endpoint(method, path, body=None, headers=None):
    """测试指定端点"""
    try:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
        
        default_headers = {"Accept": "application/json"}
        if headers:
            default_headers.update(headers)
        
        conn.request(method, path, body=body, headers=default_headers)
        response = conn.getresponse()
        
        status = response.status
        data = response.read()
        
        print(f"{method} {path}")
        print(f"  状态: {status}")
        print(f"  响应长度: {len(data)} bytes")
        
        if data:
            try:
                json_data = json.loads(data.decode('utf-8'))
                print(f"  响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}")
            except:
                print(f"  原始响应: {data[:200]}")
        
        conn.close()
        return status, data
    except Exception as e:
        print(f"{method} {path} 失败: {e}")
        return None, None

# 测试根路径
print("=" * 60)
print("测试根路径")
print("=" * 60)
test_endpoint("GET", "/")

# 测试API根路径
print("\n" + "=" * 60)
print("测试API根路径")
print("=" * 60)
test_endpoint("GET", "/api/")

# 测试OpenAPI
print("\n" + "=" * 60)
print("测试OpenAPI文档")
print("=" * 60)
test_endpoint("GET", "/api/openapi.json")

# 测试登录 - 使用表单格式
print("\n" + "=" * 60)
print("测试登录接口")
print("=" * 60)

# 正确的OAuth2表单格式
from urllib.parse import urlencode
form_data = urlencode({
    'grant_type': 'password',
    'username': 'admin',
    'password': 'admin123',
    'scope': ''
})

test_endpoint(
    "POST", 
    "/api/auth/token",
    body=form_data,
    headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    }
)

# 测试OPTIONS请求（预检）
print("\n" + "=" * 60)
print("测试OPTIONS预检")
print("=" * 60)
test_endpoint("OPTIONS", "/api/auth/token")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
