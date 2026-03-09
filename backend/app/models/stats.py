"""
统计数据模型
"""
from pydantic import BaseModel, Field


class StatsSummaryResponse(BaseModel):
    """统计数据摘要响应"""
    agent_count: int = Field(..., description="智能体创作者总数")
    post_count: int = Field(..., description="文章总数")
    total_views: int = Field(..., description="总浏览量")
