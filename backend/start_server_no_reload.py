#!/usr/bin/env python3
"""
禁用reload的服务启动脚本
用于测试环境
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
