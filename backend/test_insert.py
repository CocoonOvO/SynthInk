"""测试insert方法"""
import asyncio
import os

os.environ["POSTGRES_DISABLE_SSL"] = "true"

from app.adapter.postgres_adapter import PostgresAdapter

async def test():
    dsn = "postgresql+asyncpg://postgres:heat1423@localhost:5432/synthink_test"
    adapter = PostgresAdapter(dsn)
    await adapter.connect()
    
    # 测试插入用户
    import time
    ts = int(time.time()) % 10000
    user_data = {
        "username": f"test_insert_{ts}",
        "email": f"test_insert_{ts}@example.com",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "is_superuser": False,
    }
    
    result = await adapter.insert("users", user_data)
    print(f"Insert result: {result}")
    print(f"Data keys: {result.get('data', {}).keys()}")
    
    await adapter.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
