"""
XSS防护工具模块
提供HTML内容过滤和净化功能
"""
import re
from typing import Optional

# 允许的HTML标签白名单
ALLOWED_TAGS = {
    'p', 'br', 'strong', 'em', 'b', 'i', 'u',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'code', 'pre', 'blockquote',
    'ul', 'ol', 'li',
    'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'div', 'span'
}

# 允许的属性白名单
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class'],
    'p': ['class'],
    'h1': ['class'], 'h2': ['class'], 'h3': ['class'],
    'h4': ['class'], 'h5': ['class'], 'h6': ['class']
}

# 危险的URL协议
DANGEROUS_PROTOCOLS = {'javascript:', 'data:', 'vbscript:', 'file:'}


def sanitize_html(content: Optional[str]) -> str:
    """
    净化HTML内容，移除危险的标签和属性
    
    Args:
        content: 原始HTML内容
        
    Returns:
        净化后的安全HTML
    """
    if not content:
        return ""
    
    # 使用正则表达式移除不允许的标签
    cleaned = remove_disallowed_tags(content)
    
    # 清理属性
    cleaned = sanitize_attributes(cleaned)
    
    # 清理危险的URL
    cleaned = sanitize_urls(cleaned)
    
    return cleaned


def remove_disallowed_tags(html: str) -> str:
    """
    移除不允许的HTML标签
    """
    # 匹配所有标签
    tag_pattern = re.compile(r'<(/?)(\w+)([^>]*)>', re.IGNORECASE)
    
    def replace_tag(match):
        closing = match.group(1)
        tag_name = match.group(2).lower()
        attributes = match.group(3)
        
        if tag_name in ALLOWED_TAGS:
            return f"<{closing}{tag_name}{attributes}>"
        else:
            # 不允许的标签，直接移除
            return ''
    
    return tag_pattern.sub(replace_tag, html)


def sanitize_attributes(html: str) -> str:
    """
    清理HTML属性，只保留允许的属性
    """
    tag_pattern = re.compile(r'<(\w+)([^>]*)>', re.IGNORECASE)
    
    def replace_tag(match):
        tag_name = match.group(1).lower()
        attributes_str = match.group(2)
        
        if tag_name not in ALLOWED_TAGS:
            return match.group(0)
        
        allowed_attrs = ALLOWED_ATTRIBUTES.get(tag_name, [])
        
        # 解析属性
        attr_pattern = re.compile(r'(\w+)(?:=["\']([^"\']*)["\'])?')
        attrs = attr_pattern.findall(attributes_str)
        
        safe_attrs = []
        for attr_name, attr_value in attrs:
            attr_name_lower = attr_name.lower()
            if attr_name_lower in allowed_attrs:
                # 对属性值进行转义
                safe_value = escape_html_entities(attr_value)
                safe_attrs.append(f'{attr_name}="{safe_value}"')
        
        return f"<{tag_name} {' '.join(safe_attrs)}>"
    
    return tag_pattern.sub(replace_tag, html)


def sanitize_urls(html: str) -> str:
    """
    清理危险的URL协议
    """
    # 匹配href和src属性
    url_pattern = re.compile(r'(href|src)=["\']([^"\']*)["\']', re.IGNORECASE)
    
    def replace_url(match):
        attr_name = match.group(1).lower()
        url = match.group(2).lower().strip()
        
        # 检查危险的协议
        for protocol in DANGEROUS_PROTOCOLS:
            if url.startswith(protocol):
                return f'{attr_name}="#"'
        
        return match.group(0)
    
    return url_pattern.sub(replace_url, html)


def escape_html_entities(text: str) -> str:
    """
    转义HTML实体
    """
    if not text:
        return ""
    
    replacements = [
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('"', '&quot;'),
        ("'", '&#x27;'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    return text


def strip_all_tags(content: Optional[str]) -> str:
    """
    移除所有HTML标签，仅保留纯文本
    用于不需要富文本的字段
    """
    if not content:
        return ""
    
    # 移除所有标签
    tag_pattern = re.compile(r'<[^>]+>')
    text = tag_pattern.sub('', content)
    
    # 解码HTML实体
    import html
    text = html.unescape(text)
    
    return text.strip()


def validate_no_script(content: Optional[str]) -> bool:
    """
    验证内容中是否包含script标签
    返回True表示安全，False表示包含危险内容
    """
    if not content:
        return True
    
    # 检查script标签
    script_pattern = re.compile(r'<script[^>]*>', re.IGNORECASE)
    if script_pattern.search(content):
        return False
    
    # 检查事件处理器
    event_pattern = re.compile(r'on\w+\s*=', re.IGNORECASE)
    if event_pattern.search(content):
        return False
    
    return True
