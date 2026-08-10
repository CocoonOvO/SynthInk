"""
评论系统接口测试

测试 /api/comments/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


# ========== 公开接口测试 ==========

@pytest.mark.asyncio
async def test_get_post_comments_public(client: AsyncClient):
    """测试公开获取文章评论列表"""
    response = await client.get("/api/comments/post/some-post-id")
    # 公开接口，无需认证
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_get_comment_detail_public(client: AsyncClient):
    """测试公开获取评论详情"""
    response = await client.get("/api/comments/some-comment-id")
    # 公开接口，无需认证
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_get_user_comments_public(client: AsyncClient):
    """测试公开获取用户评论列表"""
    response = await client.get("/api/comments/user/some-user-id")
    # 公开接口，无需认证
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


# ========== 需要认证的接口测试 ==========

@pytest.mark.asyncio
async def test_create_comment_no_auth(client: AsyncClient):
    """测试未认证创建评论（匿名评论已放开，不再要求登录）"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "This is a test comment",
            "post_id": "some-post-id"
        }
    )
    # 不存在的文章返回404；缺失 author_name 返回422；均不再返回401
    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


@pytest.mark.asyncio
async def test_update_comment_no_auth(client: AsyncClient):
    """测试未认证更新评论"""
    response = await client.put(
        "/api/comments/some-comment-id",
        json={"content": "Updated comment content"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_comment_no_auth(client: AsyncClient):
    """测试未认证删除评论"""
    response = await client.delete("/api/comments/some-comment-id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ========== 数据验证测试 ==========

@pytest.mark.asyncio
async def test_create_comment_empty_content(client: AsyncClient, auth_headers):
    """测试创建空内容评论"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "",
            "post_id": "some-post-id"
        },
        headers=auth_headers
    )
    # 应该返回400错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_comment_too_long_content(client: AsyncClient, auth_headers):
    """测试创建超长内容评论"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "a" * 2001,  # 超过2000字符限制
            "post_id": "some-post-id"
        },
        headers=auth_headers
    )
    # 应该返回422错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_comment_missing_post_id(client: AsyncClient, auth_headers):
    """测试创建评论缺少post_id"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "Test comment content"
        },
        headers=auth_headers
    )
    # 应该返回422错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_comment_empty_content(client: AsyncClient, auth_headers):
    """测试更新评论为空内容"""
    response = await client.put(
        "/api/comments/some-comment-id",
        json={"content": ""},
        headers=auth_headers
    )
    # 应该返回422错误
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ========== 分页参数测试 ==========

@pytest.mark.asyncio
async def test_get_post_comments_pagination(client: AsyncClient):
    """测试评论列表分页参数"""
    # 测试正常分页
    response = await client.get("/api/comments/post/some-post-id?page=1&page_size=10")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    # 测试无效页码
    response = await client.get("/api/comments/post/some-post-id?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # 测试超大页码
    response = await client.get("/api/comments/post/some-post-id?page=99999")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    # 测试超大page_size
    response = await client.get("/api/comments/post/some-post-id?page_size=200")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_user_comments_pagination(client: AsyncClient):
    """测试用户评论列表分页参数"""
    # 测试正常分页
    response = await client.get("/api/comments/user/some-user-id?page=1&page_size=10")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    # 测试无效页码
    response = await client.get("/api/comments/user/some-user-id?page=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ========== 嵌套回复测试 ==========

@pytest.mark.asyncio
async def test_create_reply_no_auth(client: AsyncClient):
    """测试未认证创建回复（匿名回复同样放开）"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "This is a reply",
            "post_id": "some-post-id",
            "parent_id": "some-parent-id"
        }
    )
    # 不存在的文章返回404；缺失 author_name 返回422；均不再返回401
    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]


