"""
文件上传路由模块
处理图片、附件等文件上传
"""
import os
import shutil
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from ..config import get_settings
from ..db_manager import db_manager
from ..models.user import User
from .auth import get_current_active_user, get_current_active_superuser

router = APIRouter()

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"application/pdf", "text/markdown", "text/plain"} | ALLOWED_IMAGE_TYPES
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 文件扩展名映射
EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
    "text/markdown": ".md",
    "text/plain": ".txt"
}


def get_upload_dir() -> Path:
    """获取上传目录"""
    upload_dir = Path(get_settings().UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def validate_file_type(content_type: str, allowed_types: set) -> bool:
    """验证文件类型"""
    return content_type in allowed_types


def validate_file_size(size: int) -> bool:
    """验证文件大小"""
    return size <= MAX_FILE_SIZE


def generate_unique_filename(original_filename: str, content_type: str) -> str:
    """生成唯一文件名"""
    ext = EXTENSION_MAP.get(content_type, Path(original_filename).suffix)
    return f"{uuid4()}{ext}"


@router.post("/image", summary="上传图片")
async def upload_image(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    上传图片文件
    
    - 支持格式: jpg, png, gif, webp
    - 最大 10MB
    - 保存到用户专属目录
    - 返回可访问的URL
    """
    # 验证文件类型
    if not validate_file_type(file.content_type, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式: {file.content_type}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename, file.content_type)
    
    # 创建用户目录
    upload_dir = get_upload_dir()
    user_dir = upload_dir / "images" / current_user.id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_path = user_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 构建下载URL
    file_url = f"/api/download/{current_user.id}/images/{filename}"

    return {
        "success": True,
        "filename": filename,
        "url": file_url,
        "size": len(content),
        "content_type": file.content_type
    }


@router.post("/avatar", summary="上传头像")
async def upload_avatar(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    上传用户头像
    
    - 支持格式: jpg, png, gif, webp
    - 建议尺寸: 200x200
    - 自动裁剪/压缩
    - 覆盖旧头像
    """
    # 验证文件类型
    if not validate_file_type(file.content_type, ALLOWED_IMAGE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式: {file.content_type}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成文件名（使用 uuid 确保唯一，避免浏览器缓存）
    ext = EXTENSION_MAP.get(file.content_type, ".jpg")
    filename = f"avatar_{uuid4().hex[:8]}{ext}"
    
    # 创建用户头像目录
    upload_dir = get_upload_dir()
    avatar_dir = upload_dir / "avatars" / current_user.id
    avatar_dir.mkdir(parents=True, exist_ok=True)
    
    # 删除旧头像
    for old_file in avatar_dir.glob("avatar_*"):
        old_file.unlink()
    
    # 保存新头像
    file_path = avatar_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 构建下载URL
    avatar_url = f"/api/download/{current_user.id}/avatars/{filename}"

    # 更新用户头像URL
    await db_manager.db.update(
        "users",
        current_user.id,
        {"avatar_url": avatar_url}
    )
    
    return {
        "success": True,
        "filename": filename,
        "url": avatar_url,
        "size": len(content),
        "content_type": file.content_type
    }


@router.post("/attachment", summary="上传附件")
async def upload_attachment(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    """
    上传附件文件
    
    - 支持格式: pdf, markdown, 图片
    - 最大 10MB
    """
    # 验证文件类型
    if not validate_file_type(file.content_type, ALLOWED_FILE_TYPES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式: {file.content_type}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename, file.content_type)
    
    # 创建用户附件目录
    upload_dir = get_upload_dir()
    attachment_dir = upload_dir / "attachments" / current_user.id
    attachment_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    file_path = attachment_dir / filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 构建下载URL
    file_url = f"/api/download/{current_user.id}/attachments/{filename}"

    return {
        "success": True,
        "filename": filename,
        "original_name": file.filename,
        "url": file_url,
        "size": len(content),
        "content_type": file.content_type
    }
