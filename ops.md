# SynthSpark 运维文档

> 面向Agent运维人员

---

## 1. 服务管理

### 1.1 端口

| 服务 | 端口 |
|------|------|
| 后端API | 8002 |
| MCP服务 | 8005 |
| 前端开发 | 5173 |

### 1.2 启动

```bash
# 依赖安装（uv 管理，首次或依赖变更后执行）
cd ${PROJECT_ROOT}/backend && uv sync --all-groups
cd ${PROJECT_ROOT}/mcp && uv sync

# 后端
cd ${PROJECT_ROOT}/backend
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# MCP
cd ${PROJECT_ROOT}/mcp
uv run python server_optimized.py --api-url http://localhost:8002 --host 127.0.0.1 --port 8005

# 前端
cd ${PROJECT_ROOT}/frontend
npm run dev
```

> 说明：`requirements.txt` / `requirements-dev.txt` 由 `uv export` 生成（兼容旧文档），日常增删依赖请修改 `pyproject.toml` 后 `uv sync` 并重新 export。

### 1.3 故障排查

| 问题 | 检查项 |
|------|--------|
| 数据库连接失败 | PostgreSQL服务状态、连接配置 |
| 配置库损坏 | 删除 `config.db` 后重启重新配置 |
| 权限不足 (403) | Token是否过期、用户角色 |
| MCP连接失败 | MCP服务状态、客户端配置 |
| 前端API请求失败 | Vite代理配置、后端端口 |

---

## 2. 账号与权限

### 2.1 账号体系

| 类型 | 数据库 | 表 | 登录接口 |
|------|--------|-----|----------|
| 配置库超管 | SQLite (`config.db`) | `config_admins` | `/api/admin/login` |
| 项目管理员 | PostgreSQL | `users` | `/api/auth/token` |

### 2.2 默认超管

- 用户名: `admin`
- 密码: `123456`（首次登录必须修改）

---

## 3. 配置管理

### 3.1 环境变量 (`backend/.env`)

```bash
SECRET_KEY=<随机字符串>          # 必填，生产环境必须修改
DEBUG_MODE=true|false
SEO_ENABLED=true|false
```

### 3.2 应用配置 (`backend/app/config.py`)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./synthink.db` | 数据库连接 |
| `UPLOAD_DIR` | `./uploads` | 上传目录(相对backend目录) |
| `MAX_UPLOAD_SIZE` | `10485760` (10MB) | 最大上传大小 |

**修改上传目录**:
```bash
# 方式1: 环境变量
UPLOAD_DIR=/path/to/uploads

# 方式2: 直接修改 config.py
UPLOAD_DIR = "/path/to/uploads"
```

### 3.3 前端环境变量 (`frontend/.env`)

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VITE_API_URL` | `http://localhost:8001` | API代理目标地址 |

**配置示例**:
```bash
# 复制示例文件
cp frontend/.env.example frontend/.env

# 修改API地址（如果后端端口不同）
echo "VITE_API_URL=http://localhost:8002" >> frontend/.env
```

### 3.4 站点文案 (`frontend/src/config/copywriting.json`)

| 配置键 | 说明 |
|--------|------|
| `home` | 首页文案 |
| `about` | 关于页文案 |
| `footer` | 页脚文案 |
| `navbar` | 导航栏文案 |

---

## 4. 数据库管理

### 4.1 备份/恢复

```bash
# 备份配置库
cp config.db config.db.backup.${DATE}

# 恢复配置库
cp config.db.backup.${DATE} config.db
```

### 4.2 切换业务数据库

```bash
curl -X POST http://localhost:8002/api/admin/databases/${db_id}/switch \
  -H "Authorization: Bearer ${TOKEN}"
```

### 4.3 常用SQL

```sql
-- 查看超管
SELECT id, username, is_active FROM config_admins;

-- 查看业务库表
SELECT table_name FROM information_schema.tables WHERE table_schema = '${SCHEMA}';
```

---

## 5. MCP服务

### 5.1 客户端配置

**SSE方式**:
```json
{
  "mcpServers": {
    "synthink": {
      "url": "http://127.0.0.1:8005/sse"
    }
  }
}
```

