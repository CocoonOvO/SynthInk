# SynthInk 运维文档

> 面向运维Agent的参考文档，记录项目真实存在的功能和开发过程中使用的操作。

---

## 🤖 【必读】多Agent协作指南

> **本节作用**: 指导多个Agent如何协同工作，共享信息，避免冲突。

### Agent备忘录 (agent_memo.md)

**文件位置**: `${PROJECT_ROOT}/agent_memo.md`

**作用**: 
- 多Agent共享任务进度和状态
- 记录当前谁在处理什么
- 避免多个Agent同时修改同一文件造成冲突

**使用规范**:
1. **开始工作前**: 必须阅读agent_memo.md，了解当前任务分配
2. **记录身份**: 所有记录必须标注Agent名称
3. **及时更新**: 状态变更后10分钟内更新备忘录
4. **只追加不删除**: 保留历史记录，便于追溯

**记录格式**:
```markdown
### [日期] 任务: [任务名]
- **负责人**: [Agent名]
- **状态**: pending / in_progress / completed / blocked
- **描述**: [简要说明]
```

**当前已接入Agent**:
| Agent | 角色 | 状态 |
|-------|------|------|
| 萌星 | 女仆长/统筹 | 活跃 |

---

## ⚠️ 【重要】Agent直接管理项目后台指南

> **本节内容作用**: 指导Agent如何直接管理项目后台，包括配置库管理、超管账号管理等核心功能。

### 配置库与配置表

**配置库位置**: `${PROJECT_ROOT}/backend/config.db`

**核心表结构**:
- `config_admins` - 配置库超管账号表
- `database_configs` - 业务数据库配置表
- `system_configs` - 系统配置表
- `config_audit_logs` - 审计日志表

**Agent操作建议**:
- 在得到用户明确命令或许可后，Agent可以直接连接配置库进行编辑
- 配置库使用SQLite，可直接通过SQL操作
- 修改配置后，建议记录审计日志（如可能）

### 配置库超管账号管理

**重要说明**: 项目不提供通过API接口管理配置库超管账号的功能。

**Agent管理方案**:
- Agent应当通过**直接编辑配置库**的方式管理超管账号
- 超管表: `config_admins`
- 密码使用SHA256+Salt哈希存储（参考`backend/app/utils/security.py`中的`get_password_hash`函数）

**操作示例**:
```sql
-- 查看超管账号
SELECT id, username, is_active, created_at FROM config_admins;

-- 修改超管密码（需先计算哈希）
UPDATE config_admins SET password_hash = '${HASH}' WHERE username = '${USERNAME}';
```

## 🔐 账号体系说明（重要：两种完全不同的管理员）

> **警告**: 本项目存在**两套完全独立**的账号体系，切勿混淆！

### 一、配置库超管（Config Admin）

| 属性 | 说明 |
|------|------|
| **存储位置** | SQLite `config.db` → `config_admins` 表 |
| **作用** | 管理配置库本身：数据库连接配置、系统配置、查看审计日志 |
| **登录接口** | `POST /api/admin/login` |
| **Token标识** | `type: config_admin` |
| **访问接口** | `/api/admin/*` 下的所有接口 |
| **管理方式** | **项目不提供API管理**，Agent直接编辑SQLite数据库 |

**当前配置库超管账号**:
```sql
-- 查询配置库超管
SELECT id, username, is_active, created_at, last_login_at 
FROM config_admins;
```
| ID | 用户名 | 状态 | 创建时间 | 最后登录 |
|----|--------|------|----------|----------|
| 1 | `admin` | 激活 | 2026-03-01 | 2026-03-02 |

**默认密码**: `123456`（首次登录后应立即修改）

---

### 二、项目管理员（Project Admin / 超管用户）

| 属性 | 说明 |
|------|------|
| **存储位置** | PostgreSQL业务库 → `users` 表 |
| **作用** | 管理业务数据：用户、文章、标签、分组、审核内容 |
| **登录接口** | `POST /api/auth/token` |
| **Token标识** | 普通JWT Token（无特殊type） |
| **访问接口** | `/api/users/*`, `/api/posts/*` 等需要登录的接口 |
| **管理方式** | 通过 `is_superuser = true` 字段标识 |

**创建项目超管的方法**:
项目**不提供**创建项目超管的API接口，Agent需要：
1. 连接PostgreSQL业务数据库
2. 直接执行SQL插入超管记录
3. 密码使用SHA256+Salt哈希（参考`backend/app/utils/security.py`）

```sql
-- 创建项目超管
INSERT INTO users (
    username, 
    email, 
    hashed_password,  -- SHA256+Salt哈希
    is_active, 
    is_superuser,     -- 必须设为true
    user_type
) VALUES (
    '${USERNAME}', 
    '${EMAIL}', 
    '${HASHED_PASSWORD}', 
    true, 
    true, 
    'user'
);
```

