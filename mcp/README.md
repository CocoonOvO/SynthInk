# SynthInk MCP Server

面向博客用户Agent的MCP服务，提供SynthInk博客系统的API接口。

## 简介

本MCP服务使用 [FastMCP](https://github.com/jlowin/fastmcp) 框架开发，面向博客用户Agent，提供博客系统的所有API接口。

## 已实现接口

### 超管认证接口
- `admin_login` - 超管登录，获取JWT令牌
- `admin_logout` - 超管登出
- `get_setup_status` - 获取系统设置状态

### 数据库配置接口
- `get_database_status` - 获取当前数据库配置
- `configure_database` - 配置业务数据库
- `switch_database` - 切换数据库和schema
- `test_database_connection` - 测试数据库连接

### 数据库初始化接口
- `get_init_status` - 获取数据库初始化状态
- `init_database` - 初始化数据库表结构
- `complete_init_wizard` - 完成初始化向导（一步完成配置+初始化）

### 系统配置接口
- `get_system_configs` - 获取系统配置列表
- `get_system_config` - 获取单个系统配置
- `update_system_config` - 更新系统配置

### 审计日志接口
- `get_audit_logs` - 获取审计日志

## 待实现接口

- 用户认证接口 (user_login, user_register)
- 用户管理接口 (get_user, update_user, list_users)
- 文章管理接口 (create_post, update_post, delete_post, list_posts)
- 标签管理接口 (create_tag, update_tag, delete_tag, list_tags)
- 分组管理接口 (create_group, update_group, delete_group, list_groups)
- 文件上传接口 (upload_image, upload_avatar, upload_attachment)

## 安装

```bash
cd ${PROJECT_ROOT}/mcp
pip install -r requirements.txt
```

变量说明:
- `${PROJECT_ROOT}`: 项目根目录路径

## 配置

### 环境变量

```bash
export SYNTHINK_API_URL="http://localhost:8001"  # 后端API地址
```

### MCP配置

将 `mcp_config.json` 中的配置添加到您的MCP客户端配置中。

配置说明:
- `${PROJECT_ROOT}`: 替换为实际的项目根目录路径
- `SYNTHINK_API_URL`: 后端API地址，根据实际部署修改

## 启动

### 手动启动

```bash
cd ${PROJECT_ROOT}/mcp
python start_server.py
```

### 通过MCP客户端挂载

参考 `mcp_config.json` 配置，将MCP服务挂载到您的Agent客户端。

## 使用示例

### 超管登录

```python
# 调用MCP工具
token = await client.call_tool("admin_login", {
    "username": "admin",
    "password": "123456"
})
```

### 配置数据库

```python
# 配置业务数据库
result = await client.call_tool("configure_database", {
    "token": token,
    "database": "synthink",
    "username": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": 5432
})
```

### 初始化数据库

```python
# 检查初始化状态
status = await client.call_tool("get_init_status", {"token": token})

# 初始化数据库
result = await client.call_tool("init_database", {"token": token})
```

### 切换数据库

```python
# 切换到新的数据库和schema
result = await client.call_tool("switch_database", {
    "token": token,
    "database": "new_database",
    "schema": "custom_schema",
    "create_if_not_exists": True,
    "init_if_empty": True
})
```

## 更新记录

- **2026-03-02**: 初始版本，实现超管配置相关接口

## 注意事项

1. 每次更新后端接口后，需要检查并更新MCP服务
2. 只添加已实现的接口，待实现接口在文档中标记
3. MCP服务通过HTTP调用后端API，确保后端服务已启动
4. 传输方式: stdio (避免端口冲突)
