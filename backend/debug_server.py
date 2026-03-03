#!/usr/bin/env python3
"""
调试服务器启动
"""
import uvicorn
import sys
import os

# 打印启动信息
print("=" * 60)
print("调试服务器启动")
print("=" * 60)
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"Python路径:")
for p in sys.path[:5]:
    print(f"  {p}")

# 导入应用并打印信息
from app.main import app
print(f"\n应用标题: {app.title}")
print(f"Docs URL: {app.docs_url}")
print(f"OpenAPI URL: {app.openapi_url}")
print(f"路由数量: {len(app.routes)}")

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="debug"
    )
