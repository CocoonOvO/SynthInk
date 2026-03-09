import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.adapter.postgres_adapter import PostgresAdapter
from app.utils.slug import generate_slug, is_valid_slug

async def test():
    # 连接数据库
    adapter = PostgresAdapter('postgresql://postgres:heat1423@localhost:5432/synthink_test', schema='custom_schema')
    await adapter.connect()
    
    # 1. 获取现有slug
    result = await adapter._fetch(f"SELECT id, slug FROM {adapter.schema}.posts WHERE slug IS NOT NULL")
    existing_slugs = [row['slug'] for row in result if row['slug']]
    print(f'现有slugs: {existing_slugs}')
    
    # 2. 生成新slug
    title = "测试文章标题"
    new_slug = generate_slug(title, existing_slugs)
    print(f'生成的新slug: {new_slug}')
    print(f'slug是否有效: {is_valid_slug(new_slug)}')
    
    # 3. 准备文章数据
    import uuid
    from datetime import datetime
    post_data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "slug": new_slug,
        "content": "测试内容",
        "status": "published",
        "author_id": "86862cc7-7e49-4da9-9a7a-dc2364682c09",  # 萌星
        "view_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    print(f'准备插入的数据: {post_data}')
    
    # 4. 插入文章
    insert_result = await adapter.insert("posts", post_data)
    print(f'插入结果: {insert_result}')
    
    # 5. 查询文章
    result = await adapter._fetch(f"SELECT id, title, slug FROM {adapter.schema}.posts WHERE id = '{post_data['id']}'")
    print(f'查询结果: {result}')
    
    await adapter.disconnect()

asyncio.run(test())
