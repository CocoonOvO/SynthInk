---
name: download-optimize
description: 远程获取特定文件/库时触发
version: 1.0.0
author: 琉璃大小姐
---

# Download-Optimize - 下载功能优化技能

## 🎯 触发条件

**远程获取特定文件/库时触发**

当你需要：
- 下载远程文件到本地
- 获取外部依赖库
- 拉取远程资源
- 克隆代码仓库

## 📋 核心功能

本技能优化了大文件的下载方式，避免直接写入文件导致的性能问题，提高下载效率和稳定性。

## 🔄 下载策略

### 策略1：小文件（< 1MB）- 直接下载

**适用场景**：
- 配置文件
- 小图片
- 文本文件
- JSON数据

**实现方式**：
```python
import httpx

# 小文件直接下载
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    content = response.content
    # 直接处理或保存
```

---

### 策略2：大文件（>= 1MB）- 系统指令下载 ⭐ 推荐

**适用场景**：
- 大型二进制文件
- 视频/音频文件
- 压缩包
- 大型数据集

**实现方式**：

#### Python代码中使用系统指令
```python
import subprocess

# 使用 curl 下载（推荐）
subprocess.run([
    "curl", "-L", "-o", "output.file", 
    "https://example.com/large-file.zip"
], check=True)

# 或使用 wget
subprocess.run([
    "wget", "-O", "output.file",
    "https://example.com/large-file.zip"
], check=True)
```

#### 异步下载（不阻塞）
```python
import asyncio

async def download_large_file(url: str, output_path: str):
    """使用系统指令异步下载大文件"""
    process = await asyncio.create_subprocess_exec(
        "curl", "-L", "-o", output_path, url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Download failed: {stderr.decode()}")
    
    return output_path
```

---

### 策略3：批量下载 - 并发优化

**适用场景**：
- 多个文件需要下载
- 批量获取资源

**实现方式**：
```python
import asyncio
import aiohttp

async def download_batch(urls: list, output_dir: str):
    """批量并发下载，但限制并发数"""
    semaphore = asyncio.Semaphore(5)  # 最多5个并发
    
    async def download_one(url):
        async with semaphore:
            filename = url.split('/')[-1]
            output_path = f"{output_dir}/{filename}"
            
            # 大文件使用系统指令
            if await is_large_file(url):
                await download_with_curl(url, output_path)
            else:
                await download_direct(url, output_path)
    
    await asyncio.gather(*[download_one(url) for url in urls])
```

---

### 策略4：Git仓库 - 使用 git 命令

**适用场景**：
- 克隆代码仓库
- 获取子模块
- 拉取特定分支

**实现方式**：
```python
import subprocess

# 克隆仓库
subprocess.run([
    "git", "clone", 
    "https://github.com/example/repo.git",
    "--depth", "1",  # 浅克隆，只下载最新版本
    "--branch", "main"
], check=True)

# 更新子模块
subprocess.run([
    "git", "submodule", "update", "--init", "--recursive"
], check=True)
```

---

## 📊 下载方式对比

| 方式 | 适用大小 | 优点 | 缺点 | 推荐度 |
|------|----------|------|------|--------|
| **直接下载** | < 1MB | 简单、快速 | 大文件占用内存 | ⭐⭐⭐ |
| **curl/wget** | >= 1MB | 流式写入、断点续传 | 依赖系统命令 | ⭐⭐⭐⭐⭐ |
| **git clone** | 仓库 | 版本控制、增量更新 | 需要git环境 | ⭐⭐⭐⭐ |
| **aiohttp** | 任意 | 异步、并发控制 | 需要额外库 | ⭐⭐⭐⭐ |

---

## 📝 完整决策流程

```
┌─────────────────────────────────────────────────────────────────┐
│                   Download-Optimize 下载决策                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   开始下载                                                       │
│       │                                                          │
│       ▼                                                          │
│   判断文件类型                                                    │
│       │                                                          │
│       ├─ Git仓库? ──是──► 使用 git clone                         │
│       │                      └─ 添加 --depth 1 优化              │
│       │                                                          │
│       ▼                                                          │
│   判断文件大小                                                    │
│       │                                                          │
│       ├─ < 1MB? ──是──► 直接下载（httpx/aiohttp）                │
│       │                      └─ 快速、简单                       │
│       │                                                          │
│       └─ >= 1MB? ──是──► 系统指令下载（curl/wget）               │
│                             └─ 流式写入、高效                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 最佳实践

### 1. 始终检查文件大小

```python
import httpx

