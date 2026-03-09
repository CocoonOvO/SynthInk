"""
数据库管理器
统一管理配置库(SQLite)和业务库(PostgreSQL/SQLite/MySQL等)
"""
import warnings
from typing import Optional

from .adapter.base import BaseAdapter
from .adapter.sqlite_config import SQLiteConfigAdapter


def create_biz_adapter(dsn: str, **kwargs) -> BaseAdapter:
    """
    工厂函数：根据DSN创建对应的数据库适配器

    Args:
        dsn: 数据库连接字符串
        **kwargs: 额外参数（如schema等）

    Returns:
        BaseAdapter: 数据库适配器实例

    支持的数据库类型：
    - postgresql://... → PostgresAdapter
    - sqlite://... → SQLiteBizAdapter
    - mysql://... → MySQLAdapter (未来扩展)
    - mongodb://... → MongoAdapter (未来扩展)
    """
    dsn_lower = dsn.lower()

    # 支持 postgresql:// 和 postgresql+asyncpg:// 格式
    if dsn_lower.startswith(("postgresql://", "postgres://", "postgresql+asyncpg://", "postgres+asyncpg://")):
        from .adapter.postgres_adapter import PostgresAdapter
        schema = kwargs.get("schema", "public")
        return PostgresAdapter(dsn, schema=schema)

    elif dsn_lower.startswith("sqlite://"):
        from .adapter.sqlite_biz import SQLiteBizAdapter
        return SQLiteBizAdapter(dsn)

    # 未来扩展：MySQL支持
    # elif dsn_lower.startswith("mysql://"):
    #     from .adapter.mysql_adapter import MySQLAdapter
    #     return MySQLAdapter(dsn, pool_size=kwargs.get("pool_size", 10))

    else:
        raise ValueError(f"Unsupported database DSN: {dsn}")


class SEOAdapterWrapper:
    """
    SEO适配器包装器

    为SEO模块提供统一的数据库访问接口，自动将表名添加seo schema前缀。
    这样SEO模块可以通过 db_manager.seo_db 访问seo schema下的表，
    而无需创建独立的适配器连接。
    """

    SEO_TABLES = {"metadata", "redirects"}

    def __init__(self, adapter: BaseAdapter):
        self._adapter = adapter

    def _add_schema_prefix(self, table: str) -> str:
        """为SEO表添加schema前缀"""
        if table in self.SEO_TABLES and not table.startswith("seo."):
            return f"seo.{table}"
        return table

    @property
    def schema(self) -> str:
        """返回业务库的schema（用于兼容）"""
        return self._adapter.schema

    async def find(self, table: str, filters=None, limit=100, offset=0, order_by=None, sort_desc=False):
        """查询数据"""
        return await self._adapter.find(
            self._add_schema_prefix(table),
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            sort_desc=sort_desc
        )

    async def get(self, table: str, id: str):
        """根据ID获取数据"""
        return await self._adapter.get(self._add_schema_prefix(table), id)

    async def insert(self, table: str, data: dict):
        """插入数据"""
        return await self._adapter.insert(self._add_schema_prefix(table), data)

    async def update(self, table: str, id: str, data: dict):
        """更新数据"""
        return await self._adapter.update(self._add_schema_prefix(table), id, data)

    async def delete(self, table: str, id: str):
        """删除数据"""
        return await self._adapter.delete(self._add_schema_prefix(table), id)

    async def count(self, table: str, filters=None):
        """统计数据"""
        return await self._adapter.count(self._add_schema_prefix(table), filters=filters)

    async def create_table(self, table: str):
        """创建表"""
        return await self._adapter.create_table(self._add_schema_prefix(table))


