"""
更新配置库中的数据库URL
"""
import asyncio
import sys
sys.path.insert(0, 'c:\\aip\\trae\\SynthInk\\backend')

from app.db_manager import db_manager

async def update_config():
    # 初始化配置库
    await db_manager.init_config_db("./config.db")

    # 更新数据库URL为正确的连接信息
    await db_manager.set_config(
        "database_url",
        "postgresql://postgres:postgres@localhost:5432/synthink",
        "PostgreSQL数据库连接URL"
    )
    print("Database URL updated")

    # 验证更新
    db_url = await db_manager.get_config("database_url")
    print(f"New Database URL: {db_url}")

if __name__ == "__main__":
    asyncio.run(update_config())
