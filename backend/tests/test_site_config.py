"""
站点配置接口测试

测试 /api/site-config（公开读取）与 /api/admin/site-config（超管读写）：
- 公开 GET：未配置返回 {}，已配置返回 dict，绝不 500
- 超管 PUT：鉴权（无 token 401 / 非超管 403）、空对象 400、超大 413、
  保存后读写往返一致
- manager 层：set/get 往返、未配置返回 None、存储类型为 json

依赖说明：
- 公开接口用例通过 http_client fixture（配置库指向临时文件），不依赖业务库
- 超管用例依赖业务库，无 TEST_DATABASE_URL 时按仓库惯例自动跳过
"""
import json
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.config_db import config_db_manager
from app.db_manager import db_manager


@pytest_asyncio.fixture
async def http_client(monkeypatch, tmp_path):
    """轻量 HTTP 客户端：全局配置库指向临时文件（不依赖业务库）"""
    db_path = tmp_path / "site_config_public.db"
    # 将全局单例的配置库路径指向临时文件，避免污染真实 config.db
    monkeypatch.setattr(config_db_manager, "db_path", Path(db_path))
    config_db_manager._initialized = False
    await config_db_manager.initialize()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 恢复全局单例状态：下次使用真实配置库时会重新初始化
    config_db_manager._initialized = False


@pytest_asyncio.fixture
async def isolated_config_db(monkeypatch, tmp_path):
    """将全局配置库指向临时文件（供依赖业务库的超管用例使用）"""
    db_path = tmp_path / "site_config_admin.db"
    monkeypatch.setattr(config_db_manager, "db_path", Path(db_path))
    config_db_manager._initialized = False
    await config_db_manager.initialize()

    yield

    config_db_manager._initialized = False


@pytest_asyncio.fixture
async def superuser_headers(client):
    """创建业务库超管认证头（自建独立超管用户，避免污染其他用例）

    register 接口本身需要超管权限（鸡生蛋问题），因此直接向业务库
    users 表插入超管用户，再通过登录接口换取令牌。
    """
    import uuid as uuid_mod

    from app.utils.security import get_password_hash

    username = f"site_cfg_{uuid_mod.uuid4().hex[:8]}"
    try:
        # 直接插入超管用户（仅测试环境使用）
        await db_manager.db.insert("users", {
            "id": str(uuid_mod.uuid4()),
            "username": username,
            "email": f"{username}@example.com",
            "hashed_password": get_password_hash("testpassword123"),
            "user_type": "user",
            "is_active": True,
            "is_superuser": True,
        })
    except Exception:
        pytest.skip("无法创建测试超管用户，数据库可能未配置")

    login = await client.post(
        "/api/auth/token",
        data={"username": username, "password": "testpassword123"}
    )
    if login.status_code != 200:
        pytest.skip("无法获取测试超管令牌，数据库可能未配置")
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


# ═══════════════ 配置库管理器层（不依赖业务库） ═══════════════

class TestSiteConfigManager:
    """站点配置存储（config.db 层）"""

    @pytest.mark.asyncio
    async def test_set_get_roundtrip(self, config_db_manager):
        """set/get 往返一致"""
        site_config = {
            "site_name": "我的博客",
            "navbar": [{"label": "首页", "url": "/"}],
            "footer": {"copyright": "© 2026"},
        }
        config_db_manager.set_site_config(site_config)
        saved = config_db_manager.get_site_config()
        assert saved == site_config

    @pytest.mark.asyncio
    async def test_get_unset_returns_none(self, config_db_manager):
        """未配置时返回 None"""
        assert config_db_manager.get_site_config() is None

    @pytest.mark.asyncio
    async def test_stored_as_json_type(self, config_db_manager):
        """存储为 system_configs key=site_config, value_type=json"""
        config_db_manager.set_site_config({"site_name": "测试"})
        row = config_db_manager.get_system_config("site_config")
        assert row is not None
        assert row.key == "site_config"
        assert row.value_type == "json"
        assert row.category == "site"
        assert row.is_editable is True
        assert row.is_secret is False


# ═══════════════ 公开读取接口（HTTP 层，不依赖业务库） ═══════════════

@pytest.mark.asyncio
async def test_public_get_unset_returns_empty(http_client):
    """公开 GET 未配置时返回 {}"""
    response = await http_client.get("/api/site-config")
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_public_get_returns_saved_dict(http_client):
    """公开 GET 返回已保存的配置 dict"""
    site_config = {"site_name": "测试站点", "navbar": []}
    config_db_manager.set_site_config(site_config)
    response = await http_client.get("/api/site-config")
    assert response.status_code == 200
    assert response.json() == site_config


