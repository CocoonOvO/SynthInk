"""
文章模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PostBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    introduction: Optional[str] = Field(None, max_length=500)
    cover_image: Optional[str] = None
    status: str = Field(default="draft")  # draft, published, archived
    slug: Optional[str] = Field(None, max_length=100, description="URL友好标识，如 python-tutorial")


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
    slug: Optional[str] = Field(None, max_length=100, description="URL友好标识")
    tags: Optional[List[str]] = None
    group_id: Optional[str] = None


class Post(PostBase):
    """文章响应模型"""
    id: str
    author_id: str
    author_name: str
    author_username: str  # 作者用户名，用于跳转到用户主页
    author_avatar: Optional[str] = None  # 作者头像URL
    author_type: str = Field(default="user", description="作者类型: user/agent")
    tags: List[str] = Field(default_factory=list)
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_db_record(cls, record: dict) -> "Post":
        """从数据库记录创建Post对象，确保slug字段被正确处理"""
        data = dict(record)
        # 确保slug字段存在
        if 'slug' not in data:
            data['slug'] = None
        # 确保author_type字段存在
        if 'author_type' not in data:
            data['author_type'] = 'user'
        return cls(**data)


class PostListItem(BaseModel):
    """文章列表项模型（精简版）"""
    id: str
    title: str
    slug: Optional[str] = None
    introduction: Optional[str] = None
    cover_image: Optional[str] = None
    author_name: str
    author_username: str  # 作者用户名，用于跳转到用户主页
    author_avatar: Optional[str] = None  # 作者头像URL
    author_type: str = Field(default="user", description="作者类型: user/agent")
    tags: List[str] = Field(default_factory=list)
    group_name: Optional[str] = None
    view_count: int = 0
    like_count: int = 0  # 点赞数
    created_at: datetime
    status: str


class PostListResponse(BaseModel):
    """文章列表响应模型"""
    items: List[PostListItem]
    total: int
