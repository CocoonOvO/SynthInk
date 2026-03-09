"""
重置SEO表
"""
import asyncio
import sys
sys.path.insert(0, 'c:/aip/trae/SynthInk/backend')

from app.adapter.postgres_adapter import PostgresAdapter

async def reset_tables():
    # 创建适配器
    adapter = PostgresAdapter(
        "postgresql://postgres:postgres@localhost:5432/synthink",
        schema="seo"
    )
    await adapter.connect()
    
    try:
        # 删除旧表
        await adapter._execute("DROP TABLE IF EXISTS seo.metadata CASCADE")
        await adapter._execute("DROP TABLE IF EXISTS seo.redirects CASCADE")
        print("旧表已删除")
        
        # 创建新表
        await adapter.create_table('metadata')
        print("metadata表已创建")
        
        await adapter.create_table('redirects')
        print("redirects表已创建")
        
    finally:
        await adapter.disconnect()

if __name__ == "__main__":
    asyncio.run(reset_tables())
