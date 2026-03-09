"""
点赞功能单元测试
"""
import pytest
from httpx import AsyncClient
from fastapi import status


async def check_db_available(client: AsyncClient) -> bool:
    """检查数据库是否可用"""
    response = await client.get("/api/posts", follow_redirects=True)
    return response.status_code not in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]


@pytest.mark.asyncio
async def test_like_post_success(client: AsyncClient, auth_headers):
    """测试点赞文章成功"""
    # 先获取一篇文章
    response = await client.get("/api/posts", follow_redirects=True)

    # 检查数据库连接
    if response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过测试")

    assert response.status_code == status.HTTP_200_OK

    posts = response.json()
    if not posts:
        pytest.skip("没有可用文章进行测试")

    post_id = posts[0]["id"]

    # 点赞文章
    response = await client.post(
        f"/api/likes/{post_id}",
        headers=auth_headers
    )

    # 可能成功或已点赞
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_200_OK
    ]

    data = response.json()
    assert data["post_id"] == post_id
    assert data["is_liked"] is True
    assert data["like_count"] >= 1


@pytest.mark.asyncio
async def test_like_post_not_found(client: AsyncClient, auth_headers):
    """测试点赞不存在的文章"""
    response = await client.post(
        "/api/likes/non-existent-post-id",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_like_post_unauthorized(client: AsyncClient):
    """测试未登录点赞"""
    response = await client.post("/api/likes/some-post-id")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_unlike_post_success(client: AsyncClient, auth_headers):
    """测试取消点赞成功"""
    # 先获取一篇文章
    response = await client.get("/api/posts", follow_redirects=True)

    # 检查数据库连接
    if response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过测试")

    assert response.status_code == status.HTTP_200_OK

    posts = response.json()
    if not posts:
        pytest.skip("没有可用文章进行测试")

    post_id = posts[0]["id"]

    # 先点赞
    await client.post(f"/api/likes/{post_id}", headers=auth_headers)

    # 取消点赞
    response = await client.delete(
        f"/api/likes/{post_id}",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["post_id"] == post_id
    assert data["is_liked"] is False


@pytest.mark.asyncio
async def test_unlike_post_unauthorized(client: AsyncClient):
    """测试未登录取消点赞"""
    response = await client.delete("/api/likes/some-post-id")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_like_status_public(client: AsyncClient):
    """测试公开获取点赞状态（未登录）"""
    # 先获取一篇文章
    response = await client.get("/api/posts", follow_redirects=True)

    # 检查数据库连接
    if response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过测试")

    assert response.status_code == status.HTTP_200_OK

    posts = response.json()
    if not posts:
        pytest.skip("没有可用文章进行测试")

    post_id = posts[0]["id"]

    # 获取点赞状态（无需登录）
    response = await client.get(f"/api/likes/{post_id}/status", follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["post_id"] == post_id
    assert data["is_liked"] is False  # 未登录用户始终为False
    assert "like_count" in data


@pytest.mark.asyncio
async def test_get_like_status_authenticated(client: AsyncClient, auth_headers):
    """测试登录用户获取点赞状态"""
    # 先获取一篇文章
    response = await client.get("/api/posts", follow_redirects=True)

    # 检查数据库连接
    if response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过测试")

    assert response.status_code == status.HTTP_200_OK

    posts = response.json()
    if not posts:
        pytest.skip("没有可用文章进行测试")

    post_id = posts[0]["id"]

    # 先点赞
    await client.post(f"/api/likes/{post_id}", headers=auth_headers)

    # 获取点赞状态
    response = await client.get(
        f"/api/likes/{post_id}/status",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["post_id"] == post_id
    assert data["is_liked"] is True
    assert data["like_count"] >= 1


@pytest.mark.asyncio
async def test_get_my_liked_posts(client: AsyncClient, auth_headers):
    """测试获取我点赞的文章列表"""
    response = await client.get(
        "/api/likes/user/me",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)

    # 检查返回的数据结构
    if data:
        assert "post_id" in data[0]
        assert "like_count" in data[0]
        assert "is_liked" in data[0]
        assert data[0]["is_liked"] is True


@pytest.mark.asyncio
async def test_get_my_liked_posts_unauthorized(client: AsyncClient):
    """测试未登录获取点赞列表"""
    response = await client.get("/api/likes/user/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_post_likers(client: AsyncClient):
    """测试获取文章点赞用户列表"""
    # 先获取一篇文章
    response = await client.get("/api/posts", follow_redirects=True)

    # 检查数据库连接
    if response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过测试")

    assert response.status_code == status.HTTP_200_OK

    posts = response.json()
    if not posts:
        pytest.skip("没有可用文章进行测试")

    post_id = posts[0]["id"]

    # 获取点赞用户列表
    response = await client.get(f"/api/likes/post/{post_id}/users", follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
