import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.adapter.postgres_adapter import PostgresAdapter

async def test():
    adapter = PostgresAdapter('postgresql://postgres:heat1423@localhost:5432/synthink_test', schema='custom_schema')
    await adapter.connect()
    
    import uuid
    from datetime import datetime
    
    # 准备数据
    post_data = {
        "id": str(uuid.uuid4()),
        "title": "测试标题",
        "slug": "测试slug",
        "content": "测试内容",
        "status": "published",
        "author_id": "86862cc7-7e49-4da9-9a7a-dc2364682c09",
        "view_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    print(f"准备插入的数据: {post_data}")
    
    # 插入
    result = await adapter.insert("posts", post_data)
    print(f"插入结果: {result}")
    
    # 查询
    check = await adapter._fetch(
        f"SELECT id, title, slug FROM {adapter.schema}.posts WHERE id = '{post_data['id']}'"
    )
    print(f"查询结果: {check}")
    
    await adapter.disconnect()

asyncio.run(test())
