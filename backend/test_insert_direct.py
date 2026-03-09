"""
直接测试insert语句
"""
import asyncio
import sys
sys.path.insert(0, 'c:\\aip\\trae\\SynthInk\\backend')

from app.db_manager import db_manager

async def test_insert():
    # 初始化配置库
    await db_manager.init_config_db("./config.db")
    
    # 初始化业务库
    await db_manager.init_biz_db()
    
    # 测试数据
    from uuid import uuid4
    user_data = {
        "id": str(uuid4()),
        "username": "testuser_direct",
        "email": "test_direct@example.com",
        "hashed_password": "hashed_password_here",
        "is_active": True,
        "is_superuser": False
    }
    
    print(f"Inserting user: {user_data['username']}")
    result = await db_manager.db.insert("users", user_data)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_insert())
