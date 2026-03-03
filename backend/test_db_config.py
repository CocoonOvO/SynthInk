import requests

# 登录获取token
resp = requests.post('http://localhost:8001/api/admin/login', json={'username': 'admin', 'password': '123456'})
token = resp.json()['access_token']
print(f'Token: {token[:50]}...')

# 配置数据库
headers = {'Authorization': f'Bearer {token}'}
data = {
    'name': 'default',
    'db_type': 'postgresql',
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'username': 'postgres',
    'password': 'heat1423',
    'is_active': True
}

resp = requests.post('http://localhost:8001/api/admin/database', json=data, headers=headers)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.text}')
