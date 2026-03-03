/**
 * 用户认证状态管理
 * 登录、登出、用户信息都存在这里
 * 虽然后端还没完全准备好，但架子先搭好
 * (´；ω；`) 反正迟早要写
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  isAdmin: boolean
  createdAt: string
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.isAdmin ?? false)

  // 登录
  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      // TODO: 等后端接口 ready 了再实现
      console.log('登录功能待实现', username, password)
      // 模拟成功
      const mockToken = 'mock_token_' + Date.now()
      token.value = mockToken
      localStorage.setItem('token', mockToken)
      return true
    } catch (error) {
      console.error('登录失败', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    loading.value = true
    try {
      // TODO: 等后端接口 ready 了再实现
      console.log('注册功能待实现', username, email, password)
      return true
    } catch (error) {
      console.error('注册失败', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token.value) return

    try {
      // TODO: 等后端接口 ready 了再实现
      // 模拟用户数据
      user.value = {
        id: 1,
        username: 'test_user',
        email: 'test@example.com',
        isAdmin: false,
        createdAt: new Date().toISOString(),
      }
    } catch (error) {
      console.error('获取用户信息失败', error)
      logout()
    }
  }

  // 初始化时尝试获取用户信息
  if (token.value) {
    fetchUserInfo()
  }

  return {
    token,
    user,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    fetchUserInfo,
  }
})
