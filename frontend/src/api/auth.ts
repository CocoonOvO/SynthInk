/**
 * 认证相关 API
 * 登录注册这些破事，天天写 (╯°□°）╯
 */
import { client } from './client'

// 用户类型
export interface User {
  id: number
  username: string
  email: string
  display_name?: string  // 后端字段名
  full_name?: string     // 兼容旧代码
  avatar?: string  // 后端返回avatar_url，映射为avatar
  bio?: string
  is_active: boolean
  is_superuser: boolean
  user_type: 'user' | 'admin'
  created_at: string
  updated_at?: string
}

// 后端原始用户类型
interface BackendUser {
  id: number
  username: string
  email: string
  display_name?: string  // 后端实际字段名
  avatar_url?: string
  bio?: string
  is_active: boolean
  is_superuser: boolean
  user_type: 'user' | 'admin'
  created_at: string
  updated_at?: string
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in?: number
}

// 注册请求
export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

// 注册响应
export interface RegisterResponse {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  created_at: string
}

// 修改密码请求
export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// 更新用户请求
export interface UpdateUserRequest {
  email?: string
  display_name?: string  // 后端实际字段名
  full_name?: string     // 兼容旧代码
  bio?: string
  avatar_url?: string
}

/**
 * 转换后端用户数据为前端格式
 */
function transformUser(backendUser: BackendUser): User {
  return {
    ...backendUser,
    full_name: backendUser.display_name,  // 兼容旧代码
    avatar_url: backendUser.avatar_url
  }
}

/**
 * 认证 API
 */
export const authApi = {
  /**
   * 用户登录
   * POST /api/auth/token
   * 注意：后端使用 form-data，不是 JSON
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await fetch('http://localhost:8002/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || '登录失败')
    }

    return response.json()
  },

  /**
   * 用户注册
   * POST /api/auth/register
   */
  register: (data: RegisterRequest): Promise<RegisterResponse> =>
    client.post('/api/auth/register', data),

  /**
   * 获取当前用户信息
   * GET /api/auth/me
   */
  getMe: async (): Promise<User> => {
    const backendUser = await client.get<BackendUser>('/api/auth/me')
    return transformUser(backendUser)
  },

  /**
   * 修改密码
   * POST /api/auth/password/reset
   */
  changePassword: (data: ChangePasswordRequest): Promise<void> =>
    client.post('/api/auth/password/reset', data),

  /**
   * 更新用户信息
   * PUT /api/users/me
   */
  updateProfile: async (data: UpdateUserRequest): Promise<User> => {
    const backendUser = await client.put<BackendUser>('/api/users/me', data)
    return transformUser(backendUser)
  },

  /**
   * 登出（前端清除token即可）
   */
  logout: (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('synthink-token')
      localStorage.removeItem('synthink-user')
    }
  },

  /**
   * 通过用户名获取用户信息
   * GET /api/users/by-username/{username}
   */
  getUserByUsername: async (username: string): Promise<User> => {
    const backendUser = await client.get<BackendUser>(`/api/users/by-username/${username}`)
    return transformUser(backendUser)
  }
}
