"""
评论路由模块
处理文章评论的CRUD操作和嵌套回复
"""
from datetime import datetime
from typing import Annotated, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db_manager import db_manager
from ..models.comment import (
    Comment, CommentCreate, CommentUpdate,
    CommentUserInfo, CommentListResponse
)
from ..models.user import User
from ..utils.xss_guard import sanitize_html
from .auth import get_current_active_user

router = APIRouter()


async def get_comment_author_info(user_id: str) -> Optional[CommentUserInfo]:
    """
    获取评论作者信息
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户信息，如果不存在则返回None
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        return None
    
    try:
        result = await db_manager.db.get("users", user_id)
        if not result.get("success") or not result.get("data"):
            return None
        
        user_data = result["data"]
        return CommentUserInfo(
            id=user_data["id"],
            username=user_data["username"],
            display_name=user_data.get("display_name"),
            avatar_url=user_data.get("avatar_url")
        )
    except Exception:
        return None


async def build_comment_tree(
    comments: List[dict],
    parent_id: Optional[str] = None,
    max_depth: int = 3,
    current_depth: int = 0
) -> List[Comment]:
    """
    构建评论树结构
    
    Args:
        comments: 原始评论数据列表
        parent_id: 父评论ID
        max_depth: 最大递归深度
        current_depth: 当前深度
    
    Returns:
        嵌套的评论列表
    """
    if current_depth >= max_depth:
        return []
    
    result = []
    for comment_data in comments:
        if comment_data.get("parent_id") == parent_id:
            # 获取作者信息
            author = await get_comment_author_info(comment_data["author_id"])
            if not author:
                continue
            
            # 构建评论对象
            comment = Comment(
                id=comment_data["id"],
                post_id=comment_data["post_id"],
                author=author,
                content=comment_data["content"],
                parent_id=comment_data.get("parent_id"),
                is_deleted=comment_data.get("is_deleted", False),
                created_at=comment_data["created_at"],
                updated_at=comment_data["updated_at"],
                replies=[]
            )
            
            # 递归获取子回复
            if current_depth < max_depth - 1:
                comment.replies = await build_comment_tree(
                    comments, comment.id, max_depth, current_depth + 1
                )
            
            # 计算回复数量
            comment.reply_count = len([
                c for c in comments
                if c.get("parent_id") == comment.id and not c.get("is_deleted", False)
            ])
            
            # 计算总回复数量（递归）
            def count_total_replies(comments_list: List[dict], pid: str) -> int:
                count = 0
                for c in comments_list:
                    if c.get("parent_id") == pid and not c.get("is_deleted", False):
                        count += 1
                        count += count_total_replies(comments_list, c["id"])
                return count
            
            comment.total_reply_count = count_total_replies(comments, comment.id)
            
            result.append(comment)
    
    # 按时间排序
    result.sort(key=lambda x: x.created_at)
    return result


async def count_total_comments(post_id: str) -> int:
    """
    统计文章的总评论数（不包括已删除的）
    
    Args:
        post_id: 文章ID
    
    Returns:
        评论数量
    """
    result = await db_manager.db.find(
        "comments",
        filters={"post_id": post_id, "is_deleted": False}
    )
    if result.get("success"):
        return len(result.get("data", []))
    return 0


@router.post("", response_model=Comment, status_code=status.HTTP_201_CREATED, summary="创建评论")
async def create_comment(
    comment_data: CommentCreate,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Comment:
    """
    创建评论或回复
    
    - 普通评论：不指定parent_id
    - 回复评论：指定parent_id为要回复的评论ID
    - 最多支持3层嵌套回复
    """
    # 检查文章是否存在
    post_result = await db_manager.db.get("posts", comment_data.post_id)
    if not post_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文章不存在"
        )
    
    # 检查文章是否已发布（只有已发布文章可以评论）
    post = post_result["data"]
    if post.get("status") != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能评论已发布的文章"
        )
    
    # 如果指定了parent_id，检查父评论是否存在
    if comment_data.parent_id:
        parent_result = await db_manager.db.get("comments", comment_data.parent_id)
        if not parent_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )
        
        parent = parent_result["data"]
        
        # 检查父评论是否属于同一篇文章
        if parent["post_id"] != comment_data.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能回复同一篇文章下的评论"
            )
        
        # 检查嵌套深度（最多3层）
        depth = 1
        current_parent_id = parent.get("parent_id")
        while current_parent_id:
            depth += 1
            parent_result = await db_manager.db.get("comments", current_parent_id)
            if parent_result.get("success"):
                current_parent_id = parent_result["data"].get("parent_id")
            else:
                break
        
        if depth >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评论嵌套层数超过限制（最多3层）"
            )
    
    # 创建评论
    now = datetime.utcnow()
    comment_dict = {
        "id": str(uuid4()),
        "post_id": comment_data.post_id,
        "author_id": current_user.id,
        "content": sanitize_html(comment_data.content),  # XSS防护：净化HTML内容
        "parent_id": comment_data.parent_id,
        "is_deleted": False,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db_manager.db.insert("comments", comment_dict)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建评论失败"
        )
    
    # 构建响应
    author = await get_comment_author_info(current_user.id)
    return Comment(
        id=comment_dict["id"],
        post_id=comment_dict["post_id"],
        author=author,
        content=comment_dict["content"],
        parent_id=comment_dict["parent_id"],
        is_deleted=False,
        created_at=now,
        updated_at=now,
        replies=[],
        reply_count=0,
        total_reply_count=0
    )


@router.get("/", response_model=CommentListResponse, summary="获取文章评论列表")
async def get_post_comments_by_query(
    post_id: str = Query(..., description="文章ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> CommentListResponse:
    """
    获取文章的评论列表（通过Query参数）
    
    - 返回顶层评论及其嵌套回复
    - 支持分页（仅对顶层评论分页）
    - 最多返回3层嵌套回复
    """
    # 复用现有的获取逻辑
    return await _get_post_comments_impl(post_id, page, page_size)


async def _get_post_comments_impl(
    post_id: str,
    page: int = 1,
    page_size: int = 20
) -> CommentListResponse:
    """
    获取文章评论列表的实现函数
    
    Args:
        post_id: 文章ID
        page: 页码
        page_size: 每页数量
    
    Returns:
        评论列表响应
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        # 数据库未初始化，返回空列表
        return CommentListResponse(total=0, comments=[])
    
    # 检查文章是否存在
    try:
        post_result = await db_manager.db.get("posts", post_id)
        if not post_result.get("success") or not post_result.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文章不存在"
            )
    except HTTPException:
        raise
    except Exception:
        # 数据库异常，返回空列表
        return CommentListResponse(total=0, comments=[])
    
    # 获取所有评论（未删除的）
    try:
        result = await db_manager.db.find(
            "comments",
            filters={"post_id": post_id, "is_deleted": False},
            sort_by="created_at",
            sort_desc=False
        )
        
        if not result.get("success"):
            return CommentListResponse(total=0, comments=[])
        
        all_comments = result.get("data", [])
    except Exception:
        # 数据库异常，返回空列表
        return CommentListResponse(total=0, comments=[])
    
    # 分离顶层评论和回复
    top_level_comments = [c for c in all_comments if c.get("parent_id") is None]
    
    # 分页
    total = len(top_level_comments)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paged_comments = top_level_comments[start_idx:end_idx]
    
    # 构建评论树
    try:
        comment_tree = await build_comment_tree(all_comments, parent_id=None)
        
        # 只保留当前页的顶层评论
        paged_ids = {c["id"] for c in paged_comments}
        filtered_tree = [c for c in comment_tree if c.id in paged_ids]
        
        return CommentListResponse(total=total, comments=filtered_tree)
    except Exception:
        # 构建树异常，返回空列表
        return CommentListResponse(total=0, comments=[])


