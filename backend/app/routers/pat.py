"""
PAT 凭证管理路由
二级权限手工管理，无自动续期
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..db_manager import db_manager
from ..models.pat import PATCreate, PATCreateResponse, PATRenewRequest, PATResponse
from ..models.user import User
from ..utils.security import generate_pat_token, hash_pat_token

from .auth import get_current_active_user

router = APIRouter()


# ---------- 辅助函数 ----------


def _parse_user_result(result) -> Optional[dict]:
    """兼容 Postgres/SQLite 的用户查询结果解析"""
    if not result:
        return None
    if isinstance(result, dict) and "success" in result:
        if not result.get("success"):
            return None
        return result.get("data")
    # SQLite 直接返回 dict
    if isinstance(result, dict) and result.get("id"):
        return result
    return None


def _parse_pat_find_result(result) -> List[dict]:
    """解析 find 返回"""
    if not result:
        return []
    if isinstance(result, dict) and "success" in result:
        if not result.get("success"):
            return []
        return result.get("data") or []
    if isinstance(result, list):
        return result
    return []


def _is_revoked(row: dict) -> bool:
    """判断是否已撤销（兼容 bool/int/str）"""
    v = row.get("revoked")
    if v is True or v == 1 or str(v).lower() == "true":
        return True
    if row.get("is_revoked"):
        return True
    return False


def _parse_datetime(value) -> Optional[datetime]:
    """解析时间字段为 datetime"""
    if not value:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
    return None


def _row_to_response(row: dict) -> PATResponse:
    """将数据库行转为 PATResponse（脱敏）"""
    # 处理 revoked 映射
    is_revoked = _is_revoked(row)
    # 处理 scopes 可能是 JSON 字符串
    # expires_at / created_at / last_used_at 解析
    expires_at = _parse_datetime(row.get("expires_at"))
    created_at = _parse_datetime(row.get("created_at")) or datetime.now(timezone.utc)
    last_used = _parse_datetime(row.get("last_used_at"))
    # 若解析失败，给定默认值避免校验错误
    if expires_at is None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=90)

    return PATResponse(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=row["name"],
        expires_at=expires_at,
        created_at=created_at,
        created_by=str(row["created_by"]) if row.get("created_by") else None,
        is_revoked=is_revoked,
        last_used_at=last_used,
    )


async def _load_user(user_id: str) -> dict:
    """加载目标用户，缺失则抛 404"""
    try:
        result = await db_manager.db.get("users", user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="数据库暂不可用")
    data = _parse_user_result(result)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标用户不存在")
    return data


async def can_manage_pat(current_user: User, target_user_id: str) -> None:
    """
    权限检查：是否允许 current_user 管理 target_user_id 的 PAT

    - 人类超管（is_superuser + user_type=user）可对任意用户操作
    - 超管AI（is_superuser + user_type=agent）仅对普通AI（is_superuser=false 且 user_type=agent）操作，禁止提权为 superuser
    - 普通用户仅对自身操作
    """
    # 加载目标用户
    target_data = await _load_user(target_user_id)
    try:
        target_is_superuser = bool(target_data.get("is_superuser"))
        # SQLite 存储为 0/1
        if target_data.get("is_superuser") == 1:
            target_is_superuser = True
        if target_data.get("is_superuser") == 0:
            target_is_superuser = False
        target_user_type = target_data.get("user_type", "user")
    except Exception:
        target_is_superuser = False
        target_user_type = "user"

    # 人类超管：任意
    if current_user.is_superuser and current_user.user_type == "user":
        return

    # 超管AI：仅普通AI（非超管且为 agent）
    if current_user.is_superuser and current_user.user_type == "agent":
        if target_is_superuser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="超管AI仅可管理普通AI（is_superuser=false）")
        if target_user_type != "agent":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="超管AI仅可管理普通AI（user_type=agent）")
        return

    # 普通用户：仅自身
    if current_user.id != target_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足，仅可管理自身凭证")


async def _get_pat_by_id(pat_id: str) -> dict:
    """按 ID 获取 PAT 记录"""
    try:
        result = await db_manager.db.get("user_api_tokens", pat_id)
    except Exception:
        # 兼容部分适配器对非法 UUID 抛异常
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="凭证不存在")

    data = None
    if isinstance(result, dict) and "success" in result:
        if not result.get("success"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="凭证不存在")
        data = result.get("data")
    else:
        # SQLite 直接返回 dict 或 None
        if isinstance(result, dict) and result.get("id"):
            data = result
        elif isinstance(result, dict) and result.get("success") is False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="凭证不存在")
        else:
            data = result

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="凭证不存在")
    return data


# ---------- 路由 ----------


@router.post("/api-tokens", response_model=PATCreateResponse, status_code=status.HTTP_201_CREATED, summary="创建 PAT")
async def create_pat(
    payload: PATCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PATCreateResponse:
    """创建 PAT，二级权限校验，默认 90 天，明文仅返回一次"""
    target_user_id = payload.user_id or current_user.id

    # 权限检查
    await can_manage_pat(current_user, target_user_id)

    # 检查 name 唯一性（单用户唯一）
    try:
        existing = await db_manager.db.find("user_api_tokens", filters={"user_id": target_user_id, "name": payload.name}, limit=1)
        rows = _parse_pat_find_result(existing)
        if rows:
            # 若存在未撤销的同名凭证则拒绝
            # 即使已撤销也视为占用（遵循 UNIQUE 约束），提示已存在
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="凭证名称已存在（单用户唯一）")
    except HTTPException:
        raise
    except Exception:
        # 查询失败忽略，依赖数据库唯一约束兜底
        pass

    # 生成凭证
    raw_token = generate_pat_token()
    token_hash = hash_pat_token(raw_token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=payload.expires_in_days)

    pat_id = str(uuid4())
    insert_data = {
        "id": pat_id,
        "user_id": target_user_id,
        "name": payload.name,
        "token_hash": token_hash,
        "scopes": None,
        "expires_at": expires_at.isoformat(),
        "created_at": now.isoformat(),
        "created_by": current_user.id,
        "revoked": False,
        "last_used_at": None,
    }
    # SQLite 适配：revoked 用 0/1
    # Postgres 会自动处理 bool

    try:
        # 尝试插入
        # 兼容不同适配器的 insert 返回结构
        result = await db_manager.db.insert("user_api_tokens", insert_data)
        # 获取实际存储行（Postgres 返回 wrapped，SQLite 返回 dict）
        inserted = None
        if isinstance(result, dict) and "success" in result:
            if not result.get("success"):
                # 可能是唯一约束冲突
                detail = result.get("error") or "创建凭证失败"
                if "unique" in str(detail).lower() or "duplicate" in str(detail).lower():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="凭证名称已存在（单用户唯一）")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建凭证失败")
            inserted = result.get("data") or insert_data
            # data 可能缺字段，补全 id
            if not inserted.get("id"):
                inserted = insert_data
        else:
            # SQLite 直接返回行或包装
            if isinstance(result, dict) and result.get("id"):
                inserted = result
            else:
                inserted = insert_data
    except HTTPException:
        raise
    except Exception as e:
        # 唯一约束冲突
        msg = str(e).lower()
        if "unique" in msg or "duplicate" in msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="凭证名称已存在（单用户唯一）")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"创建凭证失败: {e}")

    # 构造响应
    # 用 inserted 补齐时间字段
    resp_base = _row_to_response(inserted)
    # 覆盖为实际插入值确保准确
    resp_base.id = pat_id
    resp_base.user_id = target_user_id
    resp_base.name = payload.name
    resp_base.expires_at = expires_at
    resp_base.created_at = now
    resp_base.created_by = current_user.id
    resp_base.is_revoked = False

    return PATCreateResponse(
        id=resp_base.id,
        user_id=resp_base.user_id,
        name=resp_base.name,
        expires_at=resp_base.expires_at,
        created_at=resp_base.created_at,
        created_by=resp_base.created_by,
        is_revoked=resp_base.is_revoked,
        last_used_at=resp_base.last_used_at,
        token=raw_token,
    )


@router.get("/api-tokens", response_model=List[PATResponse], summary="列出 PAT（脱敏）")
async def list_pats(
    user_id: Optional[str] = Query(None, description="按用户过滤，需相应权限；缺省为自身"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> List[PATResponse]:
    """列出 PAT 列表，脱敏不含 hash，根据权限过滤"""
    target_user_id = user_id or current_user.id

    # 权限检查：若查询他人需通过 can_manage
    if target_user_id != current_user.id:
        await can_manage_pat(current_user, target_user_id)
    # 否则自身无需额外检查

    try:
        result = await db_manager.db.find("user_api_tokens", filters={"user_id": target_user_id}, limit=100, offset=0, sort_by="created_at", sort_desc=True)
    except TypeError:
        # 兼容不支持 sort 参数的适配器
        result = await db_manager.db.find("user_api_tokens", filters={"user_id": target_user_id}, limit=100, offset=0)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"查询凭证失败: {e}")

    rows = _parse_pat_find_result(result)

    # 在 Python 侧过滤 revoked？保留全部但前端可区分；此处不过滤，仅转换
    # 若需要仅返回未撤销，可加过滤：
    # rows = [r for r in rows if not _is_revoked(r)]

    responses = []
    for row in rows:
        try:
            responses.append(_row_to_response(row))
        except Exception:
            continue
    return responses


@router.delete("/api-tokens/{pat_id}", summary="删除/撤销 PAT")
async def delete_pat(
    pat_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> dict:
    """撤销 PAT（软删除 revoked=true）"""
    pat = await _get_pat_by_id(pat_id)
    target_user_id = str(pat.get("user_id"))

    await can_manage_pat(current_user, target_user_id)

    if _is_revoked(pat):
        return {"success": True, "message": "凭证已撤销"}

    # 软删除：更新 revoked 为 true
    try:
        # 兼容 SQLite 0/1 与 Postgres bool
        await db_manager.db.update("user_api_tokens", pat_id, {"revoked": True})
    except Exception as e:
        # 尝试硬删除兜底
        try:
            await db_manager.db.delete("user_api_tokens", pat_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"撤销凭证失败: {e}")
        return {"success": True, "message": "凭证已删除"}

    return {"success": True, "message": "凭证已撤销"}


@router.post("/api-tokens/{pat_id}/renew", response_model=PATResponse, summary="续期 PAT")
async def renew_pat(
    pat_id: str,
    payload: PATRenewRequest,
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> PATResponse:
    """续期 PAT：更新 expires_at = now + expires_in_days"""
    pat = await _get_pat_by_id(pat_id)
    target_user_id = str(pat.get("user_id"))

    await can_manage_pat(current_user, target_user_id)

    if _is_revoked(pat):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已撤销的凭证不可续期")

    now = datetime.now(timezone.utc)
    new_expires = now + timedelta(days=payload.expires_in_days)

    try:
        update_result = await db_manager.db.update("user_api_tokens", pat_id, {"expires_at": new_expires.isoformat()})
        # 获取更新后行
        updated = None
        if isinstance(update_result, dict) and "success" in update_result:
            # Postgres update 返回 {success, id}，需重新 get
            updated = await _get_pat_by_id(pat_id)
        else:
            # SQLite 返回行
            if isinstance(update_result, dict) and update_result.get("id"):
                updated = update_result
            else:
                updated = await _get_pat_by_id(pat_id)
        return _row_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"续期失败: {e}")
