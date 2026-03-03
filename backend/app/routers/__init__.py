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
from .admin import router as admin_router
from ..mcp import mcp_router

# 创建主路由
api_router = APIRouter(prefix="/api")

# 注册子路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(posts_router, prefix="/posts", tags=["文章"])
api_router.include_router(tags_router, prefix="/tags", tags=["标签"])
api_router.include_router(groups_router, prefix="/groups", tags=["分组"])
api_router.include_router(upload_router, prefix="/upload", tags=["上传"])
api_router.include_router(admin_router, tags=["Admin - 超管配置"])
api_router.include_router(mcp_router, tags=["MCP服务"])

__all__ = ["api_router"]
