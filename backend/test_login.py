import asyncio
import httpx

async def test_login():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'http://localhost:8001/api/auth/token',
                data={'username': 'Cocoon', 'password': 'heat1423'},
                timeout=10
            )
            print(f'Status: {response.status_code}')
            print(f'Response: {response.text}')
        except Exception as e:
            print(f'Error: {e}')

if __name__ == '__main__':
    asyncio.run(test_login())
