"""
数据库迁移脚本：支持匿名点赞和性能优化
- 修改 likes 表结构，支持匿名点赞
- 添加 posts.like_count 缓存字段
- 创建必要的索引
"""
import asyncio
import asyncpg
import os
import sys
import sqlite3

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def migrate():
    """执行数据库迁移"""
    print("🚀 开始数据库迁移...")
    
    # 从配置库读取数据库连接信息
    config_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.db")
    
    if not os.path.exists(config_db_path):
        print(f"❌ 配置库不存在: {config_db_path}")
        return
    
    conn_sqlite = sqlite3.connect(config_db_path)
    cursor = conn_sqlite.cursor()
    
    # 获取数据库配置 - 使用正确的字段名
    cursor.execute("SELECT schema, database, host, port, username, password FROM database_configs WHERE is_active = 1 LIMIT 1")
    row = cursor.fetchone()
    conn_sqlite.close()
    
    if not row:
        print("❌ 未找到活跃的数据库配置")
        return
    
    schema, db_name, host, port, user, password = row
    
    # 构建DSN
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    print(f"📡 连接到数据库: {db_name}, schema={schema}")
    
    # 建立连接
    conn = await asyncpg.connect(dsn)
    
    try:
        # 设置搜索路径
        await conn.execute(f'SET search_path TO {schema}')
        
        # 1. 检查并添加 posts.like_count 字段
        print("\n1️⃣ 添加 posts.like_count 字段...")
        await conn.execute(f"""
            ALTER TABLE {schema}.posts 
            ADD COLUMN IF NOT EXISTS like_count INTEGER DEFAULT 0
        """)
        print("   ✅ like_count 字段已添加")
        
        # 2. 初始化 like_count（统计现有点赞数）
        print("\n2️⃣ 初始化 like_count 数据...")
        await conn.execute(f"""
            UPDATE {schema}.posts p 
            SET like_count = COALESCE((
                SELECT COUNT(*) 
                FROM {schema}.likes l 
                WHERE l.post_id = p.id
            ), 0)
        """)
        print("   ✅ like_count 数据已初始化")
        
        # 3. 修改 likes 表结构
        print("\n3️⃣ 修改 likes 表结构...")
        
        # 添加匿名token字段
        await conn.execute(f"""
            ALTER TABLE {schema}.likes 
            ADD COLUMN IF NOT EXISTS anonymous_token VARCHAR(64)
        """)
        print("   ✅ anonymous_token 字段已添加")
        
        # 添加点赞类型字段
        await conn.execute(f"""
            ALTER TABLE {schema}.likes 
            ADD COLUMN IF NOT EXISTS like_type VARCHAR(10) DEFAULT 'user'
        """)
        print("   ✅ like_type 字段已添加")
        
        # 添加IP地址字段
        await conn.execute(f"""
            ALTER TABLE {schema}.likes 
            ADD COLUMN IF NOT EXISTS ip_address INET
        """)
        print("   ✅ ip_address 字段已添加")
        
        # 修改 user_id 允许为空
        await conn.execute(f"""
            ALTER TABLE {schema}.likes 
            ALTER COLUMN user_id DROP NOT NULL
        """)
        print("   ✅ user_id 已允许为空")
        
        # 4. 创建索引
        print("\n4️⃣ 创建索引...")
        
        # 删除旧的唯一约束（如果存在）
        try:
            await conn.execute(f"""
                ALTER TABLE {schema}.likes 
                DROP CONSTRAINT IF EXISTS likes_post_id_user_id_key
            """)
            print("   ✅ 旧约束已删除")
        except:
            pass
        
        # 创建部分唯一索引：登录用户
        await conn.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_likes_post_user 
            ON {schema}.likes (post_id, user_id) 
            WHERE user_id IS NOT NULL
        """)
        print("   ✅ idx_likes_post_user 索引已创建")
        
        # 创建部分唯一索引：匿名用户
        await conn.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_likes_post_anonymous 
            ON {schema}.likes (post_id, anonymous_token) 
            WHERE anonymous_token IS NOT NULL
        """)
        print("   ✅ idx_likes_post_anonymous 索引已创建")
        
        # 创建IP地址索引（用于防刷查询）
        await conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_likes_ip_created 
            ON {schema}.likes (ip_address, created_at) 
            WHERE anonymous_token IS NOT NULL
        """)
        print("   ✅ idx_likes_ip_created 索引已创建")
        
        # 5. 更新现有数据的 like_type
        print("\n5️⃣ 更新现有数据...")
        await conn.execute(f"""
            UPDATE {schema}.likes 
            SET like_type = 'user' 
            WHERE user_id IS NOT NULL AND (like_type IS NULL OR like_type = '')
        """)
        print("   ✅ 现有数据已更新")
        
        print("\n✨ 数据库迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())
