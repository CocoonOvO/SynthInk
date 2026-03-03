#!/usr/bin/env python3
"""
测试8001端口
"""
import http.client
import json

HOST = "localhost"
PORT = 8001

conn = http.client.HTTPConnection(HOST, PORT, timeout=5)

# 测试根路径
print("=" * 60)
print("测试根路径 /")
print("=" * 60)
conn.request("GET", "/")
response = conn.getresponse()
print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
data = response.read().decode('utf-8')
print(f"响应: {data}")
conn.close()

# 测试API路径
conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
print("\n" + "=" * 60)
print("测试API路径 /api/test")
print("=" * 60)
conn.request("GET", "/api/test")
response = conn.getresponse()
print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
data = response.read().decode('utf-8')
print(f"响应: {data}")
conn.close()
