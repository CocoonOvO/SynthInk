"""
外链路由模块

管理「工具」页面展示的外部链接：
- GET 列表公开可见
- 增删改仅超管（is_superuser）可操作
"""
from datetime import datetime
from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ..db_manager import db_manager
from ..models.link import ExternalLink, ExternalLinkCreate
from ..models.user import User
from .auth import get_current_active_superuser

router = APIRouter()


@router.get("/", response_model=List[ExternalLink], summary="获取外链列表")
async def list_links(skip: int = 0, limit: int = 100) -> List[ExternalLink]:
    """
    获取所有外链（公开）

    - 按排序权重升序返回
    - 业务库未初始化时返回空列表
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        return []

    try:
        result = await db_manager.db.find(
            "external_links",
            limit=limit,
            offset=skip,
            sort_by="sort_order",
            sort_desc=False
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取外链列表失败"
            )
        return [ExternalLink(**item) for item in result.get("data", [])]
    except HTTPException:
        raise
    except Exception:
        # 数据库异常时返回空列表，保证页面可用
        return []


@router.post("/", response_model=ExternalLink, summary="创建外链", status_code=status.HTTP_201_CREATED)
async def create_link(
    link: ExternalLinkCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> ExternalLink:
    """
    创建新外链（仅超管）

    - URL 必须以 http:// 或 https:// 开头
    """
    link_data = link.model_dump()
    link_data["id"] = str(uuid4())
    link_data["created_at"] = datetime.utcnow()
    link_data["updated_at"] = datetime.utcnow()

    try:
        result = await db_manager.db.insert("external_links", link_data)
    except Exception:
        # 异常统一由全局错误处理器兜底（debug 返回详情、生产只返回通用错误）
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建外链失败"
        )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建外链失败"
        )
    return ExternalLink(**link_data)


@router.put("/{link_id}", response_model=ExternalLink, summary="更新外链")
async def update_link(
    link_id: str,
    link_update: ExternalLinkCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> ExternalLink:
    """
    更新外链信息（仅超管）
    """
    # 检查外链是否存在
    existing_result = await db_manager.db.get("external_links", link_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="外链不存在"
        )

    # 准备更新数据
    update_data = link_update.model_dump()
    update_data["updated_at"] = datetime.utcnow()

    result = await db_manager.db.update("external_links", link_id, update_data)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新外链失败"
        )

    updated_result = await db_manager.db.get("external_links", link_id)
    return ExternalLink(**updated_result["data"])


@router.delete("/{link_id}", summary="删除外链")
async def delete_link(
    link_id: str,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> dict:
    """
    删除指定外链（仅超管）
    """
    # 检查外链是否存在
    existing_result = await db_manager.db.get("external_links", link_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="外链不存在"
        )

    result = await db_manager.db.delete("external_links", link_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除外链失败"
        )

    return {"success": True, "message": "外链已删除"}
