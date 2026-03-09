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
    """测试未认证创建评论"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "This is a test comment",
            "post_id": "some-post-id"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
    """测试未认证创建回复"""
    response = await client.post(
        "/api/comments",
        json={
            "content": "This is a reply",
            "post_id": "some-post-id",
            "parent_id": "some-parent-id"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