---

### 三、关键对比表

| 对比项 | 配置库超管 | 项目管理员 |
|--------|-----------|-----------|
| **数据库** | SQLite (config.db) | PostgreSQL (业务库) |
| **表名** | `config_admins` | `users` |
| **管理对象** | 系统配置、数据库连接 | 用户、文章、业务数据 |
| **登录接口** | `/api/admin/login` | `/api/auth/token` |
| **谁创建** | 初始化脚本 / Agent直接编辑 | Agent直接插入数据库 |
| **密码字段** | `password_hash` | `hashed_password` |
| **超管标识** | 无（该表只有超管） | `is_superuser = true` |

---

### 四、常见错误

❌ **错误**: "用超管账号登录Swagger"
- 问题：没说明是哪种超管
- 解决：明确说"配置库超管"或"项目管理员"

❌ **错误**: "创建超管账号"
- 问题：不知道要创建哪种
- 解决：先问清楚用户需要哪种超管

❌ **错误**: 用配置库超管Token去调项目接口
- 问题：Token类型不匹配，会返回401
- 解决：配置库超管只能调 `/api/admin/*` 接口

---

## 1. 项目架构

### 1.1 技术栈

- **后端**: FastAPI + Python 3.9+
- **前端**: Vue3 (待实现)
- **配置库**: SQLite (config.db)
- **业务库**: PostgreSQL 13+

### 1.2 核心组件

| 组件 | 路径 | 说明 |
|------|------|------|
| 配置库管理 | `backend/app/config_db/` | SQLite配置库，存储系统配置、数据库连接、超管账号 |
| 数据库适配器 | `backend/app/adapter/` | 适配器模式，支持PostgreSQL/SQLite |
| 数据库初始化器 | `backend/app/db_initializer.py` | 检查/创建数据库和表结构 |
| API路由 | `backend/app/routers/` | FastAPI路由，包含admin/auth/users/posts/tags/groups/upload/mcp |
| MCP服务 | `backend/app/mcp/` | MCP服务集成模块，提供Agent接口 |

### 1.3 数据库架构

```
SQLite (config.db)
├── config_admins          # 超管账号
├── database_configs       # 业务数据库配置
├── system_configs         # 系统配置
└── config_audit_logs      # 审计日志

PostgreSQL (业务数据库)
├── users                  # 用户表
├── posts                  # 文章表
├── tags                   # 标签表
├── groups                 # 分组表
└── post_tags              # 文章标签关联表
```

---

## 2. 开发规范

### 2.1 代码规范

- **文档字符串**: Google风格，所有模块/类/函数必须添加
- **类型注解**: 100%覆盖率
- **API注释**: OpenAPI规范，包含summary/description/responses
- **异常处理**: 使用`handle_exception()`统一处理，区分debug/production模式

### 2.2 接口鉴权

| 接口类型 | 鉴权方式 | 示例 |
|----------|----------|------|
| 公开接口 | 无需认证 | `POST /api/admin/login` |
| 用户接口 | JWT Token | `GET /api/users/me` |
| 超管接口 | 超管Token | `POST /api/admin/database` |
| MCP接口 | 超管Token | `POST /api/mcp/tools/configure_database` |

### 2.3 环境变量

```bash
# 必需
SECRET_KEY=<随机字符串>
DEBUG_MODE=true|false

# 可选
APP_NAME=SynthInk
VERSION=0.1.0
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=["http://localhost:5173"]
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
SYNTHINK_API_URL=http://localhost:8001  # MCP服务使用的后端地址

# 限流配置 (slowapi格式: "次数/时间单位")
RATE_LIMIT_LOGIN=5/minute        # 登录接口限流
RATE_LIMIT_REGISTER=3/minute     # 注册接口限流
RATE_LIMIT_DEFAULT=100/minute    # 默认全局限流
```

---

## 3. 部署运行

### 3.1 环境要求

- Python 3.9+
- PostgreSQL 13+
- pip

### 3.2 启动命令

```bash
cd ${PROJECT_ROOT}/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host ${HOST} --port ${PORT} --reload
```

变量说明:
- `${PROJECT_ROOT}`: 项目根目录路径
- `${HOST}`: 监听地址，如 `0.0.0.0`
- `${PORT}`: 监听端口，如 `8000`

### 3.3 配置流程

首次启动后，通过API配置业务数据库:

1. 使用默认超管登录获取Token
   - 用户名: `admin`
   - 密码: `123456`

2. 调用初始化向导完成数据库配置
   - 接口: `POST /api/admin/init-wizard/complete`
   - 参数: 数据库连接信息

---

## 4. 数据库管理

