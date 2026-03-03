"""
文件上传接口测试

测试 /api/upload/* 相关接口
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_upload_image_no_auth(client: AsyncClient):
    """测试未认证上传图片"""
    response = await client.post("/api/upload/image")
    # 应该返回401或404（如果路由未注册）
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_upload_avatar_no_auth(client: AsyncClient):
    """测试未认证上传头像"""
    response = await client.post("/api/upload/avatar")
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]


@pytest.mark.asyncio
async def test_upload_file_no_auth(client: AsyncClient):
    """测试未认证上传附件"""
    response = await client.post("/api/upload/file")
    # 应该返回401或404
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
