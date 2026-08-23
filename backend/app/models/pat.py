"""
PAT 凭证模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PATCreate(BaseModel):
    """创建 PAT 请求模型"""
    # 目标用户，可选，默认自身
    user_id: Optional[str] = Field(None, description="目标用户ID，缺省为当前用户")
    name: str = Field(..., min_length=1, max_length=50, description="凭证名称，单用户唯一")
    expires_in_days: int = Field(90, ge=1, le=365, description="有效期天数，默认90")


class PATRenewRequest(BaseModel):
    """续期请求模型"""
    expires_in_days: int = Field(..., ge=1, le=365, description="续期天数")


class PATResponse(BaseModel):
    """PAT 响应模型（脱敏，不含 hash）"""
    id: str = Field(..., description="凭证ID")
    user_id: str = Field(..., description="所属用户ID")
    name: str = Field(..., description="凭证名称")
    expires_at: datetime = Field(..., description="过期时间")
    created_at: datetime = Field(..., description="创建时间")
    created_by: Optional[str] = Field(None, description="创建人ID")
    is_revoked: bool = Field(False, description="是否已撤销")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")

    model_config = {"from_attributes": True}


class PATCreateResponse(PATResponse):
    """创建成功响应，含明文 token（仅返回一次）"""
    token: str = Field(..., description="明文 PAT，stk_ 前缀，仅此一次返回")
