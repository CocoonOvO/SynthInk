"""
数据库初始化管理器

负责检查并创建业务数据库和表结构。
使用适配器模式支持多种数据库类型。
支持自定义数据库名称和schema。

Attributes:
    DEFAULT_DATABASE: 默认数据库名称
    REQUIRED_TABLES: 必需的表列表
"""
from typing import Optional, Dict, Any, List
import asyncpg

from .config_db import DatabaseConfig, DatabaseType
from .adapter.postgres_adapter import PostgresAdapter


# 必需的表列表
REQUIRED_TABLES = ["users", "posts", "tags", "groups", "post_tags"]


class DatabaseInitializer:
    """
    数据库初始化管理器
    
    职责：
    1. 检查业务数据库是否存在
    2. 创建业务数据库
    3. 检查schema是否存在（PostgreSQL）
    4. 创建schema（PostgreSQL）
    5. 检查表结构是否存在
    6. 初始化表结构
    7. 验证数据库完整性
    
    Attributes:
        config: 数据库配置对象
        admin_dsn: 管理员连接字符串（用于创建数据库）
        db_dsn: 业务数据库连接字符串
        schema: PostgreSQL schema名称
    """
    
    def __init__(self, config: DatabaseConfig):
        """
        初始化数据库初始化管理器
        
        Args:
            config: 数据库配置对象
        """
        self.config = config
        self.admin_dsn = self._build_admin_dsn()
        # 使用原始连接字符串（不含驱动）用于asyncpg
        self.db_dsn = config.get_raw_connection_string()
        self.schema = getattr(config, 'schema', 'public')
    
    def _build_admin_dsn(self) -> str:
        """
        构建管理员连接字符串
        
        用于连接到默认postgres数据库来创建业务数据库
        
        Returns:
            管理员连接字符串
        """
        if self.config.db_type == DatabaseType.POSTGRESQL:
            # 连接到默认postgres数据库
            return (
                f"postgresql://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/postgres"
            )
        elif self.config.db_type == DatabaseType.MYSQL:
            # MySQL使用不同方式
            return (
                f"mysql://{self.config.username}:{self.config.password}"
                f"@{self.config.host}:{self.config.port}/"
            )
        else:
            # SQLite不需要创建数据库
            return self.config.get_raw_connection_string()
    
    async def check_database_exists(self) -> bool:
        """
        检查业务数据库是否存在
        
        Returns:
            True - 数据库存在
            False - 数据库不存在
            
        Raises:
            RuntimeError: 不支持的数据库类型
        """
        if self.config.db_type == DatabaseType.SQLITE:
            # SQLite数据库就是文件，直接返回True
            return True
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            return await self._check_postgres_database()
        
        if self.config.db_type == DatabaseType.MYSQL:
            return await self._check_mysql_database()
        
        raise RuntimeError(f"Unsupported database type: {self.config.db_type}")
    
    async def _check_postgres_database(self) -> bool:
        """检查PostgreSQL数据库是否存在"""
        try:
            conn = await asyncpg.connect(self.admin_dsn)
            try:
                result = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1",
                    self.config.database
                )
                return result is not None
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check database: {e}")
    
    async def _check_mysql_database(self) -> bool:
        """检查MySQL数据库是否存在"""
        try:
            import aiomysql
            conn = await aiomysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password
            )
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                        (self.config.database,)
                    )
                    result = await cur.fetchone()
                    return result is not None
            finally:
                conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check database: {e}")
    
    async def create_database(self) -> Dict[str, Any]:
        """
        创建业务数据库
        
        Returns:
            包含操作结果的字典
            
        Raises:
            RuntimeError: 创建失败
        """
        if self.config.db_type == DatabaseType.SQLITE:
            # SQLite会自动创建文件
            return {"success": True, "message": "SQLite database will be created automatically"}
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            return await self._create_postgres_database()
        
        if self.config.db_type == DatabaseType.MYSQL:
            return await self._create_mysql_database()
        
        raise RuntimeError(f"Unsupported database type: {self.config.db_type}")
    
    async def _create_postgres_database(self) -> Dict[str, Any]:
        """创建PostgreSQL数据库"""
        try:
            conn = await asyncpg.connect(self.admin_dsn)
            try:
                # 检查数据库是否已存在
                exists = await conn.fetchval(
                    "SELECT 1 FROM pg_database WHERE datname = $1",
                    self.config.database
                )
                
                if exists:
                    return {
                        "success": True,
                        "message": f"Database '{self.config.database}' already exists",
                        "created": False
                    }
                
                # 创建数据库
                # 注意：PostgreSQL不支持参数化数据库名，需要转义
                safe_db_name = self._escape_identifier(self.config.database)
                await conn.execute(f"CREATE DATABASE {safe_db_name}")
                
                return {
                    "success": True,
                    "message": f"Database '{self.config.database}' created successfully",
                    "created": True
                }
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to create database: {e}")
    
    async def _create_mysql_database(self) -> Dict[str, Any]:
        """创建MySQL数据库"""
        try:
            import aiomysql
            conn = await aiomysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password
            )
            try:
                async with conn.cursor() as cur:
                    # 检查数据库是否已存在
                    await cur.execute(
                        "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
                        (self.config.database,)
                    )
                    exists = await cur.fetchone()
                    
                    if exists:
                        return {
                            "success": True,
                            "message": f"Database '{self.config.database}' already exists",
                            "created": False
                        }
                    
                    # 创建数据库
                    safe_db_name = self._escape_identifier(self.config.database)
                    await cur.execute(f"CREATE DATABASE {safe_db_name}")
                    await conn.commit()
                    
                    return {
                        "success": True,
                        "message": f"Database '{self.config.database}' created successfully",
                        "created": True
                    }
            finally:
                conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to create database: {e}")
    
    async def check_schema_exists(self) -> bool:
        """
        检查schema是否存在（仅PostgreSQL）
        
        Returns:
            True - schema存在
            False - schema不存在
        """
        if self.config.db_type != DatabaseType.POSTGRESQL:
            return True  # 非PostgreSQL直接返回True
        
        if self.schema == 'public':
            return True  # public schema总是存在
        
        try:
            conn = await asyncpg.connect(self.db_dsn)
            try:
                result = await conn.fetchval(
                    "SELECT 1 FROM information_schema.schemata WHERE schema_name = $1",
                    self.schema
                )
                return result is not None
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check schema: {e}")
    
    async def create_schema(self) -> Dict[str, Any]:
        """
        创建schema（仅PostgreSQL）
        
        Returns:
            包含操作结果的字典
        """
        if self.config.db_type != DatabaseType.POSTGRESQL:
            return {"success": True, "message": "Schema not applicable for this database type"}
        
        if self.schema == 'public':
            return {"success": True, "message": "Public schema always exists", "created": False}
        
        try:
            conn = await asyncpg.connect(self.db_dsn)
            try:
                # 检查schema是否已存在
                exists = await conn.fetchval(
                    "SELECT 1 FROM information_schema.schemata WHERE schema_name = $1",
                    self.schema
                )
                
                if exists:
                    return {
                        "success": True,
                        "message": f"Schema '{self.schema}' already exists",
                        "created": False
                    }
                
                # 创建schema
                safe_schema = self._escape_identifier(self.schema)
                await conn.execute(f"CREATE SCHEMA {safe_schema}")
                
                return {
                    "success": True,
                    "message": f"Schema '{self.schema}' created successfully",
                    "created": True
                }
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to create schema: {e}")
    
    def _escape_identifier(self, identifier: str) -> str:
        """
        转义SQL标识符
        
        防止SQL注入攻击
        
        Args:
            identifier: SQL标识符（表名、数据库名等）
            
        Returns:
            转义后的标识符
        """
        # 移除危险字符
        dangerous_chars = ";'\"\\/*%"
        for char in dangerous_chars:
            identifier = identifier.replace(char, "")
        
        # PostgreSQL和MySQL都使用双引号包裹标识符
        return f'"{identifier}"'
    
    async def check_tables_exist(self) -> Dict[str, bool]:
        """
        检查必需的表是否存在
        
        Returns:
            表名到存在状态的映射字典
        """
        if self.config.db_type == DatabaseType.SQLITE:
            return await self._check_sqlite_tables()
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            return await self._check_postgres_tables()
        
        if self.config.db_type == DatabaseType.MYSQL:
            return await self._check_mysql_tables()
        
        raise RuntimeError(f"Unsupported database type: {self.config.db_type}")
    
    async def _check_sqlite_tables(self) -> Dict[str, bool]:
        """检查SQLite表是否存在"""
        try:
            import aiosqlite
            conn = await aiosqlite.connect(self.config.database)
            try:
                result = {}
                for table in REQUIRED_TABLES:
                    cursor = await conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table,)
                    )
                    row = await cursor.fetchone()
                    result[table] = row is not None
                return result
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check tables: {e}")
    
    async def _check_postgres_tables(self) -> Dict[str, bool]:
        """检查PostgreSQL表是否存在"""
        try:
            conn = await asyncpg.connect(self.db_dsn)
            try:
                result = {}
                for table in REQUIRED_TABLES:
                    exists = await conn.fetchval(
                        """
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = $1 AND table_name = $2
                        """,
                        self.schema, table
                    )
                    result[table] = exists is not None
                return result
            finally:
                await conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check tables: {e}")
    
    async def _check_mysql_tables(self) -> Dict[str, bool]:
        """检查MySQL表是否存在"""
        try:
            import aiomysql
            conn = await aiomysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                db=self.config.database
            )
            try:
                result = {}
                async with conn.cursor() as cur:
                    for table in REQUIRED_TABLES:
                        await cur.execute(
                            """
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_schema = %s AND table_name = %s
                            """,
                            (self.config.database, table)
                        )
                        row = await cur.fetchone()
                        result[table] = row is not None
                return result
            finally:
                conn.close()
        except Exception as e:
            raise RuntimeError(f"Failed to check tables: {e}")
    
    async def init_tables(self) -> Dict[str, Any]:
        """
        初始化所有业务表
        
        使用适配器创建所有必需的表
        
        Returns:
            包含操作结果的字典
        """
        try:
            adapter = PostgresAdapter(self.db_dsn, schema=self.schema)
            await adapter.connect()
            try:
                await adapter.init_schema()
                return {
                    "success": True,
                    "message": "All tables initialized successfully",
                    "tables": REQUIRED_TABLES,
                    "schema": self.schema
                }
            finally:
                await adapter.disconnect()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize tables: {e}")
    
    async def get_init_status(self) -> Dict[str, Any]:
        """
        获取数据库初始化状态
        
        返回数据库和表的完整状态信息
        
        Returns:
            包含状态信息的字典
        """
        try:
            # 检查数据库是否存在
            db_exists = await self.check_database_exists()
            
            if not db_exists:
                return {
                    "database_exists": False,
                    "database_name": self.config.database,
                    "schema": self.schema,
                    "schema_exists": False,
                    "tables": {},
                    "all_tables_exist": False,
                    "ready": False
                }
            
            # 检查schema是否存在
            schema_exists = await self.check_schema_exists()
            
            # 检查表是否存在
            tables_status = await self.check_tables_exist()
            all_exist = all(tables_status.values())
            
            return {
                "database_exists": True,
                "database_name": self.config.database,
                "schema": self.schema,
                "schema_exists": schema_exists,
                "tables": tables_status,
                "all_tables_exist": all_exist,
                "ready": all_exist and schema_exists
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "database_exists": False,
                "database_name": self.config.database,
                "schema": self.schema,
                "schema_exists": False,
                "tables": {},
                "all_tables_exist": False,
                "ready": False
            }
    
    async def full_init(self) -> Dict[str, Any]:
        """
        完整的数据库初始化流程
        
        1. 检查并创建数据库
        2. 检查并创建schema（PostgreSQL）
        3. 检查并创建表结构
        
        Returns:
            包含完整初始化结果的字典
        """
        result = {
            "success": True,
            "database_name": self.config.database,
            "schema": self.schema,
            "steps": []
        }
        
        try:
            # 步骤1: 检查/创建数据库
            db_check = await self.check_database_exists()
            if not db_check:
                create_result = await self.create_database()
                result["steps"].append({
                    "step": "create_database",
                    "status": "created" if create_result.get("created") else "exists",
                    "message": create_result["message"]
                })
            else:
                result["steps"].append({
                    "step": "create_database",
                    "status": "exists",
                    "message": f"Database '{self.config.database}' already exists"
                })
            
            # 步骤2: 检查/创建schema（仅PostgreSQL）
            if self.config.db_type == DatabaseType.POSTGRESQL and self.schema != 'public':
                schema_check = await self.check_schema_exists()
                if not schema_check:
                    schema_result = await self.create_schema()
                    result["steps"].append({
                        "step": "create_schema",
                        "status": "created" if schema_result.get("created") else "exists",
                        "message": schema_result["message"]
                    })
                else:
                    result["steps"].append({
                        "step": "create_schema",
                        "status": "exists",
                        "message": f"Schema '{self.schema}' already exists"
                    })
            
            # 步骤3: 检查/创建表
            tables_status = await self.check_tables_exist()
            if not all(tables_status.values()):
                init_result = await self.init_tables()
                result["steps"].append({
                    "step": "init_tables",
                    "status": "initialized",
                    "message": init_result["message"],
                    "tables": init_result["tables"],
                    "schema": self.schema
                })
            else:
                result["steps"].append({
                    "step": "init_tables",
                    "status": "exists",
                    "message": "All tables already exist",
                    "tables": list(tables_status.keys())
                })
            
            result["ready"] = True
            result["message"] = "Database initialization completed successfully"
            
        except Exception as e:
            result["success"] = False
            result["ready"] = False
            result["error"] = str(e)
            result["message"] = f"Database initialization failed: {e}"
        
        return result


# 便捷函数
async def init_database(config: DatabaseConfig) -> Dict[str, Any]:
    """
    便捷函数：初始化数据库
    
    Args:
        config: 数据库配置
        
    Returns:
        初始化结果
    """
    initializer = DatabaseInitializer(config)
    return await initializer.full_init()


async def check_database_ready(config: DatabaseConfig) -> bool:
    """
    便捷函数：检查数据库是否就绪
    
    Args:
        config: 数据库配置
        
    Returns:
        True - 数据库已就绪
        False - 数据库未就绪
    """
    initializer = DatabaseInitializer(config)
    status = await initializer.get_init_status()
    return status.get("ready", False)