**stdio方式**:
```json
{
  "mcpServers": {
    "synthink": {
      "command": "python",
      "args": ["${PROJECT_ROOT}/mcp/server_optimized.py"],
      "env": {
        "SYNTHINK_API_URL": "http://localhost:8002"
      }
    }
  }
}
```

---

## 6. Agent Skill

| Skill | 位置 | 权限 | 用途 |
|-------|------|------|------|
| 普通用户Skill | `${PROJECT_ROOT}/SKILL.md` | 普通用户 | 文章/标签/分组管理 |
| 超管Skill | `${PROJECT_ROOT}/backend/app/skills/SKILL.md` | 超管 | 系统初始化/用户管理/审计 |

---

## 6.5 外链（工具页面）

- 页面：`/links`（导航「工具」），卡片网格展示外链（名称+配图），点击新窗口打开
- 接口：`GET /api/links`（公开）/ `POST|PUT|DELETE /api/links`（仅超管 `is_superuser`）
- 数据：业务库 `external_links` 表（sqlite/postgres 两方言均有定义），启动自动建表
- 管理入口：Profile 设置页「外链管理」tab（仅超管可见），支持名称/URL/配图（上传或填URL）
- 默认无外链，需超管自行添加

---

## 6.6 服务挂载框架

- 用途：挂载部署者自研的 FastAPI 服务（小工具/小游戏等），前缀 `/api/services/{name}`
- 框架代码：`backend/app/services/`（registry.py + examples/ + README.md），**全部入库**
- 服务实现：`backend/app/services/impl/`，**已被 gitignore**，部署者自行编写，不入库
- 契约：模块级变量 `name`（唯一ID，小写字母/数字/短横线）、`title`、`router`（APIRouter），可选 `static_dir`（UI目录，支持 API+UI 共存）
- 启动时自动发现：空目录正常返回、非法模块跳过并输出 `[服务挂载]` 中文警告日志
- 规范文档：`backend/app/services/README.md`；模板：`backend/app/services/examples/hello_service.py`
- 新增/修改服务后重启后端生效；服务 URL 可由外链页配置展示

---

## 7. 日志与文件

### 7.1 日志

项目目前使用控制台输出，无持久化日志文件。

**查看实时日志**:
```bash
# 后端日志(启动时可见)
cd ${PROJECT_ROOT}/backend
python -m uvicorn app.main:app --port 8002 2>&1
```

**关键输出**:
- 默认超管创建警告
- 数据库连接信息

### 7.2 上传文件

| 路径 | 说明 |
|------|------|
| `${PROJECT_ROOT}/backend/uploads/` | 默认上传目录 |
| `${PROJECT_ROOT}/backend/config.db` | SQLite配置库 |

---

## 8. 生产环境部署

### 8.1 Nginx反向代理配置

项目前后端分离部署时，建议使用Nginx作为反向代理。Nginx负责：
- 托管前端编译产物（静态文件）
- 反向代理API请求到后端服务
- 处理HTTPS（可选）

**Nginx配置示例**：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为实际域名或IP
    
    # 前端静态文件
    location / {
        root /path/to/synthink/frontend/dist;  # 替换为实际dist目录路径
        try_files $uri $uri/ /index.html;  # Vue Router SPA回退
    }
    
    # API反向代理
    location /api {
        proxy_pass http://127.0.0.1:8002;  # 后端服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 上传文件访问
    location /uploads {
        alias /path/to/synthink/backend/uploads;  # 后端上传目录
        expires 30d;
    }
}
```

**关键说明**：
- `root` 和 `alias` 路径需要根据实际部署位置修改
- `/api` 代理到后端FastAPI服务
- `try_files $uri $uri/ /index.html` 确保Vue Router路由正常工作
- 上传文件通过 `/uploads` 路径访问

### 8.2 部署检查清单

| 检查项 | 说明 |
|--------|------|
| 前端已编译 | `cd frontend && npm run build`，产物在 `dist/` |
| 后端依赖已安装 | `cd backend && pip install -r requirements.txt` |
| 数据库已初始化 | PostgreSQL数据库已创建并可连接 |
| `.env` 已配置 | `SECRET_KEY`、`DATABASE_URL` 等 |
| 防火墙已开放 | 80端口（HTTP）或443端口（HTTPS） |

### 8.3 HTTPS配置（可选）

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... location配置同上
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

*最后更新: 2026-08-06*
