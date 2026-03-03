"""
认证路由模块
处理用户登录、注册、Token刷新等
"""
from datetime import timedelta
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import get_settings
from ..db_manager import db_manager
from ..models.user import User, UserCreate, UserInDB
from ..utils.security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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
    result = await db_manager.postgres.get_user_by_username(username)
    if result.get("success") and result.get("data"):
        return UserInDB(**result["data"])
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
    result = await db_manager.postgres.get("users", user_id)
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
    result = await db_manager.postgres.get("users", user_id)
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


@router.post("/register", summary="用户注册", description="注册新用户账号", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register_user(
    request: Request,
    user_create: UserCreate
) -> User:
    """
    用户注册接口
    
    - 创建新用户（默认非管理员）
    - 返回用户信息（不包含密码）
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if user_create.email:
        result = await db_manager.postgres.find(
            "users",
            filters={"email": user_create.email},
            limit=1
        )
        if result.get("data") and len(result["data"]) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 哈希密码
    hashed_password = get_password_hash(user_create.password)
    
    # 准备用户数据
    user_data = user_create.model_dump(exclude={"password"})
    user_data["id"] = str(uuid4())
    user_data["hashed_password"] = hashed_password
    user_data["is_active"] = True
    user_data["is_superuser"] = False  # 默认非管理员
    
    # 创建用户
    result = await db_manager.postgres.insert("users", user_data)
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )
    
    # 返回用户信息（使用数据库返回的完整数据，包含created_at等字段）
    user_response_data = result["data"]
    user_response_data.pop("hashed_password", None)  # 移除密码字段
    return User(**user_response_data)


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
    result = await db_manager.postgres.get("users", current_user.id)
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
    update_result = await db_manager.postgres.update(
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
