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
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 测试1: 创建文章（自动生成slug）
    print("\n测试1: 创建文章（自动生成slug）")
    resp1 = requests.post(f'{BASE_URL}/posts/', 
        json={'title': 'Python教程', 'content': 'Python入门教程内容', 'status': 'published'},
        headers=headers)
    print(f"  状态: {resp1.status_code}")
    if resp1.status_code == 201:
        data = resp1.json()
        slug = data.get('slug')
        print(f"  返回slug: {slug}")
        print(f"  文章ID: {data.get('id')}")
        if slug:
            print("  ✅ slug生成成功！")
            
            # 测试2: 通过slug获取文章
            print(f"\n测试2: 通过slug获取文章")
            resp2 = requests.get(f'{BASE_URL}/posts/slug/{slug}')
            print(f"  状态: {resp2.status_code}")
            if resp2.status_code == 200:
                data2 = resp2.json()
                print(f"  文章标题: {data2.get('title')}")
                print(f"  文章slug: {data2.get('slug')}")
                print("  ✅ 通过slug获取文章成功！")
            else:
                print(f"  ❌ 错误: {resp2.text[:200]}")
        else:
            print("  ❌ slug为None")
    else:
        print(f"  错误: {resp1.text[:200]}")
    
    # 测试3: 创建文章（自定义slug）
    print("\n测试3: 创建文章（自定义slug）")
    resp3 = requests.post(f'{BASE_URL}/posts/', 
        json={'title': 'Vue3教程', 'content': 'Vue3入门教程内容', 'status': 'published', 'slug': 'vue3-tutorial'},
        headers=headers)
    print(f"  状态: {resp3.status_code}")
    if resp3.status_code == 201:
        data3 = resp3.json()
        print(f"  返回slug: {data3.get('slug')}")
        if data3.get('slug') == 'vue3-tutorial':
            print("  ✅ 自定义slug成功！")
        else:
            print("  ❌ 自定义slug不匹配")
    else:
        print(f"  错误: {resp3.text[:200]}")
    
    # 测试4: 重复slug检测
    print("\n测试4: 重复slug检测")
    resp4 = requests.post(f'{BASE_URL}/posts/', 
        json={'title': 'Vue3教程2', 'content': '内容', 'status': 'published', 'slug': 'vue3-tutorial'},
        headers=headers)
    print(f"  状态: {resp4.status_code}")
    if resp4.status_code == 400:
        print("  ✅ 重复slug检测成功！")
    else:
        print(f"  ❌ 应该返回400，但返回{resp4.status_code}")

if __name__ == "__main__":
    test()
