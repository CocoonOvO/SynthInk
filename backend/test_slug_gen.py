import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.slug import generate_slug

# 测试slug生成
existing = []
slug = generate_slug('测试文章标题', existing)
print(f'生成的slug: {slug}')
print(f'slug类型: {type(slug)}')
print(f'slug是否为空: {not slug}')
