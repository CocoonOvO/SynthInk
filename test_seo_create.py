"""
测试SEO创建接口，查看详细错误
"""
import requests

BASE_URL = "http://localhost:8002/api"

# 登录
login_r = requests.post(f"{BASE_URL}/auth/token", data={
    "username": "MengXing",
    "password": "mengxing2026"
})
token = login_r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 测试创建SEO元数据
payload = {
    "resource_id": "test-resource-001",
    "resource_type": "post",
    "slug": "test-post-001",
    "meta_title": "测试文章SEO标题",
    "meta_description": "这是一个测试文章的SEO描述",
    "meta_keywords": "测试,SEO,文章",
    "canonical_url": "http://example.com/posts/test-post-001",
    "og_title": "测试文章OG标题",
    "og_description": "这是一个测试文章的OG描述",
    "og_image": "http://example.com/images/test.jpg"
}

print("发送请求:", payload)
response = requests.post(f"{BASE_URL}/seo/metadata", headers=headers, json=payload)
print(f"\n状态码: {response.status_code}")
print(f"响应: {response.text}")
