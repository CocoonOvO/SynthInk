"""
详细测试Bug
"""
import requests
from datetime import datetime

BASE_URL = 'http://localhost:8002/api'

def test_register_detail():
    """详细测试用户注册 - BUG-011"""
    print('=== 详细测试用户注册 (BUG-011) ===')
    try:
        url = f'{BASE_URL}/auth/register'
        timestamp = datetime.now().strftime('%H%M%S')
        payload = {
            'username': f'testuser_{timestamp}',
            'email': f'test{timestamp}@example.com',
            'password': 'TestPass123!'
        }
        print(f'请求URL: {url}')
        print(f'请求数据: {payload}')

        response = requests.post(url, json=payload, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应头: {dict(response.headers)}')
        print(f'响应内容: {response.text}')
        return response.status_code in [201, 200, 409]
    except Exception as e:
        print(f'异常: {type(e).__name__}: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_login_detail():
    """详细测试用户登录 - BUG-012"""
    print('\n=== 详细测试用户登录 (BUG-012) ===')
    try:
        url = f'{BASE_URL}/auth/token'
        data = {
            'username': 'admin',
            'password': 'admin123'
        }
        print(f'请求URL: {url}')
        print(f'请求数据: {data}')
        print(f'请求方式: POST (form-data)')

        response = requests.post(url, data=data, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应内容: {response.text}')
        return response.status_code == 200
    except Exception as e:
        print(f'异常: {type(e).__name__}: {str(e)}')
        return False

def test_like_detail():
    """详细测试点赞状态 - BUG-014"""
    print('\n=== 详细测试点赞状态 (BUG-014) ===')
    try:
        # 先尝试GET方法
        url = f'{BASE_URL}/likes/status?post_id=test-post-id'
        print(f'请求URL: {url}')
        print(f'请求方式: GET')

        response = requests.get(url, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应内容: {response.text}')

        # 再尝试POST方法
        print('\n尝试POST方法...')
        response2 = requests.post(url, timeout=10)
        print(f'POST状态码: {response2.status_code}')
        print(f'POST响应内容: {response2.text}')

        return response.status_code == 200
    except Exception as e:
        print(f'异常: {type(e).__name__}: {str(e)}')
        return False

if __name__ == '__main__':
    test_register_detail()
    test_login_detail()
    test_like_detail()