async def get_file_size(url: str) -> int:
    """获取远程文件大小"""
    async with httpx.AsyncClient() as client:
        response = await client.head(url)
        return int(response.headers.get('content-length', 0))

# 根据大小选择下载方式
size = await get_file_size(url)
if size > 1024 * 1024:  # 1MB
    await download_with_curl(url, output)
else:
    await download_direct(url, output)
```

### 2. 添加进度显示

```python
import subprocess
import sys

# curl 自带进度条
subprocess.run([
    "curl", "-L", "--progress-bar",
    "-o", "output.file", url
])

# 或使用 wget 的进度显示
subprocess.run([
    "wget", "--progress=bar:force",
    "-O", "output.file", url
])
```

### 3. 错误处理和重试

```python
import subprocess
import time

async def download_with_retry(url: str, output: str, max_retries: int = 3):
    """带重试的下载"""
    for attempt in range(max_retries):
        try:
            subprocess.run(
                ["curl", "-L", "-o", output, url],
                check=True,
                timeout=300  # 5分钟超时
            )
            return output
        except subprocess.CalledProcessError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
```

### 4. 验证下载完整性

```python
import hashlib

def verify_checksum(file_path: str, expected_hash: str) -> bool:
    """验证文件完整性"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest() == expected_hash
```

---

## 🎯 关键原则

1. **大文件用系统指令** - 避免内存占用过高
2. **小文件直接下载** - 简单高效
3. **Git仓库用git命令** - 保持版本控制
4. **始终添加错误处理** - 网络不稳定很常见
5. **验证文件完整性** - 防止下载损坏

---

## 📚 代码示例

### 完整下载工具类

```python
import os
import subprocess
import httpx
from typing import Optional

class DownloadManager:
    """下载管理器 - 由琉璃大小姐精心设计"""
    
    # 大文件阈值：1MB
    LARGE_FILE_THRESHOLD = 1024 * 1024
    
    @staticmethod
    async def get_file_size(url: str) -> int:
        """获取远程文件大小"""
        async with httpx.AsyncClient() as client:
            response = await client.head(url, follow_redirects=True)
            return int(response.headers.get('content-length', 0))
    
    @staticmethod
    def download_with_curl(url: str, output_path: str):
        """使用curl下载（适合大文件）"""
        subprocess.run([
            "curl", "-L", "--progress-bar",
            "-o", output_path, url
        ], check=True)
    
    @staticmethod
    async def download_direct(url: str, output_path: str):
        """直接下载（适合小文件）"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
    
    @classmethod
    async def download(cls, url: str, output_path: str) -> str:
        """
        智能下载 - 自动选择最佳方式
        
        Args:
            url: 远程文件URL
            output_path: 本地保存路径
            
        Returns:
            保存的文件路径
        """
        # 获取文件大小
        try:
            size = await cls.get_file_size(url)
        except:
            size = 0  # 无法获取大小时假设为小文件
        
        # 根据大小选择下载方式
        if size > cls.LARGE_FILE_THRESHOLD:
            print(f"[INFO] 大文件检测 ({size} bytes)，使用curl下载...")
            cls.download_with_curl(url, output_path)
        else:
            print(f"[INFO] 小文件检测 ({size} bytes)，直接下载...")
            await cls.download_direct(url, output_path)
        
        return output_path

# 使用示例
# await DownloadManager.download("https://example.com/file.zip", "./file.zip")
```

---

## 🔗 相关技能

- **workrule** - 基础工作规则
- **code-order** - 开发流程规范
- **project_use** - 项目使用和维护

---

## ⚠️ 注意事项

1. **Windows兼容性**：curl在Windows 10+自带，旧版本需要安装或使用PowerShell的Invoke-WebRequest
2. **权限问题**：确保有写入目标目录的权限
3. **磁盘空间**：下载前检查磁盘空间是否充足
4. **网络代理**：如果处于代理环境，需要配置curl/wget的代理设置

---

*由琉璃大小姐精心整理，高效而优雅* ✨
