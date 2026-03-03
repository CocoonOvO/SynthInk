"""
数据库管理器
统一管理配置库(SQLite)和业务库(PostgreSQL/SQLite)
"""
from typing import Optional, Union

from .adapter.sqlite_config import SQLiteConfigAdapter
from .adapter.postgres_adapter import PostgresAdapter
from .adapter.sqlite_biz import SQLiteBizAdapter


class DatabaseManager:
    """
    数据库管理器
    
    职责：
    1. 管理配置库(SQLite)连接
    2. 管理业务库(PostgreSQL)连接
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
        self._postgres_adapter: Optional[PostgresAdapter] = None
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
    
    # ========== 业务库(PostgreSQL) ==========
    
    async def init_postgres_db(self, dsn: Optional[str] = None, schema: Optional[str] = None) -> None:
        """
        初始化业务库
        
        Args:
            dsn: 数据库连接字符串，如果为None则从配置库读取
                 支持格式：
                 - postgresql://... (PostgreSQL)
                 - sqlite+aiosqlite://... (SQLite)
            schema: PostgreSQL schema名称，如果为None则从配置库读取，默认为"public"
        """
        if dsn is None:
            # 从配置库读取数据库连接信息
            dsn = await self.get_config("database_url")
            if not dsn:
                raise ValueError("Database URL not found in config")
        
        # 从配置库读取schema配置（仅PostgreSQL）
        if schema is None and "sqlite" not in dsn.lower():
            schema = await self.get_config("database_schema", "public")
        
        # 根据DSN选择适配器
        dsn_lower = dsn.lower()
        if "sqlite" in dsn_lower:
            # 使用SQLite适配器（测试环境）
            self._postgres_adapter = SQLiteBizAdapter(dsn)
        else:
            # 使用PostgreSQL适配器（生产环境），传入schema配置
            self._postgres_adapter = PostgresAdapter(dsn, schema=schema)
        
        await self._postgres_adapter.connect()
        await self._postgres_adapter.init_schema()
    
    @property
    def postgres(self) -> PostgresAdapter:
        """获取业务库适配器"""
        if self._postgres_adapter is None:
            raise RuntimeError("PostgreSQL database not initialized. Call init_postgres_db() first.")
        return self._postgres_adapter
    
    @property
    def db(self) -> PostgresAdapter:
        """业务库的快捷访问方式"""
        return self.postgres
    
    # ========== 统一初始化 ==========
    
    async def initialize(self, config_db_path: str = "./config.db") -> None:
        """
        初始化所有数据库
        
        执行顺序：
        1. 初始化SQLite配置库
        2. 从配置库读取PostgreSQL连接信息
        3. 初始化PostgreSQL业务库
        
        Args:
            config_db_path: 配置库文件路径
        """
        # 1. 初始化配置库
        await self.init_config_db(config_db_path)
        
        # 2. 初始化业务库
        await self.init_postgres_db()
    
    async def close(self) -> None:
        """关闭所有数据库连接"""
        if self._postgres_adapter:
            await self._postgres_adapter.disconnect()
            self._postgres_adapter = None
        
        if self._config_adapter:
            await self._config_adapter.disconnect()
            self._config_adapter = None
    
    # ========== 状态检查 ==========
    
    @property
    def is_config_ready(self) -> bool:
        """配置库是否已初始化"""
        return self._config_adapter is not None
    
    @property
    def is_postgres_ready(self) -> bool:
        """业务库是否已初始化"""
        return self._postgres_adapter is not None
    
    @property
    def is_ready(self) -> bool:
        """所有数据库是否都已就绪"""
        return self.is_config_ready and self.is_postgres_ready


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
            # 使用 db.postgres 或 db.db 访问业务库
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


async def get_postgres_db() -> PostgresAdapter:
    """
    获取业务库适配器（用于FastAPI依赖注入）
    
    Usage:
        @router.get("/")
        async def endpoint(pg: PostgresAdapter = Depends(get_postgres_db)):
            result = await pg.get("users", user_id)
    """
    return db_manager.postgres
