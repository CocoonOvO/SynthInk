"""
应用入口文件
"""
from .app import app
from .routers import api_router

# 注册API路由
app.include_router(api_router)

# TODO: 注册其他路由或中间件
# - 静态文件服务
# - 前端路由回退

if __name__ == "__main__":
    import uvicorn
    import sys
    from .config import get_settings
    
    settings = get_settings()
    
    # 解析命令行参数
    port = 8000
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG_MODE,
        log_level="debug" if settings.DEBUG_MODE else "info",
    )
