"""
MCP服务集成模块

将MCP服务集成到FastAPI后端，提供SSE端点供MCP客户端连接。
"""
from .router import mcp_router

__all__ = ["mcp_router"]
