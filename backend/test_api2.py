"""测试API接口 - 检查所有路由"""
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
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
        print()
        
        # 测试GET /api/openapi.json
        print("测试GET /api/openapi.json...")
        response = await client.get("/api/openapi.json")
        print(f"状态码: {response.status_code}")
        print()
        
        # 测试GET /api/docs
        print("测试GET /api/docs...")
        response = await client.get("/api/docs")
        print(f"状态码: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test())
