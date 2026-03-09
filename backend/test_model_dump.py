import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.post import PostCreate

# 模拟创建文章
post = PostCreate(title='测试文章标题', content='测试内容', status='published')
post_data = post.model_dump(exclude={"tags"})

print(f'post_data: {post_data}')
print(f'slug in post_data: {"slug" in post_data}')
print(f'post_data["slug"]: {post_data.get("slug")}')
print(f'not post_data.get("slug"): {not post_data.get("slug")}')

# 模拟设置slug
if not post_data.get("slug"):
    post_data["slug"] = "测试文章标题"
    print(f'设置后的slug: {post_data["slug"]}')
