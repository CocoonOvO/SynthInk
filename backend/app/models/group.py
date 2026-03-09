"""
分组模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupBase(BaseModel):
    """分组基础模型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    icon: Optional[str] = None
    sort_order: int = 0


class GroupCreate(GroupBase):
    """分组创建模型"""
    pass


class Group(GroupBase):
    """分组响应模型"""
    id: str
    post_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
