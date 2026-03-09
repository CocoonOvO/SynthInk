"""
SEO数据库集成测试

测试SEO系统与PostgreSQL数据库的连接
验证schema、表结构和基本CRUD操作
"""
import asyncio
import asyncpg
from datetime import datetime
import uuid


async def test_seo_db_integration():
    """测试SEO数据库集成"""
    # 数据库连接信息
    dsn = "postgresql://postgres:heat1423@localhost:5432/synthink_test"
    schema = "seo"
    
    print(f"[SEO集成测试] 连接到数据库...")
    conn = await asyncpg.connect(dsn)
    
    try:
        # 1. 验证schema存在
        print(f"[SEO集成测试] 验证schema存在...")
        schema_exists = await conn.fetchval(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = $1",
            schema
        )
        assert schema_exists is not None, f"Schema '{schema}' 不存在"
        print(f"[SEO集成测试] ✓ Schema '{schema}' 存在")
        
        # 2. 验证表存在
        print(f"[SEO集成测试] 验证表存在...")
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = $1",
            schema
        )
        table_names = [t['table_name'] for t in tables]
        assert 'metadata' in table_names, "metadata表不存在"
        assert 'redirects' in table_names, "redirects表不存在"
        print(f"[SEO集成测试] ✓ 表存在: {table_names}")
        
        # 3. 测试metadata表CRUD
        print(f"[SEO集成测试] 测试metadata表CRUD...")
        test_slug = f"test-post-{uuid.uuid4().hex[:8]}"
        test_resource_id = str(uuid.uuid4())
        
        # 创建
        insert_result = await conn.fetchrow(f"""
            INSERT INTO {schema}.metadata 
            (resource_id, resource_type, slug, meta_title, meta_description, meta_keywords)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """, test_resource_id, 'post', test_slug, 'Test Title', 'Test Description', 'test, keywords')
        metadata_id = insert_result['id']
        print(f"[SEO集成测试] ✓ 创建metadata记录: {metadata_id}")
        
        # 读取
        read_result = await conn.fetchrow(f"""
            SELECT * FROM {schema}.metadata WHERE slug = $1
        """, test_slug)
        assert read_result is not None, "读取失败"
        assert read_result['meta_title'] == 'Test Title'
        print(f"[SEO集成测试] ✓ 读取metadata记录成功")
        
        # 更新
        await conn.execute(f"""
            UPDATE {schema}.metadata 
            SET meta_title = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, 'Updated Title', metadata_id)
        updated = await conn.fetchrow(f"""
            SELECT meta_title FROM {schema}.metadata WHERE id = $1
        """, metadata_id)
        assert updated['meta_title'] == 'Updated Title'
        print(f"[SEO集成测试] ✓ 更新metadata记录成功")
        
        # 4. 测试redirects表CRUD
        print(f"[SEO集成测试] 测试redirects表CRUD...")
        test_old_slug = f"old-slug-{uuid.uuid4().hex[:8]}"
        test_new_slug = f"new-slug-{uuid.uuid4().hex[:8]}"
        
        # 创建
        redirect_result = await conn.fetchrow(f"""
            INSERT INTO {schema}.redirects (old_slug, new_slug, redirect_type)
            VALUES ($1, $2, $3)
            RETURNING id
        """, test_old_slug, test_new_slug, 301)
        redirect_id = redirect_result['id']
        print(f"[SEO集成测试] ✓ 创建redirect记录: {redirect_id}")
        
        # 读取
        redirect_read = await conn.fetchrow(f"""
            SELECT * FROM {schema}.redirects WHERE old_slug = $1
        """, test_old_slug)
        assert redirect_read is not None
        assert redirect_read['new_slug'] == test_new_slug
        print(f"[SEO集成测试] ✓ 读取redirect记录成功")
        
        # 更新hit_count
        await conn.execute(f"""
            UPDATE {schema}.redirects 
            SET hit_count = hit_count + 1
            WHERE id = $1
        """, redirect_id)
        redirect_updated = await conn.fetchrow(f"""
            SELECT hit_count FROM {schema}.redirects WHERE id = $1
        """, redirect_id)
        assert redirect_updated['hit_count'] == 1
        print(f"[SEO集成测试] ✓ 更新redirect hit_count成功")
        
        # 5. 清理测试数据
        print(f"[SEO集成测试] 清理测试数据...")
        await conn.execute(f"DELETE FROM {schema}.metadata WHERE id = $1", metadata_id)
        await conn.execute(f"DELETE FROM {schema}.redirects WHERE id = $1", redirect_id)
        print(f"[SEO集成测试] ✓ 清理完成")
        
        print(f"\n[SEO集成测试] ✓✓✓ 所有测试通过! ✓✓✓")
        return True
        
    except Exception as e:
        print(f"[SEO集成测试] ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await conn.close()


if __name__ == "__main__":
    success = asyncio.run(test_seo_db_integration())
    exit(0 if success else 1)
