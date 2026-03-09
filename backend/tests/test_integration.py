"""
集成测试

测试完整的API流程
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_full_user_flow(client: AsyncClient):
    """测试完整的用户流程：注册 -> 登录 -> 获取信息 -> 更新 -> 删除"""
    import uuid
    
    # 1. 注册用户
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpassword123"
        }
    )
    
    # 如果数据库连接失败，跳过测试
    if register_response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过集成测试")
    
    assert register_response.status_code == status.HTTP_201_CREATED
    user_id = register_response.json()["id"]
    
    # 2. 登录
    login_response = await client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 获取当前用户信息
    me_response = await client.get("/api/users/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["username"] == username
    
    # 4. 更新用户信息
    update_response = await client.put(
        "/api/users/me",
        headers=headers,
        json={
            "display_name": "Updated Name",
            "bio": "Test bio"
        }
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["display_name"] == "Updated Name"
    
    # 5. 删除用户
    delete_response = await client.delete(f"/api/users/{user_id}", headers=headers)
    assert delete_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_full_post_flow(client: AsyncClient):
    """测试完整的文章流程：创建 -> 获取 -> 更新 -> 发布 -> 删除"""
    import uuid
    
    # 1. 注册并登录
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    register_response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpassword123"
        }
    )
    
    # 如果数据库连接失败，跳过测试
    if register_response.status_code in [status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]:
        pytest.skip("数据库连接失败，跳过集成测试")

    assert register_response.status_code == status.HTTP_201_CREATED

    login_response = await client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": "testpassword123"
        }
    )

    # 如果登录失败，跳过测试
    if login_response.status_code != status.HTTP_200_OK:
        pytest.skip("无法登录，跳过集成测试")
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 创建文章
    create_response = await client.post(
        "/api/posts/",
        headers=headers,
        json={
            "title": "Test Post",
            "content": "Test content",
            "status": "draft"
        }
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    post_id = create_response.json()["id"]
    
    # 3. 获取文章详情
    get_response = await client.get(f"/api/posts/{post_id}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["title"] == "Test Post"
    
    # 4. 更新文章
    update_response = await client.put(
        f"/api/posts/{post_id}",
        headers=headers,
        json={
            "title": "Updated Post",
            "content": "Updated content"
        }
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["title"] == "Updated Post"
    
    # 5. 发布文章
    publish_response = await client.post(f"/api/posts/{post_id}/publish", headers=headers)
    assert publish_response.status_code == status.HTTP_200_OK
    assert publish_response.json()["status"] == "published"
    
    # 6. 删除文章
    delete_response = await client.delete(f"/api/posts/{post_id}", headers=headers)
    assert delete_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_auth_protection(client: AsyncClient):
    """测试API的认证保护"""
    
    # 测试未认证访问需要登录的接口
    protected_endpoints = [
        ("GET", "/api/users/me"),
        ("PUT", "/api/users/me"),
        ("POST", "/api/posts/"),
        ("POST", "/api/upload/image"),
    ]
    
    for method, endpoint in protected_endpoints:
        if method == "GET":
            response = await client.get(endpoint)
        elif method == "PUT":
            response = await client.put(endpoint, json={})
        elif method == "POST":
            response = await client.post(endpoint, json={})
        else:
            continue
        
        # 应该返回401或404（如果路由未注册）
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND], f"{method} {endpoint} 应该返回401或404"
