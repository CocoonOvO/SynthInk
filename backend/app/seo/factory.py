"""
SEO适配器工厂

提供SEO模块的数据库访问接口

注意: 现在SEO模块通过 db_manager.seo_db 访问数据库，
不再创建独立的适配器实例。此模块保留向后兼容的函数。
"""
from typing import Optional
from ..db_manager import db_manager
from .config import get_seo_settings, SEOSettings


# SEO表名常量
SEO_TABLE_METADATA = "metadata"
SEO_TABLE_REDIRECTS = "redirects"


def get_seo_adapter():
    """
    获取SEO数据库访问接口

    返回 db_manager.seo_db 包装器，自动处理seo schema前缀。
    这是推荐的访问方式，避免创建独立的数据库连接。

    Returns:
        SEOAdapterWrapper: SEO数据库访问包装器

    Example:
        >>> adapter = get_seo_adapter()
        >>> result = await adapter.find(SEO_TABLE_METADATA, {"slug": "test"})
    """
    return db_manager.seo_db


# 向后兼容: 保留旧函数名
async def create_seo_adapter(
    settings: Optional[SEOSettings] = None,
    main_database_url: Optional[str] = None
):
    """
    [废弃] 请使用 get_seo_adapter()

    为向后兼容保留，现在直接返回 db_manager.seo_db。
    不再创建独立的适配器实例。

    Args:
        settings: 忽略，保留参数仅用于兼容
        main_database_url: 忽略，保留参数仅用于兼容

    Returns:
        SEOAdapterWrapper: SEO数据库访问包装器
    """
    import warnings
    warnings.warn(
        "create_seo_adapter() is deprecated, use get_seo_adapter() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return db_manager.seo_db


async def init_seo_tables(adapter=None) -> None:
    """
    初始化SEO表结构

    Args:
        adapter: 忽略，保留参数仅用于兼容。
                现在自动使用 db_manager.seo_db。

    Note:
        表结构通过适配器的create_table方法创建
        具体字段由适配器实现决定
    """
    # 使用 db_manager.seo_db 初始化表
    seo_db = db_manager.seo_db

    # 创建metadata表
    await seo_db.create_table(SEO_TABLE_METADATA)

    # 创建redirects表
    await seo_db.create_table(SEO_TABLE_REDIRECTS)
