"""
使用萌星账号运行阻塞的测试
"""
import requests
import json

BASE_URL = 'http://localhost:8002/api'
TOKEN = None

def login_mengxing():
    """使用萌星账号登录"""
    global TOKEN
    print('=== 使用萌星账号登录 ===')
    try:
        url = f'{BASE_URL}/auth/token'
        data = {
            'username': 'MengXing',
            'password': 'mengxing2026'
        }
        response = requests.post(url, data=data, timeout=10)
        print(f'状态码: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            TOKEN = result.get('access_token')
            print(f'登录成功！Token: {TOKEN[:30]}...')
            return True
        else:
            print(f'登录失败: {response.text}')
            return False
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_get_current_user():
    """测试获取当前用户"""
    print('\n=== 测试获取当前用户 (/auth/me) ===')
    try:
        url = f'{BASE_URL}/auth/me'
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(url, headers=headers, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_create_post():
    """测试创建文章"""
    print('\n=== 测试创建文章 (/posts) ===')
    try:
        url = f'{BASE_URL}/posts'
        headers = {'Authorization': f'Bearer {TOKEN}'}
        payload = {
            'title': '测试文章 - 萌星',
            'content': '这是使用萌星账号创建的测试文章',
            'status': 'draft'
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code in [200, 201]
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_create_comment():
    """测试创建评论"""
    print('\n=== 测试创建评论 ===')
    # 先获取一篇文章ID
    try:
        url = f'{BASE_URL}/posts?page_size=1'
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json().get('posts'):
            post_id = response.json()['posts'][0]['id']
            print(f'使用文章ID: {post_id}')
            
            # 创建评论
            url = f'{BASE_URL}/posts/{post_id}/comments'
            headers = {'Authorization': f'Bearer {TOKEN}'}
            payload = {
                'content': '这是使用萌星账号创建的测试评论'
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f'状态码: {response.status_code}')
            print(f'响应: {response.text}')
            return response.status_code in [200, 201]
        else:
            print('没有可用的文章')
            return False
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_like_post():
    """测试点赞文章"""
    print('\n=== 测试点赞文章 ===')
    try:
        # 先获取一篇文章ID
        url = f'{BASE_URL}/posts?page_size=1'
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json().get('posts'):
            post_id = response.json()['posts'][0]['id']
            print(f'使用文章ID: {post_id}')
            
            # 点赞
            url = f'{BASE_URL}/posts/{post_id}/like'
            headers = {'Authorization': f'Bearer {TOKEN}'}
            response = requests.post(url, headers=headers, timeout=10)
            print(f'状态码: {response.status_code}')
            print(f'响应: {response.text}')
            return response.status_code in [200, 201]
        else:
            print('没有可用的文章')
            return False
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_get_users_me():
    """测试获取当前用户信息 (/users/me)"""
    print('\n=== 测试获取当前用户信息 (/users/me) ===')
    try:
        url = f'{BASE_URL}/users/me'
        headers = {'Authorization': f'Bearer {TOKEN}'}
        response = requests.get(url, headers=headers, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def main():
    print('='*60)
    print('使用萌星账号运行阻塞测试')
    print('='*60)
    
    # 1. 登录获取Token
    if not login_mengxing():
        print('\n登录失败，无法继续测试')
        return
    
    results = []
    
    # 2. 测试获取当前用户 (/auth/me)
    results.append(('获取当前用户(/auth/me)', test_get_current_user()))
    
    # 3. 测试获取当前用户信息 (/users/me)
    results.append(('获取当前用户(/users/me)', test_get_users_me()))
    
    # 4. 测试创建文章
    results.append(('创建文章', test_create_post()))
    
    # 5. 测试创建评论
    results.append(('创建评论', test_create_comment()))
    
    # 6. 测试点赞
    results.append(('点赞文章', test_like_post()))
    
    # 汇总结果
    print('\n' + '='*60)
    print('测试结果汇总')
    print('='*60)
    for name, result in results:
        status = '✅ 通过' if result else '❌ 失败'
        print(f'{status}: {name}')
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f'\n总计: {passed}/{total} ({passed/total*100:.0f}%)')

if __name__ == '__main__':
    main()