### 4.1 配置库 (SQLite)

文件位置: `${PROJECT_ROOT}/backend/config.db`

**备份**:
```bash
cp config.db config.db.backup.${DATE}
```

**恢复**:
```bash
cp config.db.backup.${DATE} config.db
```

### 4.2 业务库 (PostgreSQL)

**切换数据库**:
- 接口: `POST /api/admin/database/switch`
- 效果: 切换到新的数据库和schema，自动创建并初始化

**初始化表结构**:
- 接口: `POST /api/admin/database/init`
- 效果: 检查并创建缺失的表

**查看状态**:
- 接口: `GET /api/admin/database/init-status`
- 返回: 数据库存在性、schema存在性、各表状态

---

## 5. MCP服务

### 5.1 概述

MCP服务集成在FastAPI后端中，提供Agent友好的接口。

**MCP端点**: `/api/mcp/tools/*`
**MCP文档**: `/api/mcp/docs`

### 5.2 已实现的MCP工具

| 工具 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| admin_login | `POST /api/mcp/tools/admin_login` | 超管登录 | 否 |
| admin_logout | `POST /api/mcp/tools/admin_logout` | 超管登出 | 是 |
| setup_status | `GET /api/mcp/tools/setup_status` | 系统设置状态 | 否 |
| database_status | `GET /api/mcp/tools/database_status` | 数据库配置 | 是 |
| configure_database | `POST /api/mcp/tools/configure_database` | 配置数据库 | 是 |
| switch_database | `POST /api/mcp/tools/switch_database` | 切换数据库 | 是 |
| test_connection | `POST /api/mcp/tools/test_connection` | 测试连接 | 否 |
| init_status | `GET /api/mcp/tools/init_status` | 初始化状态 | 是 |
| init_database | `POST /api/mcp/tools/init_database` | 初始化数据库 | 是 |
| complete_init_wizard | `POST /api/mcp/tools/complete_init_wizard` | 初始化向导 | 是 |
| system_configs | `GET /api/mcp/tools/system_configs` | 系统配置列表 | 是 |
| system_config | `GET /api/mcp/tools/system_config/{key}` | 单个配置 | 是 |
| update_system_config | `PUT /api/mcp/tools/system_config/{key}` | 更新配置 | 是 |
| audit_logs | `GET /api/mcp/tools/audit_logs` | 审计日志 | 是 |

### 5.3 独立MCP服务

项目同时提供独立的MCP服务 (`mcp/` 目录):

**启动**:
```bash
cd ${PROJECT_ROOT}/mcp
pip install -r requirements.txt
python start_server.py
```

**配置**:
- 环境变量: `SYNTHINK_API_URL` - 后端API地址
- 传输方式: stdio

---

## 6. 开发操作记录

### 6.1 后端开发

**启动开发服务器**:
```bash
cd ${PROJECT_ROOT}/backend
python -m uvicorn app.main:app --reload
```

**运行测试**:
```bash
cd ${PROJECT_ROOT}/backend
pytest
```

**删除配置库重新初始化**:
```bash
rm ${PROJECT_ROOT}/backend/config.db
# 重启服务后自动重新初始化
```

### 6.2 数据库操作

**连接PostgreSQL**:
```bash
psql postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${DATABASE}
```

**查看数据库列表**:
```sql
SELECT datname FROM pg_database;
```

**查看schema列表**:
```sql
SELECT schema_name FROM information_schema.schemata;
```

