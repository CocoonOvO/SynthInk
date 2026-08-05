"""
外链模型

外链（external link）是「工具」页面展示的外部链接卡片，
包含名称、URL 与配图，由超管维护、公开可见。
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExternalLinkBase(BaseModel):
    """外链基础字段"""
    name: str = Field(..., min_length=1, max_length=100, description="外链名称")
    url: str = Field(..., min_length=1, max_length=500, description="外链URL")
    cover_image: Optional[str] = Field(None, max_length=500, description="配图URL")
    sort_order: int = Field(default=0, description="排序权重（小的在前）")

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        """只允许 http/https 协议，防止 javascript: 等危险链接"""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL必须以 http:// 或 https:// 开头")
        return v


class ExternalLinkCreate(ExternalLinkBase):
    """创建/更新外链的请求体"""
    pass


class ExternalLink(ExternalLinkBase):
    """外链完整信息"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
