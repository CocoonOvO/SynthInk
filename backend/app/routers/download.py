"""
文件下载路由模块
处理文件下载和删除
"""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..config import get_settings
from ..models.user import User
from .auth import get_current_active_user

router = APIRouter()


def get_upload_dir() -> Path:
    """获取上传目录"""
    upload_dir = Path(get_settings().UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.get("/{user_id}/{file_type}/{filename}", summary="获取文件")
async def get_file(
    user_id: str,
    file_type: str,
    filename: str
) -> FileResponse:
    """
    获取上传的文件

    - 公开访问
    - 支持图片和附件
    """
    # 验证文件类型
    if file_type not in ["images", "avatars", "attachments"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件类型"
        )

    # 构建文件路径
    upload_dir = get_upload_dir()
    file_path = upload_dir / file_type / user_id / filename

    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 确定媒体类型
    media_type = None
    ext = Path(filename).suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif ext == ".png":
        media_type = "image/png"
    elif ext == ".gif":
        media_type = "image/gif"
    elif ext == ".webp":
        media_type = "image/webp"
    elif ext == ".pdf":
        media_type = "application/pdf"
    elif ext == ".md":
        media_type = "text/markdown"
    elif ext == ".txt":
        media_type = "text/plain"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@router.delete("/{user_id}/{file_type}/{filename}", summary="删除文件")
async def delete_file(
    user_id: str,
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    删除上传的文件

    - 需要登录
    - 只能删除自己的文件（超管除外）
    """
    # 验证文件类型
    if file_type not in ["images", "avatars", "attachments"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件类型"
        )

    # 检查权限（只能删除自己的文件，除非是超管）
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此文件"
        )

    # 构建文件路径
    upload_dir = get_upload_dir()
    file_path = upload_dir / file_type / user_id / filename

    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )

    # 删除文件
    file_path.unlink()

    return {
        "success": True,
        "message": "文件已删除"
    }
