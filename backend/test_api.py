"""测试API接口"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 测试注册
        print("测试注册接口...")
        response = await client.post("/api/auth/register", json={
            "username": "testapi",
            "email": "testapi@example.com",
            "password": "password123"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

if __name__ == "__main__":
    asyncio.run(test())
