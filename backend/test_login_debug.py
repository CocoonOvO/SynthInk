"""调试登录问题"""
import requests
import sys
sys.path.insert(0, 'c:/aip/trae/SynthInk/backend')

BASE_URL = 'http://localhost:8002/api'

# 测试登录
print('=== 测试登录 ===')
url = f'{BASE_URL}/auth/token'
data = {
    'username': 'MengXing',
    'password': 'mengxing2026'
}

# 使用form-data格式
response = requests.post(url, data=data, timeout=10)
print(f'状态码: {response.status_code}')
print(f'响应: {response.text}')

# 也测试一下Cocoon
print('\n=== 测试Cocoon登录 ===')
data2 = {
    'username': 'Cocoon',
    'password': 'heat1423'
}
response2 = requests.post(url, data=data2, timeout=10)
print(f'状态码: {response2.status_code}')
print(f'响应: {response2.text}')

# 测试刚注册的用户
print('\n=== 测试刚注册的用户 ===')
data3 = {
    'username': 'testuser_0305175112',
    'password': 'TestPass123!'
}
response3 = requests.post(url, data=data3, timeout=10)
print(f'状态码: {response3.status_code}')
print(f'响应: {response3.text}')
