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
        """URL 校验：
        - 允许 http:// 或 https:// 绝对链接
        - 允许单个 / 开头的站内相对路径（如 /api/services/xxx/，用于挂载同域服务）
        - 拦截 // 协议相对地址与 javascript: 等危险协议
        """
        v = v.strip()
        if v.startswith("/"):
            if v.startswith("//"):
                raise ValueError("URL不能以 // 开头（协议相对地址），站内路径请用单个 / 开头")
            return v
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL必须以 http:// 或 https:// 开头，或以 / 开头使用站内路径")
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
