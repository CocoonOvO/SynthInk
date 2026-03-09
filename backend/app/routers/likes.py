"""
点赞路由
处理文章点赞相关接口
支持登录用户和匿名用户点赞
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header, Request
from datetime import datetime, timedelta
import secrets
import hashlib

from app.models import Like, LikeCreate, LikeStatus, PostWithLikeStatus
from app.routers.auth import get_current_user, get_current_user_optional
from app.db_manager import db_manager

router = APIRouter(tags=["点赞"])

# 匿名点赞限制配置
ANONYMOUS_DAILY_LIMIT = 20  # 匿名用户每日点赞上限
IP_DAILY_LIMIT = 50  # 每IP每日点赞上限


def generate_anonymous_token() -> str:
    """生成匿名用户token"""
    return secrets.token_urlsafe(32)


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 尝试从X-Forwarded-For获取（代理环境）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # 从X-Real-IP获取
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 直接从连接获取
    if request.client:
        return request.client.host
    
    return "unknown"


async def check_anonymous_rate_limit(ip_address: str) -> tuple[bool, str]:
    """
    检查匿名用户点赞频率限制
    
    Returns:
        (是否允许, 错误信息)
    """
    result = await db_manager.db.check_ip_like_limit(ip_address, IP_DAILY_LIMIT)
    
    if not result.get("success"):
        # 数据库错误时允许操作（降级处理）
        return True, ""
    
    return result.get("allowed", True), result.get("message", "")


async def increment_post_like_count(post_id: str) -> bool:
    """原子增加文章点赞数"""
    result = await db_manager.db.increment_like_count(post_id)
    return result.get("success", False)


async def decrement_post_like_count(post_id: str) -> bool:
    """原子减少文章点赞数"""
    result = await db_manager.db.decrement_like_count(post_id)
    return result.get("success", False)


async def get_post_like_count(post_id: str) -> int:
    """从缓存字段获取点赞数"""
    result = await db_manager.db.get("posts", post_id)
    if result.get("success") and result.get("data"):
        return result["data"].get("like_count", 0)
    return 0


@router.post("/{post_id}", response_model=LikeStatus, status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: str,
    request: Request,
    x_anonymous_token: Optional[str] = Header(None, alias="X-Anonymous-Token", description="匿名用户token，首次点赞可不传"),
    current_user = Depends(get_current_user_optional)
):
    """
    点赞文章
    
    - **post_id**: 文章ID
    - 支持登录用户和匿名用户
    - 匿名用户需要传递 anonymous_token（首次可不传，会返回新的token）
    - 重复点赞会返回已点赞状态
    """
    ip_address = get_client_ip(request)
    
    # 检查文章是否存在
    post_result = await db_manager.db.get("posts", post_id)
    if not post_result.get("success") or not post_result.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    if current_user:
        # ========== 登录用户点赞 ==========
        user_id = str(current_user.id)
        
        # 检查是否已点赞
        existing_like = await db_manager.db.find(
            "likes",
            filters={"post_id": post_id, "user_id": user_id},
            limit=1
        )
        
        if existing_like.get("success") and len(existing_like.get("data", [])) > 0:
            # 已点赞，返回当前状态
            like_count = await get_post_like_count(post_id)
            return LikeStatus(
                post_id=post_id,
                like_count=like_count,
                is_liked=True
            )
        
        # 创建点赞记录
        like_data = {
            "post_id": post_id,
            "user_id": user_id,
            "like_type": "user",
            "created_at": datetime.utcnow()
        }
        
        result = await db_manager.db.insert("likes", like_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="点赞失败"
            )
        
        # 原子增加点赞数
        await increment_post_like_count(post_id)
        like_count = await get_post_like_count(post_id)
        
        return LikeStatus(
            post_id=post_id,
            like_count=like_count,
            is_liked=True
        )
    
    else:
        # ========== 匿名用户点赞 ==========
        # 检查频率限制
        allowed, error_msg = await check_anonymous_rate_limit(ip_address)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_msg
            )
        
        # 生成或验证token
        token = x_anonymous_token
        if not token:
            token = generate_anonymous_token()
            is_new_token = True
        else:
            is_new_token = False
        
        # 检查是否已点赞
        existing_like = await db_manager.db.find(
            "likes",
            filters={"post_id": post_id, "anonymous_token": token},
            limit=1
        )
        
        if existing_like.get("success") and len(existing_like.get("data", [])) > 0:
            # 已点赞，返回当前状态
            like_count = await get_post_like_count(post_id)
            return LikeStatus(
                post_id=post_id,
                like_count=like_count,
                is_liked=True,
                anonymous_token=token if is_new_token else None
            )
        
        # 创建点赞记录
        like_data = {
            "post_id": post_id,
            "anonymous_token": token,
            "like_type": "anonymous",
            "ip_address": ip_address,
            "created_at": datetime.utcnow()
        }
        
        result = await db_manager.db.insert("likes", like_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="点赞失败"
            )
        
        # 原子增加点赞数
        await increment_post_like_count(post_id)
        like_count = await get_post_like_count(post_id)
        
        return LikeStatus(
            post_id=post_id,
            like_count=like_count,
            is_liked=True,
            anonymous_token=token if is_new_token else None
        )


@router.delete("/{post_id}", response_model=LikeStatus)
async def unlike_post(
    post_id: str,
    x_anonymous_token: Optional[str] = Header(None, alias="X-Anonymous-Token", description="匿名用户token"),
    current_user = Depends(get_current_user_optional)
):
    """
    取消点赞
    
    - **post_id**: 文章ID
    - 登录用户无需传递 anonymous_token
    - 匿名用户必须传递 anonymous_token
    """
    if current_user:
        # ========== 登录用户取消点赞 ==========
        user_id = str(current_user.id)
        
        # 先找到点赞记录的ID
        existing_like = await db_manager.db.find(
            "likes",
            filters={"post_id": post_id, "user_id": user_id},
            limit=1
        )
        
        # 如果存在点赞记录，则删除
        if existing_like.get("success") and len(existing_like.get("data", [])) > 0:
            like_id = existing_like["data"][0]["id"]
            await db_manager.db.delete("likes", like_id)
            # 原子减少点赞数
            await decrement_post_like_count(post_id)
    
    else:
        # ========== 匿名用户取消点赞 ==========
        if not x_anonymous_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="匿名用户需要提供 X-Anonymous-Token"
            )
        
        # 找到点赞记录
        existing_like = await db_manager.db.find(
            "likes",
            filters={"post_id": post_id, "anonymous_token": x_anonymous_token},
            limit=1
        )
        
        # 如果存在点赞记录，则删除
        if existing_like.get("success") and len(existing_like.get("data", [])) > 0:
            like_id = existing_like["data"][0]["id"]
            await db_manager.db.delete("likes", like_id)
            # 原子减少点赞数
            await decrement_post_like_count(post_id)
    
    # 获取最新点赞数
    like_count = await get_post_like_count(post_id)
    
    return LikeStatus(
        post_id=post_id,
        like_count=like_count,
        is_liked=False
    )


@router.get("/{post_id}/status", response_model=LikeStatus)
async def get_like_status(
    post_id: str,
    x_anonymous_token: Optional[str] = Header(None, alias="X-Anonymous-Token", description="匿名用户token"),
    current_user = Depends(get_current_user_optional)
):
    """
    获取文章点赞状态
    
    - **post_id**: 文章ID
    - 登录用户无需传递 anonymous_token
    - 匿名用户传递 anonymous_token 可查询自己是否点赞
    - 文章不存在时返回 like_count=0, is_liked=false（而非404）
    """
    # 获取点赞数（使用缓存字段）
    like_count = await get_post_like_count(post_id)
    
    # 检查当前用户是否已点赞
    is_liked = False
    
    if current_user:
        # 登录用户检查
        user_id = str(current_user.id)
        try:
            existing_like = await db_manager.db.find(
                "likes",
                filters={"post_id": post_id, "user_id": user_id},
                limit=1
            )
            is_liked = existing_like.get("success") and len(existing_like.get("data", [])) > 0
        except Exception:
            is_liked = False
    
    elif x_anonymous_token:
        # 匿名用户检查
        try:
            existing_like = await db_manager.db.find(
                "likes",
                filters={"post_id": post_id, "anonymous_token": x_anonymous_token},
                limit=1
            )
            is_liked = existing_like.get("success") and len(existing_like.get("data", [])) > 0
        except Exception:
            is_liked = False
    
    return LikeStatus(
        post_id=post_id,
        like_count=like_count,
        is_liked=is_liked
    )


@router.get("/user/me", response_model=List[PostWithLikeStatus])
async def get_my_liked_posts(
    current_user = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取当前用户点赞的文章列表
    
    - 需要登录
    - 返回文章ID和点赞状态列表
    """
    user_id = str(current_user.id)
    
    # 获取用户点赞记录
    result = await db_manager.db.find(
        "likes",
        filters={"user_id": user_id},
        sort_by="created_at",
        sort_desc=True,
        limit=page_size,
        offset=(page - 1) * page_size
    )
    
    if not result.get("success"):
        return []
    
    likes_data = result.get("data", [])
    
    # 构建响应列表
    liked_posts = []
    for like_data in likes_data:
        post_id = like_data["post_id"]
        
        # 从缓存字段获取点赞数
        like_count = await get_post_like_count(post_id)
        
        liked_posts.append(PostWithLikeStatus(
            post_id=post_id,
            like_count=like_count,
            is_liked=True
        ))
    
    return liked_posts


