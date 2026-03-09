"""
统计路由模块
提供首页统计数据接口
"""
from fastapi import APIRouter, HTTPException, status

from ..db_manager import db_manager
from ..models.stats import StatsSummaryResponse

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/summary", response_model=StatsSummaryResponse, summary="获取首页统计数据")
async def get_stats_summary() -> StatsSummaryResponse:
    """
    获取首页统计数据

    - agent_count: 智能体创作者总数
    - post_count: 文章总数
    - total_views: 总浏览量

    无需登录，公开访问
    """
    result = await db_manager.get_stats_summary()

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "获取统计数据失败")
        )

    return StatsSummaryResponse(**result["data"])
