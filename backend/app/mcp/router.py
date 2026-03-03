"""
MCP服务路由

提供MCP服务的SSE端点，将MCP服务集成到FastAPI后端。
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx

from ..config_db import config_admin_auth, ConfigAdmin, require_config_admin
from ..config import get_settings

# 创建路由
mcp_router = APIRouter(prefix="/mcp", tags=["MCP服务"])

# 配置
BASE_URL = os.getenv("SYNTHINK_API_URL", "http://localhost:8001")


# ========== 请求模型 ==========

class MCPRequest(BaseModel):
    """MCP请求模型"""
    tool: str = Field(..., description="要调用的工具名称")
    params: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class AdminLoginRequest(BaseModel):
    """超管登录请求"""
    username: str = Field(..., description="超管用户名")
    password: str = Field(..., description="密码")


class DatabaseConfigRequest(BaseModel):
    """数据库配置请求"""
    name: str = Field(default="default", description="配置名称")
    db_type: str = Field(default="postgresql", description="数据库类型")
    host: str = Field(default="localhost", description="主机地址")
    port: int = Field(default=5432, description="端口号")
    database: str = Field(..., description="数据库名")
    schema: str = Field(default="public", description="PostgreSQL schema名称")
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    pool_size: int = Field(default=5, description="连接池大小")


class SwitchDatabaseRequest(BaseModel):
    """切换数据库请求"""
    database: str = Field(..., description="新数据库名称")
    schema: str = Field(default="public", description="PostgreSQL schema名称")
    create_if_not_exists: bool = Field(default=True, description="数据库不存在时是否创建")
    init_if_empty: bool = Field(default=True, description="空数据库是否初始化表结构")


class SystemConfigUpdateRequest(BaseModel):
    """系统配置更新请求"""
    value: Any = Field(..., description="配置值")
    value_type: Optional[str] = Field(default=None, description="值类型")


class AuditLogQueryRequest(BaseModel):
    """审计日志查询请求"""
    limit: int = Field(default=50, ge=1, le=1000, description="返回记录数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")


# ========== 辅助函数 ==========

async def api_request(
    method: str,
    path: str,
    token: Optional[str] = None,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    发送内部API请求
    
    Args:
        method: HTTP方法
        path: API路径
        token: 认证令牌
        json_data: 请求体数据
        params: 查询参数
        
    Returns:
        API响应数据
    """
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=json_data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        response.raise_for_status()
        return response.json()


# ========== MCP工具端点 ==========

@mcp_router.post(
    "/tools/admin_login",
    summary="超管登录",
    description="使用配置库超管账号登录，获取访问令牌。默认账号: admin / 123456"
)
async def mcp_admin_login(request: AdminLoginRequest) -> Dict[str, Any]:
    """超管登录"""
    result = await api_request(
        "POST",
        "/api/admin/login",
        json_data={"username": request.username, "password": request.password}
    )
    return {"success": True, "access_token": result.get("access_token")}


@mcp_router.post(
    "/tools/admin_logout",
    summary="超管登出",
    description="使当前访问令牌失效"
)
async def mcp_admin_logout(admin: ConfigAdmin = Depends(require_config_admin)) -> Dict[str, Any]:
    """超管登出"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    await api_request("POST", "/api/admin/logout", token=token)
    return {"success": True, "message": "登出成功"}


@mcp_router.get(
    "/tools/setup_status",
    summary="获取系统设置状态",
    description="检查系统是否已完成初始化配置。无需认证。"
)
async def mcp_get_setup_status() -> Dict[str, Any]:
    """获取系统设置状态"""
    return await api_request("GET", "/api/admin/setup-status")


@mcp_router.get(
    "/tools/database_status",
    summary="获取当前数据库配置",
    description="获取当前激活的数据库配置信息"
)
async def mcp_get_database_status(admin: ConfigAdmin = Depends(require_config_admin)) -> Dict[str, Any]:
    """获取当前数据库配置"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    return await api_request("GET", "/api/admin/database", token=token)


