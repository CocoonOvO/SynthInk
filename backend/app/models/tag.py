"""
标签模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")  # HEX颜色


class TagCreate(TagBase):
    """标签创建模型"""
    pass


class Tag(TagBase):
    """标签响应模型"""
    id: str
    post_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
