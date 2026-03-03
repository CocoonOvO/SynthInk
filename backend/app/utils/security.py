"""
安全工具模块
处理密码哈希、JWT令牌等安全相关功能
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib
import secrets

from ..config import get_settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    使用SHA256 + salt进行验证
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码 (格式: salt$hash)
    
    Returns:
        是否匹配
    """
    try:
        salt, stored_hash = hashed_password.split('$')
        computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)
    except (ValueError, AttributeError):
        return False


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    使用SHA256 + salt进行哈希
    
    Args:
        password: 明文密码
    
    Returns:
        哈希后的密码 (格式: salt$hash)
    """
    # 生成随机salt
    salt = secrets.token_hex(16)
    # 计算哈希
    hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hash_value}"


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的数据，如果无效则返回None
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
