#!/usr/bin/env python3
"""
直接测试uvicorn是否能正确处理请求
"""
from fastapi import FastAPI
import uvicorn

# 创建一个简单的测试应用
test_app = FastAPI()

@test_app.get("/")
async def root():
    return {"message": "Hello from test app"}

@test_app.get("/api/test")
async def test():
    return {"message": "API test endpoint"}

if __name__ == "__main__":
    print("启动测试服务器...")
    uvicorn.run(test_app, host="0.0.0.0", port=8001)
