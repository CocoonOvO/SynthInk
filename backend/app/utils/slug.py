"""
Slug生成工具模块
提供URL友好的标识符生成和唯一性保证
"""
import re
import unicodedata
from typing import List, Optional


def normalize_chinese(text: str) -> str:
    """
    将中文字符转换为拼音或保留原样
    简化处理：保留中文，后续可通过pypinyin库转换
    """
    # 目前直接保留中文，URL编码会自动处理
    # 如需拼音转换，可添加 pypinyin 依赖
    return text


def generate_base_slug(text: str) -> str:
    """
    从文本生成基础slug
    
    处理流程：
    1. Unicode规范化
    2. 转小写
    3. 替换空格为连字符
    4. 移除非字母数字中文连字符的字符
    5. 合并多个连字符
    """
    if not text:
        return "untitled"
    
    # Unicode规范化
    text = unicodedata.normalize('NFKC', text)
    
    # 转小写
    text = text.lower()
    
    # 替换空格、下划线为连字符
    text = re.sub(r'[\s_]+', '-', text)
    
    # 保留字母、数字、中文、连字符
    # 中文字符范围：\u4e00-\u9fff
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff\-]', '', text)
    
    # 合并多个连字符
    text = re.sub(r'-+', '-', text)
    
    # 移除首尾连字符
    text = text.strip('-')
    
    # 如果为空，返回默认slug
    if not text:
        return "untitled"
    
    # 限制长度（保留前100字符）
    if len(text) > 100:
        text = text[:100].rsplit('-', 1)[0]  # 在最后一个连字符处截断
    
    return text


def ensure_unique_slug(base_slug: str, existing_slugs: List[str]) -> str:
    """
    确保slug唯一性
    
    如果base_slug已存在，添加数字后缀：
    - base-slug
    - base-slug-1
    - base-slug-2
    - ...
    """
    if base_slug not in existing_slugs:
        return base_slug
    
    counter = 1
    while True:
        new_slug = f"{base_slug}-{counter}"
        if new_slug not in existing_slugs:
            return new_slug
        counter += 1
        
        # 防止无限循环
        if counter > 999:
            # 使用时间戳后缀
            import time
            return f"{base_slug}-{int(time.time())}"


def generate_slug(text: str, existing_slugs: Optional[List[str]] = None) -> str:
    """
    生成唯一的slug
    
    Args:
        text: 原始文本（通常是标题）
        existing_slugs: 已存在的slug列表，用于保证唯一性
        
    Returns:
        唯一的slug字符串
        
    Example:
        >>> generate_slug("Python 入门教程", ["python-ru-men-jiao-cheng"])
        "python-ru-men-jiao-cheng-1"
    """
    if existing_slugs is None:
        existing_slugs = []
    
    base_slug = generate_base_slug(text)
    return ensure_unique_slug(base_slug, existing_slugs)


def is_valid_slug(slug: str) -> bool:
    """
    验证slug格式是否有效
    
    规则：
    - 只能包含小写字母、数字、中文、连字符
    - 不能以连字符开头或结尾
    - 不能包含连续连字符
    - 长度1-100字符
    """
    if not slug:
        return False
    
    if len(slug) > 100:
        return False
    
    # 检查格式：允许小写字母、数字、中文、连字符
    # 中文字符范围：\u4e00-\u9fff
    pattern = r'^[a-z0-9\u4e00-\u9fff]+(-[a-z0-9\u4e00-\u9fff]+)*$'
    return bool(re.match(pattern, slug))


def slugify_title(title: str) -> str:
    """
    将标题转换为slug的便捷函数
    不保证唯一性，仅做格式转换
    """
    return generate_base_slug(title)
