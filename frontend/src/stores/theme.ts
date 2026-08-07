/**
 * 主题状态管理
 * 精简版主题系统 - 10个核心主题
 * 主题元数据（名称/图标/分类）统一由 src/config/themes.ts 提供
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { THEMES, THEME_CATEGORY_LABELS, type Theme } from '@/config/themes'
import { getSiteConfig } from '@/config/siteConfig'

// 向后兼容导出（旧代码路径：@/stores/theme）
export type { Theme } from '@/config/themes'
export { themeCategories } from '@/config/themes'

// 本地存储键名
const THEME_STORAGE_KEY = 'synthink-theme'

// 旧主题映射（用于迁移）
const legacyThemeMap: Record<string, Theme> = {
  'dark': 'deep-space',
  'light': 'deep-space',
  'spark-lab': 'deep-space',
  'ocean': 'deep-space',
  'midnight': 'deep-space',
  'forest': 'bamboo',
  'veda': 'cyberpunk',
  'bangdream-dark': 'twins'
}

export const useThemeStore = defineStore('theme', () => {
  // 当前主题
  const currentTheme = ref<Theme>('exia')

  // 是否已初始化
  const isInitialized = ref(false)

  // 获取存储的主题（兼容旧主题）
  const getStoredTheme = (): Theme => {
    if (typeof window === 'undefined') return 'exia'
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    // 兼容旧主题映射
    if (stored && legacyThemeMap[stored]) {
      return legacyThemeMap[stored]
    }
    // 检查是否是有效的新主题
    const validThemes: Theme[] = [
      'deep-space', 'cyberpunk', 'exia',
      'sakura', 'bamboo', 'twins', 'mygo-light',
      'strawberry-cream', 'mint-choco', 'orange-soda'
    ]
    if (validThemes.includes(stored as Theme)) {
      return stored as Theme
    }
    // 首次访问（无本地存储）时，使用站点配置的默认主题（无效值回退 exia）
    const configured = getSiteConfig().site.defaultTheme
    return validThemes.includes(configured as Theme) ? (configured as Theme) : 'exia'
  }

  // 设置主题
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme

    // 应用到DOM
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', theme)
    }

    // 持久化存储
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(THEME_STORAGE_KEY, theme)
    }
  }

  // 初始化主题
  const initTheme = () => {
    if (isInitialized.value) return

    const theme = getStoredTheme()
    setTheme(theme)
    isInitialized.value = true
  }

  // 切换主题（在几个常用主题间循环）
  const toggleTheme = () => {
    const themes: Theme[] = ['deep-space', 'cyberpunk', 'sakura', 'mygo-light']
    const currentIndex = themes.indexOf(currentTheme.value)
    const nextIndex = (currentIndex + 1) % themes.length
    const nextTheme = themes[nextIndex]
    if (nextTheme) {
      setTheme(nextTheme)
    }
  }

  // 获取主题名称（由单一数据源 THEMES 查找）
  const themeName = computed(() => {
    return THEMES.find(t => t.id === currentTheme.value)?.name || '深空'
  })

  // 获取主题分类（由单一数据源 THEMES 分类判断）
  const themeCategory = computed(() => {
    const meta = THEMES.find(t => t.id === currentTheme.value)
    if (meta) {
      return THEME_CATEGORY_LABELS[meta.category]
    }
    return THEME_CATEGORY_LABELS.scifi
  })

  return {
    currentTheme,
    isInitialized,
    themeName,
    themeCategory,
    setTheme,
    initTheme,
    toggleTheme
  }
})
