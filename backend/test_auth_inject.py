"""
认证接口测试和数据注入脚本
"""
import requests
import json

BASE_URL = 'http://localhost:8002/api'

def test_register():
    """测试用户注册"""
    print('=== 测试用户注册 ===')
    try:
        url = f'{BASE_URL}/auth/register'
        payload = {
            'username': 'testuser_auth_001',
            'email': 'testuser_auth_001@example.com',
            'password': 'TestPass123!'
        }
        response = requests.post(url, json=payload, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code, response.json() if response.status_code in [200, 201] else None
    except Exception as e:
        print(f'异常: {str(e)}')
        return 500, None

def test_login():
    """测试用户登录"""
    print('\n=== 测试用户登录 (/auth/token) ===')
    try:
        url = f'{BASE_URL}/auth/token'
        data = {
            'username': 'testuser_auth_001',
            'password': 'TestPass123!'
        }
        response = requests.post(url, data=data, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code, response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f'异常: {str(e)}')
        return 500, None

def test_get_current_user(token):
    """测试获取当前用户"""
    print('\n=== 测试获取当前用户 (/auth/me) ===')
    try:
        url = f'{BASE_URL}/auth/me'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers, timeout=10)
        print(f'状态码: {response.status_code}')
        print(f'响应: {response.text}')
        return response.status_code
    except Exception as e:
        print(f'异常: {str(e)}')
        return 500

def main():
    print('='*60)
    print('认证接口测试和数据注入')
    print('='*60)
    
    # 1. 测试注册
    reg_status, reg_data = test_register()
    
    # 2. 测试登录
    login_status, login_data = test_login()
    
    # 3. 测试获取当前用户（如果有token）
    if login_data and 'access_token' in login_data:
        token = login_data['access_token']
        test_get_current_user(token)
    else:
        print('\n跳过获取当前用户测试：没有获取到token')
    
    print('\n' + '='*60)
    print('测试完成')
    print('='*60)

if __name__ == '__main__':
    main()
