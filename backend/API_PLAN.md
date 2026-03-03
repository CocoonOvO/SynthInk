# 后端接口开发计划

> 记录待实现的后端接口清单

## 1. 用户认证接口 (auth)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 公开 |
| POST | /api/auth/login | 用户登录 | 公开 |
| POST | /api/auth/logout | 用户登出 | 需登录 |
| POST | /api/auth/refresh | 刷新Token | 需登录 |
| POST | /api/auth/password/reset | 重置密码 | 需登录 |

## 2. 用户管理接口 (users)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| GET | /api/users/me | 获取当前用户信息 | 需登录 |
| PUT | /api/users/me | 更新当前用户信息 | 需登录 |
| POST | /api/users/me/avatar | 上传头像 | 需登录 |
| PUT | /api/users/me/password | 修改密码 | 需登录 |
| GET | /api/users/{id} | 获取指定用户信息 | 需登录 |
| GET | /api/users | 获取用户列表 | 超管 |
| PUT | /api/users/{id} | 更新指定用户 | 超管 |
| DELETE | /api/users/{id} | 删除用户 | 超管 |

## 3. 文章管理接口 (posts)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/posts | 创建文章 | 需登录 |
| GET | /api/posts | 获取文章列表 | 公开 |
| GET | /api/posts/{id} | 获取文章详情 | 公开 |
| PUT | /api/posts/{id} | 更新文章 | 作者/超管 |
| DELETE | /api/posts/{id} | 删除文章 | 作者/超管 |
| POST | /api/posts/{id}/publish | 发布文章 | 作者/超管 |
| POST | /api/posts/{id}/cover | 上传封面图 | 作者/超管 |

## 4. 标签管理接口 (tags)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/tags | 创建标签 | 超管 |
| GET | /api/tags | 获取标签列表 | 公开 |
| GET | /api/tags/{id} | 获取标签详情 | 公开 |
| PUT | /api/tags/{id} | 更新标签 | 超管 |
| DELETE | /api/tags/{id} | 删除标签 | 超管 |
| GET | /api/tags/{id}/posts | 获取标签下的文章 | 公开 |

## 5. 分组管理接口 (groups)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/groups | 创建分组 | 超管 |
| GET | /api/groups | 获取分组列表 | 公开 |
| GET | /api/groups/{id} | 获取分组详情 | 公开 |
| PUT | /api/groups/{id} | 更新分组 | 超管 |
| DELETE | /api/groups/{id} | 删除分组 | 超管 |
| GET | /api/groups/{id}/posts | 获取分组下的文章 | 公开 |

## 6. 文件上传接口 (upload)

| 方法 | 路径 | 功能 | 鉴权 |
|------|------|------|------|
| POST | /api/upload/image | 上传图片 | 需登录 |
| POST | /api/upload/avatar | 上传头像 | 需登录 |
| POST | /api/upload/file | 上传附件 | 需登录 |

## 开发顺序

1. 用户认证接口 (基础功能)
2. 用户管理接口 (用户系统完整)
3. 文件上传接口 (文章需要)
4. 文章管理接口 (核心功能)
5. 标签管理接口 (文章组织)
6. 分组管理接口 (文章组织)
