"""
配置库模块
管理SQLite配置数据库，包括超管认证、系统配置等
"""
from .manager import ConfigDBManager, config_db_manager
from .auth import ConfigAdminAuth, config_admin_auth, require_config_admin
from .models import ConfigAdmin, SystemConfig, DatabaseConfig, DatabaseType

__all__ = [
    "ConfigDBManager",
    "config_db_manager",
    "ConfigAdminAuth",
    "config_admin_auth",
    "require_config_admin",
    "ConfigAdmin",
    "SystemConfig",
    "DatabaseConfig",
    "DatabaseType",
]
