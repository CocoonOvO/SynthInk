/**
 * 主题状态管理
 * 精简版主题系统 - 10个核心主题
 * 
 * 科幻：深空 / 赛博朋克 / 能天使
 * 自然：樱花 / 竹林绿 / 双子 / 星歌
 * 治愈：草莓奶油 / 薄荷巧克力 / 香橙气泡
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 主题类型 - 10个核心主题
export type Theme =
  | 'deep-space'    // 深空（原dark）
  | 'cyberpunk'     // 赛博朋克
  | 'exia'          // 能天使
  | 'sakura'        // 樱花
  | 'bamboo'        // 竹林绿
  | 'twins'         // 双子
  | 'mygo-light'    // 星歌
  | 'strawberry-cream'  // 草莓奶油
  | 'mint-choco'    // 薄荷巧克力
  | 'orange-soda'   // 香橙气泡

// 主题分类
export const themeCategories = {
  scifi: ['deep-space', 'cyberpunk', 'exia'] as Theme[],
  nature: ['sakura', 'bamboo', 'twins', 'mygo-light'] as Theme[],
  healing: ['strawberry-cream', 'mint-choco', 'orange-soda'] as Theme[]
}

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
  const currentTheme = ref<Theme>('deep-space')

  // 是否已初始化
  const isInitialized = ref(false)

  // 获取存储的主题（兼容旧主题）
  const getStoredTheme = (): Theme => {
    if (typeof window === 'undefined') return 'deep-space'
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
    return validThemes.includes(stored as Theme) ? (stored as Theme) : 'deep-space'
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
    setTheme(themes[nextIndex])
  }

  // 获取主题名称
  const themeName = computed(() => {
    const names: Record<Theme, string> = {
      'deep-space': '深空',
      'cyberpunk': '赛博朋克',
      'exia': '能天使',
      'sakura': '樱花',
      'bamboo': '竹林绿',
      'twins': '双子',
      'mygo-light': '星歌',
      'strawberry-cream': '草莓奶油',
      'mint-choco': '薄荷巧克力',
      'orange-soda': '香橙气泡'
    }
    return names[currentTheme.value] || '深空'
  })

  // 获取主题分类
  const themeCategory = computed(() => {
    if (themeCategories.scifi.includes(currentTheme.value)) return '科幻'
    if (themeCategories.nature.includes(currentTheme.value)) return '自然'
    if (themeCategories.healing.includes(currentTheme.value)) return '治愈'
    return '科幻'
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
