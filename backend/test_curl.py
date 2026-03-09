import requests
import json

BASE_URL = "http://localhost:8002/api"

def test():
    # 登录
    resp = requests.post(f'{BASE_URL}/auth/token', data={'username': 'MengXing', 'password': 'mengxing2026'})
    token = resp.json()['access_token']
    print(f"登录成功，token: {token[:20]}...")
    
    # 创建文章
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.post(f'{BASE_URL}/posts', 
        json={'title': '测试文章标题CURL', 'content': '测试内容', 'status': 'published'},
        headers=headers)
    print(f"创建文章状态: {resp.status_code}")
    data = resp.json()
    print(f"返回slug: {data.get('slug')}")
    print(f"文章ID: {data.get('id')}")

if __name__ == "__main__":
    test()
