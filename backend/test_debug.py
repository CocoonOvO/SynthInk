from app.models.post import PostCreate

# 测试PostCreate
post = PostCreate(title='测试', content='内容', status='published')
data = post.model_dump(exclude={'tags'})
print(f'post_data: {data}')
print(f'slug value: {data.get("slug")}')
print(f'not slug: {not data.get("slug")}')
