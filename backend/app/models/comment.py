"""
评论模型
处理文章评论和回复
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")


class CommentCreate(CommentBase):
    """评论创建模型"""
    post_id: str = Field(..., description="文章ID")
    parent_id: Optional[str] = Field(None, description="父评论ID，用于回复")


class CommentUpdate(BaseModel):
    """评论更新模型"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")


class CommentUserInfo(BaseModel):
    """评论用户信息（精简版）"""
    id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class Comment(CommentBase):
    """评论响应模型"""
    id: str
    post_id: str
    author: CommentUserInfo
    parent_id: Optional[str] = None
    replies: List["Comment"] = Field(default_factory=list, description="子回复列表")
    reply_count: int = Field(default=0, description="直接回复数量")
    total_reply_count: int = Field(default=0, description="总回复数量（包含嵌套）")
    is_deleted: bool = Field(default=False, description="是否已删除")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CommentListItem(BaseModel):
    """评论列表项模型（精简版）"""
    id: str
    post_id: str
    author: CommentUserInfo
    content: str
    parent_id: Optional[str] = None
    reply_count: int = 0
    is_deleted: bool = False
    created_at: datetime


class CommentListResponse(BaseModel):
    """评论列表响应"""
    total: int
    comments: List[Comment]


# 解决循环引用
Comment.model_rebuild()
