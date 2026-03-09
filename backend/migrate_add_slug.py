"""
数据库迁移脚本：为posts表添加slug字段并为已有文章生成slug

执行方式:
    cd backend
    python migrate_add_slug.py

功能:
    1. 为posts表添加slug字段（如果不存在）
    2. 为所有没有slug的文章生成slug
    3. 添加唯一索引
"""

import asyncio
import sys
from pathlib import Path

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.adapter.postgres_adapter import PostgresAdapter
from app.utils.slug import generate_slug


async def migrate_add_slug():
    """执行slug迁移"""
    print("🚀 开始执行slug字段迁移...")
    
    # 直接创建适配器连接
    dsn = "postgresql://postgres:heat1423@localhost:5432/synthink_test"
    adapter = PostgresAdapter(dsn=dsn, schema="custom_schema")
    await adapter.connect()
    
    try:
        # 1. 检查并添加slug字段
        print("\n📋 步骤1: 检查并添加slug字段...")
        
        # 检查slug字段是否存在
        check_result = await adapter._fetch(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = '{adapter.schema}' 
            AND table_name = 'posts' 
            AND column_name = 'slug'
            """
        )
        
        if not check_result:
            print("   添加slug字段...")
            await adapter._execute(
                f"ALTER TABLE {adapter.schema}.posts ADD COLUMN slug VARCHAR(100)"
            )
            print("   ✅ slug字段添加成功")
        else:
            print("   ℹ️ slug字段已存在，跳过")
        
        # 2. 为已有文章生成slug
        print("\n📋 步骤2: 为已有文章生成slug...")
        
        # 获取所有没有slug的文章
        posts_result = await adapter._fetch(
            f"""
            SELECT id, title, slug 
            FROM {adapter.schema}.posts 
            WHERE slug IS NULL OR slug = ''
            ORDER BY created_at
            """
        )
        
        if not posts_result:
            print("   ℹ️ 所有文章已有slug，跳过")
        else:
            print(f"   发现 {len(posts_result)} 篇需要生成slug的文章")
            
            # 获取所有已存在的slug
            existing_slugs_result = await adapter._fetch(
                f"SELECT slug FROM {adapter.schema}.posts WHERE slug IS NOT NULL AND slug != ''"
            )
            existing_slugs = [row['slug'] for row in existing_slugs_result if row['slug']]
            
            # 为每篇文章生成slug
            updated_count = 0
            for post in posts_result:
                post_id = post['id']
                title = post['title']
                
                # 生成唯一slug
                slug = generate_slug(title, existing_slugs)
                existing_slugs.append(slug)
                
                # 更新文章
                await adapter._execute(
                    f"UPDATE {adapter.schema}.posts SET slug = $1 WHERE id = $2",
                    slug, post_id
                )
                
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"   已处理 {updated_count}/{len(posts_result)} 篇文章...")
            
            print(f"   ✅ 已为 {updated_count} 篇文章生成slug")
        
        # 3. 添加唯一索引
        print("\n📋 步骤3: 添加唯一索引...")
        
        # 检查唯一索引是否存在
        index_result = await adapter._fetch(
            f"""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'posts' 
            AND schemaname = '{adapter.schema}'
            AND indexname = 'idx_posts_slug_unique'
            """
        )
        
        if not index_result:
            print("   创建唯一索引...")
            await adapter._execute(
                f"""
                CREATE UNIQUE INDEX idx_posts_slug_unique 
                ON {adapter.schema}.posts(slug) 
                WHERE slug IS NOT NULL
                """
            )
            print("   ✅ 唯一索引创建成功")
        else:
            print("   ℹ️ 唯一索引已存在，跳过")
        
        print("\n✨ 迁移完成！所有文章现在都有slug了~")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await adapter.disconnect()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(migrate_add_slug())
    sys.exit(exit_code)
