#!/usr/bin/env python3
"""
在8002端口启动服务（禁用reload）
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        log_level="info"
    )
