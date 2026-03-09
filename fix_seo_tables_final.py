"""
修复SEO表结构 - 使用配置库中的连接信息
"""
import asyncio
import asyncpg

async def fix_tables():
    # 使用配置库中的连接信息
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='heat1423',
        database='synthink_test'
    )
    
    try:
        # 检查当前表结构
        rows = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'seo' AND table_name = 'metadata'
            ORDER BY ordinal_position
        """)
        print("📋 当前metadata表结构:")
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
        
        # 修改resource_id列类型为VARCHAR
        await conn.execute("""
            ALTER TABLE seo.metadata 
            ALTER COLUMN resource_id TYPE VARCHAR(100)
        """)
        print("\n✅ resource_id列类型已修改为VARCHAR(100)")
        
        # 验证修改结果
        rows = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'seo' AND table_name = 'metadata' AND column_name = 'resource_id'
        """)
        print(f"\n📋 修改后resource_id类型: {rows[0]['data_type']}")
        
    finally:
        await conn.close()
        print("\n✅ 修复完成！")

if __name__ == "__main__":
    asyncio.run(fix_tables())
