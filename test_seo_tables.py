"""
检查SEO表是否存在
"""
import asyncio
import sys
sys.path.insert(0, 'c:/aip/trae/SynthInk/backend')

from app.db_manager import db_manager

async def check_tables():
    await db_manager.initialize()
    
    # 检查seo schema中的表
    query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'seo'
    """
    
    async with db_manager.postgres.pool.acquire() as conn:
        rows = await conn.fetch(query)
        print("SEO schema中的表:")
        for row in rows:
            print(f"  - {row['table_name']}")
        
        if not rows:
            print("  (无表)")
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(check_tables())