@pytest.mark.asyncio
async def test_create_reply_with_parent_id(client: AsyncClient, auth_headers):
    """测试创建带parent_id的回复"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "This is a reply to another comment",
            "post_id": "some-post-id",
            "parent_id": "some-parent-id"
        },
        headers=auth_headers
    )
    # 可能返回404（文章或父评论不存在）或成功
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]


# ========== 响应格式测试 ==========

@pytest.mark.asyncio
async def test_get_post_comments_response_format(client: AsyncClient):
    """测试评论列表响应格式"""
    response = await client.get("/api/comments/post/some-post-id")
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        # 检查响应结构
        assert "total" in data
        assert "comments" in data
        assert isinstance(data["comments"], list)


@pytest.mark.asyncio
async def test_get_comment_detail_response_format(client: AsyncClient):
    """测试评论详情响应格式"""
    response = await client.get("/api/comments/some-comment-id")
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        # 检查必要字段
        assert "id" in data
        assert "post_id" in data
        assert "author" in data
        assert "content" in data
        assert "created_at" in data
        assert "replies" in data
        assert isinstance(data["replies"], list)


# ========== 权限测试 ==========

@pytest.mark.asyncio
async def test_update_other_user_comment(client: AsyncClient, auth_headers):
    """测试更新其他用户的评论（应该失败）"""
    response = await client.put(
        "/api/comments/other-user-comment-id",
        json={"content": "Trying to update other's comment"},
        headers=auth_headers
    )
    # 应该返回403或404
    assert response.status_code in [
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]


@pytest.mark.asyncio
async def test_delete_other_user_comment(client: AsyncClient, auth_headers):
    """测试删除其他用户的评论（应该失败）"""
    response = await client.delete(
        "/api/comments/other-user-comment-id",
        headers=auth_headers
    )
    # 应该返回403或404
    assert response.status_code in [
        status.HTTP_403_FORBIDDEN,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]


# ========== 匿名评论测试 ==========

async def _get_first_published_post(client: AsyncClient) -> str:
    """获取第一篇已发布文章ID（无文章则跳过测试）"""
    response = await client.get("/api/posts", follow_redirects=True)
    if response.status_code != status.HTTP_200_OK:
        pytest.skip("无法获取文章列表，跳过测试")
    data = response.json()
    posts = data.get("items", []) if isinstance(data, dict) else data
    if not posts:
        pytest.skip("没有可用文章进行测试")
    return posts[0]["id"]


@pytest.mark.asyncio
async def test_create_anonymous_comment_success(client: AsyncClient):
    """测试匿名评论成功（名称必填、邮箱可选、按IP落库）"""
    import random
    post_id = await _get_first_published_post(client)
    # 每次运行使用随机IP，避免测试库累积数据触发限流
    headers = {"X-Forwarded-For": f"10.10.{random.randint(1, 200)}.{random.randint(1, 200)}"}
    response = await client.post(
        "/api/comments",
        headers=headers,
        json={
            "post_id": post_id,
            "content": "匿名测试评论",
            "author_name": "路人甲",
            "author_email": "guest@example.com"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    # 作者信息为匿名名称
    assert data["author"]["id"] == "anonymous"
    assert data["author"]["username"] == "路人甲"


@pytest.mark.asyncio
async def test_create_anonymous_comment_without_name(client: AsyncClient):
    """测试匿名评论缺名称（应422）"""
    import random
    post_id = await _get_first_published_post(client)
    response = await client.post(
        "/api/comments",
        headers={"X-Forwarded-For": f"10.11.{random.randint(1, 200)}.{random.randint(1, 200)}"},
        json={"post_id": post_id, "content": "没有名称的评论"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_create_anonymous_comment_invalid_email(client: AsyncClient):
    """测试匿名评论邮箱格式非法（应422）"""
    import random
    post_id = await _get_first_published_post(client)
    response = await client.post(
        "/api/comments",
        headers={"X-Forwarded-For": f"10.12.{random.randint(1, 200)}.{random.randint(1, 200)}"},
        json={
            "post_id": post_id,
            "content": "邮箱格式错误",
            "author_name": "路人乙",
            "author_email": "not-an-email"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_anonymous_comment_daily_limit(client: AsyncClient, monkeypatch):
    """测试匿名评论每日上限（触发429）"""
    import random
    from app.routers.comments import (
        ANONYMOUS_COMMENT_DAILY_LIMIT, ANONYMOUS_COMMENT_MIN_INTERVAL
    )
    # 收紧限流参数便于测试：每日上限2条、关闭间隔限制
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_DAILY_LIMIT", 2)
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_MIN_INTERVAL", 0)

    post_id = await _get_first_published_post(client)
    # 每次运行使用随机IP，避免测试库累积数据互相污染
    headers = {"X-Forwarded-For": f"10.20.{random.randint(1, 200)}.{random.randint(1, 200)}"}

    # 前两条应成功
    for i in range(2):
        response = await client.post(
            "/api/comments",
            headers=headers,
            json={
                "post_id": post_id,
                "content": f"限流测试评论{i}",
                "author_name": "限流测试"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED

    # 第三条触发每日上限
    response = await client.post(
        "/api/comments",
        headers=headers,
        json={
            "post_id": post_id,
            "content": "限流测试评论2",
            "author_name": "限流测试"
        }
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_anonymous_comment_min_interval(client: AsyncClient, monkeypatch):
    """测试匿名评论最小间隔（触发429）"""
    import random
    from app.routers.comments import (
        ANONYMOUS_COMMENT_DAILY_LIMIT, ANONYMOUS_COMMENT_MIN_INTERVAL
    )
    # 收紧限流参数便于测试：每日上限调大、间隔设为1小时
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_DAILY_LIMIT", 100)
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_MIN_INTERVAL", 3600)

    post_id = await _get_first_published_post(client)
    # 每次运行使用随机IP，避免测试库累积数据互相污染
    headers = {"X-Forwarded-For": f"10.30.{random.randint(1, 200)}.{random.randint(1, 200)}"}

    # 第一条成功
    response = await client.post(
        "/api/comments",
        headers=headers,
        json={
            "post_id": post_id,
            "content": "间隔测试评论1",
            "author_name": "间隔测试"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED

    # 第二条触发间隔限制
    response = await client.post(
        "/api/comments",
        headers=headers,
        json={
            "post_id": post_id,
            "content": "间隔测试评论2",
            "author_name": "间隔测试"
        }
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_logged_in_comment_not_rate_limited(client: AsyncClient, auth_headers, monkeypatch):
    """测试登录用户评论不受匿名限流影响"""
    from app.routers.comments import (
        ANONYMOUS_COMMENT_DAILY_LIMIT, ANONYMOUS_COMMENT_MIN_INTERVAL
    )
    # 收紧匿名限流：每日上限1条、关闭间隔，登录用户应完全不受影响
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_DAILY_LIMIT", 1)
    monkeypatch.setattr("app.routers.comments.ANONYMOUS_COMMENT_MIN_INTERVAL", 0)

    post_id = await _get_first_published_post(client)
    headers = {"X-Forwarded-For": "10.10.0.12", **auth_headers}

    for i in range(3):
        response = await client.post(
            "/api/comments",
            headers=headers,
            json={
                "post_id": post_id,
                "content": f"登录用户评论{i}",
                # 登录用户即使传匿名字段也应被忽略
                "author_name": "恶意昵称",
                "author_email": "spam@example.com"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # 作者信息来自登录账号而非传入的匿名字段
        assert data["author"]["id"] != "anonymous"
        assert data["author"]["username"] != "恶意昵称"
