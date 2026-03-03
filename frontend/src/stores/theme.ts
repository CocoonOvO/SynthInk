/**
 * 主题状态管理
 * 支持三种主题切换：赛博霓虹、极光紫境、暖阳橙光
 * 还能跟随系统，虽然我觉得没人会这么用
 * (´；ω；`) 但老大说要精致，我就都做了
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export type ThemeType = 'cyber' | 'aurora' | 'sunset' | 'system'

export const useThemeStore = defineStore('theme', () => {
  // 从本地存储读取主题，默认赛博霓虹
  const currentTheme = ref<ThemeType>((localStorage.getItem('theme') as ThemeType) || 'cyber')

  // 系统主题
  const systemTheme = ref<'cyber' | 'aurora'>('cyber')

  // 实际应用的主题
  const appliedTheme = computed(() => {
    if (currentTheme.value === 'system') {
      return systemTheme.value
    }
    return currentTheme.value
  })

  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const updateSystemTheme = () => {
    // 简单处理：深色模式用赛博，浅色用极光
    systemTheme.value = mediaQuery.matches ? 'cyber' : 'aurora'
  }

  // 初始化系统主题监听
  updateSystemTheme()
  mediaQuery.addEventListener('change', updateSystemTheme)

  // 应用主题到 DOM
  const applyTheme = (theme: string) => {
    document.documentElement.setAttribute('data-theme', theme)
  }

  // 切换主题
  const setTheme = (theme: ThemeType) => {
    currentTheme.value = theme
    localStorage.setItem('theme', theme)

    if (theme === 'system') {
      applyTheme(systemTheme.value)
    } else {
      applyTheme(theme)
    }
  }

  // 监听实际主题变化并应用
  watch(
    appliedTheme,
    (newTheme) => {
      applyTheme(newTheme)
    },
    { immediate: true },
  )

  // 初始化时应用主题
  if (currentTheme.value === 'system') {
    applyTheme(systemTheme.value)
  } else {
    applyTheme(currentTheme.value)
  }

  return {
    currentTheme,
    appliedTheme,
    setTheme,
  }
})
