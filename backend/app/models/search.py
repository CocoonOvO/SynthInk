"""
搜索模型
定义搜索相关的数据模型
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class SearchPostItem(BaseModel):
    """搜索结果中的文章项"""
    id: str
    title: str
    slug: str = Field(default="", description="文章slug")
    status: str = Field(default="published", description="文章状态")
    introduction: Optional[str] = None
    cover_image: Optional[str] = None
    author_id: str
    author_name: Optional[str] = None
    author_username: Optional[str] = None  # 作者用户名，用于跳转到用户主页
    author_avatar: Optional[str] = None  # 作者头像URL
    author_type: str = Field(default="user", description="作者类型: user/agent")
    tags: List[str] = Field(default_factory=list)
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    view_count: int = 0
    like_count: int = 0  # 点赞数
    created_at: datetime
    published_at: Optional[datetime] = None


class SearchTagItem(BaseModel):
    """搜索结果中的标签项"""
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    post_count: int = 0
    created_at: datetime


class SearchUserItem(BaseModel):
    """搜索结果中的用户项"""
    id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    user_type: Literal["user", "agent"] = "user"
    agent_model: Optional[str] = None
    agent_provider: Optional[str] = None
    created_at: datetime


class SearchGroupItem(BaseModel):
    """搜索结果中的分组项"""
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    post_count: int = 0
    created_at: datetime


class SearchCommentItem(BaseModel):
    """搜索结果中的评论项"""
    id: str
    post_id: str
    content: str
    author_id: str
    author_name: str
    author_display_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: datetime


class SearchResult(BaseModel):
    """搜索结果响应模型"""
    total: int = Field(default=0, description="匹配结果总数")
    posts: List[SearchPostItem] = Field(default_factory=list, description="文章结果")
    tags: List[SearchTagItem] = Field(default_factory=list, description="标签结果")
    users: List[SearchUserItem] = Field(default_factory=list, description="用户结果")
    groups: List[SearchGroupItem] = Field(default_factory=list, description="分组结果")
    comments: List[SearchCommentItem] = Field(default_factory=list, description="评论结果")


class SearchQuery(BaseModel):
    """搜索查询参数模型"""
    q: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    type: Literal["all", "posts", "tags", "users", "groups", "comments"] = Field(
        default="all", description="搜索类型"
    )
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")
    offset: int = Field(default=0, ge=0, description="偏移量")
