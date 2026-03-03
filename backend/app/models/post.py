"""
文章模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    introduction: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = None
    status: str = Field(default="draft")  # draft, published, archived


class PostCreate(PostBase):
    """文章创建模型"""
    tags: List[str] = Field(default_factory=list)
    group_id: Optional[str] = None


class PostUpdate(BaseModel):
    """文章更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    introduction: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    group_id: Optional[str] = None


class Post(PostBase):
    """文章响应模型"""
    id: str
    author_id: str
    author_name: str
    tags: List[str] = Field(default_factory=list)
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PostListItem(BaseModel):
    """文章列表项模型（精简版）"""
    id: str
    title: str
    introduction: Optional[str] = None
    cover_image: Optional[str] = None
    author_name: str
    tags: List[str] = Field(default_factory=list)
    group_name: Optional[str] = None
    view_count: int = 0
    created_at: datetime
    status: str
