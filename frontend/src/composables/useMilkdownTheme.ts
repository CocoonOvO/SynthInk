/**
 * Milkdown 主题适配
 * 接入项目主题系统，提供代码高亮类名和主题变量
 * 使用 Prism 主题根据系统主题自动切换
 */
import { ref, watch, nextTick } from 'vue'
import { useThemeStore } from '@/stores/theme'

const DARK_THEME = 'prism-tomorrow'
const LIGHT_THEME = 'prism'
let themeLink: HTMLLinkElement | null = null

export function useMilkdownTheme() {
  const themeStore = useThemeStore()
  const isDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)
  let onThemeChangeCallback: (() => void) | null = null

  const loadTheme = (dark: boolean) => {
    const themeName = dark ? DARK_THEME : LIGHT_THEME
    const themePath = `${themeName}.css`

    if (themeLink) {
      themeLink.remove()
      themeLink = null
    }

    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = `/node_modules/prismjs/themes/${themePath}`
    link.onload = () => {
      // 主题加载后的回调
      if (onThemeChangeCallback) {
        onThemeChangeCallback()
      }
    }
    link.onerror = () => console.error('加载主题失败:', themePath)

    document.head.appendChild(link)
    themeLink = link
  }

  // 应用到编辑器容器
  const applyTheme = (container: HTMLElement | null) => {
    if (!container) return
    container.setAttribute('data-theme-category', themeStore.themeCategory)
  }

  // 监听主题变化
  const watchTheme = (container: HTMLElement | null, onHighlight?: () => void) => {
    onThemeChangeCallback = onHighlight || null
    loadTheme(isDark.value)
    applyTheme(container)

    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      isDark.value = e.matches
      loadTheme(isDark.value)
    })
  }

  return {
    isDark,
    themeCategory: themeStore.themeCategory,
    currentTheme: themeStore.currentTheme,
    applyTheme,
    watchTheme
  }
}
