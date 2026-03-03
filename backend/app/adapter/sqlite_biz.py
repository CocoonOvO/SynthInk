"""
SQLite 业务库适配器（用于测试环境）
用于在测试环境中替代PostgreSQL
使用 aiosqlite 实现异步操作
"""
import json
import aiosqlite
from datetime import datetime
from typing import Any, Optional, Union, List
from pydantic import BaseModel

from .base import BaseAdapter


class SQLiteBizAdapter(BaseAdapter):
    """
    SQLite 业务数据库适配器（测试用）
    
    接口与PostgresAdapter保持一致，用于：
    - 单元测试
    - 开发环境
    - CI/CD环境
    
    注意：生产环境请使用PostgreSQL
    """
    
    # 表名常量（与PostgresAdapter保持一致）
    TABLE_USERS = "users"
    TABLE_POSTS = "posts"
    TABLE_TAGS = "tags"
    TABLE_GROUPS = "groups"
    TABLE_POST_TAGS = "post_tags"
    
    # 所有表名列表
    ALL_TABLES = [TABLE_USERS, TABLE_POSTS, TABLE_TAGS, TABLE_GROUPS, TABLE_POST_TAGS]
    
    def __init__(self, dsn: str = "sqlite+aiosqlite:///:memory:"):
        """
        初始化适配器
        
        Args:
            dsn: SQLite连接字符串
                 格式: sqlite+aiosqlite:///path/to/db.db 或 sqlite+aiosqlite:///:memory:
        """
        self.dsn = dsn
        self._conn: Optional[aiosqlite.Connection] = None
        
        # 解析数据库路径
        if ":memory:" in dsn:
            self.db_path = ":memory:"
        elif "///" in dsn:
            self.db_path = dsn.split("///")[1]
        else:
            self.db_path = "./test.db"
    
    async def connect(self) -> None:
        """建立数据库连接"""
        self._conn = await aiosqlite.connect(self.db_path)
        # 启用外键支持
        await self._conn.execute("PRAGMA foreign_keys = ON")
        # 设置行工厂为字典
        self._conn.row_factory = aiosqlite.Row
    
    async def disconnect(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            await self._conn.close()
            self._conn = None
    
    async def _execute(self, query: str, *args) -> None:
        """执行SQL语句"""
        if not self._conn:
            raise RuntimeError("Database not connected")
        await self._conn.execute(query, args)
        await self._conn.commit()
    
    async def _fetchrow(self, query: str, *args) -> Optional[dict]:
        """获取单行结果"""
        if not self._conn:
            raise RuntimeError("Database not connected")
        async with self._conn.execute(query, args) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def _fetch(self, query: str, *args) -> List[dict]:
        """获取多行结果"""
        if not self._conn:
            raise RuntimeError("Database not connected")
        async with self._conn.execute(query, args) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _generate_uuid(self) -> str:
        """生成UUID（SQLite没有内置UUID函数）"""
        import uuid
        return str(uuid.uuid4())
    
    def _json_dumps(self, data: Any) -> str:
        """将数据转换为JSON字符串"""
        if data is None:
            return None
        return json.dumps(data)
    
    def _json_loads(self, data: str) -> Any:
        """将JSON字符串转换为数据"""
        if data is None:
            return None
        return json.loads(data)
    
    # ========== 表管理 ==========
    
    async def create_table(self, name: str) -> dict[str, Any]:
        """创建数据表"""
        if name == self.TABLE_USERS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    hashed_password TEXT NOT NULL,
                    display_name TEXT,
                    avatar_url TEXT,
                    bio TEXT,
                    user_type TEXT DEFAULT 'user',
                    agent_model TEXT,
                    agent_provider TEXT,
                    agent_config TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_superuser INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_GROUPS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    icon TEXT,
                    sort_order INTEGER DEFAULT 0,
                    post_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_TAGS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT,
                    description TEXT,
                    post_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        elif name == self.TABLE_POSTS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE,
                    content TEXT,
                    summary TEXT,
                    status TEXT DEFAULT 'draft',
                    author_id TEXT NOT NULL,
                    group_id TEXT,
                    cover_image TEXT,
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    is_top INTEGER DEFAULT 0,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author_id) REFERENCES users(id),
                    FOREIGN KEY (group_id) REFERENCES groups(id)
                )
            """)
        
        elif name == self.TABLE_POST_TAGS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS post_tags (
                    post_id TEXT NOT NULL,
                    tag_id TEXT NOT NULL,
                    PRIMARY KEY (post_id, tag_id),
                    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)
        
        return {"success": True, "table": name}
    
    async def drop_table(self, name: str) -> dict[str, Any]:
        """删除数据表"""
        await self._execute(f"DROP TABLE IF EXISTS {name}")
        return {"success": True, "table": name}
    
    async def init_schema(self) -> None:
        """初始化所有表"""
        for table in self.ALL_TABLES:
            await self.create_table(table)
    
    # ========== CRUD操作 ==========
    
    async def insert(self, table: str, data: Union[BaseModel, dict]) -> dict[str, Any]:
        """插入数据"""
        if isinstance(data, BaseModel):
            data = data.model_dump()
        
        # 生成UUID（如果没有id）
        if "id" not in data or not data["id"]:
            data["id"] = self._generate_uuid()
        
        # 处理JSON字段
        if "agent_config" in data and data["agent_config"] is not None:
            data["agent_config"] = self._json_dumps(data["agent_config"])
        
        # 构建INSERT语句
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        await self._execute(query, *data.values())
        
        # 返回插入的数据
        return await self.get(table, data["id"])
    
    async def get(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """根据ID获取数据"""
        query = f"SELECT * FROM {table} WHERE id = ?"
        result = await self._fetchrow(query, id)
        
        if result and "agent_config" in result and result["agent_config"]:
            result["agent_config"] = self._json_loads(result["agent_config"])
        
        return result
    
    async def update(self, table: str, id: Union[str, int], data: dict) -> dict[str, Any]:
        """更新数据"""
        # 处理JSON字段
        if "agent_config" in data and data["agent_config"] is not None:
            data["agent_config"] = self._json_dumps(data["agent_config"])
        
        # 构建UPDATE语句
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        await self._execute(query, *data.values(), id)
        
        return await self.get(table, id)
    
    async def delete(self, table: str, id: Union[str, int]) -> dict[str, Any]:
        """删除数据"""
        query = f"DELETE FROM {table} WHERE id = ?"
        await self._execute(query, id)
        return {"success": True, "id": id}
    
    # ========== 查询操作 ==========

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
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                values.append(value)
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        # 排序
        order_clause = ""
        if sort_by:
            direction = "DESC" if sort_desc else "ASC"
            order_clause = f"ORDER BY {sort_by} {direction}"

        query = f"""
            SELECT * FROM {table}
            {where_clause}
            {order_clause}
            LIMIT ? OFFSET ?
        """

        values.extend([limit, offset])
        rows = await self._fetch(query, *values)

        # 转换结果
        results = []
        for row in rows:
            data = dict(row)
            # 处理JSON字段
            if "agent_config" in data and data["agent_config"]:
                data["agent_config"] = self._json_loads(data["agent_config"])
            results.append(data)

        return {"success": True, "data": results, "count": len(results)}

    async def count(self, table: str, filters: Optional[dict] = None) -> dict[str, Any]:
        """统计数量"""
        where_clause = ""
        values = []

        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                values.append(value)
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        query = f"SELECT COUNT(*) as count FROM {table} {where_clause}"
        row = await self._fetchrow(query, *values)

        return {"success": True, "count": row["count"]}

    async def find_one(self, table: str, **filters) -> Optional[dict]:
        """根据条件查找单条数据"""
        if not filters:
            return None

        where_clause = " AND ".join([f"{k} = ?" for k in filters.keys()])
        query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1"

        result = await self._fetchrow(query, *filters.values())

        if result and "agent_config" in result and result["agent_config"]:
            result["agent_config"] = self._json_loads(result["agent_config"])

        return result

    async def find_many(self, table: str, **filters) -> List[dict]:
        """根据条件查找多条数据"""
        if filters:
            where_clause = " AND ".join([f"{k} = ?" for k in filters.keys()])
            query = f"SELECT * FROM {table} WHERE {where_clause}"
            results = await self._fetch(query, *filters.values())
        else:
            query = f"SELECT * FROM {table}"
            results = await self._fetch(query)

        for result in results:
            if "agent_config" in result and result["agent_config"]:
                result["agent_config"] = self._json_loads(result["agent_config"])

        return results
    
    # ========== 用户相关 ==========
    
    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        return await self.find_one("users", username=username)
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """根据邮箱获取用户"""
        return await self.find_one("users", email=email)
    
    # ========== 文章相关 ==========
    
    async def get_posts_by_author(self, author_id: str) -> List[dict]:
        """获取作者的所有文章"""
        return await self.find_many("posts", author_id=author_id)
    
    async def get_posts_by_group(self, group_id: str) -> List[dict]:
        """获取分组的所有文章"""
        return await self.find_many("posts", group_id=group_id)
    
    async def get_posts_by_tag(self, tag_id: str) -> List[dict]:
        """获取标签的所有文章"""
        query = """
            SELECT p.* FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            WHERE pt.tag_id = ?
        """
        return await self._fetch(query, tag_id)
