"""
测试配置库读取
"""
import asyncio
import sys
sys.path.insert(0, 'c:\\aip\\trae\\SynthInk\\backend')

from app.db_manager import db_manager

async def test_config():
    # 初始化配置库
    await db_manager.init_config_db("./config.db")

    # 读取数据库URL
    db_url = await db_manager.get_config("database_url")
    print(f"Database URL: {db_url}")

    # 读取schema
    schema = await db_manager.get_config("database_schema", "public")
    print(f"Schema: {schema}")

if __name__ == "__main__":
    asyncio.run(test_config())
