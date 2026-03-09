"""
分组路由模块
处理文章分组的CRUD操作
"""
from datetime import datetime
from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ..db_manager import db_manager
from ..models.group import Group, GroupCreate
from ..models.user import User
from .auth import get_current_active_user, get_current_active_superuser

router = APIRouter()


@router.get("/", response_model=List[Group], summary="获取分组列表")
async def list_groups(
    skip: int = 0,
    limit: int = 100
) -> List[Group]:
    """
    获取所有分组列表
    
    - 按排序顺序返回
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        # 数据库未初始化，返回空列表
        return []
    
    try:
        result = await db_manager.db.find(
            "groups",
            limit=limit,
            offset=skip,
            sort_by="sort_order",
            sort_desc=False
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取分组列表失败"
            )
        
        groups_data = result.get("data", [])
        return [Group(**group_data) for group_data in groups_data]
    except Exception as e:
        # 数据库操作异常，返回空列表
        return []


@router.post("/", response_model=Group, summary="创建分组", status_code=status.HTTP_201_CREATED)
async def create_group(
    group: GroupCreate,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Group:
    """
    创建新分组
    
    - 需要登录
    - 分组名不能重复
    """
    # 检查分组名是否已存在
    existing_result = await db_manager.db.find(
        "groups",
        filters={"name": group.name},
        limit=1
    )
    
    if existing_result.get("data") and len(existing_result["data"]) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分组名已存在"
        )
    
    # 准备分组数据
    group_data = group.model_dump()
    group_data["id"] = str(uuid4())
    group_data["post_count"] = 0
    group_data["created_at"] = datetime.utcnow()
    group_data["updated_at"] = datetime.utcnow()
    
    # 创建分组
    result = await db_manager.db.insert("groups", group_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建分组失败"
        )
    
    return Group(**group_data)


@router.get("/{group_id}", response_model=Group, summary="获取分组详情")
async def get_group(
    group_id: str
) -> Group:
    """
    获取指定分组的详细信息
    """
    result = await db_manager.db.get("groups", group_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分组不存在"
        )
    
    return Group(**result["data"])


@router.put("/{group_id}", response_model=Group, summary="更新分组")
async def update_group(
    group_id: str,
    group_update: GroupCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> Group:
    """
    更新分组信息
    
    - 管理员权限
    """
    # 检查分组是否存在
    existing_result = await db_manager.db.get("groups", group_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分组不存在"
        )
    
    # 如果修改了分组名，检查是否与其他分组冲突
    existing_group = existing_result["data"]
    if group_update.name != existing_group["name"]:
        name_check = await db_manager.db.find(
            "groups",
            filters={"name": group_update.name},
            limit=1
        )
        if name_check.get("data") and len(name_check["data"]) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分组名已存在"
            )
    
    # 准备更新数据
    update_data = group_update.model_dump()
    update_data["updated_at"] = datetime.utcnow()
    
    # 更新分组
    result = await db_manager.db.update("groups", group_id, update_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新分组失败"
        )
    
    # 获取更新后的分组
    updated_result = await db_manager.db.get("groups", group_id)
    return Group(**updated_result["data"])


@router.delete("/{group_id}", summary="删除分组")
async def delete_group(
    group_id: str,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> dict:
    """
    删除指定分组
    
    - 管理员权限
    - 删除后该分组下的文章将变为无分组状态
    """
    # 检查分组是否存在
    existing_result = await db_manager.db.get("groups", group_id)
    if not existing_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分组不存在"
        )
    
    # 将该分组下的文章设为无分组
    posts_result = await db_manager.db.find(
        "posts",
        filters={"group_id": group_id},
        limit=10000
    )
    
    if posts_result.get("success"):
        for post in posts_result["data"]:
            await db_manager.db.update(
                "posts",
                post["id"],
                {"group_id": None, "updated_at": datetime.utcnow()}
            )
    
    # 删除分组
    result = await db_manager.db.delete("groups", group_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除分组失败"
        )
    
    return {"success": True, "message": "分组已删除"}


@router.post("/reorder", summary="重新排序分组")
async def reorder_groups(
    group_orders: dict,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> List[Group]:
    """
    批量更新分组排序
    
    - 管理员权限
    - 接收分组ID和排序值的映射，例如：{"group_id_1": 0, "group_id_2": 1}
    """
    if not group_orders or not isinstance(group_orders, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的排序数据"
        )
    
    # 更新每个分组的排序
    for group_id, sort_order in group_orders.items():
        try:
            await db_manager.db.update(
                "groups",
                group_id,
                {
                    "sort_order": sort_order,
                    "updated_at": datetime.utcnow()
                }
            )
        except Exception:
            # 忽略不存在的分组
            continue
    
    # 返回更新后的分组列表
    result = await db_manager.db.find(
        "groups",
        sort_by="sort_order",
        sort_desc=False
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取更新后的分组列表失败"
        )
    
    groups_data = result.get("data", [])
    return [Group(**group_data) for group_data in groups_data]
