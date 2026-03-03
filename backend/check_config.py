"""检查配置库中的数据库配置"""
import asyncio
import os

os.environ["POSTGRES_DISABLE_SSL"] = "true"

from app.config_db import config_db_manager

async def check():
    await config_db_manager.initialize()
    
    # 获取数据库配置
    dsn = await config_db_manager.get_config("database_url")
    print(f"配置库中的DATABASE_URL: {dsn}")
    
    await config_db_manager.close()

if __name__ == "__main__":
    asyncio.run(check())
