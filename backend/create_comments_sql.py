"""
使用pg8000创建comments表
"""
import pg8000

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
    CREATE TABLE IF NOT EXISTS custom_schema.comments (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        post_id UUID NOT NULL REFERENCES custom_schema.posts(id) ON DELETE CASCADE,
        author_id UUID NOT NULL REFERENCES custom_schema.users(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        parent_id UUID REFERENCES custom_schema.comments(id) ON DELETE CASCADE,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
""")

# 创建索引
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_comments_post_id ON custom_schema.comments(post_id)
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_comments_author_id ON custom_schema.comments(author_id)
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON custom_schema.comments(parent_id)
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_comments_is_deleted ON custom_schema.comments(is_deleted)
""")

conn.commit()
print("✅ comments表创建成功！")
print("✅ 索引创建成功！")

cursor.close()
conn.close()
