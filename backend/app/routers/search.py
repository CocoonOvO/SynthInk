"""
搜索路由模块
处理全文搜索请求
"""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from ..db_manager import db_manager
from ..models.search import SearchResult, SearchQuery

router = APIRouter()


async def enrich_post_data(post_data: dict) -> dict:
    """
    丰富文章数据，添加作者名、标签、分组名等
    
    Args:
        post_data: 文章原始数据
        
    Returns:
        丰富后的文章数据
    """
    # 获取作者信息
    author_result = await db_manager.db.get("users", post_data["author_id"])
    if author_result.get("success"):
        author_data = author_result["data"]
        post_data["author_name"] = author_data.get("display_name") or author_data.get("username")
        post_data["author_username"] = author_data.get("username")  # 用户名用于跳转
        post_data["author_avatar"] = author_data.get("avatar_url")
        post_data["author_type"] = author_data.get("user_type", "user")
    else:
        post_data["author_name"] = "未知用户"
        post_data["author_username"] = "unknown"
        post_data["author_avatar"] = None
        post_data["author_type"] = "user"
    
    # 获取标签
    tags_result = await db_manager.db.get_post_tags(post_data["id"])
    if tags_result.get("success"):
        post_data["tags"] = [tag["name"] for tag in tags_result["data"]]
    else:
        post_data["tags"] = []
    
    # 获取分组信息
    if post_data.get("group_id"):
        group_result = await db_manager.db.get("groups", post_data["group_id"])
        if group_result.get("success"):
            post_data["group_name"] = group_result["data"].get("name")
        else:
            post_data["group_name"] = None
    else:
        post_data["group_name"] = None

    # 获取点赞数
    try:
        like_count_result = await db_manager.db.count(
            "likes",
            filters={"post_id": post_data["id"]}
        )
        post_data["like_count"] = like_count_result.get("count", 0)
    except Exception:
        post_data["like_count"] = 0
    
    # 确保cover_image字段存在
    if "cover_image" not in post_data:
        post_data["cover_image"] = None
    
    return post_data


@router.get("/", response_model=SearchResult, summary="全文搜索")
async def search(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    type: str = Query("all", description="搜索类型: all/posts/tags/users/groups/comments"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
) -> SearchResult:
    """
    全文搜索接口
    
    支持搜索文章、标签、用户、分组、评论。
    使用PostgreSQL的ILIKE进行模糊匹配，不区分大小写。
    
    **搜索范围**:
    - 文章: 标题、简介、内容（仅已发布）
    - 标签: 名称、描述
    - 用户: 用户名、显示名、简介（仅活跃用户）
    - 分组: 名称、描述
    - 评论: 内容（仅未删除）
    
    **排序规则**:
    - 文章: 标题匹配优先，然后按发布时间倒序
    - 标签: 按文章数量倒序
    - 用户: 按注册时间倒序
    - 分组: 按文章数量倒序
    - 评论: 按时间倒序
    
    **示例**:
    - `/api/search/?q=python` - 搜索所有类型
    - `/api/search/?q=python&type=posts` - 仅搜索文章
    - `/api/search/?q=ai&limit=10&offset=0` - 分页搜索
    """
    # 验证搜索类型
    valid_types = ["all", "posts", "tags", "users", "groups", "comments"]
    if type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的搜索类型，可选: {', '.join(valid_types)}"
        )
    
    # 执行搜索
    result = await db_manager.db.search(
        query=q,
        search_type=type,
        limit=limit,
        offset=offset
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "搜索失败")
        )
    
    data = result.get("data", {})
    
    # 丰富文章数据
    enriched_posts = []
    for post_data in data.get("posts", []):
        try:
            enriched_post = await enrich_post_data(post_data)
            enriched_posts.append(enriched_post)
        except Exception:
            continue
    data["posts"] = enriched_posts
    
    return SearchResult(**data)


@router.get("/suggest", summary="搜索建议")
async def search_suggest(
    q: str = Query(..., min_length=1, max_length=50, description="搜索关键词"),
    limit: int = Query(5, ge=1, le=10, description="建议数量")
) -> dict:
    """
    获取搜索建议

    根据输入的关键词返回相关建议，用于搜索框自动补全。
    返回标签名、文章标题、用户名等。

    **示例**:
    - `/api/search/suggest?q=py` - 返回包含"py"的建议
    """
    result = await db_manager.db.search_suggest(q, limit)

    if not result.get("success"):
        return {"suggestions": [], "error": result.get("error", "获取建议失败")}

    return {"suggestions": result.get("data", {}).get("suggestions", [])}
