"""
异常处理模块
统一API异常定义和处理
"""
from fastapi import HTTPException, status
from typing import Any, Optional


class APIException(HTTPException):
    """
    统一的API异常类
    
    继承自FastAPI的HTTPException，提供统一的异常处理
    """
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# 预定义的常见异常
class Exceptions:
    """预定义的API异常集合"""
    
    # 认证相关
    UNAUTHORIZED = APIException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    FORBIDDEN = APIException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="没有权限执行此操作",
    )
    
    # 资源相关
    NOT_FOUND = APIException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="请求的资源不存在",
    )
    
    # 请求相关
    BAD_REQUEST = APIException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="请求参数错误",
    )
    
    CONFLICT = APIException(
        status_code=status.HTTP_409_CONFLICT,
        detail="资源已存在",
    )
    
    # 服务器错误
    INTERNAL_ERROR = APIException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="服务器内部错误",
    )
    
    # 用户相关
    USER_NOT_FOUND = APIException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在",
    )
    
    USER_ALREADY_EXISTS = APIException(
        status_code=status.HTTP_409_CONFLICT,
        detail="用户名或邮箱已存在",
    )
    
    INVALID_PASSWORD = APIException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="密码错误",
    )
    
    # 文件相关
    FILE_TOO_LARGE = APIException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail="文件大小超过限制",
    )
    
    INVALID_FILE_TYPE = APIException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="不支持的文件类型",
    )
    
    FILE_NOT_FOUND = APIException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="文件不存在",
    )


def handle_exception(exception: Exception, debug: bool = False) -> APIException:
    """
    统一异常处理函数
    
    将各种异常转换为统一的APIException
    
    Args:
        exception: 原始异常
        debug: 是否调试模式（调试模式返回详细错误信息）
    
    Returns:
        统一的APIException
    """
    if isinstance(exception, APIException):
        return exception
    
    if isinstance(exception, HTTPException):
        return APIException(
            status_code=exception.status_code,
            detail=exception.detail if debug else "请求处理失败",
            headers=exception.headers,
        )
    
    # 其他异常转换为服务器内部错误
    return APIException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exception) if debug else "服务器内部错误",
    )
