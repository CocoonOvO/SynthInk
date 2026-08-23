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
    TABLE_EXTERNAL_LINKS = "external_links"
    TABLE_PAT_TOKENS = "user_api_tokens"
    TABLE_COMMENTS = "comments"
    TABLE_LIKES = "likes"
    
    # 所有表名列表
    ALL_TABLES = [TABLE_USERS, TABLE_POSTS, TABLE_TAGS, TABLE_GROUPS, TABLE_POST_TAGS, TABLE_EXTERNAL_LINKS, TABLE_PAT_TOKENS, TABLE_COMMENTS, TABLE_LIKES]

    # 白名单（与 Postgres 保持一致，供校验复用）
    VALID_TABLES = {TABLE_USERS, TABLE_POSTS, TABLE_TAGS, TABLE_GROUPS, TABLE_POST_TAGS, TABLE_EXTERNAL_LINKS, TABLE_PAT_TOKENS, TABLE_COMMENTS, TABLE_LIKES, "seo_configs", "seo_templates", "seo_analyses", "seo_reports", "metadata", "redirects"}
    
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
        
        elif name == self.TABLE_EXTERNAL_LINKS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS external_links (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    cover_image TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        elif name == self.TABLE_PAT_TOKENS:
            # PAT 凭证表（SQLite 适配：TEXT 类型，DATETIME）
            await self._execute("""
                CREATE TABLE IF NOT EXISTS user_api_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    scopes TEXT,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    revoked INTEGER DEFAULT 0,
                    last_used_at DATETIME,
                    UNIQUE(user_id, name)
                )
            """)

        elif name == self.TABLE_COMMENTS:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    author_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    author_name TEXT,
                    author_email TEXT,
                    ip_address TEXT,
                    content TEXT NOT NULL,
                    parent_id TEXT REFERENCES comments(id) ON DELETE CASCADE,
                    is_deleted INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

        elif name == self.TABLE_LIKES:
            await self._execute("""
                CREATE TABLE IF NOT EXISTS likes (
                    id TEXT PRIMARY KEY,
                    post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                    anonymous_token TEXT,
                    like_type TEXT DEFAULT 'user',
                    ip_address TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        if "scopes" in data and isinstance(data["scopes"], (dict, list)):
            data["scopes"] = self._json_dumps(data["scopes"])
        
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
        # scopes JSON 处理（PAT 表）
        if "scopes" in data and isinstance(data["scopes"], (dict, list)):
            data["scopes"] = self._json_dumps(data["scopes"])
        
        # 构建UPDATE语句
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        # 仅对含 updated_at 列的表自动更新时间戳，避免 PAT/likes 等表报错
        tables_with_updated_at = {"users", "posts", "groups", "external_links", "comments"}
        if table in tables_with_updated_at:
            query = f"UPDATE {table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        else:
            query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        
        try:
            await self._execute(query, *data.values(), id)
        except Exception as e:
            # 兼容部分旧库 updated_at 列缺失的降级：去掉 updated_at 再试一次
            if "updated_at" in query and "no such column" in str(e).lower():
                fallback = f"UPDATE {table} SET {set_clause} WHERE id = ?"
                await self._execute(fallback, *data.values(), id)
            else:
                raise
        
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

    async def search(
        self,
        query: str,
        search_type: str = "all",
        limit: int = 20,
        offset: int = 0
    ) -> dict[str, Any]:
        """
        全文搜索（SQLite简化实现）
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型 (all/posts/tags/users/groups/comments)
            limit: 返回数量
            offset: 偏移量
            
        Returns:
            搜索结果字典
        """
        results = []
        total = 0
        
        # 简单的LIKE搜索实现
        search_pattern = f"%{query}%"
        
        if search_type in ["all", "posts"]:
            # 搜索文章标题和内容
            sql = """
                SELECT id, title as name, content as description, 'post' as type,
                       author_id, created_at, updated_at
                FROM posts
                WHERE title LIKE ? OR content LIKE ?
                LIMIT ? OFFSET ?
            """
            posts = await self._fetch(sql, search_pattern, search_pattern, limit, offset)
            results.extend(posts)
            
            # 计算总数
            count_sql = "SELECT COUNT(*) as count FROM posts WHERE title LIKE ? OR content LIKE ?"
            count_result = await self._fetch(count_sql, search_pattern, search_pattern)
            total += count_result[0].get("count", 0) if count_result else 0
        
        if search_type in ["all", "tags"]:
            # 搜索标签
            sql = """
                SELECT id, name, description, 'tag' as type,
                       created_at, updated_at
                FROM tags
                WHERE name LIKE ? OR description LIKE ?
                LIMIT ? OFFSET ?
            """
            tags = await self._fetch(sql, search_pattern, search_pattern, limit, offset)
            results.extend(tags)
            
            count_sql = "SELECT COUNT(*) as count FROM tags WHERE name LIKE ? OR description LIKE ?"
            count_result = await self._fetch(count_sql, search_pattern, search_pattern)
            total += count_result[0].get("count", 0) if count_result else 0
        
        if search_type in ["all", "users"]:
            # 搜索用户
            sql = """
                SELECT id, username as name, bio as description, 'user' as type,
                       created_at, updated_at
                FROM users
                WHERE username LIKE ? OR bio LIKE ?
                LIMIT ? OFFSET ?
            """
            users = await self._fetch(sql, search_pattern, search_pattern, limit, offset)
            results.extend(users)
            
            count_sql = "SELECT COUNT(*) as count FROM users WHERE username LIKE ? OR bio LIKE ?"
            count_result = await self._fetch(count_sql, search_pattern, search_pattern)
            total += count_result[0].get("count", 0) if count_result else 0
        
        if search_type in ["all", "groups"]:
            # 搜索分组
            sql = """
                SELECT id, name, description, 'group' as type,
                       created_at, updated_at
                FROM groups
                WHERE name LIKE ? OR description LIKE ?
                LIMIT ? OFFSET ?
            """
            groups = await self._fetch(sql, search_pattern, search_pattern, limit, offset)
            results.extend(groups)
            
            count_sql = "SELECT COUNT(*) as count FROM groups WHERE name LIKE ? OR description LIKE ?"
            count_result = await self._fetch(count_sql, search_pattern, search_pattern)
            total += count_result[0].get("count", 0) if count_result else 0
        
        return {
            "items": results[:limit],
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": query,
            "type": search_type
        }

    # ========== 兼容 BaseAdapter 抽象接口的补充实现（用于 PAT 等新功能在 SQLite 测试环境可用） ==========

    @property
    def schema(self) -> str:
        """返回 schema 名称（SQLite 无 schema 概念，返回默认）"""
        return "public"

    async def get_stats_summary(self) -> dict[str, Any]:
        """获取统计摘要（SQLite 版）"""
        try:
            agent_row = await self._fetchrow("SELECT COUNT(*) as count FROM users WHERE user_type = 'agent'")
            agent_count = agent_row["count"] if agent_row else 0
            post_row = await self._fetchrow("SELECT COUNT(*) as count FROM posts")
            post_count = post_row["count"] if post_row else 0
            view_row = await self._fetchrow("SELECT COALESCE(SUM(view_count),0) as total FROM posts")
            total_views = view_row["total"] if view_row else 0
            return {"success": True, "data": {"agent_count": agent_count, "post_count": post_count, "total_views": total_views}}
        except Exception as e:
            return {"success": False, "error": f"获取统计数据失败: {e}"}

    async def execute_raw(self, query: str, *params) -> dict[str, Any]:
        """执行原始 SELECT（SQLite 占位符 ?）"""
        try:
            # 将 Postgres 占位符 $1/$2 转为 ?
            import re
            sqlite_query = re.sub(r"\$\d+", "?", query)
            rows = await self._fetch(sqlite_query, *params)
            return {"success": True, "data": rows}
        except Exception as e:
            return {"success": False, "error": f"查询执行失败: {e}"}

    async def execute_raw_command(self, query: str, *params) -> dict[str, Any]:
        """执行原始 INSERT/UPDATE/DELETE"""
        try:
            import re
            sqlite_query = re.sub(r"\$\d+", "?", query)
            await self._execute(sqlite_query, *params)
            return {"success": True, "row_count": 1}
        except Exception as e:
            return {"success": False, "error": f"命令执行失败: {e}"}

    async def get_search_suggestions(self, search_pattern: str, limit: int = 10) -> dict[str, Any]:
        """获取搜索建议（SQLite 简化）"""
        suggestions = []
        try:
            tags = await self._fetch("SELECT name FROM tags WHERE name LIKE ? ORDER BY post_count DESC LIMIT ?", search_pattern, limit)
            for row in tags:
                suggestions.append({"text": row["name"], "type": "tag"})
            posts = await self._fetch("SELECT title FROM posts WHERE status = 'published' AND title LIKE ? ORDER BY view_count DESC LIMIT ?", search_pattern, limit)
            for row in posts:
                suggestions.append({"text": row["title"], "type": "post"})
            users = await self._fetch("SELECT username, display_name FROM users WHERE is_active = 1 AND (username LIKE ? OR display_name LIKE ?) LIMIT ?", search_pattern, search_pattern, limit)
            for row in users:
                txt = row["display_name"] or row["username"]
                suggestions.append({"text": txt, "type": "user"})
            # 去重
            seen = set()
            uniq = []
            for item in suggestions:
                if item["text"] not in seen and len(uniq) < limit:
                    seen.add(item["text"])
                    uniq.append(item)
            return {"success": True, "data": uniq}
        except Exception as e:
            return {"success": False, "error": f"获取搜索建议失败: {e}"}

    async def check_ip_like_limit(self, ip_address: str, daily_limit: int) -> dict[str, Any]:
        """检查 IP 点赞限制（SQLite 降级：直接放行）"""
        return {"success": True, "allowed": True, "message": ""}

    async def check_ip_comment_limit(self, ip_address: str, daily_limit: int, min_interval: int = 0) -> dict[str, Any]:
        """检查 IP 评论限制（SQLite 降级：直接放行）"""
        return {"success": True, "allowed": True, "message": "", "retry_after": 0}

    async def increment_like_count(self, post_id: str) -> dict[str, Any]:
        """增加点赞数"""
        try:
            await self._execute("UPDATE posts SET like_count = like_count + 1 WHERE id = ?", post_id)
            return {"success": True, "row_count": 1}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def decrement_like_count(self, post_id: str) -> dict[str, Any]:
        """减少点赞数"""
        try:
            await self._execute("UPDATE posts SET like_count = like_count - 1 WHERE id = ? AND like_count > 0", post_id)
            return {"success": True, "row_count": 1}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_post_tags(self, post_id: str) -> dict[str, Any]:
        """获取文章标签"""
        try:
            rows = await self._fetch("SELECT t.* FROM tags t JOIN post_tags pt ON t.id = pt.tag_id WHERE pt.post_id = ?", post_id)
            return {"success": True, "data": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def add_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """为文章添加标签"""
        try:
            await self._execute("INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?)", post_id, tag_id)
            await self._execute("UPDATE tags SET post_count = post_count + 1 WHERE id = ?", tag_id)
            return {"success": True}
        except Exception as e:
            if "unique" in str(e).lower():
                return {"success": False, "error": "Tag already added to post"}
            return {"success": False, "error": str(e)}

    async def remove_post_tag(self, post_id: str, tag_id: str) -> dict[str, Any]:
        """移除文章标签"""
        try:
            await self._execute("DELETE FROM post_tags WHERE post_id = ? AND tag_id = ?", post_id, tag_id)
            await self._execute("UPDATE tags SET post_count = post_count - 1 WHERE id = ?", tag_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def increment_view_count(self, post_id: str) -> dict[str, Any]:
        """增加浏览计数"""
        try:
            await self._execute("UPDATE posts SET view_count = view_count + 1 WHERE id = ?", post_id)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
