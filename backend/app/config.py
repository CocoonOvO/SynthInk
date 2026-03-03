"""
配置管理模块
使用 Pydantic Settings 管理配置，支持环境变量
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 应用基础配置
    APP_NAME: str = "SynthInk"
    DEBUG_MODE: bool = True
    VERSION: str = "0.1.0"
    
    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./synthink.db"
    
    # CORS配置
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # 站点配置
    SITE_NAME: str = "SynthInk"
    SITE_DESCRIPTION: str = "AI 辅助博客站点"
    
    # 限流配置 (slowapi格式: "次数/时间单位")
    RATE_LIMIT_LOGIN: str = "5/minute"           # 登录接口限流
    RATE_LIMIT_REGISTER: str = "3/minute"        # 注册接口限流
    RATE_LIMIT_DEFAULT: str = "100/minute"       # 默认全局限流


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
