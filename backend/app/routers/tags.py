"""
标签路由模块
处理标签的CRUD操作
"""
from datetime import datetime
from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ..db_manager import db_manager
from ..models.tag import Tag, TagCreate
from ..models.user import User
from .auth import get_current_active_user, get_current_active_superuser

router = APIRouter()


@router.get("/", response_model=List[Tag], summary="获取标签列表")
async def list_tags(
    skip: int = 0,
    limit: int = 100
) -> List[Tag]:
    """
    获取所有标签列表
    
    - 按使用数量排序
    """
    result = await db_manager.postgres.find(
        "tags",
        limit=limit,
        offset=skip,
        sort_by="post_count",
        sort_desc=True
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取标签列表失败"
        )
    
    tags_data = result.get("data", [])
    return [Tag(**tag_data) for tag_data in tags_data]


@router.post("/", response_model=Tag, summary="创建标签", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> Tag:
    """
    创建新标签
    
    - 管理员权限
    - 标签名不能重复
    """
    # 检查标签名是否已存在
    existing_result = await db_manager.postgres.find(
        "tags",
        filters={"name": tag.name},
        limit=1
    )
    
    if existing_result.get("data") and len(existing_result["data"]) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="标签名已存在"
        )
    
    # 准备标签数据
    tag_data = tag.model_dump()
    tag_data["id"] = str(uuid4())
    tag_data["post_count"] = 0
    tag_data["created_at"] = datetime.utcnow()
    
    # 创建标签
    result = await db_manager.postgres.insert("tags", tag_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建标签失败"
        )
    
    return Tag(**tag_data)


@router.get("/{tag_id}", response_model=Tag, summary="获取标签详情")
async def get_tag(
    tag_id: str
) -> Tag:
    """
    获取指定标签的详细信息
    """
    result = await db_manager.postgres.get("tags", tag_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    return Tag(**result["data"])


@router.put("/{tag_id}", response_model=Tag, summary="更新标签")
async def update_tag(
    tag_id: str,
    tag_update: TagCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> Tag:
    """
    更新标签信息
    
    - 管理员权限
    """
    # 检查标签是否存在
    existing_result = await db_manager.postgres.get("tags", tag_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 如果修改了标签名，检查是否与其他标签冲突
    existing_tag = existing_result["data"]
    if tag_update.name != existing_tag["name"]:
        name_check = await db_manager.postgres.find(
            "tags",
            filters={"name": tag_update.name},
            limit=1
        )
        if name_check.get("data") and len(name_check["data"]) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名已存在"
            )
    
    # 准备更新数据
    update_data = tag_update.model_dump()
    
    # 更新标签
    result = await db_manager.postgres.update("tags", tag_id, update_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新标签失败"
        )
    
    # 获取更新后的标签
    updated_result = await db_manager.postgres.get("tags", tag_id)
    return Tag(**updated_result["data"])


@router.delete("/{tag_id}", summary="删除标签")
async def delete_tag(
    tag_id: str,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> dict:
    """
    删除指定标签
    
    - 管理员权限
    - 删除后相关文章的标签关联也会被移除
    """
    # 检查标签是否存在
    existing_result = await db_manager.postgres.get("tags", tag_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 删除标签（关联的文章标签关联会自动删除）
    result = await db_manager.postgres.delete("tags", tag_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除标签失败"
        )
    
    return {"success": True, "message": "标签已删除"}
