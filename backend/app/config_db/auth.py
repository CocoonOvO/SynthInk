"""
配置库超管认证模块
独立于博客用户认证，专门用于配置库超管登录和权限验证
"""
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from .manager import config_db_manager
from .models import ConfigAdmin
from ..utils.security import verify_password


class ConfigAdminLogin(BaseModel):
    """超管登录请求模型"""
    username: str
    password: str


class ConfigAdminToken(BaseModel):
    """超管登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin_id: int
    username: str
    is_default_password: bool = False  # 标记是否使用默认密码
    security_warning: Optional[str] = None  # 安全警告信息


class ConfigAdminAuth:
    """
    配置库超管认证类
    
    职责：
    1. 超管登录验证
    2. JWT令牌生成和验证
    3. 依赖注入验证
    
    注意：与博客用户认证完全分离，使用不同的密钥和机制
    """
    
    # 使用不同的密钥前缀，避免与博客用户认证冲突
    TOKEN_TYPE = "config_admin"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS = 7  # 超管令牌7天过期
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    def _get_secret_key(self) -> str:
        """从配置库获取JWT密钥"""
        secret = config_db_manager.get_system_config_value("jwt_secret_key", "")
        if not secret:
            # 如果没有配置，使用默认（不推荐生产环境使用）
            import secrets
            secret = secrets.token_urlsafe(32)
        # 添加前缀区分不同类型的令牌
        return f"{self.TOKEN_TYPE}:{secret}"
    
    def authenticate_admin(self, username: str, password: str) -> Optional[ConfigAdmin]:
        """
        验证超管账号密码
        
        Args:
            username: 用户名
            password: 明文密码
            
        Returns:
            验证成功返回ConfigAdmin对象，失败返回None
        """
        admin = config_db_manager.get_admin_by_username(username)
        
        if not admin:
            return None
        
        if not admin.is_active:
            return None
        
        if not verify_password(password, admin.password_hash):
            return None
        
        return admin
    
    def create_access_token(
        self,
        admin_id: int,
        username: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建超管访问令牌
        
        Args:
            admin_id: 超管ID
            username: 用户名
            expires_delta: 过期时间增量
            
        Returns:
            JWT令牌字符串
        """
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": str(admin_id),
            "username": username,
            "type": self.TOKEN_TYPE,
            "exp": expire,
            "iat": datetime.now(UTC)
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            self._get_secret_key(),
            algorithm=self.ALGORITHM
        )
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        解码并验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            解码后的payload，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                self._get_secret_key(),
                algorithms=[self.ALGORITHM]
            )
            
            # 验证令牌类型
            if payload.get("type") != self.TOKEN_TYPE:
                return None
            
            return payload
            
        except JWTError:
            return None
    
    async def get_current_admin(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
    ) -> ConfigAdmin:
        """
        获取当前登录的超管（FastAPI依赖）
        
        Usage:
            @router.get("/admin-only")
            async def admin_endpoint(admin: ConfigAdmin = Depends(config_admin_auth.get_current_admin)):
                return {"message": f"Hello {admin.username}"}
        
        Args:
            request: FastAPI请求对象
            credentials: HTTP认证凭证
            
        Returns:
            ConfigAdmin对象
            
        Raises:
            HTTPException: 认证失败时抛出401错误
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # 检查是否有认证头
        if not credentials:
            raise credentials_exception
        
        token = credentials.credentials
        payload = self.decode_token(token)
        
        if payload is None:
            raise credentials_exception
        
        # 获取管理员ID
        admin_id = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
        
        # 查询管理员
        admin = config_db_manager.get_admin_by_id(int(admin_id))
        if admin is None:
            raise credentials_exception
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        
        return admin
    
    async def get_current_admin_optional(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[ConfigAdmin]:
        """
        可选的当前超管获取（FastAPI依赖）
        
        与get_current_admin不同，此依赖不会抛出异常，而是返回None
        
        Usage:
            @router.get("/some-endpoint")
            async def endpoint(admin: Optional[ConfigAdmin] = Depends(config_admin_auth.get_current_admin_optional)):
                if admin:
                    return {"message": f"Hello admin {admin.username}"}
                return {"message": "Hello guest"}
        """
        if not credentials:
            return None
        
        token = credentials.credentials
        payload = self.decode_token(token)
        
        if payload is None:
            return None
        
        admin_id = payload.get("sub")
        if admin_id is None:
            return None
        
        admin = config_db_manager.get_admin_by_id(int(admin_id))
        if admin is None or not admin.is_active:
            return None
        
        return admin
    
    def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> ConfigAdminToken:
        """
        超管登录
        
        Args:
            username: 用户名
            password: 密码
            ip_address: 登录IP地址
            
        Returns:
            ConfigAdminToken对象
            
        Raises:
            HTTPException: 登录失败时抛出401错误
        """
        admin = self.authenticate_admin(username, password)
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 更新登录信息
        config_db_manager.update_admin_login(admin.id, ip_address or "")
        
        # 记录登录日志
        config_db_manager.add_audit_log(
            admin_id=admin.id,
            admin_username=admin.username,
            action="login",
            target_type="admin",
            target_id=str(admin.id),
            ip_address=ip_address
        )
        
        # 创建令牌
        access_token = self.create_access_token(
            admin_id=admin.id,
            username=admin.username
        )
        
        # 检查是否使用默认密码
        is_default = getattr(admin, 'is_default', False) or admin.username == "admin"
        security_warning = None
        if is_default:
            security_warning = "警告：您正在使用默认密码，请立即修改密码以确保安全！"
        
        return ConfigAdminToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            admin_id=admin.id,
            username=admin.username,
            is_default_password=is_default,
            security_warning=security_warning
        )
    
    def logout(self, admin: ConfigAdmin, ip_address: Optional[str] = None) -> None:
        """
        超管登出
        
        记录登出日志（JWT令牌本身无法失效，只能等过期）
        
        Args:
            admin: 当前超管
            ip_address: IP地址
        """
        config_db_manager.add_audit_log(
            admin_id=admin.id,
            admin_username=admin.username,
            action="logout",
            target_type="admin",
            target_id=str(admin.id),
            ip_address=ip_address
        )


# 全局配置库超管认证实例
config_admin_auth = ConfigAdminAuth()


# 快捷依赖函数
def require_config_admin(
    admin: ConfigAdmin = Depends(config_admin_auth.get_current_admin)
) -> ConfigAdmin:
    """
    要求配置库超管权限的快捷依赖
    
    Usage:
        @router.post("/setup-database")
        async def setup_database(admin: ConfigAdmin = Depends(require_config_admin)):
            # 只有超管可以访问
            pass
    """
    return admin


def optional_config_admin(
    admin: Optional[ConfigAdmin] = Depends(config_admin_auth.get_current_admin_optional)
) -> Optional[ConfigAdmin]:
    """
    可选配置库超管权限的快捷依赖
    """
    return admin
