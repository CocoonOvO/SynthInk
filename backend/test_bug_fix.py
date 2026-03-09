"""
Bug修复测试脚本
测试BUG-011到BUG-014
"""
import requests
from datetime import datetime

BASE_URL = 'http://localhost:8002/api'

def test_register():
    """测试用户注册 - BUG-011"""
    print('--- 测试用户注册 (BUG-011) ---')
    try:
        url = f'{BASE_URL}/auth/register'
        timestamp = datetime.now().strftime('%H%M%S')
        payload = {
            'username': f'testuser_{timestamp}',
            'email': f'test{timestamp}@example.com',
            'password': 'TestPass123!'
        }
        response = requests.post(url, json=payload, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text[:500]}')
        return response.status_code in [201, 200, 409]
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_login():
    """测试用户登录 - BUG-012"""
    print('\n--- 测试用户登录 (BUG-012) ---')
    try:
        url = f'{BASE_URL}/auth/token'
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = requests.post(url, data=data, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text[:500]}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_comments_list():
    """测试评论列表 - BUG-013"""
    print('\n--- 测试评论列表 (BUG-013) ---')
    try:
        url = f'{BASE_URL}/comments/?post_id=test-post-id'
        response = requests.get(url, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text[:500]}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

def test_like_status():
    """测试点赞状态 - BUG-014"""
    print('\n--- 测试点赞状态 (BUG-014) ---')
    try:
        url = f'{BASE_URL}/likes/status?post_id=test-post-id'
        response = requests.get(url, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text[:500]}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {str(e)}')
        return False

if __name__ == '__main__':
    print('='*60)
    print('Bug修复验证测试')
    print('='*60)

    results = {
        'BUG-011 (注册)': test_register(),
        'BUG-012 (登录)': test_login(),
        'BUG-013 (评论列表)': test_comments_list(),
        'BUG-014 (点赞状态)': test_like_status(),
    }

    print('\n' + '='*60)
    print('测试结果汇总')
    print('='*60)
    for bug, passed in results.items():
        status = '✅ 通过' if passed else '❌ 失败'
        print(f'{bug}: {status}')
