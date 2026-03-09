import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.adapter.postgres_adapter import PostgresAdapter
from app.utils.slug import generate_slug

async def test():
    # 连接数据库
    adapter = PostgresAdapter('postgresql://postgres:heat1423@localhost:5432/synthink_test', schema='custom_schema')
    await adapter.connect()
    
    # 测试get_existing_slugs逻辑
    result = await adapter.find(
        "posts",
        filters=None,
        limit=10000,
        columns=["id", "slug"]
    )
    print(f'find result: {result}')
    
    slugs = []
    for post in result.get("data", []):
        if post.get("slug"):
            slugs.append(post["slug"])
    print(f'existing slugs: {slugs}')
    
    # 测试生成slug
    title = "测试文章标题"
    new_slug = generate_slug(title, slugs)
    print(f'generated slug: {new_slug}')
    
    await adapter.disconnect()

asyncio.run(test())
