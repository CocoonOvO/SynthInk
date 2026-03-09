"""
SEO Schema 初始化脚本

在业务库中创建seo schema并初始化相关表结构
"""
import asyncio
import asyncpg


async def init_seo_schema():
    """初始化SEO schema和表"""
    # 数据库连接信息
    dsn = "postgresql://postgres:heat1423@localhost:5432/synthink_test"
    schema = "seo"
    
    print(f"[SEO初始化] 连接到数据库...")
    conn = await asyncpg.connect(dsn)
    
    try:
        # 1. 创建schema
        print(f"[SEO初始化] 创建schema: {schema}")
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"[SEO初始化] Schema '{schema}' 创建成功或已存在")
        
        # 2. 创建metadata表
        print(f"[SEO初始化] 创建metadata表...")
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.metadata (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                resource_id UUID NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                slug VARCHAR(200) NOT NULL UNIQUE,
                meta_title VARCHAR(100),
                meta_description VARCHAR(300),
                meta_keywords VARCHAR(500),
                canonical_url VARCHAR(500),
                og_title VARCHAR(100),
                og_description VARCHAR(300),
                og_image VARCHAR(500),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print(f"[SEO初始化] metadata表创建成功")
        
        # 3. 创建redirects表
        print(f"[SEO初始化] 创建redirects表...")
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.redirects (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                old_slug VARCHAR(200) NOT NULL UNIQUE,
                new_slug VARCHAR(200) NOT NULL,
                redirect_type INTEGER DEFAULT 301,
                hit_count INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print(f"[SEO初始化] redirects表创建成功")
        
        # 4. 创建索引
        print(f"[SEO初始化] 创建索引...")
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_metadata_resource_id 
            ON {schema}.metadata(resource_id)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_metadata_resource_type 
            ON {schema}.metadata(resource_type)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_metadata_slug 
            ON {schema}.metadata(slug)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_redirects_old_slug 
            ON {schema}.redirects(old_slug)
        """)
        print(f"[SEO初始化] 索引创建成功")
        
        # 5. 验证表是否存在
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = $1
        """, schema)
        print(f"[SEO初始化] Schema '{schema}' 中的表: {[t['table_name'] for t in tables]}")
        
        print(f"\n[SEO初始化] ✓ 所有初始化操作完成!")
        
    except Exception as e:
        print(f"[SEO初始化] ✗ 错误: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_seo_schema())
