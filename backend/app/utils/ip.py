"""
客户端 IP 获取工具

统一各路由的 IP 获取逻辑（原先 admin.py 与 likes.py 各有一份实现），
供评论/点赞等需要 IP 落库与限流的接口复用。
"""
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端IP地址

    优先级：X-Forwarded-For（代理环境取第一个）> X-Real-IP > 直接连接 IP，
    取不到时返回 "unknown"，保证后续落库/限流不因缺 IP 而报错。

    Args:
        request: FastAPI请求对象

    Returns:
        IP地址字符串
    """
    # 代理环境下优先使用 X-Forwarded-For（取第一个真实客户端IP）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    # Nginx 反向代理常用的 X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 直接从连接获取
    if request.client:
        return request.client.host

    return "unknown"
