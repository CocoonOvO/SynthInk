import asyncio
from app.adapter.postgres_adapter import PostgresAdapter

async def check():
    adapter = PostgresAdapter('postgresql://postgres:heat1423@localhost:5432/synthink_test', schema='custom_schema')
    await adapter.connect()
    
    # 查询最新的文章
    result = await adapter._fetch("SELECT id, title, slug FROM custom_schema.posts ORDER BY created_at DESC LIMIT 1")
    print('最新文章:', result)
    
    await adapter.disconnect()

asyncio.run(check())
