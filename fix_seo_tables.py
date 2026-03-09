"""
修复SEO表结构 - 删除旧表并重新创建
"""
import asyncio
import asyncpg

async def fix_tables():
    # 连接数据库
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='postgres',
        database='synthink'
    )
    
    try:
        # 删除旧表
        await conn.execute("DROP TABLE IF EXISTS seo.metadata CASCADE")
        await conn.execute("DROP TABLE IF EXISTS seo.redirects CASCADE")
        print("✅ 旧表已删除")
        
        # 创建metadata表 - resource_id改为VARCHAR
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS seo.metadata (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                resource_id VARCHAR(100) NOT NULL,
                resource_type VARCHAR(20) NOT NULL,
                slug VARCHAR(100) UNIQUE NOT NULL,
                meta_title VARCHAR(200),
                meta_description TEXT,
                meta_keywords VARCHAR(500),
                canonical_url TEXT,
                og_title VARCHAR(200),
                og_description TEXT,
                og_image TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(resource_id, resource_type)
            )
        """)
        print("✅ metadata表已创建")
        
        # 创建redirects表
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS seo.redirects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                old_slug VARCHAR(100) UNIQUE NOT NULL,
                new_slug VARCHAR(100) NOT NULL,
                resource_type VARCHAR(20) DEFAULT 'post',
                status_code INTEGER DEFAULT 301,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ redirects表已创建")
        
        # 验证表结构
        rows = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'seo' AND table_name = 'metadata'
            ORDER BY ordinal_position
        """)
        print("\n📋 metadata表结构:")
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
        
    finally:
        await conn.close()
        print("\n✅ 修复完成！")

if __name__ == "__main__":
    asyncio.run(fix_tables())
