import requests

BASE_URL = "http://localhost:8002/api"

# 登录
resp = requests.post(f'{BASE_URL}/auth/token', data={'username': 'MengXing', 'password': 'mengxing2026'})
token = resp.json()['access_token']
print(f"登录成功")

# 测试带斜杠和不带斜杠的URL
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 不带斜杠
print("\n测试 /api/posts (不带斜杠):")
resp1 = requests.post(f'{BASE_URL}/posts', 
    json={'title': '测试1', 'content': '内容', 'status': 'published'},
    headers=headers, allow_redirects=False)
print(f"  状态: {resp1.status_code}")
print(f"  是否有重定向: {resp1.is_redirect}")
if resp1.is_redirect:
    print(f"  Location: {resp1.headers.get('Location')}")

# 带斜杠
print("\n测试 /api/posts/ (带斜杠):")
resp2 = requests.post(f'{BASE_URL}/posts/', 
    json={'title': '测试2', 'content': '内容', 'status': 'published'},
    headers=headers, allow_redirects=False)
print(f"  状态: {resp2.status_code}")
print(f"  返回slug: {resp2.json().get('slug') if resp2.status_code == 201 else 'N/A'}")
