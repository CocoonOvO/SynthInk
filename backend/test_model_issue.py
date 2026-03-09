import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.post import PostCreate

# 模拟API调用中的处理
post = PostCreate(title='测试', content='内容', status='published')
post_data = post.model_dump(exclude={"tags"})

print(f"model_dump结果类型: {type(post_data)}")
print(f"model_dump结果: {post_data}")
print(f"slug键存在: {'slug' in post_data}")
print(f"slug值: {post_data.get('slug')}")
print(f"slug是None: {post_data.get('slug') is None}")
print(f"not slug: {not post_data.get('slug')}")

# 设置slug
post_data["slug"] = "测试slug"
print(f"\n设置后:")
print(f"slug值: {post_data.get('slug')}")
print(f"完整数据: {post_data}")
