"""
FastAPI依赖模块
提供各种依赖注入功能
"""
from fastapi import Depends, HTTPException, status

from .config_db import config_db_manager, ConfigAdmin, require_config_admin


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


def check_database_configured() -> bool:
    """
    检查业务数据库是否已配置（同步版本）
    
    用于非异步上下文的检查
    """
    return config_db_manager.has_database_config()


async def require_database_configured() -> None:
    """
    要求业务数据库已配置的依赖
    
    用于需要数据库但未直接使用db_manager的场景
    
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


# 快捷依赖函数
require_admin = require_config_admin
"""要求超管权限的快捷依赖"""
