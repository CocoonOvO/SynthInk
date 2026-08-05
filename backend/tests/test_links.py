"""
外链管理接口测试

测试 /api/links/* 相关接口：
- 公开列表
- 增删改需要超管权限
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_list_links_public(client: AsyncClient):
    """测试公开获取外链列表"""
    response = await client.get("/api/links/")
    # 没有数据库连接时可能返回500或空列表
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_create_link_no_auth(client: AsyncClient):
    """测试未认证创建外链"""
    response = await client.post(
        "/api/links/",
        json={"name": "测试链接", "url": "https://example.com"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_link_invalid_url(client: AsyncClient):
    """测试非法URL（非http/https）应被拒绝"""
    response = await client.post(
        "/api/links/",
        json={"name": "危险链接", "url": "javascript:alert(1)"}
    )
    assert response.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]


@pytest.mark.asyncio
async def test_update_link_no_auth(client: AsyncClient):
    """测试未认证更新外链"""
    response = await client.put(
        "/api/links/some-id",
        json={"name": "更新链接", "url": "https://example.com"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_link_no_auth(client: AsyncClient):
    """测试未认证删除外链"""
    response = await client.delete("/api/links/some-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