@router.get("/post/{post_id}/users", response_model=List[dict])
async def get_post_likers(
    post_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取点赞用户列表
    
    - **post_id**: 文章ID
    - 无需登录
    - 只返回登录用户的基本信息（匿名用户不显示）
    """
    # 检查文章是否存在
    try:
        post_result = await db_manager.db.get("posts", post_id)
        if not post_result.get("success") or not post_result.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 获取点赞记录（只取登录用户）
    result = await db_manager.db.find(
        "likes",
        filters={"post_id": post_id, "like_type": "user"},
        sort_by="created_at",
        sort_desc=True,
        limit=page_size,
        offset=(page - 1) * page_size
    )
    
    if not result.get("success"):
        return []
    
    likes_data = result.get("data", [])
    
    # 获取用户信息
    likers = []
    for like_data in likes_data:
        user_id = like_data.get("user_id")
        if not user_id:
            continue
            
        user_result = await db_manager.db.get("users", user_id)
        
        if user_result.get("success") and user_result.get("data"):
            user_data = user_result["data"]
            likers.append({
                "id": user_id,
                "username": user_data.get("username"),
                "display_name": user_data.get("display_name"),
                "avatar_url": user_data.get("avatar_url"),
                "liked_at": like_data["created_at"]
            })
    
    return likers
