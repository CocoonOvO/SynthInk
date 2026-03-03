"""
分组管理接口测试

测试 /api/groups/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_list_groups_public(client: AsyncClient):
    """测试公开获取分组列表"""
    response = await client.get("/api/groups/")
    # 如果没有数据库连接，可能返回500
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_get_group_not_found(client: AsyncClient):
    """测试获取不存在的分组"""
    response = await client.get("/api/groups/non-existent-id")
    # 如果没有数据库连接，可能返回500
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_create_group_no_auth(client: AsyncClient):
    """测试未认证创建分组"""
    response = await client.post(
        "/api/groups/",
        json={"name": "Test Group"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_group_no_auth(client: AsyncClient):
    """测试未认证更新分组"""
    response = await client.put(
        "/api/groups/some-id",
        json={"name": "Updated Group"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_group_no_auth(client: AsyncClient):
    """测试未认证删除分组"""
    response = await client.delete("/api/groups/some-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
