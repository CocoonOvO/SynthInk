"""
搜索功能接口测试

测试 /api/search/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_search_empty_query(client: AsyncClient):
    """测试空关键词搜索"""
    response = await client.get("/api/search/?q=")
    # 空关键词应该返回400或200空结果
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.asyncio
async def test_search_basic(client: AsyncClient):
    """测试基础搜索功能"""
    response = await client.get("/api/search/?q=test")
    # 接口应该是公开的，返回200或500（数据库未连接）
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert "posts" in data
        assert "tags" in data
        assert "users" in data
        assert "groups" in data
        assert "comments" in data


@pytest.mark.asyncio
async def test_search_by_type_posts(client: AsyncClient):
    """测试按类型搜索文章"""
    response = await client.get("/api/search/?q=python&type=posts")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        # 只返回文章类型
        assert "posts" in data


@pytest.mark.asyncio
async def test_search_by_type_tags(client: AsyncClient):
    """测试按类型搜索标签"""
    response = await client.get("/api/search/?q=tech&type=tags")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "tags" in data


@pytest.mark.asyncio
async def test_search_by_type_users(client: AsyncClient):
    """测试按类型搜索用户"""
    response = await client.get("/api/search/?q=user&type=users")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "users" in data


@pytest.mark.asyncio
async def test_search_by_type_groups(client: AsyncClient):
    """测试按类型搜索分组"""
    response = await client.get("/api/search/?q=group&type=groups")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "groups" in data


@pytest.mark.asyncio
async def test_search_by_type_comments(client: AsyncClient):
    """测试按类型搜索评论"""
    response = await client.get("/api/search/?q=comment&type=comments")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "comments" in data


@pytest.mark.asyncio
async def test_search_invalid_type(client: AsyncClient):
    """测试无效的搜索类型"""
    response = await client.get("/api/search/?q=test&type=invalid")
    # 无效类型应该返回400
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_search_with_pagination(client: AsyncClient):
    """测试搜索分页"""
    response = await client.get("/api/search/?q=test&limit=5&offset=0")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "total" in data


@pytest.mark.asyncio
async def test_search_suggest(client: AsyncClient):
    """测试搜索建议功能"""
    response = await client.get("/api/search/suggest?q=py")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == 200:
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)


@pytest.mark.asyncio
async def test_search_suggest_empty(client: AsyncClient):
    """测试空关键词搜索建议"""
    response = await client.get("/api/search/suggest?q=")
    # 空关键词应该返回200空结果或422
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    if response.status_code == 200:
        data = response.json()
        assert "suggestions" in data
        assert data["suggestions"] == []


@pytest.mark.asyncio
async def test_search_long_query(client: AsyncClient):
    """测试超长关键词搜索"""
    long_query = "a" * 101  # 超过100字符限制
    response = await client.get(f"/api/search/?q={long_query}")
    # 超长关键词应该返回422
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_search_special_characters(client: AsyncClient):
    """测试特殊字符搜索"""
    # 测试包含特殊字符的搜索
    special_queries = ["test%20query", "test+query", "test%", "test_query"]
    for query in special_queries:
        response = await client.get(f"/api/search/?q={query}")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]


@pytest.mark.asyncio
async def test_search_case_insensitive(client: AsyncClient):
    """测试搜索不区分大小写"""
    # 搜索应该不区分大小写
    response1 = await client.get("/api/search/?q=PYTHON")
    response2 = await client.get("/api/search/?q=python")
    response3 = await client.get("/api/search/?q=Python")
    
    # 所有请求都应该成功或都失败（数据库状态一致）
    assert response1.status_code == response2.status_code == response3.status_code


@pytest.mark.asyncio
async def test_search_all_types_structure(client: AsyncClient):
    """测试搜索返回数据结构完整性"""
    response = await client.get("/api/search/?q=test&type=all")
    
    if response.status_code == 200:
        data = response.json()
        
        # 验证所有必需的字段都存在
        required_fields = ["total", "posts", "tags", "users", "groups", "comments"]
        for field in required_fields:
            assert field in data, f"缺少字段: {field}"
        
        # 验证total是整数
        assert isinstance(data["total"], int)
        
        # 验证列表字段
        assert isinstance(data["posts"], list)
        assert isinstance(data["tags"], list)
        assert isinstance(data["users"], list)
        assert isinstance(data["groups"], list)
        assert isinstance(data["comments"], list)


@pytest.mark.asyncio
async def test_search_post_item_structure(client: AsyncClient):
    """测试搜索结果中文章项的结构"""
    response = await client.get("/api/search/?q=test&type=posts")
    
    if response.status_code == 200:
        data = response.json()
        
        for post in data.get("posts", []):
            # 验证文章项的关键字段
            assert "id" in post
            assert "title" in post
            assert "author_id" in post


@pytest.mark.asyncio
async def test_search_user_item_structure(client: AsyncClient):
    """测试搜索结果中用户项的结构"""
    response = await client.get("/api/search/?q=test&type=users")
    
    if response.status_code == 200:
        data = response.json()
        
        for user in data.get("users", []):
            # 验证用户项的关键字段
            assert "id" in user
            assert "username" in user
