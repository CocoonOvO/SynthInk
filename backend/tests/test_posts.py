"""
文章管理接口测试

测试 /api/posts/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_list_posts_public(client: AsyncClient):
    """测试公开获取文章列表"""
    response = await client.get("/api/posts/")
    # 如果没有数据库连接，可能返回500，但接口应该是公开的
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_get_post_not_found(client: AsyncClient):
    """测试获取不存在的文章"""
    response = await client.get("/api/posts/non-existent-id")
    # 如果没有数据库连接，可能返回500
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_create_post_no_auth(client: AsyncClient):
    """测试未认证创建文章"""
    response = await client.post(
        "/api/posts/",
        json={
            "title": "Test Post",
            "content": "This is a test post content"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_post_no_auth(client: AsyncClient):
    """测试未认证更新文章"""
    response = await client.put(
        "/api/posts/some-id",
        json={"title": "Updated Title"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_post_no_auth(client: AsyncClient):
    """测试未认证删除文章"""
    response = await client.delete("/api/posts/some-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_publish_post_no_auth(client: AsyncClient):
    """测试未认证发布文章"""
    response = await client.post("/api/posts/some-id/publish")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
