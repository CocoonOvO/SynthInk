#!/usr/bin/env python3
"""
检查FastAPI应用的路由配置
"""
import sys
sys.path.insert(0, 'C:\\aip\\trae\\SynthInk\\backend')

from app.main import app

print("=" * 60)
print("FastAPI 应用路由检查")
print("=" * 60)

print(f"\n应用标题: {app.title}")
print(f"应用版本: {app.version}")
print(f"Docs URL: {app.docs_url}")
print(f"OpenAPI URL: {app.openapi_url}")

print("\n" + "-" * 60)
print("所有路由:")
print("-" * 60)

for i, route in enumerate(app.routes):
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', {'N/A'})
        methods_str = ','.join(methods) if methods else 'N/A'
        print(f"{i+1:3}. {methods_str:20} {route.path}")

print("\n" + "=" * 60)
