---
name: "synthink-superadmin"
description: "SynthInk超管系统操作指南。Invoke when 需要进行系统初始化、数据库配置、用户管理、审计日志查看等超管操作。"
---

# SynthInk 超管操作指南

> **Base URL**: `http://localhost:8002/api`
> **鉴权方式**: Bearer Token (JWT) - 需要超管权限

---

## 场景1：超管认证

### 超管登录
```
POST /admin/login
{
  "username": "admin",
  "password": "123456"
}
```
**返回**: `{access_token: "...", token_type: "bearer", admin_id: "..."}`

### 修改超管密码
```
POST /admin/change-password
Authorization: Bearer {superadmin_token}
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

---

## 场景2：系统初始化

### 获取系统设置状态
```
GET /admin/setup-status
```
**返回**: `{is_initialized: false, current_step: 1, steps: [...]}`

### 配置业务数据库
```
POST /admin/database
Authorization: Bearer {superadmin_token}
{
  "name": "default",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "synthink",
  "schema": "public",
  "username": "postgres",
  "password": "password"
}
```

### 测试数据库连接
```
POST /admin/database/test
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "synthink",
  "username": "postgres",
  "password": "password"
}
```

### 初始化数据库（创建表结构）
```
POST /admin/database/init
Authorization: Bearer {superadmin_token}
```

### 完成初始化向导
```
POST /admin/init-wizard/complete
Authorization: Bearer {superadmin_token}
{
  "site_name": "SynthInk博客",
  "site_description": "一个优雅的博客系统"
}
```

---

## 场景3：系统配置管理

### 获取系统配置列表
```
GET /admin/configs
Authorization: Bearer {superadmin_token}
```

### 获取单个配置
```
GET /admin/configs/{config_key}
Authorization: Bearer {superadmin_token}
```

### 更新系统配置
```
PUT /admin/configs/{config_key}
Authorization: Bearer {superadmin_token}
{
  "value": "配置值",
  "description": "配置说明"
}
```

### 批量更新配置
```
PUT /admin/configs
Authorization: Bearer {superadmin_token}
{
  "configs": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

### 删除配置
```
DELETE /admin/configs/{config_key}
Authorization: Bearer {superadmin_token}
```

---

## 场景4：用户管理（超管）

### 获取用户列表
```
GET /users/
Authorization: Bearer {superadmin_token}
```

### 超管创建用户
```
POST /auth/register
Authorization: Bearer {superadmin_token}
{
  "username": "新用户",
  "email": "user@example.com",
  "password": "password",
  "user_type": "user"
}
```
**注**: 超管可以创建普通用户(user)或Agent(agent)

### 删除任意用户
```
DELETE /users/{user_id}
Authorization: Bearer {superadmin_token}
```

---

## 场景5：审计日志

### 获取审计日志列表
```
GET /admin/audit-logs
Authorization: Bearer {superadmin_token}
```

### 获取审计日志详情
```
GET /admin/audit-logs/{log_id}
Authorization: Bearer {superadmin_token}
```

---

## 场景6：数据库管理

### 获取数据库状态
```
GET /admin/database/status
Authorization: Bearer {superadmin_token}
```

### 获取所有数据库配置
```
GET /admin/databases
Authorization: Bearer {superadmin_token}
```

### 切换业务数据库
```
POST /admin/database/switch
Authorization: Bearer {superadmin_token}
{
  "name": "database_name"
}
```

### 删除数据库配置
```
DELETE /admin/database/{name}
Authorization: Bearer {superadmin_token}
```

---

## 完整工作流

### 系统初始化流程
```
1. GET /admin/setup-status → 检查初始化状态
2. POST /admin/login → 超管登录（默认账号admin/123456）
3. POST /admin/database/test → 测试数据库连接
4. POST /admin/database → 配置业务数据库
5. POST /admin/database/init → 初始化表结构
6. POST /admin/init-wizard/complete → 完成初始化
```

### 创建新用户流程
```
1. POST /admin/login → 超管登录
2. POST /auth/register → 创建新用户（需超管token）
```

### 修改系统配置流程
```
1. POST /admin/login → 超管登录
2. GET /admin/configs → 查看当前配置
3. PUT /admin/configs/{key} → 更新配置
```
