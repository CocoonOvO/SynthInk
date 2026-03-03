#!/usr/bin/env python3
"""
使用原始socket测试
"""
import socket

HOST = "127.0.0.1"
PORT = 8000

# 创建socket连接
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((HOST, PORT))

# 发送HTTP请求
request = b"GET /api/openapi.json HTTP/1.1\r\nHost: localhost:8000\r\nAccept: application/json\r\n\r\n"
sock.sendall(request)

# 接收响应
response = b""
while True:
    try:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    except socket.timeout:
        break

sock.close()

# 打印响应
print("原始HTTP响应:")
print("=" * 60)
print(response.decode('utf-8', errors='replace')[:1000])
