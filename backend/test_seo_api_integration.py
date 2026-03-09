"""
SEO API集成测试
测试所有SEO接口的完整流程
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8002"

# 测试账号（使用已有的测试账号）
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

async def get_access_token() -> str:
    """获取访问令牌"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None

async def test_seo_api_flow():
    """测试SEO API完整流程"""
    print("=" * 60)
    print("🚀 SEO API集成测试开始")
    print("=" * 60)
    
    # 1. 获取token
    print("\n[1/8] 获取访问令牌...")
    token = await get_access_token()
    if not token:
        print("❌ 无法获取token，测试终止")
        return False
    print("✅ 获取token成功")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # 2. 获取现有元数据列表
        print("\n[2/8] 获取SEO元数据列表...")
        response = await client.get(f"{BASE_URL}/api/seo/metadata")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {len(data.get('items', []))} 条元数据")
            for item in data.get('items', [])[:3]:
                print(f"   - {item['slug']}: {item['meta_title'][:30]}...")
        else:
            print(f"❌ 获取失败: {response.status_code} - {response.text}")
        
        # 3. 创建新的SEO元数据
        print("\n[3/8] 创建新的SEO元数据...")
        new_metadata = {
            "resource_id": "test-resource-001",
            "resource_type": "post",
            "slug": f"test-article-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "meta_title": "测试文章 - SEO集成测试",
            "meta_description": "这是一篇用于SEO集成测试的文章，验证API功能是否正常。",
            "meta_keywords": "测试,SEO,API,集成",
            "canonical_url": "https://synthink.com/posts/test-article",
            "og_title": "测试文章",
            "og_description": "SEO集成测试文章",
            "og_image": "https://synthink.com/images/test.png"
        }
        response = await client.post(
            f"{BASE_URL}/api/seo/metadata",
            json=new_metadata,
            headers=headers
        )
        if response.status_code == 201:
            created_id = response.json().get("id")
            print(f"✅ 创建成功，ID: {created_id}")
        else:
            print(f"❌ 创建失败: {response.status_code} - {response.text}")
            created_id = None
        
        # 4. 获取刚创建的元数据
        if created_id:
            print(f"\n[4/8] 获取刚创建的元数据...")
            response = await client.get(f"{BASE_URL}/api/seo/metadata/{new_metadata['slug']}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取成功: {data['slug']}")
                print(f"   标题: {data['meta_title']}")
                print(f"   描述: {data['meta_description'][:50]}...")
            else:
                print(f"❌ 获取失败: {response.status_code}")
        
        # 5. 更新元数据
        if created_id:
            print(f"\n[5/8] 更新SEO元数据...")
            update_data = {
                "meta_title": "更新后的标题 - SEO测试",
                "meta_description": "这是更新后的描述，用于验证更新接口。",
                "meta_keywords": "更新,测试,SEO"
            }
            response = await client.put(
                f"{BASE_URL}/api/seo/metadata/{new_metadata['slug']}",
                json=update_data,
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ 更新成功")
            else:
                print(f"❌ 更新失败: {response.status_code} - {response.text}")
        
        # 6. 获取重定向列表
        print("\n[6/8] 获取重定向规则列表...")
        response = await client.get(f"{BASE_URL}/api/seo/redirects")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取到 {len(data.get('items', []))} 条重定向规则")
            for item in data.get('items', [])[:3]:
                print(f"   - {item['old_slug']} → {item['new_slug']} ({item['hit_count']}次)")
        else:
            print(f"❌ 获取失败: {response.status_code}")
        
        # 7. 创建新的重定向规则
        print("\n[7/8] 创建新的重定向规则...")
        new_redirect = {
            "old_slug": f"old-test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "new_slug": new_metadata['slug'],
            "redirect_type": 301
        }
        response = await client.post(
            f"{BASE_URL}/api/seo/redirects",
            json=new_redirect,
            headers=headers
        )
        if response.status_code == 201:
            print(f"✅ 重定向创建成功: {new_redirect['old_slug']} → {new_redirect['new_slug']}")
        else:
            print(f"❌ 创建失败: {response.status_code} - {response.text}")
        
        # 8. 获取SEO统计
        print("\n[8/8] 获取SEO统计信息...")
        response = await client.get(f"{BASE_URL}/api/seo/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 统计信息:")
            print(f"   - 元数据总数: {data.get('metadata_count', 0)}")
            print(f"   - 重定向总数: {data.get('redirect_count', 0)}")
            print(f"   - 总重定向次数: {data.get('total_hits', 0)}")
        else:
            print(f"❌ 获取失败: {response.status_code}")
        
        # 清理：删除测试数据
        print("\n[清理] 删除测试数据...")
        if created_id:
            response = await client.delete(
                f"{BASE_URL}/api/seo/metadata/{new_metadata['slug']}",
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ 测试元数据已删除")
            else:
                print(f"⚠️ 删除失败: {response.status_code}")
        
        # 删除测试重定向
        response = await client.delete(
            f"{BASE_URL}/api/seo/redirects/{new_redirect['old_slug']}",
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ 测试重定向已删除")
        else:
            print(f"⚠️ 删除失败: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ SEO API集成测试完成！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    asyncio.run(test_seo_api_flow())
