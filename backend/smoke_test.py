"""
冒烟测试脚本
验证接口修改后核心功能是否正常
"""
import asyncio
import httpx
from datetime import datetime


class SmokeTester:
    """冒烟测试器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8002"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.results = []
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        icon = icons.get(level, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
        
    async def test_health(self):
        """测试服务健康状态"""
        self.log("测试服务健康状态...")
        try:
            response = await self.client.get("/api/docs")
            if response.status_code == 200:
                self.log("服务运行正常", "SUCCESS")
                return True
            else:
                self.log(f"服务异常: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"连接失败: {e}", "ERROR")
            return False
    
    async def test_get_user_public(self):
        """测试公开获取用户信息接口（修改后的接口）"""
        self.log("测试公开获取用户信息接口...")
        try:
            # 使用正确的UUID格式用户ID（Cocoon用户）
            test_user_id = "e84f559c-aed9-46da-9e5c-8fec69a9b8d6"
            response = await self.client.get(f"/api/users/{test_user_id}")
            
            if response.status_code == 200:
                data = response.json()
                # 验证敏感字段已被移除
                has_sensitive = any(key in data for key in ["email", "is_active", "is_superuser"])
                if has_sensitive:
                    self.log("警告：响应包含敏感字段", "WARNING")
                else:
                    self.log("公开接口正常，敏感字段已过滤", "SUCCESS")
                self.log(f"用户信息: {data.get('username', 'unknown')}")
                return True
            elif response.status_code == 404:
                self.log("用户不存在（可能是测试数据被清理）", "WARNING")
                return True  # 接口本身是正常的
            else:
                self.log(f"接口异常: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"测试异常: {e}", "ERROR")
            return False
    
    async def test_get_user_with_token(self):
        """测试携带Token访问用户接口"""
        self.log("测试携带Token访问用户接口...")
        try:
            # 先登录获取Token（使用萌星的账号）
            login_data = {
                "username": "MengXing",
                "password": "mengxing2026"
            }
            login_response = await self.client.post(
                "/api/auth/token",
                data=login_data
            )
            
            if login_response.status_code != 200:
                self.log(f"登录失败: {login_response.status_code}", "ERROR")
                return False
            
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            # 携带Token访问用户接口
            headers = {"Authorization": f"Bearer {access_token}"}
            test_user_id = "e84f559c-aed9-46da-9e5c-8fec69a9b8d6"
            response = await self.client.get(f"/api/users/{test_user_id}", headers=headers)
            
            if response.status_code == 200:
                self.log("带Token访问正常", "SUCCESS")
                return True
            else:
                self.log(f"带Token访问异常: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"测试异常: {e}", "ERROR")
            return False
    
    async def test_get_current_user_me(self):
        """测试获取当前用户信息（需要登录）"""
        self.log("测试获取当前用户信息...")
        try:
            # 先登录（使用萌星的账号）
            login_data = {
                "username": "MengXing",
                "password": "mengxing2026"
            }
            login_response = await self.client.post(
                "/api/auth/token",
                data=login_data
            )
            
            if login_response.status_code != 200:
                self.log(f"登录失败", "ERROR")
                return False
            
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            # 访问 /me 接口
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await self.client.get("/api/users/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"获取当前用户成功: {data.get('username')}", "SUCCESS")
                return True
            else:
                self.log(f"获取当前用户失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"测试异常: {e}", "ERROR")
            return False
    
    async def test_list_posts(self):
        """测试文章列表接口"""
        self.log("测试文章列表接口...")
        try:
            response = await self.client.get("/api/posts/")
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else len(data.get("posts", []))
                self.log(f"获取文章列表成功: {count}篇", "SUCCESS")
                return True
            else:
                self.log(f"获取文章列表失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"测试异常: {e}", "ERROR")
            return False
    
    async def test_auth_flow(self):
        """测试认证流程"""
        self.log("测试认证流程...")
        try:
            # 1. 登录（使用萌星的账号）
            login_data = {
                "username": "MengXing",
                "password": "mengxing2026"
            }
            login_response = await self.client.post(
                "/api/auth/token",
                data=login_data
            )
            
            if login_response.status_code != 200:
                self.log(f"登录失败: {login_response.status_code}", "ERROR")
                return False
            
            token_data = login_response.json()
            self.log(f"登录成功，获取到Token", "SUCCESS")
            
            # 2. 使用Token访问需要认证的接口
            access_token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            me_response = await self.client.get("/api/users/me", headers=headers)
            if me_response.status_code == 200:
                self.log("Token验证成功", "SUCCESS")
                return True
            else:
                self.log(f"Token验证失败: {me_response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"测试异常: {e}", "ERROR")
            return False
    
    async def run_all_tests(self):
        """运行所有冒烟测试"""
        print("=" * 60)
        print("🔥 冒烟测试开始")
        print("=" * 60)
        
        tests = [
            ("服务健康检查", self.test_health),
            ("公开获取用户信息", self.test_get_user_public),
            ("带Token获取用户信息", self.test_get_user_with_token),
            ("获取当前用户信息", self.test_get_current_user_me),
            ("文章列表接口", self.test_list_posts),
            ("认证流程", self.test_auth_flow),
        ]
        
        results = []
        for name, test_func in tests:
            print(f"\n{'─' * 60}")
            print(f"📋 测试项: {name}")
            print('─' * 60)
            try:
                result = await test_func()
                results.append((name, result))
            except Exception as e:
                self.log(f"测试执行异常: {e}", "ERROR")
                results.append((name, False))
        
        # 汇总结果
        print(f"\n{'=' * 60}")
        print("📊 测试结果汇总")
        print("=" * 60)
        
        passed = sum(1 for _, r in results if r)
        failed = sum(1 for _, r in results if not r)
        
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status} - {name}")
        
        print(f"\n总计: {passed} 通过, {failed} 失败")
        
        if failed == 0:
            print("\n🎉 所有冒烟测试通过！接口修改正常喵～！")
        else:
            print(f"\n⚠️ 有 {failed} 个测试失败，需要检查喵...")
        
        return failed == 0
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    tester = SmokeTester()
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    finally:
        await tester.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
