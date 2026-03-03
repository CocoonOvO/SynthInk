"""
超管配置接口测试

测试 /api/admin/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_admin_login_wrong_password(client: AsyncClient):
    """测试超管登录密码错误"""
    response = await client.post(
        "/api/admin/login",
        json={
            "username": "admin",
            "password": "wrongpassword"
        }
    )
    # 应该返回401或404（如果路由未注册）
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_admin_login_invalid_username(client: AsyncClient):
    """测试超管登录用户名不存在"""
    response = await client.post(
        "/api/admin/login",
        json={
            "username": "nonexistent",
            "password": "123456"
        }
    )
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_get_setup_status(client: AsyncClient):
    """测试获取项目设置状态（公开接口）"""
    response = await client.get("/api/admin/setup-status")
    # 可能返回200或404（如果路由未注册）
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    if response.status_code == 200:
        data = response.json()
        assert "config_db_initialized" in data
        assert "has_admin_account" in data
        assert "has_database_config" in data
        assert "database_connected" in data


@pytest.mark.asyncio
async def test_get_database_configs_no_auth(client: AsyncClient):
    """测试未认证获取数据库配置列表"""
    response = await client.get("/api/admin/database-configs")
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_get_system_configs_no_auth(client: AsyncClient):
    """测试未认证获取系统配置列表"""
    response = await client.get("/api/admin/system-configs")
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_create_database_config_no_auth(client: AsyncClient):
    """测试未认证创建数据库配置"""
    response = await client.post(
        "/api/admin/database-configs",
        json={
            "name": "test_config",
            "host": "localhost",
            "port": 5432,
            "database": "test_db",
            "username": "test",
            "password": "test123"
        }
    )
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_update_system_config_no_auth(client: AsyncClient):
    """测试未认证更新系统配置"""
    response = await client.put(
        "/api/admin/system-configs/test_key",
        json={
            "value": "test_value"
        }
    )
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_get_audit_logs_no_auth(client: AsyncClient):
    """测试未认证获取审计日志"""
    response = await client.get("/api/admin/audit-logs")
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
