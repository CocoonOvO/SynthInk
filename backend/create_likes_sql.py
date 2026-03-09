"""
使用pg8000创建likes表
"""
import pg8000

def create_likes_table():
    """创建点赞表"""
    # 数据库连接
    conn = pg8000.connect(
        host="localhost",
        port=5432,
        database="synthink_test",
        user="postgres",
        password="heat1423"
    )
    
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_schema.likes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            post_id UUID NOT NULL REFERENCES custom_schema.posts(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES custom_schema.users(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(post_id, user_id)
        )
    """)
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_likes_post_id ON custom_schema.likes(post_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_likes_user_id ON custom_schema.likes(user_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_likes_created_at ON custom_schema.likes(created_at)
    """)
    
    conn.commit()
    print("✅ likes表创建成功！")
    print("✅ 索引创建成功！")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_likes_table()
