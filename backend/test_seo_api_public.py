"""
SEO API公开接口测试（无需登录）
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8002"

async def test_public_seo_apis():
    """测试公开的SEO API"""
    print("=" * 60)
    print("🚀 SEO公开API测试开始")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # 1. 获取SEO元数据列表
        print("\n[1/5] 获取SEO元数据列表...")
        response = await client.get(f"{BASE_URL}/api/seo/metadata")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ 成功！获取到 {len(items)} 条元数据")
            for item in items[:3]:
                print(f"   📄 {item['slug']}: {item['meta_title'][:40]}...")
        else:
            print(f"❌ 失败: {response.text[:200]}")
        
        # 2. 获取单个元数据
        print("\n[2/5] 获取单个SEO元数据 (python-tutorial)...")
        response = await client.get(f"{BASE_URL}/api/seo/metadata/python-tutorial")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！")
            print(f"   📄 Slug: {data['slug']}")
            print(f"   📝 标题: {data['meta_title']}")
            print(f"   📋 描述: {data['meta_description'][:60]}...")
            print(f"   🏷️  关键词: {data['meta_keywords']}")
        else:
            print(f"❌ 失败: {response.text[:200]}")
        
        # 3. 获取重定向列表
        print("\n[3/5] 获取重定向规则列表...")
        response = await client.get(f"{BASE_URL}/api/seo/redirects")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            print(f"✅ 成功！获取到 {len(items)} 条重定向规则")
            for item in items:
                print(f"   🔄 {item['old_slug']} → {item['new_slug']} (301, {item['hit_count']}次)")
        else:
            print(f"❌ 失败: {response.text[:200]}")
        
        # 4. 获取单个重定向
        print("\n[4/5] 获取单个重定向规则 (old-python-tutorial)...")
        response = await client.get(f"{BASE_URL}/api/seo/redirects/old-python-tutorial")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！")
            print(f"   🔄 {data['old_slug']} → {data['new_slug']}")
            print(f"   📊 类型: {data['redirect_type']}, 点击: {data['hit_count']}次")
        else:
            print(f"❌ 失败: {response.text[:200]}")
        
        # 5. 获取SEO统计
        print("\n[5/5] 获取SEO统计信息...")
        response = await client.get(f"{BASE_URL}/api/seo/stats")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！")
            print(f"   📊 元数据总数: {data.get('metadata_count', 0)}")
            print(f"   🔄 重定向总数: {data.get('redirect_count', 0)}")
            print(f"   👆 总重定向次数: {data.get('total_hits', 0)}")
        else:
            print(f"❌ 失败: {response.text[:200]}")
    
    print("\n" + "=" * 60)
    print("✅ SEO公开API测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_public_seo_apis())