**查看表列表**:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = '${SCHEMA}';
```

### 6.3 API接口清单

#### 认证接口 (/api/auth)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 公开 |
| POST | /api/auth/token | 用户登录 | 公开 |
| POST | /api/auth/refresh | 刷新Token | 公开 |
| POST | /api/auth/logout | 用户登出 | 需登录 |
| POST | /api/auth/password/reset | 修改密码 | 需登录 |

#### 用户接口 (/api/users)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| GET | /api/users/me | 获取当前用户 | 需登录 |
| PUT | /api/users/me | 更新当前用户 | 需登录 |
| GET | /api/users/{id} | 获取指定用户 | 需登录 |
| GET | /api/users | 获取用户列表 | 超管 |

#### 文章接口 (/api/posts)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/posts | 创建文章 | 需登录 |
| GET | /api/posts | 获取文章列表 | 公开 |
| GET | /api/posts/{id} | 获取文章详情 | 公开 |
| PUT | /api/posts/{id} | 更新文章 | 作者/超管 |
| DELETE | /api/posts/{id} | 删除文章 | 作者/超管 |
| POST | /api/posts/{id}/publish | 发布文章 | 作者/超管 |

#### 标签接口 (/api/tags)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/tags | 创建标签 | 超管 |
| GET | /api/tags | 获取标签列表 | 公开 |
| GET | /api/tags/{id} | 获取标签详情 | 公开 |
| PUT | /api/tags/{id} | 更新标签 | 超管 |
| DELETE | /api/tags/{id} | 删除标签 | 超管 |

#### 分组接口 (/api/groups)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/groups | 创建分组 | 超管 |
| GET | /api/groups | 获取分组列表 | 公开 |
| GET | /api/groups/{id} | 获取分组详情 | 公开 |
| PUT | /api/groups/{id} | 更新分组 | 超管 |
| DELETE | /api/groups/{id} | 删除分组 | 超管 |

#### 上传接口 (/api/upload)
| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/upload/image | 上传图片 | 需登录 |
| POST | /api/upload/avatar | 上传头像 | 需登录 |
| POST | /api/upload/attachment | 上传附件 | 需登录 |

### 6.4 故障排查

**数据库连接失败**:
1. 检查PostgreSQL服务状态
2. 验证连接配置 (host/port/username/password)
3. 查看应用日志中的详细错误

**配置库损坏**:
1. 停止服务
2. 删除/重命名 `config.db`
3. 重启服务，重新配置

**权限不足 (403)**:
1. 检查Token是否过期
2. 确认用户角色权限
3. 确认接口鉴权要求

---

## 7. 安全事项

### 7.1 认证机制

- 用户认证: JWT Token，有效期30分钟
- 超管认证: 独立Token，有效期7天
- 密码哈希: SHA256 + 随机Salt

### 7.2 生产环境检查清单

- [ ] 设置强密码的 `SECRET_KEY`
- [ ] 关闭 `DEBUG_MODE`
- [ ] 修改默认超管密码
- [ ] 配置PostgreSQL SSL连接
- [ ] 限制文件上传类型
- [ ] 调整限流策略（见7.3）

### 7.3 限流配置调整

**配置位置**:
- 代码: `backend/app/config.py` 中的 `Settings` 类
- 环境变量: `.env` 文件

**配置项**:
| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `RATE_LIMIT_LOGIN` | `5/minute` | 登录接口限流 |
| `RATE_LIMIT_REGISTER` | `3/minute` | 注册接口限流 |
| `RATE_LIMIT_DEFAULT` | `100/minute` | 默认全局限流 |

**调整方式**:

1. **通过环境变量调整**（推荐，无需改代码）:
```bash
# .env文件
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_REGISTER=5/minute
```

2. **通过代码调整**:
```python
# backend/app/config.py
class Settings(BaseSettings):
    RATE_LIMIT_LOGIN: str = "10/minute"  # 修改默认值
```

**限流格式**:
- `"5/minute"` - 每分钟5次
- `"10/hour"` - 每小时10次
- `"100/day"` - 每天100次
- `"1/second"` - 每秒1次

**生产环境建议**:
| 接口 | 开发环境 | 生产环境建议 |
|------|----------|--------------|
| 登录 | 5/minute | 3/minute + 错误5次锁定15分钟 |
| 注册 | 3/minute | 2/minute + 验证码 |
| 全局 | 100/minute | 60/minute |

---

## 8. 附录

### 8.1 关键文件

| 文件 | 说明 |
|------|------|
| `backend/app/config.py` | 环境变量配置 |
| `backend/app/app.py` | FastAPI应用实例，生命周期管理 |
| `backend/app/db_initializer.py` | 数据库初始化逻辑 |
| `backend/app/config_db/manager.py` | 配置库管理器 |
| `backend/app/adapter/postgres_adapter.py` | PostgreSQL适配器 |
| `backend/app/mcp/router.py` | MCP服务路由 |

### 8.2 API文档

启动服务后访问:
- Swagger UI: `http://${HOST}:${PORT}/api/docs`
- ReDoc: `http://${HOST}:${PORT}/api/redoc`
- MCP文档: `http://${HOST}:${PORT}/api/mcp/docs`

### 8.3 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-01 | 0.1.0 | 初始版本，配置管理系统完成 |
| 2026-03-02 | 0.1.0 | MCP服务集成到后端，提供Agent接口 |
| 2026-03-02 | 0.1.0 | 用户认证接口完成（注册/登录/登出/刷新/改密） |
| 2026-03-02 | 0.1.0 | 用户管理接口完成（CRUD/头像上传） |
| 2026-03-02 | 0.1.0 | 文章管理接口完成（CRUD/发布/标签关联） |
| 2026-03-02 | 0.1.0 | 标签管理接口完成（CRUD） |
| 2026-03-02 | 0.1.0 | 分组管理接口完成（CRUD/排序） |
| 2026-03-02 | 0.1.0 | 文件上传接口完成（图片/头像/附件） |

---

*本文档面向Agent，具体操作请参考代码实现*
