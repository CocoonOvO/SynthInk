"""
测试点赞状态修复 - 使用正确的路由路径
"""
import requests

BASE_URL = 'http://localhost:8002/api'

def test_like_status():
    """测试点赞状态 - 使用正确的路由路径"""
    print('=== 测试点赞状态 (BUG-014) ===')

    post_id = 'test-post-id'

    # 正确的路径是 /{post_id}/status
    url = f'{BASE_URL}/likes/{post_id}/status'
    print(f'请求URL: {url}')
    print(f'请求方式: GET')

    response = requests.get(url, timeout=10)
    print(f'状态码: {response.status_code}')
    print(f'响应内容: {response.text}')

    if response.status_code == 200:
        print('✅ BUG-014 已修复!')
        return True
    else:
        print('❌ 仍然失败')
        return False

if __name__ == '__main__':
    success = test_like_status()
    print(f'\n最终结果: {"✅ 通过" if success else "❌ 失败"}')
