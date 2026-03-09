"""
点赞模型
处理文章点赞功能
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LikeBase(BaseModel):
    """点赞基础模型"""
    post_id: str = Field(..., description="文章ID")


class LikeCreate(LikeBase):
    """点赞创建模型"""
    pass


class Like(BaseModel):
    """点赞响应模型"""
    id: str
    post_id: str
    user_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LikeStatus(BaseModel):
    """点赞状态响应"""
    post_id: str
    like_count: int = Field(default=0, description="点赞总数")
    is_liked: bool = Field(default=False, description="当前用户是否已点赞")
    anonymous_token: Optional[str] = Field(default=None, description="匿名用户token（仅首次匿名点赞时返回）")


class PostWithLikeStatus(BaseModel):
    """带点赞状态的文章信息"""
    post_id: str
    like_count: int = 0
    is_liked: bool = False
