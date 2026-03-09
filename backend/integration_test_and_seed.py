"""
集成测试和数据写入脚本
测试后端API并写入测试数据
"""
import asyncio
import httpx
import sys
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8002"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.headers = {}
        self.test_results = []
        
    async def close(self):
        await self.client.aclose()
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "📝", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "📝")
        print(f"{prefix} [{timestamp}] {message}")
        self.test_results.append({"time": timestamp, "level": level, "message": message})
    
    async def test_health(self):
        """测试健康检查接口 - 使用API文档端点"""
        self.log("测试健康检查接口...")
        try:
            # 尝试访问API文档端点作为健康检查
            response = await self.client.get("/api/docs")
            if response.status_code == 200:
                self.log(f"服务运行正常! API文档可访问", "SUCCESS")
                return True
            else:
                self.log(f"健康检查失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"健康检查异常: {e}", "ERROR")
            return False
    
    async def test_register(self, username, email, password):
        """测试用户注册"""
        self.log(f"测试用户注册: {username}...")
        try:
            response = await self.client.post(
                "/api/auth/register",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                data = response.json()
                self.log(f"注册成功! 用户ID: {data.get('id')}", "SUCCESS")
                return data
            elif response.status_code == 400:
                self.log(f"用户可能已存在: {response.text}", "WARNING")
                return None
            else:
                self.log(f"注册失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"注册异常: {e}", "ERROR")
            return None
    
    async def test_login(self, username, password):
        """测试用户登录"""
        self.log(f"测试用户登录: {username}...")
        try:
            response = await self.client.post(
                "/api/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.log(f"登录成功! Token获取成功", "SUCCESS")
                return data
            else:
                self.log(f"登录失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"登录异常: {e}", "ERROR")
            return None
    
    async def test_get_me(self):
        """测试获取当前用户信息"""
        self.log("测试获取当前用户信息...")
        try:
            response = await self.client.get("/api/users/me", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                self.log(f"获取成功! 用户: {data.get('username')}", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_create_post(self, title, content, status="draft"):
        """测试创建文章"""
        self.log(f"测试创建文章: {title}...")
        try:
            response = await self.client.post(
                "/api/posts/",
                headers=self.headers,
                json={"title": title, "content": content, "status": status}
            )
            if response.status_code == 201:
                data = response.json()
                self.log(f"文章创建成功! ID: {data.get('id')}", "SUCCESS")
                return data
            else:
                self.log(f"创建失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建异常: {e}", "ERROR")
            return None
    
    async def test_list_posts(self):
        """测试获取文章列表"""
        self.log("测试获取文章列表...")
        try:
            response = await self.client.get("/api/posts/")
            if response.status_code == 200:
                data = response.json()
                # API返回的是列表格式
                if isinstance(data, list):
                    self.log(f"获取成功! 共 {len(data)} 篇文章", "SUCCESS")
                else:
                    posts = data.get("posts", [])
                    self.log(f"获取成功! 共 {len(posts)} 篇文章", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_create_tag(self, name, description=""):
        """测试创建标签"""
        self.log(f"测试创建标签: {name}...")
        try:
            response = await self.client.post(
                "/api/tags/",
                headers=self.headers,
                json={"name": name, "description": description}
            )
            if response.status_code == 201:
                data = response.json()
                self.log(f"标签创建成功! ID: {data.get('id')}", "SUCCESS")
                return data
            elif response.status_code == 400:
                self.log(f"标签可能已存在: {response.text}", "WARNING")
                return None
            else:
                self.log(f"创建失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建异常: {e}", "ERROR")
            return None
    
    async def test_list_tags(self):
        """测试获取标签列表"""
        self.log("测试获取标签列表...")
        try:
            response = await self.client.get("/api/tags/")
            if response.status_code == 200:
                data = response.json()
                # API返回的是列表格式
                if isinstance(data, list):
                    self.log(f"获取成功! 共 {len(data)} 个标签", "SUCCESS")
                else:
                    tags = data.get("tags", [])
                    self.log(f"获取成功! 共 {len(tags)} 个标签", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def test_create_group(self, name, description=""):
        """测试创建分组"""
        self.log(f"测试创建分组: {name}...")
        try:
            response = await self.client.post(
                "/api/groups/",
                headers=self.headers,
                json={"name": name, "description": description}
            )
            if response.status_code == 201:
                data = response.json()
                self.log(f"分组创建成功! ID: {data.get('id')}", "SUCCESS")
                return data
            elif response.status_code == 400:
                self.log(f"分组可能已存在: {response.text}", "WARNING")
                return None
            else:
                self.log(f"创建失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建异常: {e}", "ERROR")
            return None
    
    async def test_list_groups(self):
        """测试获取分组列表"""
        self.log("测试获取分组列表...")
        try:
            response = await self.client.get("/api/groups/")
            if response.status_code == 200:
                data = response.json()
                # API返回的是列表格式
                if isinstance(data, list):
                    self.log(f"获取成功! 共 {len(data)} 个分组", "SUCCESS")
                else:
                    groups = data.get("groups", [])
                    self.log(f"获取成功! 共 {len(groups)} 个分组", "SUCCESS")
                return data
            else:
                self.log(f"获取失败: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"获取异常: {e}", "ERROR")
            return None
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.log("=" * 60)
        self.log("🐱 喵娘集成测试开始！")
        self.log("=" * 60)
        
        # 1. 健康检查
        if not await self.test_health():
            self.log("服务未就绪，终止测试", "ERROR")
            return False
        
        # 2. 注册用户
        test_username = f"testuser_{datetime.now().strftime('%m%d%H%M%S')}"
        test_email = f"{test_username}@example.com"
        test_password = "TestPass123!"
        
        user = await self.test_register(test_username, test_email, test_password)
        
        # 3. 登录（普通用户）
        if not await self.test_login(test_username, test_password):
            self.log("登录失败，尝试使用现有用户登录...", "WARNING")
            # 尝试使用已存在的用户
            if not await self.test_login("Cocoon", "heat1423"):
                self.log("备用登录也失败，终止测试", "ERROR")
                return False
        
        # 4. 获取当前用户
        me = await self.test_get_me()
        
        # 5. 创建文章
        post1 = await self.test_create_post(
            "喵娘的测试文章",
            "这是一篇由喵娘自动创建的测试文章~喵！\n\n用来测试后端API是否正常工作。",
            "published"
        )
        post2 = await self.test_create_post(
            "草稿文章",
            "这是一篇草稿文章，还没有发布~",
            "draft"
        )
        
        # 6. 获取文章列表
        await self.test_list_posts()
        
        # 7. 切换到管理员账号创建标签和分组
        self.log("切换到管理员账号...")
        if await self.test_login("Cocoon", "heat1423"):
            # 8. 创建标签（管理员权限）
            tag1 = await self.test_create_tag("测试", "测试用标签")
            tag2 = await self.test_create_tag("喵娘", "喵娘专用标签")
            tag3 = await self.test_create_tag("API测试", "API测试相关")
            
            # 9. 获取标签列表
            await self.test_list_tags()
            
            # 10. 创建分组（管理员权限）
            group1 = await self.test_create_group("技术文章", "技术相关的文章")
            group2 = await self.test_create_group("生活随笔", "日常生活记录")
            
            # 11. 获取分组列表
            await self.test_list_groups()
        else:
            self.log("管理员登录失败，跳过标签和分组创建", "WARNING")
        
        self.log("=" * 60)
        self.log("🎉 集成测试完成！喵~")
        self.log("=" * 60)
        
        # 统计结果
        success_count = sum(1 for r in self.test_results if r["level"] == "SUCCESS")
        error_count = sum(1 for r in self.test_results if r["level"] == "ERROR")
        warning_count = sum(1 for r in self.test_results if r["level"] == "WARNING")
        
        self.log(f"测试结果统计:")
        self.log(f"  ✅ 成功: {success_count}")
        self.log(f"  ⚠️  警告: {warning_count}")
        self.log(f"  ❌ 错误: {error_count}")
        
        return error_count == 0


async def main():
    tester = APITester()
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