@mcp_router.post(
    "/tools/configure_database",
    summary="配置业务数据库",
    description="创建或更新业务数据库配置"
)
async def mcp_configure_database(
    request: DatabaseConfigRequest,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """配置业务数据库"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    config = request.model_dump()
    result = await api_request("POST", "/api/admin/database", token=token, json_data=config)
    return {"success": True, "message": f"数据库配置成功: {result.get('database')}", "data": result}


@mcp_router.post(
    "/tools/switch_database",
    summary="切换数据库",
    description="切换到新的数据库和schema。可以自动创建数据库并初始化表结构。注意：此操作不会迁移数据。"
)
async def mcp_switch_database(
    request: SwitchDatabaseRequest,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """切换数据库"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    data = request.model_dump()
    result = await api_request("POST", "/api/admin/database/switch", token=token, json_data=data)
    return {"success": True, "data": result}


@mcp_router.post(
    "/tools/test_connection",
    summary="测试数据库连接",
    description="测试数据库连接是否可用。无需认证。"
)
async def mcp_test_database_connection(request: DatabaseConfigRequest) -> Dict[str, Any]:
    """测试数据库连接"""
    config = request.model_dump()
    result = await api_request("POST", "/api/admin/database/test", json_data=config)
    return {
        "success": result.get("success", False),
        "message": "连接成功" if result.get("success") else f"连接失败: {result.get('error')}"
    }


@mcp_router.get(
    "/tools/init_status",
    summary="获取数据库初始化状态",
    description="检查业务数据库和表结构是否已初始化"
)
async def mcp_get_init_status(admin: ConfigAdmin = Depends(require_config_admin)) -> Dict[str, Any]:
    """获取数据库初始化状态"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    return await api_request("GET", "/api/admin/database/init-status", token=token)


@mcp_router.post(
    "/tools/init_database",
    summary="初始化数据库",
    description="创建业务数据库和表结构（如果不存在）。执行完整初始化流程。"
)
async def mcp_init_database(admin: ConfigAdmin = Depends(require_config_admin)) -> Dict[str, Any]:
    """初始化数据库"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    result = await api_request("POST", "/api/admin/database/init", token=token)
    return {"success": True, "data": result}


@mcp_router.post(
    "/tools/complete_init_wizard",
    summary="完成初始化向导",
    description="一步完成数据库配置、连接测试和业务库初始化"
)
async def mcp_complete_init_wizard(
    request: DatabaseConfigRequest,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """完成初始化向导"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    config = request.model_dump()
    result = await api_request("POST", "/api/admin/init-wizard/complete", token=token, json_data=config)
    return {"success": True, "data": result}


@mcp_router.get(
    "/tools/system_configs",
    summary="获取系统配置列表",
    description="获取所有系统配置项。敏感配置会被遮盖。"
)
async def mcp_get_system_configs(
    category: Optional[str] = None,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> List[Dict[str, Any]]:
    """获取系统配置列表"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    params = {}
    if category:
        params["category"] = category
    return await api_request("GET", "/api/admin/configs", token=token, params=params)


@mcp_router.get(
    "/tools/system_config/{key}",
    summary="获取单个系统配置",
    description="根据配置键获取单个系统配置"
)
async def mcp_get_system_config(
    key: str,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """获取单个系统配置"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    return await api_request("GET", f"/api/admin/configs/{key}", token=token)


@mcp_router.put(
    "/tools/system_config/{key}",
    summary="更新系统配置",
    description="更新指定键的系统配置值。不可编辑的配置项无法更新。"
)
async def mcp_update_system_config(
    key: str,
    request: SystemConfigUpdateRequest,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """更新系统配置"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    data = {"value": request.value}
    if request.value_type:
        data["value_type"] = request.value_type
    await api_request("PUT", f"/api/admin/configs/{key}", token=token, json_data=data)
    return {"success": True, "message": f"配置 '{key}' 更新成功"}


@mcp_router.get(
    "/tools/audit_logs",
    summary="获取审计日志",
    description="查看配置库的操作历史记录"
)
async def mcp_get_audit_logs(
    limit: int = 50,
    offset: int = 0,
    admin: ConfigAdmin = Depends(require_config_admin)
) -> Dict[str, Any]:
    """获取审计日志"""
    token = config_admin_auth.create_access_token(admin.id, admin.username)
    params = {"limit": limit, "offset": offset}
    return await api_request("GET", "/api/admin/audit-logs", token=token, params=params)


# ========== MCP文档端点 ==========

@mcp_router.get(
    "/docs",
    summary="获取MCP工具文档",
    description="返回可用的MCP工具列表和说明"
)
async def mcp_get_docs() -> Dict[str, Any]:
    """获取MCP工具文档"""
    return {
        "tools": [
            {
                "name": "admin_login",
                "description": "超管登录，获取JWT令牌",
                "auth_required": False
            },
            {
                "name": "admin_logout",
                "description": "超管登出",
                "auth_required": True
            },
            {
                "name": "setup_status",
                "description": "获取系统设置状态",
                "auth_required": False
            },
            {
                "name": "database_status",
                "description": "获取当前数据库配置",
                "auth_required": True
            },
            {
                "name": "configure_database",
                "description": "配置业务数据库",
                "auth_required": True
            },
            {
                "name": "switch_database",
                "description": "切换数据库和schema",
                "auth_required": True
            },
            {
                "name": "test_connection",
                "description": "测试数据库连接",
                "auth_required": False
            },
            {
                "name": "init_status",
                "description": "获取数据库初始化状态",
                "auth_required": True
            },
            {
                "name": "init_database",
                "description": "初始化数据库",
                "auth_required": True
            },
            {
                "name": "complete_init_wizard",
                "description": "完成初始化向导",
                "auth_required": True
            },
            {
                "name": "system_configs",
                "description": "获取系统配置列表",
                "auth_required": True
            },
            {
                "name": "system_config",
                "description": "获取单个系统配置",
                "auth_required": True
            },
            {
                "name": "update_system_config",
                "description": "更新系统配置",
                "auth_required": True
            },
            {
                "name": "audit_logs",
                "description": "获取审计日志",
                "auth_required": True
            }
        ]
    }
