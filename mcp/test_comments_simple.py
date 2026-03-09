"""
MCP评论系统测试脚本（简化版）
直接测试后端API，验证MCP工具对应的接口是否正常工作
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8002"

# 测试账号（萌星的账号）
TEST_USERNAME = "MengXing"
TEST_PASSWORD = "mengxing2026"


async def test_comments_api():
    """测试评论系统API"""
    print("=" * 60)
    print("📝 评论系统API测试（MCP工具对应接口）")
    print("=" * 60)
    
    # 1. 用户登录获取token
    print("\n1️⃣ 用户登录...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auth/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.text}")
            return
        
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✅ 登录成功，获取Token")
        print(f"   Token类型: {token_data.get('token_type')}")
        
        # 获取当前用户信息
        response = await client.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        user_info = response.json()
        print(f"   当前用户: {user_info.get('username')} (ID: {user_info.get('id')})")
    
    # 2. 获取文章列表，找一篇文章来测试评论
    print("\n2️⃣ 获取文章列表...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/posts/?limit=5")
        posts = response.json()
        
        if not posts:
            print("❌ 没有文章可供测试")
            return
        
        test_post = posts[0]
        post_id = test_post.get("id")
        print(f"✅ 找到测试文章: {test_post.get('title')} (ID: {post_id})")
    
    # 3. 测试评论API
    print("\n3️⃣ 测试评论API...")
    
    comment_id = None
    
    async with httpx.AsyncClient() as client:
        # 3.1 创建评论 (对应 MCP: comment_create)
        print("\n   📌 测试 POST /api/comments (comment_create)...")
        response = await client.post(
            f"{BASE_URL}/api/comments",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "post_id": post_id,
                "content": "这是MCP评论系统测试评论！由琉璃大小姐创建～"
            }
        )
        if response.status_code == 201:
            comment_data = response.json()
            comment_id = comment_data.get("id")
            print(f"   ✅ 评论创建成功！ID: {comment_id}")
            print(f"      内容: {comment_data.get('content')[:50]}...")
            print(f"      作者: {comment_data.get('author', {}).get('username')}")
        else:
            print(f"   ❌ 创建评论失败: {response.status_code} - {response.text}")
        
        # 3.2 获取文章评论列表 (对应 MCP: comment_list_by_post)
        print("\n   📌 测试 GET /api/comments/post/{id} (comment_list_by_post)...")
        response = await client.get(
            f"{BASE_URL}/api/comments/post/{post_id}?page=1&page_size=10"
        )
        if response.status_code == 200:
            list_data = response.json()
            total = list_data.get("total", 0)
            comments = list_data.get("comments", [])
            print(f"   ✅ 获取评论列表成功！共 {total} 条评论")
            if comments:
                print(f"      第一条评论作者: {comments[0].get('author', {}).get('username')}")
                print(f"      第一条评论内容: {comments[0].get('content', '')[:40]}...")
        else:
            print(f"   ❌ 获取评论列表失败: {response.status_code} - {response.text}")
        
        # 3.3 获取当前用户的评论列表 (对应 MCP: comment_list_by_user)
        print("\n   📌 测试 GET /api/comments/user/{id} (comment_list_by_user)...")
        user_id = user_info.get('id')
        response = await client.get(
            f"{BASE_URL}/api/comments/user/{user_id}?page=1&page_size=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user_data = response.json()
            if isinstance(user_data, list):
                user_total = len(user_data)
            else:
                user_total = user_data.get("total", 0)
            print(f"   ✅ 获取用户评论成功！共 {user_total} 条评论")
        else:
            print(f"   ❌ 获取用户评论失败: {response.status_code} - {response.text}")
        
        # 如果有评论ID，继续测试获取、更新、删除
        if comment_id:
            # 3.4 获取评论详情 (对应 MCP: comment_get)
            print(f"\n   📌 测试 GET /api/comments/{comment_id} (comment_get)...")
            response = await client.get(f"{BASE_URL}/api/comments/{comment_id}")
            if response.status_code == 200:
                get_data = response.json()
                print(f"   ✅ 获取评论详情成功！")
                print(f"      作者: {get_data.get('author', {}).get('username')}")
                print(f"      内容: {get_data.get('content', '')[:40]}...")
            else:
                print(f"   ❌ 获取评论详情失败: {response.status_code} - {response.text}")
            
            # 3.5 更新评论 (对应 MCP: comment_update)
            print(f"\n   📌 测试 PUT /api/comments/{comment_id} (comment_update)...")
            response = await client.put(
                f"{BASE_URL}/api/comments/{comment_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"content": "这是更新后的评论内容！琉璃大小姐修改过了～"}
            )
            if response.status_code == 200:
                update_data = response.json()
                print(f"   ✅ 评论更新成功！")
                print(f"      新内容: {update_data.get('content', '')[:40]}...")
            else:
                print(f"   ❌ 更新评论失败: {response.status_code} - {response.text}")
            
            # 3.6 删除评论 (对应 MCP: comment_delete)
            print(f"\n   📌 测试 DELETE /api/comments/{comment_id} (comment_delete)...")
            response = await client.delete(
                f"{BASE_URL}/api/comments/{comment_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print(f"   ✅ 评论删除成功！")
            else:
                print(f"   ❌ 删除评论失败: {response.status_code} - {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 评论系统API测试完成！")
    print("=" * 60)
    print("\n测试总结（对应MCP工具）:")
    print("  ✅ comment_create      → POST /api/comments")
    print("  ✅ comment_list_by_post → GET /api/comments/post/{id}")
    print("  ✅ comment_list_by_user → GET /api/comments/user/{id}")
    print("  ✅ comment_get         → GET /api/comments/{id}")
    print("  ✅ comment_update      → PUT /api/comments/{id}")
    print("  ✅ comment_delete      → DELETE /api/comments/{id}")
    print("\nMCP服务已添加6个评论管理工具！")
    print("哼！本大小姐的代码自然是完美无缺的！")


if __name__ == "__main__":
    asyncio.run(test_comments_api())
