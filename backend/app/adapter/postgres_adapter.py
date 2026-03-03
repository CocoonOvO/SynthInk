"""
PostgreSQL 业务库适配器
用于存储业务数据：用户、文章、标签、分组等
使用 asyncpg 实现异步操作
"""
import json
from datetime import datetime
from typing import Any, Optional, Union, List
import asyncpg
from pydantic import BaseModel

from .base import BaseAdapter


class PostgresAdapter(BaseAdapter):
    """
    PostgreSQL 业务数据库适配器
    
    存储内容：
    - 用户数据 (users)
    - 文章数据 (posts)
    - 标签数据 (tags)
    - 分组数据 (groups)
    - 文章-标签关联 (post_tags)
    
    支持自定义schema，便于多租户或多项目隔离
    """
    
    # 表名常量
    TABLE_USERS = "users"
    TABLE_POSTS = "posts"
    TABLE_TAGS = "tags"
    TABLE_GROUPS = "groups"
    TABLE_POST_TAGS = "post_tags"
    
    # 所有表名列表
    ALL_TABLES = [TABLE_USERS, TABLE_POSTS, TABLE_TAGS, TABLE_GROUPS, TABLE_POST_TAGS]
    
    def __init__(self, dsn: str, schema: str = "public"):
        """
        初始化适配器
        
        Args:
            dsn: PostgreSQL 连接字符串
                 格式: postgresql://user:password@host:port/database
            schema: PostgreSQL schema名称，默认为"public"
        """
        self.dsn = dsn
        self.schema = schema
        self._pool: Optional[asyncpg.Pool] = None
    
    def _normalize_dsn(self, dsn: str) -> str:
        """
        标准化DSN格式
        
        将 postgresql+asyncpg:// 转换为 postgresql://
        因为asyncpg只接受 postgresql:// 或 postgres:// 格式
        
        Args:
            dsn: 原始DSN字符串
            
        Returns:
            标准化后的DSN字符串
        """
        if dsn.startswith("postgresql+asyncpg://"):
            return dsn.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif dsn.startswith("postgres+asyncpg://"):
            return dsn.replace("postgres+asyncpg://", "postgresql://", 1)
        return dsn
    
    def _get_table_name(self, table: str) -> str:
        """获取带schema的完整表名"""
        return f"{self.schema}.{table}"

    async def connect(self) -> None:
        """建立数据库连接池

        支持多种连接策略：
        1. 标准TCP连接
        2. 禁用SSL的TCP连接（本地开发环境）
        3. 带SSL的TCP连接（生产环境）

        在Windows环境下，可能需要特殊处理
        """
        import os
        import sys
        import ssl

        # 标准化DSN格式
        normalized_dsn = self._normalize_dsn(self.dsn)

        # 检查是否需要禁用SSL（本地开发环境）
        disable_ssl = os.getenv("POSTGRES_DISABLE_SSL", "").lower() in ("true", "1", "yes")

        # 连接配置选项
        connect_options = {
            "min_size": 1,  # 减小连接池大小，便于测试
            "max_size": 10,
            "command_timeout": 60,
        }

        # 在Windows环境下，添加特殊处理
        if sys.platform == "win32":
            # Windows下可能需要禁用某些优化
            connect_options["server_settings"] = {
                "jit": "off",  # 禁用JIT，避免某些兼容性问题
            }

        # 尝试不同的连接策略
        connection_strategies = []

        # 策略1: 标准连接（根据环境变量决定是否禁用SSL）
        if disable_ssl:
            connection_strategies.append(("禁用SSL", {"ssl": False}))
        else:
            connection_strategies.append(("标准", {}))

        # 策略2: 如果标准连接失败，尝试相反的策略
        if not disable_ssl:
            connection_strategies.append(("禁用SSL", {"ssl": False}))
        else:
            connection_strategies.append(("标准", {}))

        # 策略3: 使用不验证证书的SSL（某些云数据库需要）
        if not disable_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connection_strategies.append(("SSL不验证证书", {"ssl": ssl_context}))

        last_error = None
        for strategy_name, ssl_options in connection_strategies:
            for attempt in range(2):  # 每种策略重试2次
                try:
                    options = {**connect_options, **ssl_options}
                    self._pool = await asyncpg.create_pool(
                        normalized_dsn,
                        **options
                    )
                    # 测试连接
                    async with self._pool.acquire() as conn:
                        await conn.fetchrow("SELECT 1")
                    print(f"[PostgreSQL] 使用 '{strategy_name}' 策略连接成功")
                    return  # 连接成功
                except Exception as e:
                    last_error = e
                    if attempt < 1:  # 不是最后一次尝试
                        import asyncio
                        await asyncio.sleep(0.3)

        # 所有尝试都失败了
        raise RuntimeError(f"无法连接到PostgreSQL数据库: {last_error}")
    
    async def disconnect(self) -> None:
        """关闭数据库连接池"""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def _execute(self, query: str, *args) -> str:
        """执行SQL语句（不返回结果）"""
        if not self._pool:
            raise RuntimeError("Database not connected")
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def _fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """获取单行结果"""
        if not self._pool:
            raise RuntimeError("Database not connected")
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def _fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """获取多行结果"""
        if not self._pool:
            raise RuntimeError("Database not connected")
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def create_table(self, name: str) -> dict[str, Any]:
        """
        创建业务表
        
        根据表名自动创建对应的表结构，支持自定义schema
        """
        # 构建完整的表名（包含schema）
        full_table_name = f"{self.schema}.{name}"
        
        if name == self.TABLE_USERS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    display_name VARCHAR(100),
                    avatar_url TEXT,
                    bio TEXT,
                    user_type VARCHAR(10) DEFAULT 'user',
                    agent_model VARCHAR(50),
                    agent_provider VARCHAR(50),
                    agent_config JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_superuser BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_GROUPS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT,
                    sort_order INTEGER DEFAULT 0,
                    post_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_TAGS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    color VARCHAR(7),
                    post_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_POSTS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    introduction TEXT,
                    cover_image TEXT,
                    status VARCHAR(20) DEFAULT 'draft',
                    author_id UUID REFERENCES {self.schema}.users(id) ON DELETE CASCADE,
                    group_id UUID REFERENCES {self.schema}.groups(id) ON DELETE SET NULL,
                    view_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP WITH TIME ZONE
                )
            """)
        
        elif name == self.TABLE_POST_TAGS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    post_id UUID REFERENCES {self.schema}.posts(id) ON DELETE CASCADE,
                    tag_id UUID REFERENCES {self.schema}.tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (post_id, tag_id)
                )
            """)
        
        else:
            return {"success": False, "error": f"Unknown table: {name}"}
        
        return {"success": True, "message": f"Table '{full_table_name}' created"}
    
    async def drop_table(self, name: str) -> dict[str, Any]:
        """删除表"""
        await self._execute(f"DROP TABLE IF EXISTS {name}")
        return {"success": True, "message": f"Table '{name}' dropped"}
    
    async def insert(self, table: str, data: Union[BaseModel, dict]) -> dict[str, Any]:
        """
        插入数据
        
        自动处理 Pydantic 模型和字典
        返回完整数据（包含数据库生成的字段如created_at）
        """
        if isinstance(data, BaseModel):
            data_dict = data.model_dump(exclude_unset=True)
        else:
            data_dict = data.copy()
        
        # 处理特殊字段
        if "agent_config" in data_dict and isinstance(data_dict["agent_config"], dict):
            data_dict["agent_config"] = json.dumps(data_dict["agent_config"])
        
        # 构建SQL
        columns = list(data_dict.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = list(data_dict.values())
        
        full_table = self._get_table_name(table)
        query = f"""
            INSERT INTO {full_table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        row = await self._fetchrow(query, *values)
        
        # 转换为字典并处理特殊字段
        result = dict(row)
        
        # 处理JSON字段
        if "agent_config" in result and result["agent_config"]:
            result["agent_config"] = json.loads(result["agent_config"])
        
        # 将UUID转为字符串
        for key in ["id", "author_id", "group_id", "post_id", "tag_id"]:
            if key in result and result[key]:
                result[key] = str(result[key])
        
        # 处理datetime字段
        for key in ["created_at", "updated_at", "published_at"]:
            if key in result and result[key]:
                result[key] = result[key].isoformat() if hasattr(result[key], 'isoformat') else result[key]
        
        return {"success": True, "id": str(result["id"]), "data": result}
    
    async def get(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """根据ID获取数据"""
        full_table = self._get_table_name(table)
        query = f"SELECT * FROM {full_table} WHERE id = $1"
        row = await self._fetchrow(query, id)
        
        if row is None:
            return {"success": False, "error": f"Record not found in {table}"}
        
        # 转换为字典
        data = dict(row)
        
        # 处理JSON字段
        if "agent_config" in data and data["agent_config"]:
            data["agent_config"] = json.loads(data["agent_config"])
        
        # 将UUID转为字符串
        for key in ["id", "author_id", "group_id", "post_id", "tag_id"]:
            if key in data and data[key]:
                data[key] = str(data[key])
        
        return {"success": True, "data": data}
    
    async def update(self, table: str, id: Union[str, int], data: dict) -> dict[str, Any]:
        """更新数据"""
        if not data:
            return {"success": False, "error": "No data to update"}
        
        # 处理特殊字段
        if "agent_config" in data and isinstance(data["agent_config"], dict):
            data["agent_config"] = json.dumps(data["agent_config"])
        
        # 自动更新 updated_at
        if table in [self.TABLE_USERS, self.TABLE_POSTS, self.TABLE_GROUPS]:
            data["updated_at"] = datetime.utcnow()
        
        # 构建SET子句
        columns = list(data.keys())
        set_clause = ", ".join([f"{col} = ${i+2}" for i, col in enumerate(columns)])
        values = list(data.values())
        
        full_table = self._get_table_name(table)
        query = f"""
            UPDATE {full_table}
            SET {set_clause}
            WHERE id = $1
            RETURNING id
        """
        
        row = await self._fetchrow(query, id, *values)
        
        if row is None:
            return {"success": False, "error": f"Record not found in {table}"}
        
        return {"success": True, "id": str(row["id"])}
    
    async def delete(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """删除数据"""
        full_table = self._get_table_name(table)
        query = f"DELETE FROM {full_table} WHERE id = $1 RETURNING id"
        row = await self._fetchrow(query, id)
        
        if row is None:
            return {"success": False, "error": f"Record not found in {table}"}
        
        return {"success": True, "message": f"Record deleted from {table}"}
    
    async def find(
        self,
        table: str,
        filters: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ) -> dict[str, Any]:
        """
        条件查询
        
        支持简单等于过滤，复杂查询需要专用方法
        """
        # 构建WHERE子句
        where_clause = ""
        values = []
        
        if filters:
            conditions = []
            for i, (key, value) in enumerate(filters.items()):
                conditions.append(f"{key} = ${i+1}")
                values.append(value)
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
        
        # 排序
        order_clause = ""
        if sort_by:
            direction = "DESC" if sort_desc else "ASC"
            order_clause = f"ORDER BY {sort_by} {direction}"
        
        full_table = self._get_table_name(table)
        query = f"""
            SELECT * FROM {full_table}
            {where_clause}
            {order_clause}
            LIMIT ${len(values)+1} OFFSET ${len(values)+2}
        """
        
        values.extend([limit, offset])
        rows = await self._fetch(query, *values)
        
        # 转换结果
        results = []
        for row in rows:
            data = dict(row)
            # 处理JSON字段
            if "agent_config" in data and data["agent_config"]:
                data["agent_config"] = json.loads(data["agent_config"])
            # UUID转字符串
            for key in ["id", "author_id", "group_id", "post_id", "tag_id"]:
                if key in data and data[key]:
                    data[key] = str(data[key])
            results.append(data)
        
        return {"success": True, "data": results, "count": len(results)}
    
    async def count(self, table: str, filters: Optional[dict] = None) -> dict[str, Any]:
        """统计数量"""
        where_clause = ""
        values = []
        
        if filters:
            conditions = []
            for i, (key, value) in enumerate(filters.items()):
                conditions.append(f"{key} = ${i+1}")
                values.append(value)
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
        
        full_table = self._get_table_name(table)
        query = f"SELECT COUNT(*) as count FROM {full_table} {where_clause}"
        row = await self._fetchrow(query, *values)
        
        return {"success": True, "count": row["count"]}
    
    async def init_schema(self) -> None:
        """初始化所有业务表"""
        # 按依赖顺序创建表
        await self.create_table(self.TABLE_USERS)
        await self.create_table(self.TABLE_GROUPS)
        await self.create_table(self.TABLE_TAGS)
        await self.create_table(self.TABLE_POSTS)
        await self.create_table(self.TABLE_POST_TAGS)
    
    # ========== 业务特有方法 ==========
    
    async def get_user_by_username(self, username: str) -> dict[str, Any]:
        """根据用户名获取用户（用于登录）"""
        query = f"SELECT * FROM {self.schema}.users WHERE username = $1"
        row = await self._fetchrow(query, username)
        
        if row is None:
            return {"success": False, "error": "User not found"}
        
        data = dict(row)
        if data.get("agent_config"):
            data["agent_config"] = json.loads(data["agent_config"])
        data["id"] = str(data["id"])
        
        return {"success": True, "data": data}
    
    async def get_posts_by_author(self, author_id: str, **kwargs) -> dict[str, Any]:
        """获取指定作者的文章列表"""
        filters = {"author_id": author_id}
        if "status" in kwargs:
            filters["status"] = kwargs.pop("status")
        return await self.find(self.TABLE_POSTS, filters=filters, **kwargs)
    
    async def get_posts_by_group(self, group_id: str, **kwargs) -> dict[str, Any]:
        """获取指定分组的文章列表"""
        return await self.find(
            self.TABLE_POSTS,
            filters={"group_id": group_id},
            **kwargs
        )
    
    async def get_post_tags(self, post_id: str) -> dict[str, Any]:
        """获取文章的所有标签"""
        query = f"""
            SELECT t.* FROM {self.schema}.tags t
            JOIN {self.schema}.post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = $1
        """
        rows = await self._fetch(query, post_id)
        
        results = []
        for row in rows:
            data = dict(row)
            data["id"] = str(data["id"])
            results.append(data)
        
        return {"success": True, "data": results}
    
    async def add_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """为文章添加标签"""
        try:
            await self._execute(
                f"INSERT INTO {self.schema}.post_tags (post_id, tag_id) VALUES ($1, $2)",
                post_id, tag_id
            )
            return {"success": True}
        except asyncpg.UniqueViolationError:
            return {"success": False, "error": "Tag already added to post"}
    
    async def remove_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """移除文章的标签"""
        await self._execute(
            f"DELETE FROM {self.schema}.post_tags WHERE post_id = $1 AND tag_id = $2",
            post_id, tag_id
        )
        return {"success": True}
    
    async def increment_view_count(self, post_id: str) -> dict[str, Any]:
        """增加文章浏览计数"""
        await self._execute(
            f"UPDATE {self.schema}.posts SET view_count = view_count + 1 WHERE id = $1",
            post_id
        )
        return {"success": True}
