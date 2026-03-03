"""
测试数据填充脚本（快速版 - 使用不同用户名避免限流）

通过后端API接口写入测试数据
包含：用户、文章、标签、分组
"""
import asyncio
import httpx
from datetime import datetime, timedelta
import random
import time

BASE_URL = "http://localhost:8001"

# 使用时间戳生成唯一用户名
TIMESTAMP = int(time.time()) % 10000

# 测试数据
TEST_USERS = [
    {"username": f"alice_{TIMESTAMP}", "email": f"alice_{TIMESTAMP}@example.com", "password": "password123"},
    {"username": f"bob_{TIMESTAMP}", "email": f"bob_{TIMESTAMP}@example.com", "password": "password123"},
    {"username": f"charlie_{TIMESTAMP}", "email": f"charlie_{TIMESTAMP}@example.com", "password": "password123"},
]

TEST_TAGS = [
    {"name": "Python", "description": "Python编程语言", "color": "#3776AB"},
    {"name": "JavaScript", "description": "JS前端开发", "color": "#F7DF1E"},
    {"name": "FastAPI", "description": "现代Python Web框架", "color": "#009688"},
    {"name": "Vue.js", "description": "渐进式JavaScript框架", "color": "#4FC08D"},
    {"name": "AI", "description": "人工智能", "color": "#FF6B6B"},
    {"name": "机器学习", "description": "Machine Learning", "color": "#9B59B6"},
    {"name": "深度学习", "description": "Deep Learning", "color": "#3498DB"},
    {"name": "生活随笔", "description": "日常生活记录", "color": "#E67E22"},
]

TEST_GROUPS = [
    {"name": "技术分享", "description": "技术文章和教程", "icon": "💻", "sort_order": 1},
    {"name": "AI前沿", "description": "人工智能最新动态", "icon": "🤖", "sort_order": 2},
    {"name": "生活感悟", "description": "生活中的思考和感悟", "icon": "📝", "sort_order": 3},
    {"name": "读书笔记", "description": "阅读心得和书评", "icon": "📚", "sort_order": 4},
    {"name": "项目实战", "description": "实际项目经验分享", "icon": "🚀", "sort_order": 5},
]

TEST_POSTS = [
    {
        "title": "FastAPI入门指南：构建高性能Python后端",
        "content": """# FastAPI入门指南

FastAPI是一个现代、高性能的Python Web框架，基于Starlette和Pydantic构建。

## 主要特性

- **高性能**：基于Starlette，性能媲美Node.js和Go
- **类型提示**：基于Python类型提示，自动数据验证
- **自动文档**：自动生成OpenAPI和Swagger UI
- **异步支持**：原生支持async/await

## 快速开始

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 总结

FastAPI是构建现代Python Web应用的绝佳选择！
""",
        "introduction": "介绍FastAPI框架的核心特性和使用方法",
        "tags": ["Python", "FastAPI"],
        "group": "技术分享",
    },
    {
        "title": "Vue3组合式API实战心得",
        "content": """# Vue3组合式API实战心得

Vue 3引入了组合式API（Composition API），让代码组织更加灵活。

## 为什么选择组合式API

1. **更好的逻辑复用**：通过composables复用逻辑
2. **更清晰的代码组织**：相关逻辑可以放在一起
3. **更好的TypeScript支持**：类型推断更完善

## 实战示例

```vue
<script setup>
import { ref, computed } from 'vue'

const count = ref(0)
const double = computed(() => count.value * 2)

function increment() {
  count.value++
}
</script>
```

## 总结

组合式API让Vue开发体验更上一层楼！
""",
        "introduction": "分享Vue3组合式API在实际项目中的应用经验",
        "tags": ["JavaScript", "Vue.js"],
        "group": "技术分享",
    },
    {
        "title": "深度学习入门：从感知机到神经网络",
        "content": """# 深度学习入门

深度学习是机器学习的一个分支，通过多层神经网络学习数据的层次化表示。

## 感知机

感知机是最简单的神经网络单元。

## 神经网络

多层感知机构成了神经网络：

1. 输入层
2. 隐藏层
3. 输出层

## 激活函数

- ReLU
- Sigmoid
- Tanh

## 总结

深度学习正在改变我们的世界！
""",
        "introduction": "深入浅出介绍深度学习的基本概念和发展历程",
        "tags": ["AI", "机器学习", "深度学习"],
        "group": "AI前沿",
    },
    {
        "title": "周末的咖啡时光",
        "content": """# 周末的咖啡时光

这个周末，我在街角发现了一家宝藏咖啡店。

## 环境

木质装潢，暖黄灯光，还有轻柔的爵士乐。

## 咖啡

点了一杯手冲埃塞俄比亚，花香和果酸的平衡恰到好处。

## 思考

有时候，慢下来才能发现生活中的美好。

> "生活不是等待暴风雨过去，而是学会在雨中跳舞。"

## 结语

下周还要来！
""",
        "introduction": "记录一个慵懒周末的咖啡探店体验",
        "tags": ["生活随笔"],
        "group": "生活感悟",
    },
    {
        "title": "《黑客与画家》读书笔记",
        "content": """# 《黑客与画家》读书笔记

Paul Graham的经典之作，探讨黑客文化与创业精神。

## 核心观点

1. **黑客与画家的相似性**：都是创作者，都需要审美
2. **创业公司的本质**：快速成长的技术公司
3. **财富创造**：创造财富而非掠夺财富

## 金句摘录

> "优秀的软件就像优秀的画作，需要反复打磨。"

## 个人感悟

这本书改变了我对编程和创业的理解。

## 推荐指数

⭐⭐⭐⭐⭐
""",
        "introduction": "Paul Graham经典著作的阅读心得",
        "tags": ["读书笔记"],
        "group": "读书笔记",
    },
    {
        "title": "从零搭建博客系统：SynthInk项目实战",
        "content": """# SynthInk项目实战

记录从零搭建AI辅助博客系统的完整过程。

## 技术栈

- **后端**：FastAPI + PostgreSQL
- **前端**：Vue3 + Element Plus
- **AI集成**：MCP服务

## 开发心得

多Agent协作开发让效率提升了不少！

## 总结

这是一个充满挑战但收获满满的项目。
""",
        "introduction": "完整记录SynthInk博客系统的开发过程",
        "tags": ["Python", "FastAPI", "Vue.js"],
        "group": "项目实战",
    },
]


