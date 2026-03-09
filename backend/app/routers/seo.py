"""
SEO管理路由

提供SEO元数据和重定向规则的CRUD接口
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from ..seo.models import SEOMetadata, SEORedirect
from ..seo.factory import SEO_TABLE_METADATA, SEO_TABLE_REDIRECTS, get_seo_adapter
from ..db_manager import db_manager
from .auth import get_current_user


async def get_resource_slug(resource_type: str, resource_id: str) -> Optional[str]:
    """
    从业务数据库获取资源的slug
    
    Args:
        resource_type: 资源类型 (post, tag, group)
        resource_id: 资源ID
        
    Returns:
        slug字符串，如果不存在返回None
    """
    try:
        table_map = {
            "post": "posts",
            "tag": "tags",
            "group": "groups"
        }
        table = table_map.get(resource_type)
        if not table:
            return None
        
        result = await db_manager.db.get(table, resource_id)
        if result.get("success") and result.get("data"):
            return result["data"].get("slug")
        return None
    except Exception:
        return None


router = APIRouter(prefix="/seo", tags=["SEO管理"])


# ========== 请求/响应模型 ==========

class SEOMetadataCreate(BaseModel):
    """创建SEO元数据请求"""
    resource_id: str = Field(..., description="关联的业务资源ID")
    resource_type: str = Field(..., description="资源类型: post, tag, group")
    slug: Optional[str] = Field(None, description="URL标识，不指定则使用业务数据库中的slug", min_length=1, max_length=200)
    meta_title: Optional[str] = Field(None, description="SEO标题", max_length=100)
    meta_description: Optional[str] = Field(None, description="SEO描述", max_length=300)
    meta_keywords: Optional[str] = Field(None, description="关键词", max_length=500)
    canonical_url: Optional[str] = Field(None, description="规范URL", max_length=500)
    og_title: Optional[str] = Field(None, description="OG标题", max_length=100)
    og_description: Optional[str] = Field(None, description="OG描述", max_length=300)
    og_image: Optional[str] = Field(None, description="OG图片URL", max_length=500)


class SEOMetadataUpdate(BaseModel):
    """更新SEO元数据请求"""
    meta_title: Optional[str] = Field(None, description="SEO标题", max_length=100)
    meta_description: Optional[str] = Field(None, description="SEO描述", max_length=300)
    meta_keywords: Optional[str] = Field(None, description="关键词", max_length=500)
    canonical_url: Optional[str] = Field(None, description="规范URL", max_length=500)
    og_title: Optional[str] = Field(None, description="OG标题", max_length=100)
    og_description: Optional[str] = Field(None, description="OG描述", max_length=300)
    og_image: Optional[str] = Field(None, description="OG图片URL", max_length=500)


class SEORedirectCreate(BaseModel):
    """创建重定向规则请求"""
    old_slug: str = Field(..., description="旧URL标识", min_length=1, max_length=200)
    new_slug: str = Field(..., description="新URL标识", min_length=1, max_length=200)
    redirect_type: int = Field(default=301, description="301永久/302临时重定向")


class SEORedirectUpdate(BaseModel):
    """更新重定向规则请求"""
    new_slug: Optional[str] = Field(None, description="新URL标识", max_length=200)
    redirect_type: Optional[int] = Field(None, description="301永久/302临时重定向")


class SEOListResponse(BaseModel):
    """SEO数据列表响应"""
    total: int = Field(..., description="总数")
    items: List[dict] = Field(..., description="数据列表")


# ========== 依赖注入 ==========

async def get_seo_db():
    """
    获取SEO数据库访问接口

    返回 db_manager.seo_db 包装器，自动处理seo schema前缀。
    这是推荐的访问方式，避免创建独立的数据库连接。
    """
    return db_manager.seo_db


# ========== SEO元数据接口 ==========

@router.post("/metadata", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_seo_metadata(
    data: SEOMetadataCreate,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    创建SEO元数据
    
    需要认证。如果未指定slug，会自动从业务数据库获取。
    """
    # 准备数据
    metadata_dict = data.model_dump()
    
    # 如果未提供slug，从业务数据库获取
    if not metadata_dict.get("slug"):
        resource_slug = await get_resource_slug(data.resource_type, data.resource_id)
        if not resource_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"资源 {data.resource_type}/{data.resource_id} 不存在或未设置slug"
            )
        metadata_dict["slug"] = resource_slug
    
    # 检查slug是否已存在
    existing = await adapter.find(
        table=SEO_TABLE_METADATA,
        filters={"slug": metadata_dict["slug"]},
        limit=1
    )
    if existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{metadata_dict['slug']}' 已存在"
        )
    
    # 创建数据
    metadata_dict["created_at"] = datetime.utcnow().isoformat()
    metadata_dict["updated_at"] = datetime.utcnow().isoformat()
    
    result = await adapter.insert(table=SEO_TABLE_METADATA, data=metadata_dict)
    
    return {
        "id": result.get("id"),
        "message": "SEO元数据创建成功",
        "slug": metadata_dict["slug"]
    }


