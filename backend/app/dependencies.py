"""
FastAPI依赖模块
提供各种依赖注入功能，包括数据库连接检查等
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request

from .config_db import config_db_manager, ConfigAdmin, require_config_admin
from .adapter.postgres_adapter import PostgresAdapter


class DatabaseNotConfiguredException(HTTPException):
    """数据库未配置异常"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "业务数据库未配置",
                "code": "DATABASE_NOT_CONFIGURED",
                "description": "项目尚未配置业务数据库，请使用配置库超管账号访问 /api/admin/database 进行配置"
            }
        )


class DatabaseConnectionFailedException(HTTPException):
    """数据库连接失败异常"""
    
    def __init__(self, error_message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "业务数据库连接失败",
                "code": "DATABASE_CONNECTION_FAILED",
                "error": error_message
            }
        )


async def get_postgres_adapter(request: Request) -> PostgresAdapter:
    """
    获取业务数据库适配器（FastAPI依赖）
    
    此依赖会：
    1. 检查是否已配置业务数据库
    2. 检查数据库连接状态
    3. 返回适配器实例
    
    如果数据库未配置或连接失败，会抛出相应的HTTP异常
    
    Usage:
        @router.get("/posts")
        async def list_posts(db: PostgresAdapter = Depends(get_postgres_adapter)):
            return await db.find("posts")
    
    Raises:
        DatabaseNotConfiguredException: 数据库未配置
        DatabaseConnectionFailedException: 数据库连接失败
    """
    # 从 app.state 获取适配器实例
    postgres_adapter: Optional[PostgresAdapter] = getattr(request.app.state, "postgres_adapter", None)
    
    # 检查是否已配置业务数据库
    if not config_db_manager.has_database_config():
        raise DatabaseNotConfiguredException()
    
    # 如果适配器已存在且已连接，直接返回
    if postgres_adapter is not None:
        # 这里可以添加连接健康检查
        return postgres_adapter
    
    # 获取数据库配置
    db_config = config_db_manager.get_active_database_config()
    if db_config is None:
        raise DatabaseNotConfiguredException()
    
    # 尝试连接数据库
    try:
        postgres_adapter = PostgresAdapter(db_config.get_connection_string())
        await postgres_adapter.connect()
        
        # 将适配器实例存储到 app.state
        request.app.state.postgres_adapter = postgres_adapter
        
        # 更新连接状态
        config_db_manager.update_database_connection_status(
            db_config.id, is_connected=True
        )
        
        return postgres_adapter
        
    except Exception as e:
        # 更新连接状态为失败
        config_db_manager.update_database_connection_status(
            db_config.id, is_connected=False, error=str(e)
        )
        raise DatabaseConnectionFailedException(str(e))


async def close_postgres_adapter(request: Request) -> None:
    """关闭业务数据库连接"""
    postgres_adapter: Optional[PostgresAdapter] = getattr(request.app.state, "postgres_adapter", None)
    if postgres_adapter is not None:
        await postgres_adapter.disconnect()
        request.app.state.postgres_adapter = None


def check_database_configured() -> bool:
    """
    检查业务数据库是否已配置（同步版本）
    
    用于非异步上下文的检查
    """
    return config_db_manager.has_database_config()


async def require_database_configured(request: Request) -> None:
    """
    要求业务数据库已配置的依赖
    
    用于需要数据库但未使用get_postgres_adapter的场景
    
    Usage:
        @router.get("/check")
        async def check(_: None = Depends(require_database_configured)):
            return {"status": "configured"}
    """
    if not config_db_manager.has_database_config():
        raise DatabaseNotConfiguredException()


# 预定义的依赖组合
class AdminDependencies:
    """
    超管依赖组合类
    
    提供常用的超管权限依赖组合
    """
    
    @staticmethod
    async def admin_only(
        admin: ConfigAdmin = Depends(require_config_admin)
    ) -> ConfigAdmin:
        """仅需要超管权限"""
        return admin
    
    @staticmethod
    async def admin_with_db(
        admin: ConfigAdmin = Depends(require_config_admin),
        db: PostgresAdapter = Depends(get_postgres_adapter)
    ) -> tuple[ConfigAdmin, PostgresAdapter]:
        """需要超管权限和数据库连接"""
        return admin, db


# 快捷依赖函数
require_admin = require_config_admin
"""要求超管权限的快捷依赖"""

require_db = get_postgres_adapter
"""要求业务数据库的快捷依赖"""
