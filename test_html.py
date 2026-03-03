#!/usr/bin/env python3
"""
检查返回的HTML内容
"""
import http.client

HOST = "localhost"
PORT = 8000

conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
conn.request("GET", "/", headers={"Accept": "text/html"})
response = conn.getresponse()

print(f"状态: {response.status}")
print(f"内容类型: {response.getheader('Content-Type', 'N/A')}")
print(f"服务器: {response.getheader('Server', 'N/A')}")
print("\n响应内容:")
print("-" * 60)
data = response.read().decode('utf-8')
print(data)
conn.close()