@router.get("/metadata", response_model=SEOListResponse)
async def list_seo_metadata(
    resource_type: Optional[str] = Query(None, description="资源类型过滤"),
    search: Optional[str] = Query(None, description="搜索slug或标题"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    adapter=Depends(get_seo_db)
):
    """
    获取SEO元数据列表
    
    支持分页和过滤
    """
    filters = {}
    if resource_type:
        filters["resource_type"] = resource_type
    
    # 查询数据
    offset = (page - 1) * page_size
    result = await adapter.find(
        table=SEO_TABLE_METADATA,
        filters=filters,
        limit=page_size,
        offset=offset
    )
    
    # 获取总数
    count_result = await adapter.count(table=SEO_TABLE_METADATA, filters=filters)
    total = count_result.get("count", 0)
    
    # 搜索过滤（内存中过滤）
    items = result.get("data", [])
    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item.get("slug", "").lower()
            or search_lower in (item.get("meta_title") or "").lower()
        ]
    
    return {
        "total": total,
        "items": items
    }


@router.get("/metadata/{slug}", response_model=dict)
async def get_seo_metadata(
    slug: str,
    adapter=Depends(get_seo_db)
):
    """
    获取指定slug的SEO元数据
    """
    result = await adapter.find(
        table=SEO_TABLE_METADATA,
        filters={"slug": slug},
        limit=1
    )
    
    if not result.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slug '{slug}' 的SEO元数据不存在"
        )
    
    return result["data"][0]


@router.put("/metadata/{slug}", response_model=dict)
async def update_seo_metadata(
    slug: str,
    data: SEOMetadataUpdate,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    更新SEO元数据
    
    需要认证
    """
    # 查找现有数据
    existing = await adapter.find(
        table=SEO_TABLE_METADATA,
        filters={"slug": slug},
        limit=1
    )
    
    if not existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slug '{slug}' 的SEO元数据不存在"
        )
    
    # 更新数据
    update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow().isoformat()
    
    record_id = existing["data"][0]["id"]
    await adapter.update(
        table=SEO_TABLE_METADATA,
        id=record_id,
        data=update_dict
    )
    
    return {
        "message": "SEO元数据更新成功"
    }


@router.delete("/metadata/{slug}", response_model=dict)
async def delete_seo_metadata(
    slug: str,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    删除SEO元数据
    
    需要认证
    """
    # 查找现有数据
    existing = await adapter.find(
        table=SEO_TABLE_METADATA,
        filters={"slug": slug},
        limit=1
    )
    
    if not existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slug '{slug}' 的SEO元数据不存在"
        )
    
    # 删除数据
    record_id = existing["data"][0]["id"]
    await adapter.delete(table=SEO_TABLE_METADATA, id=record_id)
    
    return {
        "message": "SEO元数据删除成功"
    }


