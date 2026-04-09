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
    TABLE_COMMENTS = "comments"
    
    # 所有表名列表
    ALL_TABLES = [TABLE_USERS, TABLE_POSTS, TABLE_TAGS, TABLE_GROUPS, TABLE_POST_TAGS, TABLE_COMMENTS]
    
    def __init__(self, dsn: str, schema: str = "public"):
        """
        初始化适配器
        
        Args:
            dsn: PostgreSQL 连接字符串
                 格式: postgresql://user:password@host:port/database
            schema: PostgreSQL schema名称，默认为"public"
        """
        self.dsn = dsn
        self._schema = schema
        self._pool: Optional[asyncpg.Pool] = None
    
    @property
    def schema(self) -> str:
        """获取数据库schema名称"""
        return self._schema
    
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
    
    # 允许的表名白名单（防止SQL注入）
    VALID_TABLES = {
        'users', 'posts', 'tags', 'groups', 'post_tags', 'comments', 'likes',
        'seo_configs', 'seo_templates', 'seo_analyses', 'seo_reports',
        'metadata', 'redirects'  # SEO模块相关表
    }
    
    def _get_table_name(self, table: str) -> str:
        """
        获取带schema的完整表名
        
        进行表名白名单校验，防止SQL注入攻击
        支持两种格式：
        1. 纯表名（如 'posts'）-> 返回 '{schema}.posts'
        2. 带schema前缀（如 'seo.metadata'）-> 直接返回，只校验表名部分
        """
        # 检查是否已包含schema前缀
        if '.' in table:
            # 分离schema和表名
            parts = table.split('.')
            if len(parts) != 2:
                raise ValueError(f"Invalid table name format: {table}. Expected 'schema.table' or 'table'")
            schema_part, table_part = parts
            # 验证schema和表名格式（只允许字母、数字、下划线）
            if not schema_part.replace('_', '').isalnum():
                raise ValueError(f"Invalid schema name format: {schema_part}")
            if not table_part.replace('_', '').isalnum():
                raise ValueError(f"Invalid table name format: {table_part}")
            # 表名白名单校验（只校验表名部分）
            if table_part not in self.VALID_TABLES:
                raise ValueError(f"Invalid table name: {table_part}. Must be one of: {', '.join(sorted(self.VALID_TABLES))}")
            return table
        else:
            # 纯表名，使用当前schema
            # 表名白名单校验
            if table not in self.VALID_TABLES:
                raise ValueError(f"Invalid table name: {table}. Must be one of: {', '.join(sorted(self.VALID_TABLES))}")
            # 额外的表名格式校验（只允许字母、数字、下划线）
            if not table.replace('_', '').isalnum():
                raise ValueError(f"Invalid table name format: {table}")
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
    
    @property
    def pool(self) -> Optional[asyncpg.Pool]:
        """获取数据库连接池"""
        return self._pool
    
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
                    slug VARCHAR(100) UNIQUE,
                    content TEXT NOT NULL,
                    introduction TEXT,
                    cover_image TEXT,
                    status VARCHAR(20) DEFAULT 'draft',
                    author_id UUID REFERENCES {self.schema}.users(id) ON DELETE CASCADE,
                    group_id UUID REFERENCES {self.schema}.groups(id) ON DELETE SET NULL,
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
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
        
        elif name == self.TABLE_COMMENTS:
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    post_id UUID NOT NULL REFERENCES {self.schema}.posts(id) ON DELETE CASCADE,
                    author_id UUID NOT NULL REFERENCES {self.schema}.users(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    parent_id UUID REFERENCES {self.schema}.comments(id) ON DELETE CASCADE,
                    is_deleted BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == 'metadata':
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    resource_id VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(20) NOT NULL,
                    slug VARCHAR(100) UNIQUE NOT NULL,
                    meta_title VARCHAR(200),
                    meta_description TEXT,
                    meta_keywords VARCHAR(500),
                    canonical_url TEXT,
                    og_title VARCHAR(200),
                    og_description TEXT,
                    og_image TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(resource_id, resource_type)
                )
            """)
        
        elif name == 'redirects':
            await self._execute(f"""
                CREATE TABLE IF NOT EXISTS {full_table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    old_slug VARCHAR(100) UNIQUE NOT NULL,
                    new_slug VARCHAR(100) NOT NULL,
                    resource_type VARCHAR(20) DEFAULT 'post',
                    status_code INTEGER DEFAULT 301,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
        
        # 处理datetime字符串转换为datetime对象
        from datetime import datetime
        for key in ["created_at", "updated_at", "published_at"]:
            if key in data_dict and isinstance(data_dict[key], str):
                try:
                    # 尝试解析ISO格式时间字符串
                    data_dict[key] = datetime.fromisoformat(data_dict[key].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # 如果解析失败，删除该字段让数据库使用默认值
                    del data_dict[key]
        
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
        for key in ["id", "author_id", "group_id", "post_id", "tag_id", "parent_id"]:
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
        for key in ["id", "author_id", "group_id", "post_id", "tag_id", "parent_id"]:
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
        
        # 处理datetime字符串转换为datetime对象
        for key in ["created_at", "updated_at", "published_at"]:
            if key in data and isinstance(data[key], str):
                try:
                    # 尝试解析ISO格式时间字符串
                    data[key] = datetime.fromisoformat(data[key].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # 如果解析失败，删除该字段
                    del data[key]
        
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
        await self.create_table(self.TABLE_COMMENTS)
    
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
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # 添加关联
                    await conn.execute(
                        f"INSERT INTO {self.schema}.post_tags (post_id, tag_id) VALUES ($1, $2)",
                        post_id, tag_id
                    )
                    # 更新标签使用计数
                    await conn.execute(
                        f"UPDATE {self.schema}.tags SET post_count = post_count + 1 WHERE id = $1",
                        tag_id
                    )
            return {"success": True}
        except asyncpg.UniqueViolationError:
            return {"success": False, "error": "Tag already added to post"}

    async def remove_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """移除文章的标签"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 移除关联
                await conn.execute(
                    f"DELETE FROM {self.schema}.post_tags WHERE post_id = $1 AND tag_id = $2",
                    post_id, tag_id
                )
                # 更新标签使用计数
                await conn.execute(
                    f"UPDATE {self.schema}.tags SET post_count = post_count - 1 WHERE id = $1",
                    tag_id
                )
        return {"success": True}
    
    async def increment_view_count(self, post_id: str) -> dict[str, Any]:
        """增加文章浏览计数"""
        await self._execute(
            f"UPDATE {self.schema}.posts SET view_count = view_count + 1 WHERE id = $1",
            post_id
        )
        return {"success": True}
    
    # ========== 搜索功能 ==========
    
    async def search(
        self,
        query: str,
        search_type: str = "all",
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        全文搜索
        
        使用PostgreSQL的tsvector进行全文搜索，支持中文。
        现阶段使用简单的LIKE查询作为基础实现，后续可升级为tsvector。
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型 (all/posts/tags/users/groups/comments)
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            搜索结果字典，包含各类型数据
        """
        if not query or not query.strip():
            return {
                "success": True,
                "data": {
                    "posts": [],
                    "tags": [],
                    "users": [],
                    "groups": [],
                    "comments": [],
                    "total": 0
                }
            }
        
        search_pattern = f"%{query.strip()}%"
        results = {
            "posts": [],
            "tags": [],
            "users": [],
            "groups": [],
            "comments": [],
            "total": 0
        }
        
        # BUG-028修复: 当type=all时，limit应该限制所有结果的总数
        # 使用remaining_limit来跟踪剩余可返回的结果数
        remaining_limit = limit
        
        try:
            # 搜索文章
            if search_type in ["all", "posts"] and remaining_limit > 0:
                posts_query = f"""
                    SELECT id, title, slug, introduction, content, cover_image, status,
                           author_id, group_id, view_count, created_at, updated_at
                    FROM {self.schema}.posts
                    WHERE status = 'published'
                    AND (title ILIKE $1 OR introduction ILIKE $1 OR content ILIKE $1)
                    ORDER BY 
                        CASE 
                            WHEN title ILIKE $2 THEN 1
                            WHEN introduction ILIKE $2 THEN 2
                            ELSE 3
                        END,
                        created_at DESC
                    LIMIT $3 OFFSET $4
                """
                exact_pattern = f"%{query.strip()}%"
                posts_rows = await self._fetch(posts_query, search_pattern, exact_pattern, remaining_limit if search_type != "all" else remaining_limit, offset)
                
                for row in posts_rows:
                    if search_type == "all" and len(results["posts"]) >= remaining_limit:
                        break
                    data = dict(row)
                    data["id"] = str(data["id"])
                    data["author_id"] = str(data["author_id"]) if data.get("author_id") else None
                    data["group_id"] = str(data["group_id"]) if data.get("group_id") else None
                    # BUG-029修复: 确保slug和status字段存在
                    data["slug"] = data.get("slug", "")
                    data["status"] = data.get("status", "published")
                    results["posts"].append(data)
                
                if search_type == "all":
                    remaining_limit -= len(results["posts"])
                
                # 获取文章总数
                posts_count_query = f"""
                    SELECT COUNT(*) as count FROM {self.schema}.posts
                    WHERE status = 'published'
                    AND (title ILIKE $1 OR introduction ILIKE $1 OR content ILIKE $1)
                """
                posts_count_row = await self._fetchrow(posts_count_query, search_pattern)
                results["total"] += posts_count_row["count"] if posts_count_row else 0
            
            # 搜索标签
            if search_type in ["all", "tags"] and remaining_limit > 0:
                tags_query = f"""
                    SELECT * FROM {self.schema}.tags
                    WHERE name ILIKE $1 OR description ILIKE $1
                    ORDER BY post_count DESC, name ASC
                    LIMIT $2 OFFSET $3
                """
                tags_rows = await self._fetch(tags_query, search_pattern, remaining_limit if search_type != "all" else remaining_limit, offset)
                
                for row in tags_rows:
                    if search_type == "all" and len(results["tags"]) >= remaining_limit:
                        break
                    data = dict(row)
                    data["id"] = str(data["id"])
                    results["tags"].append(data)
                
                if search_type == "all":
                    remaining_limit -= len(results["tags"])
                
                # 获取标签总数
                tags_count_query = f"""
                    SELECT COUNT(*) as count FROM {self.schema}.tags
                    WHERE name ILIKE $1 OR description ILIKE $1
                """
                tags_count_row = await self._fetchrow(tags_count_query, search_pattern)
                results["total"] += tags_count_row["count"] if tags_count_row else 0
            
            # 搜索用户
            if search_type in ["all", "users"] and remaining_limit > 0:
                users_query = f"""
                    SELECT id, username, display_name, avatar_url, bio, user_type, 
                           agent_model, agent_provider, created_at
                    FROM {self.schema}.users
                    WHERE is_active = true
                    AND (username ILIKE $1 OR display_name ILIKE $1 OR bio ILIKE $1)
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                """
                users_rows = await self._fetch(users_query, search_pattern, remaining_limit if search_type != "all" else remaining_limit, offset)
                
                for row in users_rows:
                    if search_type == "all" and len(results["users"]) >= remaining_limit:
                        break
                    data = dict(row)
                    data["id"] = str(data["id"])
                    results["users"].append(data)
                
                if search_type == "all":
                    remaining_limit -= len(results["users"])
                
                # 获取用户总数
                users_count_query = f"""
                    SELECT COUNT(*) as count FROM {self.schema}.users
                    WHERE is_active = true
                    AND (username ILIKE $1 OR display_name ILIKE $1 OR bio ILIKE $1)
                """
                users_count_row = await self._fetchrow(users_count_query, search_pattern)
                results["total"] += users_count_row["count"] if users_count_row else 0
            
            # 搜索分组
            if search_type in ["all", "groups"] and remaining_limit > 0:
                groups_query = f"""
                    SELECT * FROM {self.schema}.groups
                    WHERE name ILIKE $1 OR description ILIKE $1
                    ORDER BY post_count DESC, sort_order ASC
                    LIMIT $2 OFFSET $3
                """
                groups_rows = await self._fetch(groups_query, search_pattern, remaining_limit if search_type != "all" else remaining_limit, offset)
                
                for row in groups_rows:
                    if search_type == "all" and len(results["groups"]) >= remaining_limit:
                        break
                    data = dict(row)
                    data["id"] = str(data["id"])
                    results["groups"].append(data)
                
                if search_type == "all":
                    remaining_limit -= len(results["groups"])
                
                # 获取分组总数
                groups_count_query = f"""
                    SELECT COUNT(*) as count FROM {self.schema}.groups
                    WHERE name ILIKE $1 OR description ILIKE $1
                """
                groups_count_row = await self._fetchrow(groups_count_query, search_pattern)
                results["total"] += groups_count_row["count"] if groups_count_row else 0
            
            # 搜索评论
            if search_type in ["all", "comments"] and remaining_limit > 0:
                comments_query = f"""
                    SELECT c.*, u.username as author_name, u.display_name as author_display_name,
                           u.avatar_url as author_avatar_url
                    FROM {self.schema}.comments c
                    JOIN {self.schema}.users u ON c.author_id = u.id
                    WHERE c.is_deleted = false
                    AND c.content ILIKE $1
                    ORDER BY c.created_at DESC
                    LIMIT $2 OFFSET $3
                """
                comments_rows = await self._fetch(comments_query, search_pattern, remaining_limit if search_type != "all" else remaining_limit, offset)
                
                for row in comments_rows:
                    if search_type == "all" and len(results["comments"]) >= remaining_limit:
                        break
                    data = dict(row)
                    data["id"] = str(data["id"])
                    data["post_id"] = str(data["post_id"]) if data.get("post_id") else None
                    data["author_id"] = str(data["author_id"]) if data.get("author_id") else None
                    data["parent_id"] = str(data["parent_id"]) if data.get("parent_id") else None
                    results["comments"].append(data)
                
                if search_type == "all":
                    remaining_limit -= len(results["comments"])
                
                # 获取评论总数
                comments_count_query = f"""
                    SELECT COUNT(*) as count FROM {self.schema}.comments
                    WHERE is_deleted = false
                    AND content ILIKE $1
                """
                comments_count_row = await self._fetchrow(comments_count_query, search_pattern)
                results["total"] += comments_count_row["count"] if comments_count_row else 0

            return {"success": True, "data": results}

        except Exception as e:
            return {"success": False, "error": f"搜索失败: {str(e)}"}

    async def search_suggest(self, query: str, limit: int = 5) -> dict[str, Any]:
        """
        获取搜索建议

        根据输入的关键词返回相关建议，用于搜索框自动补全。
        返回标签名、文章标题、用户名等。

        Args:
            query: 搜索关键词
            limit: 建议数量

        Returns:
            建议列表，格式: [{"text": "...", "type": "tag|post|user"}, ...]
        """
        if not query or not query.strip():
            return {"success": True, "data": {"suggestions": []}}

        search_pattern = f"%{query.strip()}%"
        suggestions = []

        try:
            # 搜索标签建议
            tags_query = f"""
                SELECT name, 'tag' as type FROM {self.schema}.tags
                WHERE name ILIKE $1
                ORDER BY post_count DESC
                LIMIT $2
            """
            tags_rows = await self._fetch(tags_query, search_pattern, limit)
            for row in tags_rows:
                suggestions.append({
                    "text": row["name"],
                    "type": "tag"
                })

            # 搜索文章标题建议
            posts_query = f"""
                SELECT title, 'post' as type FROM {self.schema}.posts
                WHERE status = 'published' AND title ILIKE $1
                ORDER BY view_count DESC, created_at DESC
                LIMIT $2
            """
            posts_rows = await self._fetch(posts_query, search_pattern, limit)
            for row in posts_rows:
                suggestions.append({
                    "text": row["title"],
                    "type": "post"
                })

            # 搜索用户建议
            users_query = f"""
                SELECT username, display_name, 'user' as type
                FROM {self.schema}.users
                WHERE is_active = true AND (username ILIKE $1 OR display_name ILIKE $1)
                ORDER BY created_at DESC
                LIMIT $2
            """
            users_rows = await self._fetch(users_query, search_pattern, limit)
            for row in users_rows:
                display_text = row["display_name"] or row["username"]
                suggestions.append({
                    "text": display_text,
                    "type": "user"
                })

            # 去重并限制数量
            seen = set()
            unique_suggestions = []
            for item in suggestions:
                if item["text"] not in seen and len(unique_suggestions) < limit:
                    seen.add(item["text"])
                    unique_suggestions.append(item)

            return {"success": True, "data": {"suggestions": unique_suggestions}}

        except Exception as e:
            return {"success": False, "error": f"获取搜索建议失败: {str(e)}"}

    async def get_stats_summary(self) -> dict[str, Any]:
        """
        获取统计数据摘要

        使用单次聚合查询获取：
        - 智能体创作者数量（user_type='agent'）
        - 文章总数
        - 总浏览量（所有文章view_count之和）
        """
        try:
            query = f"""
                SELECT
                    (SELECT COUNT(*) FROM {self.schema}.users WHERE user_type = 'agent') as agent_count,
                    (SELECT COUNT(*) FROM {self.schema}.posts) as post_count,
                    (SELECT COALESCE(SUM(view_count), 0) FROM {self.schema}.posts) as total_views
            """

            row = await self._fetchrow(query)

            return {
                "success": True,
                "data": {
                    "agent_count": row["agent_count"],
                    "post_count": row["post_count"],
                    "total_views": row["total_views"]
                }
            }
        except Exception as e:
            return {"success": False, "error": f"获取统计数据失败: {str(e)}"}

    # ========== T056: 原始SQL执行方法封装 ==========

    async def execute_raw(self, query: str, *params) -> dict[str, Any]:
        """
        执行原始SQL查询（SELECT）

        用于执行无法通过标准CRUD方法实现的复杂查询。
        参数使用参数化方式传递，防止SQL注入。
        """
        try:
            rows = await self._fetch(query, *params)
            results = [dict(row) for row in rows]
            return {"success": True, "data": results}
        except Exception as e:
            return {"success": False, "error": f"查询执行失败: {str(e)}"}

    async def execute_raw_command(self, query: str, *params) -> dict[str, Any]:
        """
        执行原始SQL命令（INSERT/UPDATE/DELETE）

        用于执行无法通过标准CRUD方法实现的复杂操作。
        参数使用参数化方式传递，防止SQL注入。
        """
        try:
            row_count = await self._execute(query, *params)
            return {"success": True, "row_count": row_count}
        except Exception as e:
            return {"success": False, "error": f"命令执行失败: {str(e)}"}

    async def get_search_suggestions(self, search_pattern: str, limit: int = 10) -> dict[str, Any]:
        """
        获取搜索建议

        搜索标签、文章标题、用户等，返回建议列表。
        """
        suggestions = []

        try:
            # 搜索标签建议
            tags_query = f"""
                SELECT name, 'tag' as type FROM {self.schema}.tags
                WHERE name ILIKE $1
                ORDER BY post_count DESC
                LIMIT $2
            """
            tags_rows = await self._fetch(tags_query, search_pattern, limit)
            for row in tags_rows:
                suggestions.append({"text": row["name"], "type": "tag"})

            # 搜索文章标题建议
            posts_query = f"""
                SELECT title, 'post' as type FROM {self.schema}.posts
                WHERE status = 'published' AND title ILIKE $1
                ORDER BY view_count DESC, created_at DESC
                LIMIT $2
            """
            posts_rows = await self._fetch(posts_query, search_pattern, limit)
            for row in posts_rows:
                suggestions.append({"text": row["title"], "type": "post"})

            # 搜索用户建议
            users_query = f"""
                SELECT username, display_name, 'user' as type
                FROM {self.schema}.users
                WHERE is_active = true AND (username ILIKE $1 OR display_name ILIKE $1)
                ORDER BY created_at DESC
                LIMIT $2
            """
            users_rows = await self._fetch(users_query, search_pattern, limit)
            for row in users_rows:
                display_text = row["display_name"] or row["username"]
                suggestions.append({"text": display_text, "type": "user"})

            # 去重并限制数量
            seen = set()
            unique_suggestions = []
            for item in suggestions:
                if item["text"] not in seen and len(unique_suggestions) < limit:
                    seen.add(item["text"])
                    unique_suggestions.append(item)

            return {"success": True, "data": unique_suggestions}

        except Exception as e:
            return {"success": False, "error": f"获取搜索建议失败: {str(e)}"}

    async def check_ip_like_limit(self, ip_address: str, daily_limit: int) -> dict[str, Any]:
        """
        检查IP点赞次数限制

        检查指定IP在今日内的点赞次数是否超过限制。
        """
        from datetime import datetime, timedelta

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        query = f"""
            SELECT COUNT(*) as count
            FROM {self.schema}.likes
            WHERE ip_address = $1::inet
            AND created_at >= $2
            AND anonymous_token IS NOT NULL
        """

        try:
            row = await self._fetchrow(query, ip_address, today_start)
            ip_count = row["count"] if row else 0

            if ip_count >= daily_limit:
                return {
                    "success": True,
                    "allowed": False,
                    "message": f"该IP今日点赞次数已达上限 ({daily_limit}次)"
                }

            return {"success": True, "allowed": True, "message": ""}

        except Exception as e:
            # 数据库错误时允许操作（降级处理）
            return {"success": True, "allowed": True, "message": ""}

    async def increment_like_count(self, post_id: str) -> dict[str, Any]:
        """
        原子增加文章点赞数
        """
        query = f"""
            UPDATE {self.schema}.posts
            SET like_count = like_count + 1
            WHERE id = $1
        """
        try:
            row_count = await self._execute(query, post_id)
            return {"success": True, "row_count": row_count}
        except Exception as e:
            return {"success": False, "error": f"增加点赞数失败: {str(e)}"}

    async def decrement_like_count(self, post_id: str) -> dict[str, Any]:
        """
        原子减少文章点赞数
        """
        query = f"""
            UPDATE {self.schema}.posts
            SET like_count = like_count - 1
            WHERE id = $1 AND like_count > 0
        """
        try:
            row_count = await self._execute(query, post_id)
            return {"success": True, "row_count": row_count}
        except Exception as e:
            return {"success": False, "error": f"减少点赞数失败: {str(e)}"}
