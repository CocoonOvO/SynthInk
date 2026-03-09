"""
XSS防护工具单元测试
测试HTML净化、标签过滤、URL清理等功能
"""
import pytest
from app.utils.xss_guard import (
    sanitize_html,
    remove_disallowed_tags,
    sanitize_attributes,
    sanitize_urls,
    escape_html_entities,
    strip_all_tags,
    validate_no_script,
    ALLOWED_TAGS,
    ALLOWED_ATTRIBUTES,
    DANGEROUS_PROTOCOLS
)


class TestSanitizeHtml:
    """测试HTML净化主函数"""

    def test_empty_content(self):
        """测试空内容"""
        assert sanitize_html("") == ""
        assert sanitize_html(None) == ""

    def test_plain_text(self):
        """测试纯文本"""
        text = "Hello World"
        assert sanitize_html(text) == "Hello World"

    def test_allowed_tags(self):
        """测试允许的标签保留"""
        html = "<p>Hello</p><strong>World</strong>"
        result = sanitize_html(html)
        assert "<p" in result  # 可能有空格
        assert "<strong" in result

    def test_disallowed_tags_removed(self):
        """测试不允许的标签被移除（但内容保留）"""
        html = "<p>Hello</p><script>alert('xss')</script>"
        result = sanitize_html(html)
        assert "<p" in result
        assert "<script>" not in result
        # script标签被移除，但内容保留
        assert "alert" in result

    def test_script_tag_removed(self):
        """测试script标签被移除（内容保留）"""
        html = "<script>alert('xss')</script>"
        result = sanitize_html(html)
        assert "<script>" not in result
        # script标签被移除，但内容保留
        assert "alert" in result

    def test_style_tag_removed(self):
        """测试style标签被移除（内容保留）"""
        html = "<style>body{color:red}</style>"
        result = sanitize_html(html)
        assert "<style>" not in result
        # style标签被移除，但内容保留
        assert "body" in result

    def test_mixed_content(self):
        """测试混合内容"""
        html = "<p>Safe content</p><iframe src='evil.com'></iframe>"
        result = sanitize_html(html)
        assert "<p" in result
        assert "<iframe>" not in result
        assert "iframe" not in result


class TestRemoveDisallowedTags:
    """测试标签移除功能"""

    def test_keep_allowed_tags(self):
        """测试保留允许的标签"""
        for tag in ['p', 'div', 'span', 'h1', 'a', 'img']:
            html = f"<{tag}>content</{tag}>"
            result = remove_disallowed_tags(html)
            assert f"<{tag}>" in result

    def test_remove_disallowed_tags(self):
        """测试移除不允许的标签（内容保留）"""
        html = "<script>alert('xss')</script>"
        result = remove_disallowed_tags(html)
        assert "<script>" not in result
        # 内容保留
        assert "alert" in result

    def test_remove_iframe(self):
        """测试移除iframe"""
        html = "<iframe src='http://evil.com'></iframe>"
        result = remove_disallowed_tags(html)
        assert "<iframe>" not in result

    def test_remove_form(self):
        """测试移除form"""
        html = "<form><input></form>"
        result = remove_disallowed_tags(html)
        assert "<form>" not in result

    def test_self_closing_tags(self):
        """测试自闭合标签"""
        html = "<br/><hr/>"
        result = remove_disallowed_tags(html)
        assert "<br/>" in result
        assert "<hr/>" not in result  # hr不在白名单中

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        html = "<SCRIPT>alert('xss')</SCRIPT>"
        result = remove_disallowed_tags(html)
        assert "<SCRIPT>" not in result
        assert "<script>" not in result
        # 内容保留
        assert "alert" in result


class TestSanitizeAttributes:
    """测试属性清理功能"""

    def test_keep_allowed_attributes(self):
        """测试保留允许的属性"""
        html = '<a href="http://example.com" title="Link">text</a>'
        result = sanitize_attributes(html)
        assert 'href="http://example.com"' in result
        assert 'title="Link"' in result

    def test_remove_disallowed_attributes(self):
        """测试移除不允许的属性"""
        html = '<a href="http://example.com" onclick="alert(1)">text</a>'
        result = sanitize_attributes(html)
        assert 'href=' in result
        assert 'onclick' not in result

    def test_img_allowed_attributes(self):
        """测试img允许的属性"""
        html = '<img src="image.jpg" alt="Image" title="Title">'
        result = sanitize_attributes(html)
        assert 'src="image.jpg"' in result
        assert 'alt="Image"' in result
        assert 'title="Title"' in result

    def test_code_class_attribute(self):
        """测试code标签的class属性"""
        html = '<code class="python">print("hello")</code>'
        result = sanitize_attributes(html)
        assert 'class="python"' in result

    def test_escape_quotes_in_attributes(self):
        """测试转义属性中的引号"""
        html = '<a title="He said &quot;Hello&quot;"></a>'
        result = sanitize_attributes(html)
        # 引号被双重转义：&quot; -> &amp;quot;
        assert '&amp;quot;' in result