# ========== 重定向规则接口 ==========

@router.post("/redirects", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_redirect(
    data: SEORedirectCreate,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    创建URL重定向规则
    
    需要认证
    """
    # 检查old_slug是否已存在
    existing = await adapter.find(
        table=SEO_TABLE_REDIRECTS,
        filters={"old_slug": data.old_slug},
        limit=1
    )
    if existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"旧slug '{data.old_slug}' 的重定向规则已存在"
        )
    
    # 创建数据
    redirect_dict = data.model_dump()
    redirect_dict["hit_count"] = 0
    redirect_dict["created_at"] = datetime.utcnow().isoformat()
    
    result = await adapter.insert(table=SEO_TABLE_REDIRECTS, data=redirect_dict)
    
    return {
        "id": result.get("id"),
        "message": "重定向规则创建成功"
    }


@router.get("/redirects", response_model=SEOListResponse)
async def list_redirects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    adapter=Depends(get_seo_db)
):
    """
    获取重定向规则列表
    
    支持分页
    """
    offset = (page - 1) * page_size
    result = await adapter.find(
        table=SEO_TABLE_REDIRECTS,
        limit=page_size,
        offset=offset
    )
    
    # 获取总数
    count_result = await adapter.count(table=SEO_TABLE_REDIRECTS)
    total = count_result.get("count", 0)
    
    return {
        "total": total,
        "items": result.get("data", [])
    }


@router.get("/redirects/{old_slug}", response_model=dict)
async def get_redirect(
    old_slug: str,
    adapter=Depends(get_seo_db)
):
    """
    获取指定旧slug的重定向规则
    """
    result = await adapter.find(
        table=SEO_TABLE_REDIRECTS,
        filters={"old_slug": old_slug},
        limit=1
    )
    
    if not result.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"旧slug '{old_slug}' 的重定向规则不存在"
        )
    
    return result["data"][0]


@router.put("/redirects/{old_slug}", response_model=dict)
async def update_redirect(
    old_slug: str,
    data: SEORedirectUpdate,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    更新重定向规则
    
    需要认证
    """
    # 查找现有数据
    existing = await adapter.find(
        table=SEO_TABLE_REDIRECTS,
        filters={"old_slug": old_slug},
        limit=1
    )
    
    if not existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"旧slug '{old_slug}' 的重定向规则不存在"
        )
    
    # 更新数据
    update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
    
    record_id = existing["data"][0]["id"]
    await adapter.update(
        table=SEO_TABLE_REDIRECTS,
        id=record_id,
        data=update_dict
    )
    
    return {
        "message": "重定向规则更新成功"
    }


@router.delete("/redirects/{old_slug}", response_model=dict)
async def delete_redirect(
    old_slug: str,
    adapter=Depends(get_seo_db),
    current_user=Depends(get_current_user)
):
    """
    删除重定向规则
    
    需要认证
    """
    # 查找现有数据
    existing = await adapter.find(
        table=SEO_TABLE_REDIRECTS,
        filters={"old_slug": old_slug},
        limit=1
    )
    
    if not existing.get("data"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"旧slug '{old_slug}' 的重定向规则不存在"
        )
    
    # 删除数据
    record_id = existing["data"][0]["id"]
    await adapter.delete(table=SEO_TABLE_REDIRECTS, id=record_id)
    
    return {
        "message": "重定向规则删除成功"
    }


# ========== 统计接口 ==========

@router.get("/stats", response_model=dict)
async def get_seo_stats(
    adapter=Depends(get_seo_db)
):
    """
    获取SEO统计信息
    """
    metadata_count = await adapter.count(table=SEO_TABLE_METADATA)
    redirects_count = await adapter.count(table=SEO_TABLE_REDIRECTS)
    
    return {
        "metadata_count": metadata_count.get("count", 0),
        "redirects_count": redirects_count.get("count", 0)
    }
