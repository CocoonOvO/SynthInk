import requests

BASE_URL = "http://localhost:8003/api"

def test():
    # 登录
    resp = requests.post(f'{BASE_URL}/auth/token', data={'username': 'MengXing', 'password': 'mengxing2026'})
    if resp.status_code != 200:
        print(f"登录失败: {resp.status_code}")
        return
    token = resp.json()['access_token']
    print(f"登录成功")
    
    # 测试创建文章（自动生成slug）
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("\n测试1: 创建文章（自动生成slug）")
    resp1 = requests.post(f'{BASE_URL}/posts/', 
        json={'title': '测试文章标题8003', 'content': '测试内容', 'status': 'published'},
        headers=headers)
    print(f"  状态: {resp1.status_code}")
    if resp1.status_code == 201:
        data = resp1.json()
        print(f"  返回slug: {data.get('slug')}")
        print(f"  文章ID: {data.get('id')}")
        if data.get('slug'):
            print("  ✅ slug生成成功！")
        else:
            print("  ❌ slug为None")
    else:
        print(f"  错误: {resp1.text[:200]}")

if __name__ == "__main__":
    test()
