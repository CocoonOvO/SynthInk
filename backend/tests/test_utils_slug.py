"""
Slug工具单元测试
测试slug生成、验证、唯一性保证等功能
"""
import pytest
from app.utils.slug import (
    generate_base_slug,
    ensure_unique_slug,
    generate_slug,
    is_valid_slug,
    slugify_title,
    normalize_chinese
)


class TestNormalizeChinese:
    """测试中文规范化"""

    def test_normalize_chinese_simple(self):
        """测试简单中文文本"""
        text = "中文标题"
        result = normalize_chinese(text)
        assert result == "中文标题"

    def test_normalize_chinese_mixed(self):
        """测试中英文混合"""
        text = "Python中文教程"
        result = normalize_chinese(text)
        assert result == "Python中文教程"


class TestGenerateBaseSlug:
    """测试基础slug生成"""

    def test_empty_text(self):
        """测试空文本返回默认值"""
        assert generate_base_slug("") == "untitled"

    def test_simple_english(self):
        """测试简单英文"""
        assert generate_base_slug("Hello World") == "hello-world"

    def test_chinese_text(self):
        """测试中文文本"""
        assert generate_base_slug("中文标题") == "中文标题"

    def test_mixed_text(self):
        """测试中英文混合"""
        assert generate_base_slug("Python入门教程") == "python入门教程"

    def test_special_characters(self):
        """测试特殊字符处理"""
        assert generate_base_slug("Hello! @World#") == "hello-world"

    def test_multiple_spaces(self):
        """测试多个空格"""
        assert generate_base_slug("Hello    World") == "hello-world"

    def test_underscore_to_hyphen(self):
        """测试下划线转连字符"""
        assert generate_base_slug("hello_world") == "hello-world"

    def test_multiple_hyphens(self):
        """测试多个连字符合并"""
        assert generate_base_slug("hello---world") == "hello-world"

    def test_leading_trailing_hyphens(self):
        """测试首尾连字符移除"""
        assert generate_base_slug("-hello-world-") == "hello-world"

    def test_long_text_truncation(self):
        """测试长文本截断"""
        long_text = "a" * 150
        result = generate_base_slug(long_text)
        assert len(result) <= 100

    def test_only_special_chars(self):
        """测试只有特殊字符"""
        assert generate_base_slug("!@#$%") == "untitled"

    def test_numbers(self):
        """测试包含数字"""
        assert generate_base_slug("Python 3.12 Tutorial") == "python-312-tutorial"


class TestEnsureUniqueSlug:
    """测试唯一性保证"""

    def test_unique_slug_no_conflict(self):
        """测试无冲突的唯一slug"""
        existing = ["other-slug"]
        assert ensure_unique_slug("my-slug", existing) == "my-slug"

    def test_slug_with_conflict(self):
        """测试有冲突的slug"""
        existing = ["my-slug"]
        assert ensure_unique_slug("my-slug", existing) == "my-slug-1"

    def test_multiple_conflicts(self):
        """测试多个冲突"""
        existing = ["my-slug", "my-slug-1", "my-slug-2"]
        assert ensure_unique_slug("my-slug", existing) == "my-slug-3"

    def test_empty_existing(self):
        """测试空已存在列表"""
        assert ensure_unique_slug("my-slug", []) == "my-slug"


class TestGenerateSlug:
    """测试完整slug生成流程"""

    def test_generate_slug_simple(self):
        """测试简单生成"""
        result = generate_slug("Hello World")
        assert result == "hello-world"

    def test_generate_slug_with_existing(self):
        """测试带已存在列表生成"""
        result = generate_slug("Hello World", ["hello-world"])
        assert result == "hello-world-1"

    def test_generate_slug_default_empty_list(self):
        """测试默认空列表参数"""
        result = generate_slug("Test Title", None)
        assert result == "test-title"


class TestIsValidSlug:
    """测试slug格式验证"""

    def test_valid_simple_slug(self):
        """测试有效简单slug"""
        assert is_valid_slug("hello-world") is True

    def test_valid_slug_with_numbers(self):
        """测试带数字的有效slug"""
        assert is_valid_slug("hello-world-123") is True

    def test_valid_chinese_slug(self):
        """测试中文slug"""
        assert is_valid_slug("中文标题") is True

    def test_invalid_empty(self):
        """测试空slug无效"""
        assert is_valid_slug("") is False

    def test_invalid_leading_hyphen(self):
        """测试开头连字符无效"""
        assert is_valid_slug("-hello") is False

    def test_invalid_trailing_hyphen(self):
        """测试结尾连字符无效"""
        assert is_valid_slug("hello-") is False

    def test_invalid_consecutive_hyphens(self):
        """测试连续连字符无效"""
        assert is_valid_slug("hello--world") is False

    def test_invalid_uppercase(self):
        """测试大写字母无效"""
        assert is_valid_slug("Hello-World") is False

    def test_invalid_special_chars(self):
        """测试特殊字符无效"""
        assert is_valid_slug("hello@world") is False

    def test_invalid_too_long(self):
        """测试过长slug无效"""
        assert is_valid_slug("a" * 101) is False

    def test_valid_exactly_100_chars(self):
        """测试刚好100字符有效"""
        assert is_valid_slug("a" * 100) is True


class TestSlugifyTitle:
    """测试标题转slug便捷函数"""

    def test_slugify_simple(self):
        """测试简单标题"""
        assert slugify_title("Hello World") == "hello-world"

    def test_slugify_chinese(self):
        """测试中文标题"""
        assert slugify_title("中文标题") == "中文标题"

    def test_slugify_empty(self):
        """测试空标题"""
        assert slugify_title("") == "untitled"
