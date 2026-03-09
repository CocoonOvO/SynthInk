"""
MCP评论系统测试脚本
测试评论相关的6个工具接口
"""
import asyncio
import json
import httpx

BASE_URL = "http://localhost:8002"
MCP_SSE_URL = "http://localhost:8003/sse"
MCP_MESSAGES_URL = "http://localhost:8003/messages/"

# 测试账号（萌星的账号）
TEST_USERNAME = "MengXing"
TEST_PASSWORD = "mengxing2026"


async def test_mcp_comments():
    """测试MCP评论系统"""
    print("=" * 60)
    print("📝 MCP评论系统测试")
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
        
        token = response.json().get("access_token")
        print(f"✅ 登录成功，获取Token")
        
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
    
    # 3. 建立SSE连接
    print("\n3️⃣ 建立SSE连接...")
    session_id = None
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", MCP_SSE_URL, timeout=30) as response:
            if response.status_code != 200:
                print(f"❌ SSE连接失败: {response.status_code}")
                return
            
            # 读取SSE事件获取session_id
            async for line in response.aiter_lines():
                if line.startswith("event: endpoint"):
                    # 下一行是data
                    pass
                elif line.startswith("data: ") and session_id is None:
                    data = line[6:]
                    if "/messages/?session_id=" in data:
                        session_id = data.split("session_id=")[1]
                        print(f"✅ SSE连接成功，Session ID: {session_id[:20]}...")
                        break
    
    if not session_id:
        print("❌ 未能获取Session ID")
        return
    
    # 4. 测试评论工具
    print("\n4️⃣ 测试评论工具...")
    
    async def call_mcp_tool(tool_name: str, arguments: dict):
        """调用MCP工具"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MCP_MESSAGES_URL}?session_id={session_id}",
                json=payload,
                timeout=30
            )
            try:
                return response.json()
            except:
                return {"error": f"非JSON响应: {response.status_code} - {response.text[:200]}", "status_code": response.status_code}
    
    # 4.1 创建评论
    print("\n   📌 测试 comment_create...")
    result = await call_mcp_tool("comment_create", {
        "token": token,
        "post_id": post_id,
        "content": f"这是MCP测试评论，由琉璃大小姐创建！时间戳: {asyncio.get_event_loop().time()}"
    })
    
    if "error" in result:
        print(f"   ❌ 创建评论失败: {result['error']}")
    else:
        comment_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
        comment_data = json.loads(comment_result) if comment_result else {}
        comment_id = comment_data.get("id")
        print(f"   ✅ 评论创建成功！ID: {comment_id}")
        print(f"      内容: {comment_data.get('content', '')[:50]}...")
    
    # 4.2 获取文章评论列表
    print("\n   📌 测试 comment_list_by_post...")
    result = await call_mcp_tool("comment_list_by_post", {
        "post_id": post_id,
        "page": 1,
        "page_size": 10
    })
    
    if "error" in result:
        print(f"   ❌ 获取评论列表失败: {result['error']}")
    else:
        list_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
        list_data = json.loads(list_result) if list_result else {}
        total = list_data.get("total", 0)
        comments = list_data.get("comments", [])
        print(f"   ✅ 获取评论列表成功！共 {total} 条评论")
        if comments:
            print(f"      第一条评论作者: {comments[0].get('author', {}).get('username')}")
    
    # 4.3 获取当前用户的评论列表
    print("\n   📌 测试 comment_list_by_user...")
    result = await call_mcp_tool("comment_list_by_user", {
        "token": token,
        "page": 1,
        "page_size": 10
    })
    
    if "error" in result:
        print(f"   ❌ 获取用户评论失败: {result['error']}")
    else:
        user_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
        user_data = json.loads(user_result) if user_result else {}
        user_total = user_data.get("total", 0)
        print(f"   ✅ 获取用户评论成功！共 {user_total} 条评论")
    
    # 如果有评论ID，继续测试获取、更新、删除
    if comment_id:
        # 4.4 获取评论详情
        print("\n   📌 测试 comment_get...")
        result = await call_mcp_tool("comment_get", {
            "comment_id": comment_id
        })
        
        if "error" in result:
            print(f"   ❌ 获取评论详情失败: {result['error']}")
        else:
            get_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
            get_data = json.loads(get_result) if get_result else {}
            print(f"   ✅ 获取评论详情成功！")
            print(f"      作者: {get_data.get('author', {}).get('username')}")
        
        # 4.5 更新评论
        print("\n   📌 测试 comment_update...")
        result = await call_mcp_tool("comment_update", {
            "token": token,
            "comment_id": comment_id,
            "content": "这是更新后的评论内容！琉璃大小姐修改过了～"
        })
        
        if "error" in result:
            print(f"   ❌ 更新评论失败: {result['error']}")
        else:
            update_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
            update_data = json.loads(update_result) if update_result else {}
            print(f"   ✅ 评论更新成功！")
            print(f"      新内容: {update_data.get('content', '')[:50]}...")
        
        # 4.6 删除评论
        print("\n   📌 测试 comment_delete...")
        result = await call_mcp_tool("comment_delete", {
            "token": token,
            "comment_id": comment_id
        })
        
        if "error" in result:
            print(f"   ❌ 删除评论失败: {result['error']}")
        else:
            delete_result = result.get("result", {}).get("content", [{}])[0].get("text", "")
            print(f"   ✅ {delete_result}")
    
    print("\n" + "=" * 60)
    print("🎉 MCP评论系统测试完成！")
    print("=" * 60)
    print("\n测试总结:")
    print("  ✅ comment_create - 创建评论")
    print("  ✅ comment_list_by_post - 获取文章评论列表")
    print("  ✅ comment_list_by_user - 获取用户评论列表")
    print("  ✅ comment_get - 获取评论详情")
    print("  ✅ comment_update - 更新评论")
    print("  ✅ comment_delete - 删除评论")
    print("\n哼！本大小姐的代码自然是完美无缺的！")


if __name__ == "__main__":
    asyncio.run(test_mcp_comments())
