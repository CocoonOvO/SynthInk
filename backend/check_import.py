#!/usr/bin/env python3
"""
检查app模块导入
"""
import sys
print("Python路径:")
for p in sys.path:
    print(f"  {p}")

print("\n尝试导入app.main:")
try:
    import app.main
    print(f"  成功: {app.main.__file__}")
    print(f"  app对象: {app.main.app}")
    print(f"  应用标题: {app.main.app.title}")
except Exception as e:
    print(f"  失败: {e}")

print("\n检查当前目录:")
import os
print(f"  当前目录: {os.getcwd()}")
print(f"  文件列表: {os.listdir('.')}")
