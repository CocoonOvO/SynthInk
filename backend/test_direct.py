#!/usr/bin/env python3
"""
直接测试FastAPI应用
"""
import sys
sys.path.insert(0, 'C:\\aip\\trae\\SynthInk\\backend')

from fastapi.testclient import TestClient

# 导入应用
from app.main import app

client = TestClient(app)

def test_root():
    """测试根路径"""
    response = client.get("/")
    print(f"GET / - 状态: {response.status_code}")
    print(f"响应: {response.text[:200]}")
    return response.status_code == 200

def test_api_docs():
    """测试API文档"""
    response = client.get("/api/docs")
    print(f"GET /api/docs - 状态: {response.status_code}")
    print(f"内容类型: {response.headers.get('content-type', 'N/A')}")
    return response.status_code == 200

def test_openapi():
    """测试OpenAPI"""
    response = client.get("/api/openapi.json")
    print(f"GET /api/openapi.json - 状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"API标题: {data.get('info', {}).get('title', 'N/A')}")
        print(f"路径数: {len(data.get('paths', {}))}")
    return response.status_code == 200

def test_login():
    """测试登录"""
    response = client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": "admin",
            "password": "admin123",
            "scope": ""
        }
    )
    print(f"POST /api/auth/token - 状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"登录成功! Token: {data.get('access_token', 'N/A')[:50]}...")
        return data.get('access_token')
    else:
        print(f"错误: {response.text}")
        return None

def list_routes():
    """列出所有路由"""
    print("\n已注册的路由:")
    print("-" * 60)
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ','.join(route.methods)
            print(f"  {methods:20} {route.path}")

if __name__ == "__main__":
    print("=" * 60)
    print("直接测试FastAPI应用")
    print("=" * 60)
    
    list_routes()
    
    print("\n【1】测试根路径...")
    test_root()
    
    print("\n【2】测试API文档...")
    test_api_docs()
    
    print("\n【3】测试OpenAPI...")
    test_openapi()
    
    print("\n【4】测试登录...")
    token = test_login()
    
    if token:
        print("\n" + "=" * 60)
        print("✅ 测试通过！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 登录失败")
        print("=" * 60)
