import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db_manager import db_manager
from app.utils.slug import generate_slug, is_valid_slug

async def test():
    # 初始化数据库连接
    await db_manager.initialize()
    
    # 1. 获取现有slug
    result = await db_manager.postgres._fetch(f"SELECT id, slug FROM {db_manager.postgres.schema}.posts WHERE slug IS NOT NULL")
    existing_slugs = [row['slug'] for row in result if row['slug']]
    print(f'现有slugs数量: {len(existing_slugs)}')
    
    # 2. 生成新slug
    title = "测试文章标题DBM"
    new_slug = generate_slug(title, existing_slugs)
    print(f'生成的新slug: {new_slug}')
    
    # 3. 准备文章数据
    import uuid
    from datetime import datetime
    post_data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "slug": new_slug,
        "content": "测试内容",
        "status": "published",
        "author_id": "86862cc7-7e49-4da9-9a7a-dc2364682c09",
        "view_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    print(f'准备插入的数据包含slug: {post_data.get("slug")}')
    
    # 4. 插入文章
    insert_result = await db_manager.postgres.insert("posts", post_data)
    print(f'插入结果success: {insert_result.get("success")}')
    print(f'插入结果data包含slug: {insert_result.get("data", {}).get("slug")}')
    
    # 5. 查询文章
    result = await db_manager.postgres._fetch(f"SELECT id, title, slug FROM {db_manager.postgres.schema}.posts WHERE id = '{post_data['id']}'")
    print(f'查询结果: {result}')
    
    await db_manager.close()

asyncio.run(test())
