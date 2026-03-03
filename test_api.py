#!/usr/bin/env python3
"""
测试后端API是否正常工作
"""
import urllib.request
import urllib.parse
import json
import ssl

# 禁用SSL验证（开发环境）
ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "http://localhost:8000"

def test_root():
    """测试根路径"""
    try:
        req = urllib.request.Request(f"{BASE_URL}/")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"根路径状态: {response.status}")
            data = response.read().decode('utf-8')
            print(f"响应类型: {'HTML' if '<html' in data.lower() else 'JSON/API'}")
            return True
    except Exception as e:
        print(f"根路径测试失败: {e}")
        return False

def test_openapi():
    """测试OpenAPI文档"""
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/openapi.json")
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"OpenAPI状态: {response.status}")
            raw_data = response.read()
            print(f"原始数据长度: {len(raw_data)} bytes")
            if len(raw_data) > 0:
                data = json.loads(raw_data.decode('utf-8'))
                print(f"API标题: {data.get('info', {}).get('title', 'N/A')}")
                print(f"API版本: {data.get('info', {}).get('version', 'N/A')}")
                paths = list(data.get('paths', {}).keys())[:5]
                print(f"部分API路径: {paths}")
                return True
            else:
                print("OpenAPI返回空内容")
                return False
    except Exception as e:
        print(f"OpenAPI测试失败: {e}")
        return False

def login_admin():
    """登录管理员账号 - 使用表单格式"""
    try:
        # 准备表单数据 - 必须严格使用OAuth2格式
        form_data = {
            'grant_type': 'password',
            'username': 'admin',
            'password': 'admin123',
            'scope': '',
            'client_id': '',
            'client_secret': ''
        }
        
        data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        req = urllib.request.Request(
            f"{BASE_URL}/api/auth/token",
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"登录状态: {response.status}")
            result = json.loads(response.read().decode('utf-8'))
            print(f"登录成功!")
            print(f"Token类型: {result.get('token_type', 'N/A')}")
            token = result.get('access_token', 'N/A')
            if len(token) > 50:
                print(f"Token: {token[:50]}...")
            else:
                print(f"Token: {token}")
            return token
    except urllib.error.HTTPError as e:
        print(f"登录失败: HTTP {e.code}")
        error_body = e.read().decode('utf-8')
        print(f"错误信息: {error_body}")
        return None
    except Exception as e:
        print(f"登录异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_user_info(token):
    """获取用户信息"""
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/users/me",
            headers={
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"获取用户信息状态: {response.status}")
            result = json.loads(response.read().decode('utf-8'))
            print(f"用户信息:")
            print(f"  用户名: {result.get('username', 'N/A')}")
            print(f"  邮箱: {result.get('email', 'N/A')}")
            print(f"  超级用户: {result.get('is_superuser', False)}")
            print(f"  激活状态: {result.get('is_active', False)}")
            return True
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return False

def list_routes():
    """列出所有API路由"""
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/openapi.json")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            paths = data.get('paths', {})
            print(f"\n可用API端点 ({len(paths)} 个):")
            print("-" * 60)
            for path, methods in sorted(paths.items()):
                for method, info in methods.items():
                    if method != 'parameters':
                        summary = info.get('summary', 'N/A')
                        print(f"  {method.upper():6} {path:30} - {summary}")
            return True
    except Exception as e:
        print(f"获取路由列表失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  SynthInk API 测试与管理员登录")
    print("=" * 60)
    
    print("\n【1】测试根路径...")
    test_root()
    
    print("\n【2】测试OpenAPI文档...")
    test_openapi()
    
    print("\n【3】列出所有API端点...")
    list_routes()
    
    print("\n【4】登录管理员账号...")
    print("   账号: admin")
    print("   密码: admin123")
    token = login_admin()
    
    if token:
        print("\n【5】获取用户信息...")
        get_user_info(token)
        
        print("\n" + "=" * 60)
        print("  ✅ 登录成功！管理员Token已获取")
        print("=" * 60)
        print(f"\n完整Token (用于测试):")
        print(f"{token}")
    else:
        print("\n" + "=" * 60)
        print("  ❌ 登录失败")
        print("=" * 60)