class DatabaseManager:
    """
    数据库管理器 - 数据库无关设计

    职责：
    1. 管理配置库(SQLite)连接
    2. 管理业务库(任意类型)连接
    3. 提供统一的数据库访问接口
    4. 处理数据库初始化
    """

    _instance: Optional['DatabaseManager'] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._config_adapter: Optional[SQLiteConfigAdapter] = None
        self._biz_adapter: Optional[BaseAdapter] = None
        self._initialized = True

    # ========== 配置库(SQLite) ==========

    async def init_config_db(self, db_path: str = "./config.db") -> None:
        """
        初始化配置库

        Args:
            db_path: SQLite数据库文件路径
        """
        self._config_adapter = SQLiteConfigAdapter(db_path)
        await self._config_adapter.connect()
        await self._config_adapter.init_schema()

    @property
    def config(self) -> SQLiteConfigAdapter:
        """获取配置库适配器"""
        if self._config_adapter is None:
            raise RuntimeError("Config database not initialized. Call init_config_db() first.")
        return self._config_adapter

    async def get_config(self, key: str, default=None):
        """获取配置值（快捷方法）"""
        return await self.config.get_config(key, default)

    async def set_config(self, key: str, value, description: str = ""):
        """设置配置值（快捷方法）"""
        return await self.config.set_config(key, value, description)

    # ========== 业务库（数据库无关） ==========

    async def init_biz_db(self, dsn: str, **kwargs) -> None:
        """
        初始化业务库 - 数据库无关接口

        Args:
            dsn: 数据库连接字符串，支持多种数据库类型
            **kwargs: 额外参数（如schema等）

        示例:
            # PostgreSQL
            await db_manager.init_biz_db("postgresql://user:pass@host/db", schema="public")

            # SQLite
            await db_manager.init_biz_db("sqlite:///path/to/db.sqlite")

            # 未来：MySQL
            # await db_manager.init_biz_db("mysql://user:pass@host/db")
        """
        self._biz_adapter = create_biz_adapter(dsn, **kwargs)
        await self._biz_adapter.connect()
        await self._biz_adapter.init_schema()

    @property
    def db(self) -> BaseAdapter:
        """
        获取业务库适配器（抽象接口）

        这是访问业务库的唯一推荐方式，完全数据库无关
        """
        if self._biz_adapter is None:
            raise RuntimeError("Business database not initialized. Call init_biz_db() first.")
        return self._biz_adapter

    @property
    def seo_db(self) -> 'SEOAdapterWrapper':
        """
        获取SEO数据库访问接口

        返回一个包装器，自动将表名添加seo schema前缀。
        SEO模块应使用此属性访问seo schema下的表，避免创建独立连接。

        Usage:
            result = await db_manager.seo_db.find("metadata", {"slug": "test"})
            result = await db_manager.seo_db.insert("redirects", {...})
        """
        if self._biz_adapter is None:
            raise RuntimeError("Business database not initialized. Call init_biz_db() first.")
        return SEOAdapterWrapper(self._biz_adapter)

    # 向后兼容（标记为废弃）
    @property
    def postgres(self) -> BaseAdapter:
        """
        [废弃] 请使用 db 属性

        为向后兼容保留，将在v2.0移除
        """
        warnings.warn(
            "db_manager.postgres is deprecated, use db_manager.db instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.db

    # 向后兼容（标记为废弃）
    async def init_postgres_db(self, dsn: Optional[str] = None, schema: Optional[str] = None) -> None:
        """
        [废弃] 请使用 init_biz_db()

        为向后兼容保留，将在v2.0移除
        """
        warnings.warn(
            "init_postgres_db() is deprecated, use init_biz_db() instead",
            DeprecationWarning,
            stacklevel=2
        )

        if dsn is None:
            dsn = await self.get_config("database_url")
            if not dsn:
                raise ValueError("Database URL not found in config")

        if schema is None and "sqlite" not in dsn.lower():
            schema = await self.get_config("database_schema", "public")

        await self.init_biz_db(dsn, schema=schema)

    # ========== 统一初始化（解耦） ==========

    async def initialize(
        self,
        config_db_path: str = "./config.db",
        biz_dsn: Optional[str] = None,
        **biz_kwargs
    ) -> None:
        """
        初始化所有数据库

        Args:
            config_db_path: 配置库路径
            biz_dsn: 业务库DSN，为None时从配置库读取
            **biz_kwargs: 业务库额外参数

        解耦点：
        1. 业务库类型由DSN决定，代码无感知
        2. 支持外部传入DSN，不强制依赖配置库
        3. 支持任意数据库类型（通过工厂函数扩展）
        """
        # 1. 初始化配置库
        await self.init_config_db(config_db_path)

        # 2. 获取业务库DSN
        if biz_dsn is None:
            biz_dsn = await self.config.get_config("database_url")
            if not biz_dsn:
                raise ValueError("Business database URL not found in config")

        # 3. 初始化业务库（数据库类型由DSN决定）
        await self.init_biz_db(biz_dsn, **biz_kwargs)

    async def close(self) -> None:
        """关闭所有数据库连接"""
        if self._biz_adapter:
            await self._biz_adapter.disconnect()
            self._biz_adapter = None

        if self._config_adapter:
            await self._config_adapter.disconnect()
            self._config_adapter = None

    # ========== 状态检查（抽象化） ==========

    @property
    def is_config_ready(self) -> bool:
        """配置库是否已初始化"""
        return self._config_adapter is not None

    @property
    def is_biz_db_ready(self) -> bool:
        """业务库是否已初始化"""
        return self._biz_adapter is not None

    # 向后兼容（标记为废弃）
    @property
    def is_postgres_ready(self) -> bool:
        """
        [废弃] 请使用 is_biz_db_ready

        为向后兼容保留，将在v2.0移除
        """
        warnings.warn(
            "is_postgres_ready is deprecated, use is_biz_db_ready instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.is_biz_db_ready

    @property
    def is_ready(self) -> bool:
        """所有数据库是否都已就绪"""
        return self.is_config_ready and self.is_biz_db_ready

    # ========== 统计数据 ==========

    async def get_stats_summary(self) -> dict:
        """
        获取统计数据摘要

        Returns:
            {
                "success": True,
                "data": {
                    "agent_count": int,    # 智能体创作者总数
                    "post_count": int,     # 文章总数
                    "total_views": int     # 总浏览量
                }
            }
        """
        if not self._biz_adapter:
            return {
                "success": False,
                "error": "Database not initialized"
            }
        return await self._biz_adapter.get_stats_summary()


# 全局数据库管理器实例
db_manager = DatabaseManager()


# ========== FastAPI依赖注入函数 ==========

async def get_db_manager() -> DatabaseManager:
    """
    获取数据库管理器（用于FastAPI依赖注入）

    Usage:
        @router.get("/")
        async def endpoint(db: DatabaseManager = Depends(get_db_manager)):
            # 使用 db.config 访问配置库
            # 使用 db.db 访问业务库
            pass
    """
    return db_manager


async def get_config_db() -> SQLiteConfigAdapter:
    """
    获取配置库适配器（用于FastAPI依赖注入）

    Usage:
        @router.get("/")
        async def endpoint(config: SQLiteConfigAdapter = Depends(get_config_db)):
            value = await config.get_config("some_key")
    """
    return db_manager.config


async def get_biz_db() -> BaseAdapter:
    """
    获取业务库适配器（抽象接口）

    这是依赖注入的推荐方式，完全数据库无关

    Usage:
        @router.get("/")
        async def endpoint(db: BaseAdapter = Depends(get_biz_db)):
            result = await db.get("users", user_id)
    """
    return db_manager.db


# 向后兼容（标记为废弃）
async def get_postgres_db() -> BaseAdapter:
    """
    [废弃] 请使用 get_biz_db()

    为向后兼容保留，将在v2.0移除
    """
    warnings.warn(
        "get_postgres_db() is deprecated, use get_biz_db() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return db_manager.db