class TestSanitizeUrls:
    """测试URL清理功能"""

    def test_safe_http_url(self):
        """测试安全的HTTP URL"""
        html = '<a href="http://example.com">link</a>'
        result = sanitize_urls(html)
        assert 'href="http://example.com"' in result

    def test_safe_https_url(self):
        """测试安全的HTTPS URL"""
        html = '<a href="https://example.com">link</a>'
        result = sanitize_urls(html)
        assert 'href="https://example.com"' in result

    def test_dangerous_javascript_protocol(self):
        """测试危险的javascript协议"""
        html = '<a href="javascript:alert(\'xss\')">link</a>'
        result = sanitize_urls(html)
        assert 'href="#' in result
        assert 'javascript:' not in result

    def test_dangerous_data_protocol(self):
        """测试危险的data协议"""
        html = '<a href="data:text/html,<script>alert(1)</script>">link</a>'
        result = sanitize_urls(html)
        assert 'href="#' in result

    def test_img_src_sanitization(self):
        """测试img src清理"""
        html = '<img src="javascript:alert(1)">'
        result = sanitize_urls(html)
        assert 'src="#' in result

    def test_case_insensitive_protocol(self):
        """测试协议大小写不敏感"""
        html = '<a href="JAVASCRIPT:alert(1)">link</a>'
        result = sanitize_urls(html)
        assert 'href="#' in result


class TestEscapeHtmlEntities:
    """测试HTML实体转义"""

    def test_escape_ampersand(self):
        """测试转义&"""
        assert escape_html_entities("&") == "&amp;"

    def test_escape_less_than(self):
        """测试转义<"""
        assert escape_html_entities("<") == "&lt;"

    def test_escape_greater_than(self):
        """测试转义>"""
        assert escape_html_entities(">") == "&gt;"

    def test_escape_double_quote(self):
        """测试转义双引号"""
        assert escape_html_entities('"') == "&quot;"

    def test_escape_single_quote(self):
        """测试转义单引号"""
        assert escape_html_entities("'") == "&#x27;"

    def test_escape_multiple(self):
        """测试转义多个字符"""
        text = '<script>alert("xss")</script>'
        result = escape_html_entities(text)
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result

    def test_empty_string(self):
        """测试空字符串"""
        assert escape_html_entities("") == ""
        assert escape_html_entities(None) == ""


class TestStripAllTags:
    """测试移除所有标签"""

    def test_strip_simple_tags(self):
        """测试移除简单标签"""
        html = "<p>Hello</p><p>World</p>"
        result = strip_all_tags(html)
        assert "Hello" in result
        assert "World" in result
        assert "<p>" not in result

    def test_strip_nested_tags(self):
        """测试移除嵌套标签"""
        html = "<div><p><strong>Text</strong></p></div>"
        assert strip_all_tags(html) == "Text"

    def test_strip_with_entities(self):
        """测试处理HTML实体"""
        html = "<p>Hello &amp; World</p>"
        assert strip_all_tags(html) == "Hello & World"

    def test_empty_content(self):
        """测试空内容"""
        assert strip_all_tags("") == ""
        assert strip_all_tags(None) == ""

    def test_plain_text_unchanged(self):
        """测试纯文本不变"""
        text = "Just plain text"
        assert strip_all_tags(text) == "Just plain text"


class TestValidateNoScript:
    """测试脚本检测功能"""

    def test_safe_content(self):
        """测试安全内容"""
        assert validate_no_script("<p>Safe content</p>") is True

    def test_contains_script_tag(self):
        """测试包含script标签"""
        assert validate_no_script("<script>alert(1)</script>") is False

    def test_contains_script_with_attributes(self):
        """测试带属性的script标签"""
        assert validate_no_script('<script type="text/javascript">alert(1)</script>') is False

    def test_contains_event_handler(self):
        """测试包含事件处理器"""
        assert validate_no_script('<p onclick="alert(1)">text</p>') is False

    def test_contains_onerror(self):
        """测试包含onerror"""
        assert validate_no_script('<img src="x" onerror="alert(1)">') is False

    def test_case_insensitive_script(self):
        """测试大小写不敏感的script检测"""
        assert validate_no_script("<SCRIPT>alert(1)</SCRIPT>") is False

    def test_empty_content(self):
        """测试空内容"""
        assert validate_no_script("") is True
        assert validate_no_script(None) is True


class TestConstants:
    """测试常量定义"""

    def test_allowed_tags_not_empty(self):
        """测试允许标签列表不为空"""
        assert len(ALLOWED_TAGS) > 0
        assert 'p' in ALLOWED_TAGS
        assert 'script' not in ALLOWED_TAGS

    def test_allowed_attributes_structure(self):
        """测试允许属性结构"""
        assert 'a' in ALLOWED_ATTRIBUTES
        assert 'href' in ALLOWED_ATTRIBUTES['a']
        assert 'img' in ALLOWED_ATTRIBUTES
        assert 'src' in ALLOWED_ATTRIBUTES['img']

    def test_dangerous_protocols(self):
        """测试危险协议列表"""
        assert 'javascript:' in DANGEROUS_PROTOCOLS
        assert 'data:' in DANGEROUS_PROTOCOLS
