# SynthSpark 运维文档

> **面向对象**: Agent运维人员
> **文档作用**: 关键运维操作指令
> **开发文档**: 查看 `${PROJECT_ROOT}/docs/` 目录

---

## 1. 关键端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 后端API | 8002 | 主业务接口 |
| MCP服务 | 8005 | Agent连接端口 |
| 前端开发 | 5173 | Vite开发服务器 |

---

## 2. 启动顺序

```bash
# 1. 启动后端API
cd ${PROJECT_ROOT}/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 2. 启动MCP服务（等待后端启动完成）
cd ${PROJECT_ROOT}/mcp
python server_optimized.py --api-url http://localhost:8002 --host 127.0.0.1 --port 8005

# 3. 启动前端（开发环境）
cd ${PROJECT_ROOT}/frontend
npm run dev

# 4. 启动Trae IDE（最后）
```

**⚠️ 注意**: Trae的MCP客户端只在初始化时连接一次，MCP重启后必须重启Trae才能重新连接。

---

## 3. 账号体系

### 3.1 两套独立账号

| 账号类型 | 数据库 | 表名 | 登录接口 |
|----------|--------|------|----------|
| 配置库超管 | SQLite (`config.db`) | `config_admins` | `/api/admin/login` |
| 项目管理员 | PostgreSQL (业务库) | `users` | `/api/auth/token` |

### 3.2 默认超管账号

- 用户名: `admin`
- 密码: `123456`（首次登录必须修改）

---

## 4. 关键配置

### 4.1 环境变量 (`backend/.env`)

```bash
SECRET_KEY=<随机字符串>          # 必填，生产环境必须修改
DEBUG_MODE=true|false            # 调试模式
SEO_ENABLED=true|false           # SEO功能开关
```

### 4.2 应用配置 (`backend/app/config.py`)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./synthink.db` | 数据库连接 |
| `UPLOAD_DIR` | `./uploads` | 上传文件目录 |
| `MAX_UPLOAD_SIZE` | `10485760` (10MB) | 最大上传大小 |

---

## 5. 数据库管理

### 5.1 配置库备份/恢复

```bash
# 备份
cp config.db config.db.backup.${DATE}

# 恢复
cp config.db.backup.${DATE} config.db
```

### 5.2 业务数据库切换

```bash
# 通过API切换数据库
curl -X POST http://localhost:8002/api/admin/databases/${db_id}/switch \
  -H "Authorization: Bearer ${TOKEN}"
```

### 5.3 常用SQL

```sql
-- 查看超管账号
SELECT id, username, is_active FROM config_admins;

-- 查看业务数据库表
SELECT table_name FROM information_schema.tables WHERE table_schema = '${SCHEMA}';
```

---

## 6. MCP服务

### 6.1 启动命令

```bash
cd ${PROJECT_ROOT}/mcp
python server_optimized.py \
  --api-url http://localhost:8002 \
  --host 127.0.0.1 \
  --port 8005
```

### 6.2 Trae配置

```json
{
  "mcpServers": {
    "synthink": {
      "url": "http://127.0.0.1:8005/sse"
    }
  }
}
```

---

## 7. 故障排查

| 问题 | 解决方案 |
|------|----------|
| 数据库连接失败 | 检查PostgreSQL服务状态，验证连接配置 |
| 配置库损坏 | 停止服务，删除/重命名 `config.db`，重启后重新配置 |
| 权限不足 (403) | 检查Token是否过期，确认用户角色权限 |
| MCP连接失败 | 确认启动顺序正确，重启Trae IDE |
| 前端API请求失败 | 检查Vite代理配置，确认后端端口正确 |

---

## 8. 相关文档

| 文档 | 路径 |
|------|------|
| 架构设计 | `docs/architecture.md` |
| API文档 | `docs/api.md` |
| 开发规范 | `docs/development.md` |
| 数据库设计 | `docs/database.md` |
| MCP服务 | `docs/mcp.md` |
| 安全规范 | `docs/security-guidelines.md` |
| SEO设计 | `docs/seo-design.md` |
| UI动效 | `docs/ui-effects.md` |

---

*最后更新: 2026-03-10*
