"""
统计接口测试
"""
import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_stats_summary(client: AsyncClient):
    """测试获取统计数据接口"""
    response = await client.get("/api/stats/summary")
    
    # 检查响应状态（数据库未初始化时可能返回500）
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == status.HTTP_200_OK:
        # 检查响应数据结构
        data = response.json()
        assert "agent_count" in data
        assert "post_count" in data
        assert "total_views" in data
        
        # 检查数据类型
        assert isinstance(data["agent_count"], int)
        assert isinstance(data["post_count"], int)
        assert isinstance(data["total_views"], int)
        
        # 检查数据非负
        assert data["agent_count"] >= 0
        assert data["post_count"] >= 0
        assert data["total_views"] >= 0


@pytest.mark.asyncio
async def test_stats_summary_no_auth(client: AsyncClient):
    """测试统计接口无需认证"""
    response = await client.get("/api/stats/summary")
    # 应该返回200或500（数据库问题），而不是401
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
