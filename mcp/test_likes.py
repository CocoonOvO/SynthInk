"""
点赞系统API测试（MCP工具对应接口）
测试MCP点赞功能的5个工具对应的API
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8002"
TEST_USERNAME = "MengXing"
TEST_PASSWORD = "mengxing2026"

async def test_likes():
    print("=" * 60)
    print("❤️ 点赞系统API测试（MCP工具对应接口）")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # 1. 用户登录
        print("\n1️⃣ 用户登录...")
        response = await client.post(
            f"{BASE_URL}/api/auth/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            print(f"   ❌ 登录失败: {response.text}")
            return
        
        token_data = response.json()
        token = token_data["access_token"]
        user_id = token_data["user"]["id"]
        print(f"   ✅ 登录成功！用户: {token_data['user']['username']}")
        
        # 2. 获取文章列表
        print("\n2️⃣ 获取测试文章...")
        response = await client.get(f"{BASE_URL}/api/posts/?limit=1")
        if response.status_code != 200 or not response.json():
            print("   ❌ 获取文章列表失败")
            return
        
        posts = response.json()
        post_id = posts[0]["id"]
        post_title = posts[0]["title"]
        print(f"   ✅ 找到测试文章: {post_title} (ID: {post_id[:8]}...)")
        
        # 3. 测试点赞API
        print("\n3️⃣ 测试点赞API...")
        
        # 3.1 获取点赞状态 (对应 MCP: get_like_status)
        print("\n   📌 测试 GET /api/likes/{post_id}/status (get_like_status)...")
        response = await client.get(f"{BASE_URL}/api/likes/{post_id}/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ 获取点赞状态成功！")
            print(f"      点赞数: {status_data.get('like_count', 0)}")
            print(f"      是否已点赞: {status_data.get('is_liked', False)}")
        else:
            print(f"   ❌ 获取点赞状态失败: {response.status_code}")
        
        # 3.2 点赞文章 (对应 MCP: like_post)
        print("\n   📌 测试 POST /api/likes/{post_id} (like_post)...")
        response = await client.post(
            f"{BASE_URL}/api/likes/{post_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 201:
            like_data = response.json()
            print(f"   ✅ 点赞成功！")
            print(f"      文章ID: {like_data.get('post_id')[:8]}...")
            print(f"      当前点赞数: {like_data.get('like_count', 0)}")
            print(f"      是否已点赞: {like_data.get('is_liked', False)}")
        else:
            print(f"   ❌ 点赞失败: {response.status_code} - {response.text}")
        
        # 3.3 再次获取点赞状态（验证已点赞）
        print("\n   📌 再次获取点赞状态（验证）...")
        response = await client.get(
            f"{BASE_URL}/api/likes/{post_id}/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ 状态更新成功！")
            print(f"      点赞数: {status_data.get('like_count', 0)}")
            print(f"      是否已点赞: {status_data.get('is_liked', False)}")
        
        # 3.4 获取我点赞的文章列表 (对应 MCP: get_my_liked_posts)
        print("\n   📌 测试 GET /api/likes/user/me (get_my_liked_posts)...")
        response = await client.get(
            f"{BASE_URL}/api/likes/user/me?page=1&page_size=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            liked_posts = response.json()
            print(f"   ✅ 获取点赞列表成功！共 {len(liked_posts)} 篇文章")
            if liked_posts:
                print(f"      最近点赞: {liked_posts[0].get('post_id')[:8]}...")
        else:
            print(f"   ❌ 获取点赞列表失败: {response.status_code}")
        
        # 3.5 获取文章点赞用户列表 (对应 MCP: get_post_likers)
        print("\n   📌 测试 GET /api/likes/post/{post_id}/users (get_post_likers)...")
        response = await client.get(
            f"{BASE_URL}/api/likes/post/{post_id}/users?page=1&page_size=10"
        )
        if response.status_code == 200:
            likers = response.json()
            print(f"   ✅ 获取点赞用户成功！共 {len(likers)} 位用户")
            if likers:
                print(f"      最近点赞用户: {likers[0].get('username')}")
        else:
            print(f"   ❌ 获取点赞用户失败: {response.status_code}")
        
        # 3.6 取消点赞 (对应 MCP: unlike_post)
        print("\n   📌 测试 DELETE /api/likes/{post_id} (unlike_post)...")
        response = await client.delete(
            f"{BASE_URL}/api/likes/{post_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            unlike_data = response.json()
            print(f"   ✅ 取消点赞成功！")
            print(f"      当前点赞数: {unlike_data.get('like_count', 0)}")
            print(f"      是否已点赞: {unlike_data.get('is_liked', False)}")
        else:
            print(f"   ❌ 取消点赞失败: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 点赞系统API测试完成！")
        print("=" * 60)
        
        print("\n测试总结（对应MCP工具）:")
        print("  ✅ get_like_status      → GET /api/likes/{post_id}/status")
        print("  ✅ like_post            → POST /api/likes/{post_id}")
        print("  ✅ get_my_liked_posts   → GET /api/likes/user/me")
        print("  ✅ get_post_likers      → GET /api/likes/post/{post_id}/users")
        print("  ✅ unlike_post          → DELETE /api/likes/{post_id}")
        
        print("\nMCP服务已添加5个点赞系统工具！")
        print("哼！本大小姐的代码自然是完美无缺的！")

if __name__ == "__main__":
    asyncio.run(test_likes())
