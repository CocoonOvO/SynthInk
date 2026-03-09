"""直接测试数据库查询"""
import asyncio
import sys
sys.path.insert(0, 'c:/aip/trae/SynthInk/backend')

from app.db_manager import db_manager

async def test():
    # 初始化配置库
    await db_manager.init_config_db()
    
    # 初始化数据库
    await db_manager.init_biz_db()
    
    # 检查schema
    print(f'Adapter type: {type(db_manager.db).__name__}')
    # 注意：schema属性是具体适配器的实现细节，不应直接访问
    # 如需获取schema，应通过适配器提供的封装方法
    
    # 查询用户
    result = await db_manager.db.get_user_by_username('MengXing')
    print(f'Query result: {result}')
    
    # 检查密码
    if result.get('success') and result.get('data'):
        user = result['data']
        print(f"Username: {user['username']}")
        print(f"Hashed password: {user['hashed_password']}")
        
        # 验证密码
        from app.utils.security import verify_password
        is_valid = verify_password('mengxing2026', user['hashed_password'])
        print(f'Password valid: {is_valid}')

if __name__ == '__main__':
    asyncio.run(test())
