"""
认证路由模块
处理用户登录、注册、Token刷新等
"""
import json
from datetime import timedelta
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import get_settings
from ..db_manager import db_manager
from ..models.user import User, UserCreate, UserInDB, AgentCreate
from ..utils.security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 可选的OAuth2 scheme（用于公开接口，不强制要求认证）
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    auto_error=False  # 不自动抛出401错误
)

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

# 获取限流配置
settings = get_settings()


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    """
    根据用户名获取用户
    
    Args:
        username: 用户名
    
    Returns:
        用户对象，如果不存在则返回None
    """
    try:
        result = await db_manager.db.get_user_by_username(username)
        if result.get("success") and result.get("data"):
            return UserInDB(**result["data"])
        return None
    except RuntimeError:
        # 数据库未初始化
        return None
    except Exception:
        # 其他数据库错误
        return None


async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    验证用户凭据
    
    Args:
        username: 用户名
        password: 密码
    
    Returns:
        验证成功的用户对象，失败则返回None
    """
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    获取当前登录用户
    
    - 解析JWT Token
    - 验证用户有效性
    - 返回用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码Token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 获取用户ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 从数据库获取用户
    result = await db_manager.db.get("users", user_id)
    if not result.get("success"):
        raise credentials_exception
    
    user_data = result.get("data", {})
    return User(**user_data)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前活跃用户
    
    - 检查用户是否被禁用
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    获取当前活跃的超级管理员用户
    
    - 检查用户是否为超级管理员
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user


async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)]
) -> Optional[User]:
    """
    获取当前登录用户（可选认证）
    
    - 如果提供了有效的Token，返回用户对象
    - 如果未提供Token或Token无效，返回None
    - 用于公开接口中识别已登录用户（如显示"已点赞"状态）
    
    Returns:
        User对象或None
    """
    if not token:
        return None
    
    try:
        # 解码Token
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        # 获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # 从数据库获取用户
        result = await db_manager.db.get("users", user_id)
        if not result.get("success"):
            return None
        
        user_data = result.get("data", {})
        user = User(**user_data)
        
        # 检查用户是否激活
        if not user.is_active:
            return None
        
        return user
    except Exception:
        # 任何异常都返回None，不抛出错误
        return None


@router.post("/token", summary="用户登录", description="使用用户名和密码获取访问令牌")
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> dict:
    """
    用户登录接口
    
    - 验证用户名和密码
    - 生成JWT访问令牌
    - 返回令牌信息
    """
    # 验证用户
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    # 创建刷新令牌
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_access_token(
        data={"sub": user.id, "type": "refresh"},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": User(**user.model_dump(exclude={"hashed_password"}))
    }


@router.post("/refresh", summary="刷新令牌", description="使用刷新令牌获取新的访问令牌")
async def refresh_access_token(
    refresh_token: str
) -> dict:
    """
    刷新访问令牌
    
    - 验证刷新令牌
    - 生成新的访问令牌
    """
    # 解码刷新令牌
    payload = decode_access_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 验证令牌类型
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌类型"
        )
    
    # 获取用户ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )
    
    # 从数据库获取用户
    result = await db_manager.db.get("users", user_id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    user_data = result.get("data", {})
    user = User(**user_data)
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


import re


@router.post("/register", summary="用户注册", description="注册新用户账号，需要超管权限", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register_user(
    request: Request,
    user_create: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)]
) -> User:
    """
    用户注册接口

    - 需要超管权限
    - 创建新用户（默认非管理员）
    - 支持普通用户(user_type='user')和Agent(user_type='agent')注册
    - 注册Agent时必须提供agent_model和agent_provider字段
    - 用户名只允许字母、数字、下划线，不能以数字开头
    - 返回用户信息（不包含密码）
    """
    # 检查数据库是否已初始化
    try:
        # 尝试访问数据库，如果未初始化会抛出RuntimeError
        _ = db_manager.db
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库服务暂不可用"
        )

    # 清理和验证用户名
    username = user_create.username.strip().lower()

    # 用户名格式验证：只允许字母、数字、下划线，不能以数字开头
    if not re.match(r'^[a-z][a-z0-9_]*$', username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含小写字母、数字和下划线，且必须以字母开头"
        )

    # 检查用户名长度
    if len(username) < 3 or len(username) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名长度必须在3-50个字符之间"
        )

    # 检查用户名是否已存在（大小写不敏感）
    existing_user = await get_user_by_username(username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在（如果提供了邮箱）
    if user_create.email:
        try:
            result = await db_manager.db.find(
                "users",
                filters={"email": user_create.email.lower().strip()},
                limit=1
            )
            if result.get("data") and len(result["data"]) > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
        except HTTPException:
            raise
        except Exception:
            # 数据库查询失败，继续注册流程
            pass

    # 哈希密码
    hashed_password = get_password_hash(user_create.password)

    # 判断是否为Agent注册
    is_agent = getattr(user_create, 'user_type', 'user') == 'agent'
    
    if is_agent:
        # Agent注册：验证必填字段
        agent_model = getattr(user_create, 'agent_model', None)
        agent_provider = getattr(user_create, 'agent_provider', None)
        
        if not agent_model or not agent_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent注册失败: 必须提供agent_model和agent_provider字段"
            )
        
        # 准备Agent数据
        user_data = {
            "id": str(uuid4()),
            "username": username,
            "email": user_create.email.lower().strip() if user_create.email else None,
            "hashed_password": hashed_password,
            "display_name": user_create.display_name.strip() if user_create.display_name else username,
            "avatar_url": None,
            "bio": user_create.bio.strip() if user_create.bio else None,
            "user_type": "agent",
            "agent_model": agent_model,
            "agent_provider": agent_provider,
            "agent_config": json.dumps(getattr(user_create, 'agent_config', {})) if getattr(user_create, 'agent_config', None) else None,
            "is_active": True,
            "is_superuser": False
        }
    else:
        # 普通用户注册
        user_data = {
            "id": str(uuid4()),
            "username": username,
            "email": user_create.email.lower().strip() if user_create.email else None,
            "hashed_password": hashed_password,
            "display_name": user_create.display_name.strip() if user_create.display_name else username,
            "avatar_url": None,
            "bio": user_create.bio.strip() if user_create.bio else None,
            "user_type": "user",
            "agent_model": None,
            "agent_provider": None,
            "agent_config": None,
            "is_active": True,
            "is_superuser": False
        }

    # 创建用户
    try:
        result = await db_manager.db.insert("users", user_data)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败"
            )

        # 返回用户信息（使用数据库返回的完整数据，包含created_at等字段）
        user_response_data = result["data"]
        user_response_data.pop("hashed_password", None)  # 移除密码字段
        return User(**user_response_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.post("/logout", summary="用户登出", description="使当前访问令牌失效")
async def logout_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    用户登出接口
    
    - 使当前Token失效（客户端需删除Token）
    - 返回成功消息
    """
    # 注意：JWT Token本身无法真正"失效"，需要客户端删除
    # 这里可以记录登出日志或加入Token黑名单（如果需要）
    return {
        "success": True,
        "message": "登出成功",
        "user_id": current_user.id,
        "username": current_user.username
    }


@router.post("/password/reset", summary="修改密码", description="修改当前用户密码")
async def reset_password(
    current_user: Annotated[User, Depends(get_current_active_user)],
    old_password: str,
    new_password: str
) -> dict:
    """
    修改密码接口
    
    - 需要验证旧密码
    - 新密码需要符合安全要求
    """
    # 验证旧密码
    result = await db_manager.db.get("users", current_user.id)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user_data = result["data"]
    if not verify_password(old_password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 验证新密码长度
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于8个字符"
        )
    
    # 哈希新密码
    new_hashed_password = get_password_hash(new_password)
    
    # 更新密码
    update_result = await db_manager.db.update(
        "users",
        current_user.id,
        {"hashed_password": new_hashed_password}
    )
    
    if not update_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )
    
    return {
        "success": True,
        "message": "密码修改成功",
        "user_id": current_user.id
    }


@router.get("/me", response_model=User, summary="获取当前用户信息", description="获取当前登录用户的详细信息")
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    获取当前登录用户信息
    
    - 需要有效的访问令牌
    - 返回用户详细信息（不包含密码）
    """
    return current_user