@router.get("/post/{post_id}", response_model=CommentListResponse, summary="获取文章评论列表")
async def get_post_comments(
    post_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> CommentListResponse:
    """
    获取文章的评论列表（树形结构，路径参数版本）
    
    - 返回顶层评论及其嵌套回复
    - 支持分页（仅对顶层评论分页）
    - 最多返回3层嵌套回复
    """
    return await _get_post_comments_impl(post_id, page, page_size)


@router.get("/{comment_id}", response_model=Comment, summary="获取评论详情")
async def get_comment(comment_id: str) -> Comment:
    """
    获取评论详情（包含所有嵌套回复）
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        # 数据库未初始化，返回404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 获取评论
    try:
        result = await db_manager.db.get("comments", comment_id)
        if not result.get("success") or not result.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        comment_data = result["data"]
    except HTTPException:
        raise
    except Exception:
        # 数据库异常，返回404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    # 如果评论已删除且没有回复，返回404
    if comment_data.get("is_deleted", False):
        # 检查是否有回复
        try:
            replies_result = await db_manager.db.find(
                "comments",
                filters={"parent_id": comment_id, "is_deleted": False}
            )
            if not replies_result.get("success") or not replies_result.get("data"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="评论不存在"
                )
        except HTTPException:
            raise
        except Exception:
            # 数据库异常，返回404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
    
    # 获取作者信息
    author = await get_comment_author_info(comment_data["author_id"])
    if not author:
        # 作者信息获取失败，使用默认信息
        author = CommentUserInfo(
            id=comment_data["author_id"],
            username="未知用户",
            display_name=None,
            avatar_url=None
        )
    
    # 获取所有回复
    all_replies_result = await db_manager.db.find(
        "comments",
        filters={"post_id": comment_data["post_id"], "is_deleted": False}
    )
    
    all_replies = all_replies_result.get("data", []) if all_replies_result.get("success") else []
    
    # 构建评论树
    replies_tree = await build_comment_tree(all_replies, parent_id=comment_id)
    
    # 计算回复数量
    reply_count = len([
        c for c in all_replies
        if c.get("parent_id") == comment_id
    ])
    
    def count_total_replies(comments_list: List[dict], pid: str) -> int:
        count = 0
        for c in comments_list:
            if c.get("parent_id") == pid and not c.get("is_deleted", False):
                count += 1
                count += count_total_replies(comments_list, c["id"])
        return count
    
    total_reply_count = count_total_replies(all_replies, comment_id)
    
    return Comment(
        id=comment_data["id"],
        post_id=comment_data["post_id"],
        author=author,
        content=comment_data["content"] if not comment_data.get("is_deleted", False) else "[评论已删除]",
        parent_id=comment_data.get("parent_id"),
        is_deleted=comment_data.get("is_deleted", False),
        created_at=comment_data["created_at"],
        updated_at=comment_data["updated_at"],
        replies=replies_tree,
        reply_count=reply_count,
        total_reply_count=total_reply_count
    )


@router.put("/{comment_id}", response_model=Comment, summary="更新评论")
async def update_comment(
    comment_id: str,
    update_data: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> Comment:
    """
    更新评论内容
    
    - 只能更新自己的评论
    - 不能更新已删除的评论
    """
    # 获取评论
    result = await db_manager.db.get("comments", comment_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    comment_data = result["data"]
    
    # 检查是否已删除
    if comment_data.get("is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能更新已删除的评论"
        )
    
    # 检查权限
    if comment_data["author_id"] != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能更新自己的评论"
        )
    
    # 更新评论
    update_dict = {
        "content": sanitize_html(update_data.content),  # XSS防护：净化HTML内容
        "updated_at": datetime.utcnow()
    }
    
    result = await db_manager.db.update("comments", comment_id, update_dict)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新评论失败"
        )
    
    # 获取更新后的评论
    return await get_comment(comment_id)


@router.delete("/{comment_id}", summary="删除评论")
async def delete_comment(
    comment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    删除评论（软删除）
    
    - 只能删除自己的评论
    - 管理员可以删除任何评论
    - 软删除：保留评论结构，但内容显示为"[评论已删除]"
    """
    # 获取评论
    result = await db_manager.db.get("comments", comment_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )
    
    comment_data = result["data"]
    
    # 检查是否已删除
    if comment_data.get("is_deleted", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评论已被删除"
        )
    
    # 检查权限
    if comment_data["author_id"] != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能删除自己的评论"
        )
    
    # 软删除
    update_dict = {
        "is_deleted": True,
        "content": "[评论已删除]",
        "updated_at": datetime.utcnow()
    }
    
    result = await db_manager.db.update("comments", comment_id, update_dict)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除评论失败"
        )
    
    return {"success": True, "message": "评论已删除"}


