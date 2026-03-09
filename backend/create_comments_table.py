"""
创建comments表的脚本
"""
import asyncio
import asyncpg
import os

# 数据库连接信息
DSN = "postgresql://postgres:heat1423@localhost:5432/synthink"
SCHEMA = "custom_schema"


async def create_comments_table():
    """创建comments表"""
    import ssl
    
    # 禁用SSL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    conn = await asyncpg.connect(DSN, ssl=False)
    
    try:
        # 设置schema
        await conn.execute(f'SET search_path TO {SCHEMA}')
        
        # 创建表
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {SCHEMA}.comments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id UUID NOT NULL REFERENCES {SCHEMA}.posts(id) ON DELETE CASCADE,
                author_id UUID NOT NULL REFERENCES {SCHEMA}.users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                parent_id UUID REFERENCES {SCHEMA}.comments(id) ON DELETE CASCADE,
                is_deleted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_comments_post_id ON {SCHEMA}.comments(post_id)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_comments_author_id ON {SCHEMA}.comments(author_id)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON {SCHEMA}.comments(parent_id)
        """)
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_comments_is_deleted ON {SCHEMA}.comments(is_deleted)
        """)
        
        print("✅ comments表创建成功！")
        print("✅ 索引创建成功！")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_comments_table())
