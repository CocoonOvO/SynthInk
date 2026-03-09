"""
路由聚合模块
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .posts import router as posts_router
from .tags import router as tags_router
from .groups import router as groups_router
from .upload import router as upload_router
from .download import router as download_router
from .admin import router as admin_router
from .comments import router as comments_router
from .likes import router as likes_router
from .search import router as search_router
from .seo import router as seo_router
from .stats import router as stats_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(posts_router, prefix="/posts", tags=["文章"])
api_router.include_router(tags_router, prefix="/tags", tags=["标签"])
api_router.include_router(groups_router, prefix="/groups", tags=["分组"])
api_router.include_router(upload_router, prefix="/upload", tags=["上传"])
api_router.include_router(download_router, prefix="/download", tags=["下载"])
api_router.include_router(admin_router, tags=["Admin - 超管配置"])
api_router.include_router(comments_router, prefix="/comments", tags=["评论"])
api_router.include_router(likes_router, prefix="/likes", tags=["点赞"])
api_router.include_router(search_router, prefix="/search", tags=["搜索"])
api_router.include_router(seo_router, tags=["SEO管理"])
api_router.include_router(stats_router, tags=["统计"])

__all__ = ["api_router"]
