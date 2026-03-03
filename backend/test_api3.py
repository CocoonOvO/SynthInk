"""测试API接口 - 使用8001端口"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        # 测试GET /api/tags/ (公开接口)
        print("测试GET /api/tags/...")
        response = await client.get("/api/tags/")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:200]}...")
        print()
        
        # 测试POST /api/auth/register
        print("测试POST /api/auth/register...")
        response = await client.post("/api/auth/register", json={
            "username": "testapi",
            "email": "testapi@example.com",
            "password": "password123"
        })
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")

if __name__ == "__main__":
    asyncio.run(test())