@router.get("/user/{user_id}", response_model=List[Comment], summary="获取用户的评论列表")
async def get_user_comments(
    user_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> List[Comment]:
    """
    获取指定用户的所有评论（不包含嵌套回复）
    """
    # 检查数据库是否已初始化
    try:
        _ = db_manager.db
    except RuntimeError:
        # 数据库未初始化，返回空列表
        return []
    
    # 获取用户的评论
    try:
        result = await db_manager.db.find(
            "comments",
            filters={"author_id": user_id, "is_deleted": False},
            sort_by="created_at",
            sort_desc=True,
            limit=page_size,
            offset=(page - 1) * page_size
        )
        
        if not result.get("success"):
            return []
        
        comments_data = result.get("data", [])
    except Exception:
        # 数据库异常，返回空列表
        return []
    
    # 构建评论列表
    comments = []
    for comment_data in comments_data:
        author = await get_comment_author_info(comment_data["author_id"])
        if not author:
            continue
        
        # 计算回复数量
        try:
            replies_result = await db_manager.db.find(
                "comments",
                filters={"parent_id": comment_data["id"], "is_deleted": False}
            )
            reply_count = len(replies_result.get("data", [])) if replies_result.get("success") else 0
        except Exception:
            reply_count = 0
        
        # 处理parent_id，确保是字符串或None
        parent_id = comment_data.get("parent_id")
        if parent_id is not None:
            parent_id = str(parent_id)
        
        try:
            comments.append(Comment(
                id=comment_data["id"],
                post_id=comment_data["post_id"],
                author=author,
                content=comment_data["content"],
                parent_id=parent_id,
                is_deleted=False,
                created_at=comment_data["created_at"],
                updated_at=comment_data["updated_at"],
                replies=[],
                reply_count=reply_count,
                total_reply_count=reply_count
            ))
        except Exception:
            # 构建评论对象失败，跳过
            continue
    
    return comments
