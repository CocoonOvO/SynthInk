"""
服务挂载示例（契约模板）

复制本文件到 backend/app/services/impl/ 目录（该目录已被 gitignore），
然后改写成你自己的服务即可。注意：
- 模块级变量 name / title / router 是必填契约字段
- static_dir 可选：提供 UI 时，在 impl/ 下建同名目录放 index.html / js / css
- API 与 UI 可在同一服务中共存（API 路由优先于静态文件）
"""
from fastapi import APIRouter

# ── 必填契约字段 ──────────────────────────────────────────────
# 唯一ID：仅允许小写字母/数字/短横线，决定挂载URL /api/services/{name}/
name = "hello"

# 显示名称（用于日志/未来的管理界面）
title = "示例服务"

# 业务接口：所有路由会自动挂到 /api/services/hello/ 下
router = APIRouter()

# ── 可选契约字段 ──────────────────────────────────────────────
# UI静态目录（相对本文件所在目录）：
# 在 impl/hello/static/ 下放 index.html 等文件，
# 浏览器访问 /api/services/hello/ 即可打开整个界面
# static_dir = "static"


# ── 接口示例 ──────────────────────────────────────────────────
@router.get("/api/ping")
async def ping():
    """健康检查：GET /api/services/hello/api/ping"""
    return {"pong": True, "service": title}


@router.get("/api/echo")
async def echo(message: str = "你好，服务挂载"):
    """回显接口：GET /api/services/hello/api/echo?message=xxx"""
    return {"echo": message}
