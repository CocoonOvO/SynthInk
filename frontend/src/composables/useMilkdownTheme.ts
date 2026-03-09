/**
 * Milkdown 主题适配
 * 接入项目主题系统，提供代码高亮类名和主题变量
 */
import { computed, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'

// 代码高亮主题映射
const hljsThemeMap: Record<string, string> = {
  // 科幻系 - 霓虹暗色
  scifi: 'hljs-scifi',
  // 自然系 - 柔和亮色
  nature: 'hljs-nature',
  // 治愈系 - 温暖色调
  healing: 'hljs-healing'
}

export function useMilkdownTheme() {
  const themeStore = useThemeStore()

  // 当前代码高亮类名
  const hljsClass = computed(() => {
    return hljsThemeMap[themeStore.themeCategory] || 'hljs-scifi'
  })

  // 应用到编辑器容器
  const applyTheme = (container: HTMLElement | null) => {
    if (!container) return
    
    // 移除旧类名
    Object.values(hljsThemeMap).forEach(cls => {
      container.classList.remove(cls)
    })
    
    // 添加新类名
    container.classList.add(hljsClass.value)
    
    // 设置主题属性
    container.setAttribute('data-theme-category', themeStore.themeCategory)
  }

  // 监听主题变化
  const watchTheme = (container: HTMLElement | null) => {
    watch(() => themeStore.currentTheme, () => {
      applyTheme(container)
    }, { immediate: true })
  }

  return {
    hljsClass,
    themeCategory: computed(() => themeStore.themeCategory),
    currentTheme: computed(() => themeStore.currentTheme),
    applyTheme,
    watchTheme
  }
}