class TestDataSeeder:
    """测试数据填充器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
        self.users = []
        self.tokens = {}
        self.tags = []
        self.groups = []
        self.posts = []
    
    async def close(self):
        await self.client.aclose()
    
    async def register_user(self, user_data: dict) -> dict:
        """注册用户"""
        try:
            response = await self.client.post("/api/auth/register", json=user_data)
            if response.status_code == 201:
                print(f"  ✅ 用户创建成功: {user_data['username']}")
                return response.json()
            elif response.status_code == 400 and ("已存在" in response.text or "exists" in response.text.lower()):
                print(f"  ⚠️ 用户已存在: {user_data['username']}")
                return None
            else:
                print(f"  ❌ 用户创建失败: {user_data['username']} - {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ 用户创建异常: {user_data['username']} - {e}")
            return None
    
    async def login_user(self, username: str, password: str) -> str:
        """用户登录，获取token"""
        try:
            response = await self.client.post(
                "/api/auth/token",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"  ✅ 登录成功: {username}")
                return token
            else:
                print(f"  ❌ 登录失败: {username} - {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ 登录异常: {username} - {e}")
            return None
    
    async def create_tag(self, tag_data: dict, token: str) -> dict:
        """创建标签"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post("/api/tags/", json=tag_data, headers=headers)
            if response.status_code == 201:
                print(f"  ✅ 标签创建成功: {tag_data['name']}")
                return response.json()
            elif response.status_code == 400 and ("已存在" in response.text or "exists" in response.text.lower()):
                print(f"  ⚠️ 标签已存在: {tag_data['name']}")
                # 获取已存在的标签
                list_response = await self.client.get("/api/tags/")
                if list_response.status_code == 200:
                    for tag in list_response.json():
                        if tag["name"] == tag_data["name"]:
                            return tag
                return None
            else:
                print(f"  ❌ 标签创建失败: {tag_data['name']} - {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ 标签创建异常: {tag_data['name']} - {e}")
            return None
    
    async def create_group(self, group_data: dict, token: str) -> dict:
        """创建分组"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post("/api/groups/", json=group_data, headers=headers)
            if response.status_code == 201:
                print(f"  ✅ 分组创建成功: {group_data['name']}")
                return response.json()
            elif response.status_code == 400 and ("已存在" in response.text or "exists" in response.text.lower()):
                print(f"  ⚠️ 分组已存在: {group_data['name']}")
                # 获取已存在的分组
                list_response = await self.client.get("/api/groups/")
                if list_response.status_code == 200:
                    for group in list_response.json():
                        if group["name"] == group_data["name"]:
                            return group
                return None
            else:
                print(f"  ❌ 分组创建失败: {group_data['name']} - {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ 分组创建异常: {group_data['name']} - {e}")
            return None
    
    async def create_post(self, post_data: dict, token: str) -> dict:
        """创建文章"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post("/api/posts/", json=post_data, headers=headers)
            if response.status_code == 201:
                print(f"  ✅ 文章创建成功: {post_data['title'][:30]}...")
                return response.json()
            else:
                print(f"  ❌ 文章创建失败: {post_data['title'][:30]}... - {response.text}")
                return None
        except Exception as e:
            print(f"  ❌ 文章创建异常: {post_data['title'][:30]}... - {e}")
            return None
    
    async def publish_post(self, post_id: str, token: str):
        """发布文章"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.client.post(f"/api/posts/{post_id}/publish", headers=headers)
            if response.status_code == 200:
                print(f"  ✅ 文章发布成功: {post_id[:8]}...")
                return True
            else:
                print(f"  ❌ 文章发布失败: {post_id[:8]}... - {response.text}")
                return False
        except Exception as e:
            print(f"  ❌ 文章发布异常: {post_id[:8]}... - {e}")
            return False
    
    async def seed_users(self):
        """填充用户数据"""
        print("\n👥 创建测试用户...")
        for i, user_data in enumerate(TEST_USERS):
            user = await self.register_user(user_data)
            if user:
                self.users.append(user)
                # 登录获取token
                token = await self.login_user(user_data["username"], user_data["password"])
                if token:
                    self.tokens[user["id"]] = token
            # 添加延迟避免限流（每3个用户等待60秒）
            if (i + 1) % 3 == 0 and i < len(TEST_USERS) - 1:
                print(f"  ⏳ 等待限流重置 (60秒)...")
                await asyncio.sleep(60)
        print(f"✅ 共创建 {len(self.users)} 个用户")
    
    async def seed_tags(self):
        """填充标签数据"""
        print("\n🏷️ 创建标签...")
        if not self.users:
            print("  ⚠️ 没有可用用户，跳过标签创建")
            return
        
        # 使用第一个用户的token
        token = list(self.tokens.values())[0]
        
        for tag_data in TEST_TAGS:
            tag = await self.create_tag(tag_data, token)
            if tag:
                self.tags.append(tag)
        print(f"✅ 共创建 {len(self.tags)} 个标签")
    
    async def seed_groups(self):
        """填充分组数据"""
        print("\n📁 创建分组...")
        if not self.users:
            print("  ⚠️ 没有可用用户，跳过分组创建")
            return
        
        # 使用第一个用户的token
        token = list(self.tokens.values())[0]
        
        for group_data in TEST_GROUPS:
            group = await self.create_group(group_data, token)
            if group:
                self.groups.append(group)
        print(f"✅ 共创建 {len(self.groups)} 个分组")
    
    async def seed_posts(self):
        """填充文章数据"""
        print("\n📝 创建文章...")
        if not self.users or not self.groups:
            print("  ⚠️ 没有可用用户或分组，跳过文章创建")
            return
        
        # 创建标签名称到ID的映射
        tag_name_to_id = {tag["name"]: tag["id"] for tag in self.tags}
        # 创建分组名称到ID的映射
        group_name_to_id = {group["name"]: group["id"] for group in self.groups}
        
        for i, post_template in enumerate(TEST_POSTS):
            # 轮流使用不同用户
            user = self.users[i % len(self.users)]
            token = self.tokens.get(user["id"])
            
            if not token:
                continue
            
            # 准备文章数据
            post_data = {
                "title": post_template["title"],
                "content": post_template["content"],
                "introduction": post_template["introduction"],
                "group_id": group_name_to_id.get(post_template["group"]),
                "tag_ids": [
                    tag_name_to_id[tag_name] 
                    for tag_name in post_template["tags"] 
                    if tag_name in tag_name_to_id
                ],
            }
            
            # 创建文章
            post = await self.create_post(post_data, token)
            if post:
                self.posts.append(post)
                # 随机决定是否发布（70%概率发布）
                if random.random() < 0.7:
                    await self.publish_post(post["id"], token)
        
        print(f"✅ 共创建 {len(self.posts)} 篇文章")
    
    async def print_summary(self):
        """打印数据摘要"""
        print("\n" + "="*50)
        print("📊 测试数据填充完成")
        print("="*50)
        print(f"👥 用户: {len(self.users)} 个")
        print(f"🏷️ 标签: {len(self.tags)} 个")
        print(f"📁 分组: {len(self.groups)} 个")
        print(f"📝 文章: {len(self.posts)} 篇")
        print("="*50)
        
        # 打印用户登录信息
        print("\n🔑 测试账号（可用于登录）:")
        for user_data in TEST_USERS:
            print(f"  用户名: {user_data['username']:<20} 密码: {user_data['password']}")
    
    async def run(self):
        """运行数据填充"""
        print("🚀 开始填充测试数据...")
        print(f"📍 API地址: {self.base_url}")
        
        try:
            # 检查服务是否可用（尝试获取文档）
            response = await self.client.get("/api/docs")
            if response.status_code not in [200, 307]:
                print(f"⚠️ 服务健康检查失败: {response.status_code}")
                return
            print("✅ 后端服务连接成功\n")
            
            # 按顺序填充数据
            await self.seed_users()
            await self.seed_tags()
            await self.seed_groups()
            await self.seed_posts()
            
            # 打印摘要
            await self.print_summary()
            
        except Exception as e:
            print(f"❌ 数据填充失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()


async def main():
    seeder = TestDataSeeder()
    await seeder.run()


if __name__ == "__main__":
    asyncio.run(main())
