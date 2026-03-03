"""
集成测试和数据写入脚本
测试后端API并写入测试数据
"""
import asyncio
import httpx
import sys
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8002"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.headers = {}
        self.test_results = []
        
    async def close(self):
        await self.client.aclose()
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "📝", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        print(f"{prefix} [{timestamp}] {message}")
        self.test_results.append({"time": timestamp, "level": level, "message": message})
    
    async def test_health(self):
        """测试健康检查接口"""
        self.log("测试健康检查接口...")
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"服务状态: {data.get('status', 'unknown')}", "SUCCESS")
                self.log(f"数据库状态: {data.get('database', 'unknown')}")
                return True
            else:
                self.log(f"健康检查失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"健康检查异常: {e}", "ERROR")
            return False
    
    async def test_register(self, username, email, password):
        """测试用户注册"""
        self.log(f"测试用户注册: {username}...")
        try:
            response = await self.client.post(
                "/api/auth/register",
                json={"username": username, "email": email, "password