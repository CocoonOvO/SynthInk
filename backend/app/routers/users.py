"""
用户路由模块
处理用户信息的查询和更新
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from ..db_manager import db_manager
from ..models.user import User, UserUpdate
from .auth import get_current_active_user, get_current_active_superuser

router = APIRouter()


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    获取当前登录用户的详细信息
    """
    return current_user


@router.put("/me", response_model=User, summary="更新当前用户信息")
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    更新当前登录用户的信息
    
    - 支持更新：邮箱、显示名称、头像、简介
    - 不支持修改：用户名
    """
    # 准备更新数据
    update_data = user_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供要更新的数据"
        )
    
    # 更新用户信息
    result = await db_manager.postgres.update(
        "users",
        current_user.id,
        update_data
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户信息失败"
        )
    
    # 获取更新后的用户信息
    user_result = await db_manager.postgres.get("users", current_user.id)
    if not user_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取更新后的用户信息失败"
        )
    
    return User(**user_result["data"])


@router.get("/{user_id}", response_model=User, summary="获取指定用户信息")
async def read_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    获取指定用户的公开信息
    
    - 普通用户只能查看基本信息
    - 管理员可以查看更多信息
    """
    # 获取用户信息
    result = await db_manager.postgres.get("users", user_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_data = result["data"]
    
    # 如果不是管理员且不是查看自己，则只返回公开信息
    if not current_user.is_superuser and current_user.id != user_id:
        # 移除敏感字段
        user_data.pop("email", None)
        user_data.pop("is_active", None)
        user_data.pop("is_superuser", None)
    
    return User(**user_data)


@router.get("/", response_model=List[User], summary="获取用户列表")
async def list_users(
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    获取用户列表（管理员权限）
    
    - 支持分页
    - 仅管理员可访问
    """
    result = await db_manager.postgres.find(
        "users",
        limit=limit,
        offset=skip,
        sort_by="created_at",
        sort_desc=True
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )
    
    users_data = result.get("data", [])
    return [User(**user_data) for user_data in users_data]


@router.delete("/{user_id}", summary="删除用户")
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    删除指定用户（管理员权限或用户本人）
    
    - 用户可以删除自己的账号
    - 管理员可以删除任何账号
    """
    # 检查权限：只有管理员或用户本人可以删除
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能删除自己的账号或需要管理员权限"
        )
    
    # 检查用户是否存在
    user_result = await db_manager.postgres.get("users", user_id)
    if not user_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 删除用户
    result = await db_manager.postgres.delete("users", user_id)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )
    
    return {"success": True, "message": "用户已删除"}
