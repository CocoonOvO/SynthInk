#!/usr/bin/env python3
"""
测试8002端口
"""
import http.client
import json

HOST = "localhost"
PORT = 8002

# 测试根路径
print("=" * 60)
print("测试根路径 /")
print("=" * 60)
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
conn.request("GET", "/")
response = conn.getresponse()
print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
print(f"服务器: {response.getheader('Server', 'N/A')}")
print(f"X-Process-Time: {response.getheader('X-Process-Time', 'N/A')}")
data = response.read().decode('utf-8')
print(f"响应前200字符: {data[:200]}")
conn.close()

# 测试API文档
print("\n" + "=" * 60)
print("测试API文档 /api/openapi.json")
print("=" * 60)
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
conn.request("GET", "/api/openapi.json")
response = conn.getresponse()
print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
print(f"服务器: {response.getheader('Server', 'N/A')}")
print(f"X-Process-Time: {response.getheader('X-Process-Time', 'N/A')}")
data = response.read().decode('utf-8')
print(f"响应前200字符: {data[:200]}")
conn.close()

# 测试Swagger UI
print("\n" + "=" * 60)
print("测试Swagger UI /api/docs")
print("=" * 60)
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
conn.request("GET", "/api/docs")
response = conn.getresponse()
print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
print(f"服务器: {response.getheader('Server', 'N/A')}")
print(f"X-Process-Time: {response.getheader('X-Process-Time', 'N/A')}")
data = response.read().decode('utf-8')
print(f"响应前200字符: {data[:200]}")
conn.close()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
