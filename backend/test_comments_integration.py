"""
评论功能集成测试
测试评论API并写入测试数据
"""
import asyncio
import httpx
import sys
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8002"


class CommentTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.headers = {}
        self.test_results = []
        self.test_user_id = None
        self.test_post_id = None
        self.created_comments = []
        
    async def close(self):
        await self.client.aclose()
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "📝", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        print(f"{prefix} [{timestamp}] {message}")
        self.test_results.append({"time": timestamp, "level": level, "message": message})
    
    async def test_health(self):
        """测试服务健康状态"""
        self.log("测试服务健康状态...")
        try:
            response = await self.client.get("/api/docs")
            if response.status_code == 200:
                self.log("服务运行正常!", "SUCCESS")
                return True
            else:
                self.log(f"服务异常: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"连接失败: {e}", "ERROR")
            return False
    
    async def test_login(self, username, password):
        """测试用户登录"""
        self.log(f"登录用户: {username}...")
        try:
            response = await self.client.post(
                "/api/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.log("登录成功!", "SUCCESS")
                return True
            else:
                self.log(f"登录失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"登录异常: {e}", "ERROR")
            return False
    
    async def test_get_me(self):
        """获取当前用户信息"""
        self.log("获取当前用户信息...")
        try:
            response = await self.client.get("/api/users/me", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data.get("id")
                self.log(f"用户信息: {data.get('username')} (ID: {self.test_user_id})", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_get_posts(self):
        """获取文章列表，选择第一篇已发布文章用于测试"""
        self.log("获取文章列表...")
        try:
            response = await self.client.get("/api/posts/")
            if response.status_code == 200:
                data = response.json()
                posts = data if isinstance(data, list) else data.get("posts", [])
                
                # 找第一篇已发布的文章
                for post in posts:
                    if post.get("status") == "published":
                        self.test_post_id = post.get("id")
                        self.log(f"选择测试文章: {post.get('title')} (ID: {self.test_post_id})", "SUCCESS")
                        return post
                
                self.log("未找到已发布文章，将使用第一篇文章", "WARNING")
                if posts:
                    self.test_post_id = posts[0].get("id")
                    return posts[0]
                return None
            else:
                self.log(f"获取失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_create_comment(self, content, parent_id=None):
        """创建评论"""
        self.log(f"创建评论: {content[:30]}...")
        try:
            payload = {
                "content": content,
                "post_id": self.test_post_id
            }
            if parent_id:
                payload["parent_id"] = parent_id
                self.log(f"  -> 回复评论: {parent_id}")
            
            response = await self.client.post(
                "/api/comments",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 201:
                data = response.json()
                comment_id = data.get("id")
                self.created_comments.append(comment_id)
                self.log(f"评论创建成功! ID: {comment_id}", "SUCCESS")
                return data
            else:
                self.log(f"创建失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建异常: {e}", "ERROR")
            return None
    
    async def test_get_post_comments(self):
        """获取文章评论列表"""
        self.log(f"获取文章评论列表 (Post: {self.test_post_id})...")
        try:
            response = await self.client.get(f"/api/comments/post/{self.test_post_id}")
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                comments = data.get("comments", [])
                self.log(f"获取成功! 共 {total} 条顶层评论, {len(comments)} 条数据", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_get_comment_detail(self, comment_id):
        """获取评论详情"""
        self.log(f"获取评论详情: {comment_id}...")
        try:
            response = await self.client.get(f"/api/comments/{comment_id}")
            if response.status_code == 200:
                data = response.json()
                reply_count = len(data.get("replies", []))
                self.log(f"获取成功! 内容: {data.get('content')[:30]}... 回复数: {reply_count}", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_update_comment(self, comment_id, new_content):
        """更新评论"""
        self.log(f"更新评论: {comment_id}...")
        try:
            response = await self.client.put(
                f"/api/comments/{comment_id}",
                headers=self.headers,
                json={"content": new_content}
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"更新成功! 新内容: {data.get('content')[:30]}...", "SUCCESS")
                return data
            else:
                self.log(f"更新失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"更新异常: {e}", "ERROR")
            return None
    
    async def test_get_user_comments(self, user_id):
        """获取用户评论列表"""
        self.log(f"获取用户评论列表 (User: {user_id})...")
        try:
            response = await self.client.get(f"/api/comments/user/{user_id}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log(f"获取成功! 共 {len(data)} 条评论", "SUCCESS")
                else:
                    self.log(f"获取成功! 数据格式: {type(data)}", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_delete_comment(self, comment_id):
        """删除评论（软删除）"""
        self.log(f"删除评论: {comment_id}...")
        try:
            response = await self.client.delete(
                f"/api/comments/{comment_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"删除成功! {data.get('message')}", "SUCCESS")
                return data
            else:
                self.log(f"删除失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"删除异常: {e}", "ERROR")
            return None
    
    async def run_all_tests(self):
        """运行所有评论测试"""
        self.log("=" * 60)
        self.log("🐱 评论功能集成测试开始！")
        self.log("=" * 60)
        
        # 1. 健康检查
        if not await self.test_health():
            self.log("服务未就绪，终止测试", "ERROR")
            return False
        
        # 2. 登录（使用萌星的账号）
        if not await self.test_login("MengXing", "mengxing2026"):
            self.log("登录失败，终止测试", "ERROR")
            return False
        
        # 3. 获取当前用户信息
        me = await self.test_get_me()
        if not me:
            return False
        
        # 4. 获取文章列表
        post = await self.test_get_posts()
        if not post:
            self.log("没有可用文章，终止测试", "ERROR")
            return False
        
        self.log("-" * 60)
        self.log("📝 开始创建测试评论数据...")
        self.log("-" * 60)
        
        # 5. 创建顶层评论
        comment1 = await self.test_create_comment("这篇写得真好！学到了很多~喵！")
        comment2 = await self.test_create_comment("博主的技术分享太棒了，收藏了！")
        comment3 = await self.test_create_comment("有个问题想请教一下...")
        
        if not comment1:
            self.log("创建评论失败，终止测试", "ERROR")
            return False
        
        # 6. 创建回复（嵌套评论）
        self.log("-" * 60)
        self.log("💬 创建嵌套回复...")
        self.log("-" * 60)
        
        reply1 = await self.test_create_comment("谢谢支持！会继续努力的~", parent_id=comment1["id"])
        reply2 = await self.test_create_comment("同问，我也想知道答案", parent_id=comment3["id"])
        
        # 创建二级回复
        if reply1:
            reply1_1 = await self.test_create_comment("期待更多好文！", parent_id=reply1["id"])
        
        # 7. 获取文章评论列表
        self.log("-" * 60)
        self.log("📋 测试评论列表查询...")
        self.log("-" * 60)
        
        comments_data = await self.test_get_post_comments()
        
        # 8. 获取评论详情
        if self.created_comments:
            self.log("-" * 60)
            self.log("🔍 测试评论详情查询...")
            self.log("-" * 60)
            
            detail = await self.test_get_comment_detail(self.created_comments[0])
        
        # 9. 更新评论
        if len(self.created_comments) >= 2:
            self.log("-" * 60)
            self.log("✏️ 测试更新评论...")
            self.log("-" * 60)
            
            updated = await self.test_update_comment(
                self.created_comments[1],
                "更新后的评论内容：这篇文章真的太有帮助了！"
            )
        
        # 10. 获取用户评论
        self.log("-" * 60)
        self.log("👤 测试获取用户评论...")
        self.log("-" * 60)
        
        user_comments = await self.test_get_user_comments(self.test_user_id)
        
        # 11. 删除评论（测试软删除）
        if len(self.created_comments) >= 3:
            self.log("-" * 60)
            self.log("🗑️ 测试删除评论（软删除）...")
            self.log("-" * 60)
            
            deleted = await self.test_delete_comment(self.created_comments[2])
            
            # 验证删除后还能获取到（软删除）
            if deleted:
                self.log("验证软删除效果...")
                detail_after = await self.test_get_comment_detail(self.created_comments[2])
                if detail_after and detail_after.get("is_deleted"):
                    self.log("软删除验证成功！评论标记为已删除", "SUCCESS")
        
        # 12. 再次获取文章评论，查看完整结构
        self.log("-" * 60)
        self.log("📊 最终评论列表...")
        self.log("-" * 60)
        
        final_comments = await self.test_get_post_comments()
        
        # 统计结果
        self.log("=" * 60)
        self.log("🎉 评论功能集成测试完成！")
        self.log("=" * 60)
        
        success_count = sum(1 for r in self.test_results if r["level"] == "SUCCESS")
        error_count = sum(1 for r in self.test_results if r["level"] == "ERROR")
        warning_count = sum(1 for r in self.test_results if r["level"] == "WARNING")
        
        self.log(f"测试结果统计:")
        self.log(f"  ✅ 成功: {success_count}")
        self.log(f"  ⚠️  警告: {warning_count}")
        self.log(f"  ❌ 错误: {error_count}")
        self.log(f"  📝 创建评论数: {len(self.created_comments)}")
        
        return error_count == 0


async def main():
    tester = CommentTester()
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
