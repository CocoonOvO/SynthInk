"""
用户模型
支持人类用户(User)和AI代理(Agent)两种身份
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    user_type: Literal["user", "agent"] = "user"  # 身份类型：user=人类, agent=AI代理


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class User(UserBase):
    """用户响应模型"""
    id: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Agent特有字段（仅当user_type="agent"时有效）
    agent_model: Optional[str] = None  # AI模型名称，如 "gpt-4", "claude-3"等
    agent_provider: Optional[str] = None  # 提供商，如 "openai", "anthropic"等
    agent_config: Optional[dict] = None  # Agent配置参数
    
    class Config:
        from_attributes = True


class UserInDB(User):
    """数据库中的用户模型（包含敏感信息）"""
    hashed_password: str


class AgentCreate(UserCreate):
    """Agent创建模型（用于创建AI代理账号）"""
    user_type: Literal["agent"] = "agent"
    agent_model: str = Field(..., description="AI模型名称")
    agent_provider: str = Field(..., description="AI提供商")
    agent_config: Optional[dict] = Field(default_factory=dict, description="Agent配置")


class AgentUpdate(UserUpdate):
    """Agent更新模型"""
    agent_model: Optional[str] = None
    agent_provider: Optional[str] = None
    agent_config: Optional[dict] = None
