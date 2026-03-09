import requests

# 登录
resp = requests.post('http://localhost:8002/api/auth/token', data={'username': 'MengXing', 'password': 'mengxing2026'})
token = resp.json()['access_token']

# 创建文章
headers = {'Authorization': f'Bearer {token}'}
resp = requests.post('http://localhost:8002/api/posts', json={
    'title': '测试文章标题',
    'content': '测试内容',
    'status': 'published'
}, headers=headers)
print(f'状态: {resp.status_code}')
data = resp.json()
print(f"返回: {data}")
print(f"slug: {data.get('slug')}")