@pytest.mark.asyncio
async def test_public_get_never_500(http_client, monkeypatch):
    """配置库异常时公开 GET 兜底返回 {}，绝不 500"""
    # 模拟配置库读取异常（指向无法创建/访问的路径，teardown 自动恢复）
    monkeypatch.setattr(
        config_db_manager, "db_path", Path("/nonexistent_dir_xyz/xx.db")
    )
    config_db_manager._initialized = False
    response = await http_client.get("/api/site-config")
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.asyncio
async def test_admin_get_requires_auth(http_client):
    """超管读取接口无 token 时返回 401"""
    response = await http_client.get("/api/admin/site-config")
    assert response.status_code == 401


# ═══════════════ 超管写接口（依赖业务库，无 TEST_DATABASE_URL 时跳过） ═══════════════

@pytest.mark.asyncio
async def test_put_requires_auth(client: AsyncClient):
    """PUT 无 token 返回 401"""
    response = await client.put(
        "/api/admin/site-config",
        json={"site_name": "测试"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_put_forbidden_for_normal_user(client, superuser_headers):
    """普通用户 PUT 返回 403（非超管拒绝）"""
    import uuid as uuid_mod

    from app.utils.security import get_password_hash

    # 自建普通用户（绕过 register 的超管限制）
    username = f"site_cfg_u_{uuid_mod.uuid4().hex[:8]}"
    try:
        await db_manager.db.insert("users", {
            "id": str(uuid_mod.uuid4()),
            "username": username,
            "email": f"{username}@example.com",
            "hashed_password": get_password_hash("testpassword123"),
            "user_type": "user",
            "is_active": True,
            "is_superuser": False,
        })
    except Exception:
        pytest.skip("无法创建测试用户，数据库可能未配置")

    login = await client.post(
        "/api/auth/token",
        data={"username": username, "password": "testpassword123"}
    )
    if login.status_code != 200:
        pytest.skip("无法获取测试用户令牌，数据库可能未配置")

    response = await client.put(
        "/api/admin/site-config",
        json={"site_name": "测试"},
        headers={"Authorization": f"Bearer {login.json()['access_token']}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_put_empty_object_rejected(client, superuser_headers):
    """空对象 body 返回 400"""
    response = await client.put(
        "/api/admin/site-config",
        json={},
        headers=superuser_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_put_non_dict_rejected(client, superuser_headers):
    """非 dict body（数组）被拒绝"""
    response = await client.put(
        "/api/admin/site-config",
        json=["not", "a", "dict"],
        headers=superuser_headers
    )
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_put_too_large_rejected(client, superuser_headers):
    """超过 100KB 的配置被拒绝（413）"""
    big_config = {"pad": "x" * (100 * 1024)}
    assert len(json.dumps(big_config).encode("utf-8")) > 100 * 1024
    response = await client.put(
        "/api/admin/site-config",
        json=big_config,
        headers=superuser_headers
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_put_and_read_roundtrip(client, superuser_headers, isolated_config_db):
    """超管保存后公开读取/超管读取往返一致"""
    site_config = {
        "site_name": "测试博客",
        "navbar": [{"label": "首页", "url": "/"}],
        "footer": {"copyright": "© 2026"},
        "home": {"title": "欢迎", "content": "你好，世界"},
    }
    response = await client.put(
        "/api/admin/site-config",
        json=site_config,
        headers=superuser_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "站点配置已保存"

    # 公开读取验证往返
    response = await client.get("/api/site-config")
    assert response.status_code == 200
    assert response.json() == site_config

    # 超管读取验证往返
    response = await client.get("/api/admin/site-config", headers=superuser_headers)
    assert response.status_code == 200
    assert response.json() == site_config

    # 审计日志：保存后应有一条 update 记录（独立审计表，业务用户 id 不受配置库外键约束）
    response = await client.get(
        "/api/admin/site-config/audit-logs",
        headers=superuser_headers
    )
    assert response.status_code == 200
    logs = response.json()["logs"]
    assert len(logs) == 1
    assert logs[0]["action"] == "update"
    # admin_username 为登录操作的业务库超管用户名（fixture 随机生成）
    assert logs[0]["admin_username"].startswith("site_cfg_")
    assert logs[0]["old_value"] is None
    assert logs[0]["new_value"]["site_name"] == "测试博客"

    # 再次保存：审计应追加第二条（old_value 为上一次保存值）
    site_config["site_name"] = "改后的博客"
    response = await client.put(
        "/api/admin/site-config",
        json=site_config,
        headers=superuser_headers
    )
    assert response.status_code == 200
    response = await client.get(
        "/api/admin/site-config/audit-logs",
        headers=superuser_headers
    )
    logs = response.json()["logs"]
    assert len(logs) == 2
    assert logs[0]["new_value"]["site_name"] == "改后的博客"
    assert logs[0]["old_value"]["site_name"] == "测试博客"
