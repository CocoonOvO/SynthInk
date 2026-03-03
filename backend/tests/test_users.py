"""
用户管理接口测试

测试 /api/users/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_current_user_no_auth(client: AsyncClient):
    """测试未认证获取当前用户信息"""
    response = await client.get("/api/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """测试获取不存在的用户（需要认证）"""
    # 使用一个假的token
    headers = {"Authorization": "Bearer fake_token"}
    response = await client.get("/api/users/non-existent-id", headers=headers)
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_list_users_no_auth(client: AsyncClient):
    """测试未认证获取用户列表"""
    response = await client.get("/api/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_user_no_auth(client: AsyncClient):
    """测试未认证删除用户"""
    response = await client.delete("/api/users/some-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_user_no_auth(client: AsyncClient):
    """测试未认证更新用户"""
    response = await client.put(
        "/api/users/me",
        json={"display_name": "Test"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
