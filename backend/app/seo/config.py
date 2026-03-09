"""
SEO模块配置

独立的配置管理，支持环境变量
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class SEOSettings(BaseSettings):
    """SEO模块配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        json_schema_extra={
            "example": {
                "SEO_ENABLED": True,
                "SEO_DATABASE_URL": "sqlite:///./seo.db",
                "SEO_SSR_ENABLED": True,
                "SEO_CRAWLER_UA_KEYWORDS": ["googlebot", "baiduspider"],
                "SEO_SSR_TIMEOUT": 5.0
            }
        }
    )
    
    # SEO模块总开关
    SEO_ENABLED: bool = False
    
    # SEO数据库连接串
    # 格式:
    #   PostgreSQL: postgresql://user:pass@host:port/db?options=-csearch_path=seo
    #   MongoDB: mongodb://user:pass@host:port/db?authSource=admin
    #   SQLite: sqlite:///path/to/seo.db
    # 为空时默认使用主数据库 (settings.DATABASE_URL)
    SEO_DATABASE_URL: Optional[str] = None
    
    # SSR渲染开关
    SEO_SSR_ENABLED: bool = True
    
    # 爬虫检测配置 - User-Agent关键词
    SEO_CRAWLER_UA_KEYWORDS: List[str] = [
        "googlebot",
        "baiduspider",
        "bingbot",
        "yandex",
        "duckduckbot",
        "slurp",  # Yahoo
        "facebookexternalhit",
        "twitterbot",
        "linkedinbot",
    ]
    
    # SSR渲染配置
    SEO_SSR_TIMEOUT: float = 5.0  # SSR渲染超时时间(秒)


# 全局配置实例
seo_settings = SEOSettings()


def get_seo_settings() -> SEOSettings:
    """获取SEO配置"""
    return seo_settings
