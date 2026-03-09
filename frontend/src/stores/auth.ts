/**
 * 认证状态管理
 * 老大让我写认证store，我就写 (╯°□°）╯
 * 虽然还没对接后端，但先把架子搭好
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 用户信息类型
export interface User {
  id: number
  username: string
  email: string
  avatar_url?: string
  bio?: string
  role: 'user' | 'admin'
  created_at: string
}

// 本地存储键名
const TOKEN_STORAGE_KEY = 'synthink-token'
const USER_STORAGE_KEY = 'synthink-user'

export const useAuthStore = defineStore('auth', () => {
  // Token
  const token = ref<string | null>(null)
  
  // 用户信息
  const user = ref<User | null>(null)
  
  // 加载状态
  const isLoading = ref(false)

  // 是否已登录
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  
  // 是否管理员
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 检查token是否过期
  const isTokenExpired = (tokenStr: string): boolean => {
    try {
      const base64Url = tokenStr.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      const payload = JSON.parse(jsonPayload)
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  // 初始化（从本地存储恢复）
  const initAuth = () => {
    if (typeof window === 'undefined') return
    
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY)
    const storedUser = localStorage.getItem(USER_STORAGE_KEY)
    
    // 如果token已过期，清除登录状态
    if (storedToken && isTokenExpired(storedToken)) {
      clearAuth()
      return
    }
    
    if (storedToken) {
      token.value = storedToken
    }
    
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        user.value = null
      }
    }
  }

  // 设置认证信息
  const setAuth = (newToken: string, newUser: User) => {
    token.value = newToken
    user.value = newUser
    
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(TOKEN_STORAGE_KEY, newToken)
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser))
    }
  }

  // 清除认证信息
  const clearAuth = () => {
    token.value = null
    user.value = null
    
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      localStorage.removeItem(USER_STORAGE_KEY)
    }
  }

  // 登录（模拟）
  const login = async (username: string, password: string): Promise<boolean> => {
    isLoading.value = true
    
    try {
      // TODO: 对接后端登录API
      // const response = await api.post('/auth/login', { username, password })
      
      // 模拟登录成功
      const mockUser: User = {
        id: 1,
        username,
        email: `${username}@example.com`,
        role: 'user',
        created_at: new Date().toISOString()
      }
      
      setAuth('mock-token-' + Date.now(), mockUser)
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 注册（模拟）
  const register = async (username: string, email: string, password: string): Promise<boolean> => {
    isLoading.value = true
    
    try {
      // TODO: 对接后端注册API
      // const response = await api.post('/auth/register', { username, email, password })
      
      // 模拟注册成功
      const mockUser: User = {
        id: 1,
        username,
        email,
        role: 'user',
        created_at: new Date().toISOString()
      }
      
      setAuth('mock-token-' + Date.now(), mockUser)
      return true
    } catch (error) {
      console.error('注册失败:', error)
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 登出
  const logout = () => {
    clearAuth()
  }

  // 更新用户信息
  const updateUser = (updates: Partial<User>) => {
    if (user.value) {
      // 创建新的用户对象
      const newUser = { ...user.value }
      
      // 处理更新：undefined 值会删除该字段，其他值正常更新
      Object.entries(updates).forEach(([key, value]) => {
        if (value === undefined) {
          delete (newUser as any)[key]
        } else {
          (newUser as any)[key] = value
        }
      })
      
      user.value = newUser
      
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user.value))
      }
    }
  }

  return {
    token,
    user,
    isLoading,
    isLoggedIn,
    isAdmin,
    initAuth,
    setAuth,
    clearAuth,
    login,
    register,
    logout,
    updateUser
  }
})
