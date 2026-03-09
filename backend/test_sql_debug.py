"""
SQL调试脚本 - 测试insert语句
"""
import asyncio
import asyncpg
from datetime import datetime
from uuid import uuid4

async def test_insert():
    dsn = "postgresql://postgres:postgres@localhost:5432/synthink"
    schema = "public"
    
    conn = await asyncpg.connect(dsn)
    
    try:
        # 测试数据
        user_data = {
            "id": str(uuid4()),
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "email": f"test{datetime.now().strftime('%H%M%S')}@example.com",
            "hashed_password": "hashed_password_here",
            "is_active": True,
            "is_superuser": False
        }
        
        columns = list(user_data.keys())
        placeholders = [f"${i+1}" for i in range(len(columns))]
        values = list(user_data.values())
        
        query = f"""
            INSERT INTO {schema}.users ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        print(f"SQL Query:\n{query}")
        print(f"\nValues: {values}")
        
        row = await conn.fetchrow(query, *values)
        print(f"\nResult: {dict(row)}")
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_insert())
