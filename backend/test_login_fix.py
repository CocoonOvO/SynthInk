"""
测试登录修复 - 使用正确的用户凭据
"""
import requests
from datetime import datetime

BASE_URL = 'http://localhost:8002/api'

def test_register_and_login():
    """测试注册后立即登录"""
    print('=== 测试注册和登录流程 ===')

    # 1. 注册用户
    timestamp = datetime.now().strftime('%H%M%S')
    username = f'testuser_{timestamp}'
    password = 'TestPass123!'

    print(f'\n1. 注册用户: {username}')
    register_url = f'{BASE_URL}/auth/register'
    payload = {
        'username': username,
        'email': f'test{timestamp}@example.com',
        'password': password
    }
    response = requests.post(register_url, json=payload, timeout=10)
    print(f'注册状态码: {response.status_code}')

    if response.status_code not in [201, 200]:
        print(f'注册失败: {response.text}')
        return False

    print('注册成功!')

    # 2. 使用刚注册的用户登录
    print(f'\n2. 登录用户: {username}')
    login_url = f'{BASE_URL}/auth/token'
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(login_url, data=data, timeout=10)
    print(f'登录状态码: {response.status_code}')
    print(f'登录响应: {response.text}')

    if response.status_code == 200:
        print('登录成功! BUG-012 已修复!')
        return True
    else:
        print('登录失败!')
        return False

if __name__ == '__main__':
    success = test_register_and_login()
    print(f'\n最终结果: {"✅ 通过" if success else "❌ 失败"}')
