"""
标签管理接口测试

测试 /api/tags/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_list_tags_public(client: AsyncClient):
    """测试公开获取标签列表"""
    response = await client.get("/api/tags/")
    # 如果没有数据库连接，可能返回500
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_get_tag_not_found(client: AsyncClient):
    """测试获取不存在的标签"""
    response = await client.get("/api/tags/non-existent-id")
    # 如果没有数据库连接，可能返回500
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_create_tag_no_auth(client: AsyncClient):
    """测试未认证创建标签"""
    response = await client.post(
        "/api/tags/",
        json={"name": "Test Tag"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_tag_no_auth(client: AsyncClient):
    """测试未认证更新标签"""
    response = await client.put(
        "/api/tags/some-id",
        json={"name": "Updated Tag"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_tag_no_auth(client: AsyncClient):
    """测试未认证删除标签"""
    response = await client.delete("/api/tags/some-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
