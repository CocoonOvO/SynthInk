# MCP服务器分发与获取指南

## 概述

MCP服务器可以随项目一起发布，也可以独立部署。本文档说明其他Agent如何获取和使用SynthInk的MCP服务。

---

## 分发方式

### 方式1：代码仓库（推荐）

MCP服务器作为项目的一部分，随代码一起发布。

```
SynthInk/
├── backend/          # FastAPI后端
├── frontend/         # Vue3前端
├── mcp/             # MCP服务器 ← 在这里
│   ├── server.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

**Agent获取步骤：**

```bash
# 1. 克隆项目
git clone https://github.com/yourname/SynthInk.git
cd SynthInk

# 2. 安装MCP依赖
cd mcp
pip install -r requirements.txt

# 3. 配置助手
# 将 mcp/config.json 复制到助手配置目录
```

### 方式2：独立部署（SSE模式）

将MCP服务器部署为独立服务，供多个Agent共享。

```bash
# 在服务器上部署
docker run -d \
  --name synthink-mcp \
  -p 8002:8002 \
  -e SYNTHINK_API_URL=http://your-backend:8001 \
  synthink/mcp-server:latest
```

**Agent配置：**

```json
{
  "mcpServers": {
    "SynthInk": {
      "url": "http://your-server:8002/sse"
    }
  }
}
```

### 方式3：PyPI包

```bash
# 安装
pip install synthink-mcp

# 运行
python -m synthink_mcp --backend-url http://localhost:8001
```

---

## Agent获取MCP的完整流程

### 场景：新Agent加入项目

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         新Agent获取MCP流程                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  步骤1: 发现项目                                                              │
│  ┌─────────────┐                                                            │
│  │  浏览GitHub  │ ──► 发现SynthInk项目                                        │
│  │  或文档中心  │     看到MCP支持标识                                         │
│  └─────────────┘                                                            │
│                                                                              │
│  步骤2: 查看MCP配置                                                           │
│  ┌─────────────┐                                                            │
│  │  阅读README  │ ──► 找到mcp/config.json示例                                 │
│  │  或MCP文档   │     了解如何配置                                            │
│  └─────────────┘                                                            │
│                                                                              │
│  步骤3: 获取MCP服务器                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │  克隆代码    │ or  │  安装PyPI包  │ or  │  连接远程SSE │                   │
│  │  git clone  │     │  pip install │     │  服务       │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│                                                                              │
│  步骤4: 配置助手                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  创建/编辑助手配置文件 (如 claude_desktop_config.json)               │   │
│  │                                                                    │   │
│  │  {                                                                 │   │
│  │    "mcpServers": {                                                 │   │
│  │      "SynthInk": {                                                 │   │
│  │        "command": "python",                                        │   │
│  │        "args": ["/path/to/SynthInk/mcp/server.py"],                │   │
│  │        "env": {                                                    │   │
│  │          "SYNTHINK_API_URL": "http://localhost:8001"               │   │
│  │        }                                                           │   │
│  │      }                                                             │   │
│  │    }                                                               │   │
│  │  }                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  步骤5: 启动并使用                                                            │
│  ┌─────────────┐                                                            │
│  │  重启助手    │ ──► 助手自动发现MCP工具                                     │
│  │  开始使用   │     可以调用所有29个工具！                                  │
│  └─────────────┘                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## MCP配置格式详解

### stdio模式配置

```json
{
  "mcpServers": {
    "SynthInk": {
      "command": "python",
      "args": [
        "-u",
        "/absolute/path/to/SynthInk/mcp/server.py"
      ],
      "env": {
        "SYNTHINK_API_URL": "http://localhost:8001",
        "PYTHONPATH": "/absolute/path/to/SynthInk/mcp"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### SSE模式配置

```json
{
  "mcpServers": {
    "SynthInk": {
      "url": "http://localhost:8002/sse",
      "headers": {
        "Authorization": "Bearer optional-token"
      }
    }
  }
}
```

---

## 工具发现机制

当Agent连接到MCP服务器后，会自动获取可用工具列表：

```json
// Agent发送
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}

// MCP服务器返回
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "get_setup_status",
        "description": "获取系统设置状态...",
        "inputSchema": {
          "type": "object",
          "properties": {},
          "required": []
        }
      },
      {
        "name": "post_list",
        "description": "获取文章列表...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "skip": {"type": "integer", "default": 0},
            "limit": {"type": "integer", "default": 20},
            "status": {"type": "string", "default": "published"}
          },
          "required": []
        }
      }
      // ... 更多工具
    ]
  },
  "id": 1
}
```

---

## 实际使用示例

### 示例1：Agent查询系统状态

```python
# Agent通过MCP调用工具
result = await mcp_client.call_tool("get_setup_status", {})
print(result)
# 输出: {'config_db_initialized': True, 'database_connected': True, ...}
```

### 示例2：Agent获取文章列表

```python
# Agent调用带参数的工具
result = await mcp_client.call_tool("post_list", {
    "limit": 5,
    "status": "published"
})
print(f"获取到 {len(result)} 篇文章")
```

### 示例3：Agent创建文章

```python
# 需要认证的工具
result = await mcp_client.call_tool("post_create", {
    "title": "新文章标题",
    "content": "文章内容...",
    "token": "eyJhbGciOiJIUzI1NiIs..."  # 通过admin_login获取
})
```

---

## 最佳实践

### 对于项目维护者

1. **提供清晰的MCP文档**：在README中说明如何配置MCP
2. **提供配置模板**：提供mcp_config.json示例
3. **版本管理**：MCP服务器版本与API版本保持一致
4. **向后兼容**：工具变更时保持向后兼容

### 对于Agent开发者

1. **缓存工具列表**：避免重复获取工具列表
2. **错误处理**：处理MCP连接失败、工具调用失败等情况
3. **权限检查**：调用需要认证的工具前先获取token
4. **环境变量**：使用环境变量配置后端URL

---

## 总结

MCP服务器的分发方式：

| 方式 | 适用场景 | 复杂度 |
|------|----------|--------|
| 代码仓库 | 开发环境、开源项目 | 低 |
| 独立部署 | 生产环境、团队协作 | 中 |
| PyPI包 | 广泛使用、标准化 | 低 |

Agent获取流程：**发现 → 查看文档 → 获取代码 → 配置 → 使用**
