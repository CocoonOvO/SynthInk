"""
配置管理模块
使用 Pydantic Settings 管理配置，支持环境变量
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional, List
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # 应用基础配置
    APP_NAME: str = "SynthSpark"
    DEBUG_MODE: bool = True
    VERSION: str = "0.1.0"
    
    # 安全配置
    SECRET_KEY: str = Field(..., description="JWT 签名密钥，缺失时请复制 backend/.env.example 为 .env 并设置 SECRET_KEY（可用 `openssl rand -hex 32` 生成）")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./synthspark.db"
    
    # CORS配置 - 允许所有本地开发端口
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://localhost:5178",
        "http://localhost:5179",
        "http://localhost:5180",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5178",
        "http://127.0.0.1:5179",
        "http://127.0.0.1:5180",
        "http://127.0.0.1:3000"
    ]
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # 站点配置
    SITE_NAME: str = "SynthSpark"
    SITE_DESCRIPTION: str = "AI 辅助博客站点"
    
    # 限流配置 (slowapi格式: "次数/时间单位")
    RATE_LIMIT_LOGIN: str = "5/minute"           # 登录接口限流
    RATE_LIMIT_REGISTER: str = "3/minute"        # 注册接口限流
    RATE_LIMIT_DEFAULT: str = "100/minute"       # 默认全局限流
    RATE_LIMIT_EXEMPT_IPS: List[str] = ["127.0.0.1", "::1"]  # 不受限流的IP列表


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    try:
        return Settings()
    except ValidationError as e:
        # SECRET_KEY 缺失时给出友好提示，而非原始 pydantic 堆栈
        if any(err.get("loc") == ("SECRET_KEY",) for err in e.errors()):
            raise ValueError(
                "缺少必填环境变量 SECRET_KEY，请复制 backend/.env.example 为 backend/.env "
                "并设置 SECRET_KEY（可用 `openssl rand -hex 32` 生成随机字符串）"
            ) from e
        raise
