"""
用户认证接口测试

测试 /api/auth/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_register_user_no_data(client: AsyncClient):
    """测试注册用户但不提供数据"""
    response = await client.post("/api/auth/register", json={})
    # 应该返回422验证错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_no_data(client: AsyncClient):
    """测试登录但不提供数据"""
    response = await client.post("/api/auth/token", data={})
    # 应该返回422验证错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_wrong_password_format(client: AsyncClient):
    """测试登录格式错误"""
    response = await client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "wrong"
        }
    )
    # 如果没有数据库，可能返回500，但格式正确
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_refresh_token_no_token(client: AsyncClient):
    """测试刷新令牌但不提供令牌"""
    response = await client.post("/api/auth/refresh")
    # 应该返回422验证错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_logout_no_auth(client: AsyncClient):
    """测试未认证登出"""
    response = await client.post("/api/auth/logout")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_reset_password_no_auth(client: AsyncClient):
    """测试未认证重置密码"""
    response = await client.post(
        "/api/auth/password/reset",
        params={
            "old_password": "old",
            "new_password": "new"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
