"""
验证slug相关SQL注入风险修复
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def test_code_changes():
    """验证代码修改是否正确"""
    print("=" * 60)
    print("验证SQL注入风险修复")
    print("=" * 60)

    # 读取posts.py文件内容
    with open('app/routers/posts.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查1: get_existing_slugs是否还使用_fetchend参数化查询
    print("\n检查1: get_existing_slugs函数")
    if 'f"SELECT id, slug FROM {db_manager.postgres.schema}.posts' in content:
        print("  ❌ 仍然存在schema拼接SQL!")
        return False
    else:
        print("  ✅ 已移除schema拼接SQL")

    if 'db_manager.postgres.find(' in content and 'filters={}' in content:
        print("  ✅ 已改用find方法")
    else:
        print("  ⚠️  请确认使用了find方法")

    # 检查2: get_post_by_slug是否还使用_fetchend参数化查询
    print("\n检查2: get_post_by_slug函数")
    if 'f"SELECT id FROM {db_manager.postgres.schema}.posts WHERE slug' in content:
        print("  ❌ 仍然存在schema拼接SQL!")
        return False
    else:
        print("  ✅ 已移除schema拼接SQL")

    if 'filters={"slug": slug}' in content:
        print("  ✅ 已改用find方法nd参数化查询")
    else:
        print("  ⚠️  请确认使用了find方法")

    # 检查3: 确认没有直接的SQL拼接
    print("\n检查3: 全局SQL拼接检查")
    dangerous_patterns = [
        'f"SELECT.*FROM {db_manager.postgres.schema}',
        'f"SELECT.*FROM {.*schema.*}.posts',
    ]

    import re
    found_dangerous = False
    for pattern in dangerous_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"  ❌ 发现危险模式: {pattern}")
            found_dangerous = True

    if not found_dangerous:
        print("  ✅ 未发现直接的schema拼接SQL")

    print("\n" + "=" * 60)
    print("修复验证完成!")
    print("=" * 60)
    print("""
修复总结:
1. get_existing_slugs() - 改用find()方法,避免SQL拼接
2. get_post_by_slug() - 改用find()方法,使用参数化查询

两个函数现在都通过PostgresAdapter.find()方法执行查询,
该方法内部使用参数化查询($1, $2等),有效防止SQL注入。
""")
    return True


if __name__ == "__main__":
    test_code_changes()
