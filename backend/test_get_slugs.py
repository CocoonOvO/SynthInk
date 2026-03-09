import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.adapter.postgres_adapter import PostgresAdapter

async def test():
    adapter = PostgresAdapter('postgresql://postgres:heat1423@localhost:5432/synthink_test', schema='custom_schema')
    await adapter.connect()
    
    try:
        # 模拟 get_existing_slugs 函数
        result = await adapter._fetch(
            f"SELECT id, slug FROM {adapter.schema}.posts WHERE slug IS NOT NULL"
        )
        print(f'查询结果: {result}')
        
        slugs = []
        for row in result:
            slug = row.get("slug")
            row_id = str(row.get("id"))
            print(f'  处理: id={row_id}, slug={slug}')
            if slug:
                slugs.append(slug)
        
        print(f'最终slugs: {slugs}')
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
    
    await adapter.disconnect()

asyncio.run(test())
