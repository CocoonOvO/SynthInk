"""
点赞功能集成测试
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8002"


class LikeIntegrationTest:
    """点赞功能集成测试类"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.user_id = None
        self.test_post_id = None
        self.success_count = 0
        self.error_count = 0
    
    def log(self, message, level="INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    async def test_health(self):
        """测试服务健康"""
        try:
            response = await self.client.get("/api/docs")
            if response.status_code == 200:
                self.log("✅ 服务运行正常", "SUCCESS")
                return True
            else:
                self.log(f"❌ 服务异常: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 连接失败: {e}", "ERROR")
            return False
    
    async def test_login(self, username, password):
        """测试登录"""
        try:
            response = await self.client.post(
                "/api/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.log(f"✅ 登录成功: {username}", "SUCCESS")
                return True
            else:
                self.log(f"❌ 登录失败: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ 登录异常: {e}", "ERROR")
            return False
    
    async def test_get_me(self):
        """获取当前用户信息"""
        try:
            response = await self.client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 获取用户信息: {data.get('username')}", "SUCCESS")
                return data
            else:
                self.log(f"❌ 获取用户信息失败: {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ 获取用户信息异常: {e}", "ERROR")
            return None
    
    async def test_get_posts(self):
        """获取文章列表"""
        try:
            response = await self.client.get("/api/posts/")
            if response.status_code == 200:
                posts = response.json()
                if posts and len(posts) > 0:
                    self.test_post_id = posts[0]["id"]
                    self.log(f"✅ 获取文章列表: {len(posts)}篇文章，使用ID: {self.test_post_id[:8]}...", "SUCCESS")
                    return posts[0]
                else:
                    self.log("⚠️ 文章列表为空", "WARNING")
                    return None
            else:
                self.log(f"❌ 获取文章列表失败: {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ 获取文章列表异常: {e}", "ERROR")
            return None
    
    async def test_like_post(self, post_id):
        """测试点赞文章"""
        try:
            response = await self.client.post(
                f"/api/likes/{post_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code in [200, 201]:
                data = response.json()
                self.log(f"✅ 点赞成功: 文章 {post_id[:8]}...，当前点赞数: {data.get('like_count')}", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 点赞失败: {response.status_code} - {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 点赞异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_get_like_status(self, post_id):
        """测试获取点赞状态"""
        try:
            response = await self.client.get(
                f"/api/likes/{post_id}/status",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 获取点赞状态: 文章 {post_id[:8]}...，点赞数: {data.get('like_count')}，已点赞: {data.get('is_liked')}", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 获取点赞状态失败: {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 获取点赞状态异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_get_like_status_public(self, post_id):
        """测试公开获取点赞状态（未登录）"""
        try:
            response = await self.client.get(f"/api/likes/{post_id}/status")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 公开获取点赞状态: 文章 {post_id[:8]}...，点赞数: {data.get('like_count')}，已点赞: {data.get('is_liked')}", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 公开获取点赞状态失败: {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 公开获取点赞状态异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_get_my_liked_posts(self):
        """测试获取我点赞的文章列表"""
        try:
            response = await self.client.get(
                "/api/likes/user/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 获取我的点赞列表: {len(data)}篇文章", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 获取我的点赞列表失败: {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 获取我的点赞列表异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_get_post_likers(self, post_id):
        """测试获取文章点赞用户列表"""
        try:
            response = await self.client.get(f"/api/likes/post/{post_id}/users")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 获取点赞用户列表: 文章 {post_id[:8]}...，{len(data)}个用户", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 获取点赞用户列表失败: {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 获取点赞用户列表异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_unlike_post(self, post_id):
        """测试取消点赞"""
        try:
            response = await self.client.delete(
                f"/api/likes/{post_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 取消点赞成功: 文章 {post_id[:8]}...，当前点赞数: {data.get('like_count')}", "SUCCESS")
                self.success_count += 1
                return data
            else:
                self.log(f"❌ 取消点赞失败: {response.text}", "ERROR")
                self.error_count += 1
                return None
        except Exception as e:
            self.log(f"❌ 取消点赞异常: {e}", "ERROR")
            self.error_count += 1
            return None
    
    async def test_double_like(self, post_id):
        """测试重复点赞（幂等性）"""
        try:
            # 第一次点赞
            response1 = await self.client.post(
                f"/api/likes/{post_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            # 第二次点赞
            response2 = await self.client.post(
                f"/api/likes/{post_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response1.status_code in [200, 201] and response2.status_code in [200, 201]:
                data1 = response1.json()
                data2 = response2.json()
                
                if data1.get("like_count") == data2.get("like_count"):
                    self.log(f"✅ 重复点赞幂等性测试通过: 点赞数保持 {data1.get('like_count')}", "SUCCESS")
                    self.success_count += 1
                    return True
                else:
                    self.log(f"⚠️ 重复点赞点赞数不一致: {data1.get('like_count')} vs {data2.get('like_count')}", "WARNING")
                    return False
            else:
                self.log(f"❌ 重复点赞测试失败", "ERROR")
                self.error_count += 1
                return False
        except Exception as e:
            self.log(f"❌ 重复点赞测试异常: {e}", "ERROR")
            self.error_count += 1
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 60)
        self.log("🐱 点赞功能集成测试开始！")
        self.log("=" * 60)
        
        # 1. 健康检查
        if not await self.test_health():
            self.log("服务未就绪，终止测试", "ERROR")
            return False
        
        # 2. 登录
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
        
        post_id = self.test_post_id
        
        self.log("-" * 60)
        self.log("👍 开始点赞功能测试...")
        self.log("-" * 60)
        
        # 5. 测试公开获取点赞状态
        await self.test_get_like_status_public(post_id)
        
        # 6. 测试点赞文章
        await self.test_like_post(post_id)
        
        # 7. 测试获取点赞状态（已登录）
        await self.test_get_like_status(post_id)
        
        # 8. 测试获取我的点赞列表
        await self.test_get_my_liked_posts()
        
        # 9. 测试获取点赞用户列表
        await self.test_get_post_likers(post_id)
        
        # 10. 测试重复点赞（幂等性）
        await self.test_double_like(post_id)
        
        # 11. 测试取消点赞
        await self.test_unlike_post(post_id)
        
        # 12. 再次获取点赞状态（验证取消成功）
        status = await self.test_get_like_status(post_id)
        if status and not status.get("is_liked"):
            self.log("✅ 取消点赞验证成功", "SUCCESS")
        
        # 13. 多文章点赞测试
        self.log("-" * 60)
        self.log("👍 测试多文章点赞...")
        self.log("-" * 60)
        
        # 获取所有文章并点赞前3篇
        response = await self.client.get("/api/posts/")
        if response.status_code == 200:
            posts = response.json()
            for i, p in enumerate(posts[:3]):
                result = await self.test_like_post(p["id"])
                if result:
                    self.log(f"  文章 {i+1}: {p.get('title', '无标题')[:20]}... 点赞成功")
        
        # 汇总
        self.log("=" * 60)
        self.log("🎉 点赞功能集成测试完成！")
        self.log("=" * 60)
        self.log(f"✅ 成功: {self.success_count}")
        self.log(f"❌ 失败: {self.error_count}")
        
        if self.error_count == 0:
            self.log("🌟 所有测试通过！", "SUCCESS")
        else:
            self.log(f"⚠️ 有 {self.error_count} 个测试失败", "WARNING")
        
        return self.error_count == 0
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    test = LikeIntegrationTest()
    try:
        success = await test.run_all_tests()
        return 0 if success else 1
    finally:
        await test.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
