import requests
import json

# 登录获取token
login_url = 'http://localhost:8002/api/auth/token'
login_data = {'username': 'testuser123', 'password': 'testpass123'}

login_resp = requests.post(login_url, data=login_data)
token = login_resp.json()['access_token']

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 创建3篇测试文章
posts_url = 'http://localhost:8002/api/posts'

articles = [
    {
        'title': '测试文章1：智能体协作的魅力',
        'content': '这是一篇测试文章，介绍智能体如何协作创作。',
        'introduction': '智能体协作让创作更高效',
        'status': 'published'
    },
    {
        'title': '测试文章2：AI写作的未来',
        'content': '探讨AI在写作领域的应用前景。',
        'introduction': 'AI写作正在改变内容创作方式',
        'status': 'published'
    },
    {
        'title': '测试文章3：多智能体系统设计',
        'content': '如何设计一个高效的多智能体协作系统。',
        'introduction': '系统设计是智能体协作的基础',
        'status': 'published'
    }
]

for article in articles:
    resp = requests.post(posts_url, json=article, headers=headers)
    print(f"Created: {article['title']} - Status: {resp.status_code}")

print('测试文章创建完成！')
