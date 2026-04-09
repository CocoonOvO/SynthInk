<template>
  <!-- 顶部导航 - 按 design-system/pages/home.html 还原 -->
  <nav class="navbar" :class="{ scrolled: isScrolled }">
    <!-- Logo -->
    <router-link to="/" class="nav-logo">
      <div class="nav-logo-icon">
        <!-- Spin Logo - 三瓣旋转 -->
        <svg viewBox="0 0 24 24" fill="none">
          <!-- 上瓣 -->
          <path d="M12 4c2 2 3 5 2 8-1 2-3 3-4 2-2-1-2-4-1-7 1-2 2-3 3-3z" fill="currentColor" opacity="0.9"/>
          <!-- 右下瓣 -->
          <path d="M20 14c-2 2-5 3-8 2-2-1-3-3-2-4 1-2 4-2 7-1 2 1 3 2 3 3z" fill="currentColor" opacity="0.8"/>
          <!-- 左下瓣 -->
          <path d="M6 18c-1-3 0-6 3-7 2-1 4 0 4 2 0 2-3 4-6 5-1 0-1 0-1 0z" fill="currentColor" opacity="0.85"/>
        </svg>
      </div>
      <span class="nav-logo-text">{{ cw.logo }}</span>
    </router-link>

    <!-- 导航链接 -->
    <ul class="nav-links">
      <li v-for="item in cw.navItems" :key="item.path">
        <router-link :to="item.path">{{ item.label }}</router-link>
      </li>
    </ul>

    <!-- 右侧操作区 -->
    <div class="nav-actions">
      <!-- 写作按钮 - 只有登录后才显示 -->
      <router-link v-if="authStore.isLoggedIn" to="/write" class="nav-write-btn" title="开始创作">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
      </router-link>

      <!-- 主题选择器 -->
      <div class="theme-selector">
        <button
          class="theme-toggle-btn"
          :class="{ active: isThemePanelOpen }"
          @click.stop="toggleThemePanel"
          title="切换主题"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
        </button>

        <!-- 主题面板 -->
        <div v-if="isThemePanelOpen" class="theme-panel" v-click-outside="closeThemePanel">
          <div class="theme-panel-header">选择主题</div>
          
          <!-- 科幻 -->
          <div class="theme-category">
            <div class="theme-category-label">科幻</div>
            <div class="theme-grid">
              <div 
                v-for="theme in scifiThemes" 
                :key="theme.id"
                class="theme-option"
                :class="{ active: currentTheme === theme.id }"
                @click="setTheme(theme.id)"
              >
                <span class="theme-icon">{{ theme.icon }}</span>
                <span class="theme-name">{{ theme.name }}</span>
              </div>
            </div>
          </div>

          <!-- 自然 -->
          <div class="theme-category">
            <div class="theme-category-label">自然</div>
            <div class="theme-grid">
              <div 
                v-for="theme in natureThemes" 
                :key="theme.id"
                class="theme-option"
                :class="{ active: currentTheme === theme.id }"
                @click="setTheme(theme.id)"
              >
                <span class="theme-icon">{{ theme.icon }}</span>
                <span class="theme-name">{{ theme.name }}</span>
              </div>
            </div>
          </div>

          <!-- 治愈 -->
          <div class="theme-category">
            <div class="theme-category-label">治愈</div>
            <div class="theme-grid">
              <div 
                v-for="theme in healingThemes" 
                :key="theme.id"
                class="theme-option"
                :class="{ active: currentTheme === theme.id }"
                @click="setTheme(theme.id)"
              >
                <span class="theme-icon">{{ theme.icon }}</span>
                <span class="theme-name">{{ theme.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 登录/用户入口 -->
      <router-link v-if="!authStore.isLoggedIn" to="/login" class="nav-cta">
        登录
      </router-link>
      <router-link v-else to="/profile" class="nav-user">
        <span class="user-avatar">
          <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" class="nav-avatar-img" alt="头像">
          <span v-else>{{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}</span>
        </span>
        <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
/**
 * 导航栏组件
 * 老大让我按home.html还原导航，我就还原 (╯°□°）╯
 * 这破导航写了这么多代码，我的手指都要断了
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores'
import { useAuthStore } from '@/stores/auth'
import copywriting from '@/config/copywriting.json'
import type { Theme } from '@/stores/theme'

// 扩展HTMLElement类型以支持_clickOutside
declare global {
  interface HTMLElement {
    _clickOutside?: (event: Event) => void
  }
}

// 主题store
const themeStore = useThemeStore()
const currentTheme = ref<Theme>(themeStore.currentTheme)

// 认证store
const authStore = useAuthStore()

// 文案配置
const cw = copywriting.navbar

// 滚动状态
const isScrolled = ref(false)

// 主题面板状态
const isThemePanelOpen = ref(false)

// 主题列表 - 10个核心主题
const scifiThemes = [
  { id: 'deep-space', name: '深空', icon: '🌙' },
  { id: 'cyberpunk', name: '赛博朋克', icon: '🌃' },
  { id: 'exia', name: '能天使', icon: '⚡' },
]

const natureThemes = [
  { id: 'sakura', name: '樱花', icon: '🌸' },
  { id: 'bamboo', name: '竹林绿', icon: '🎋' },
  { id: 'twins', name: '双子', icon: '♊' },
  { id: 'mygo-light', name: '星歌', icon: '⭐' },
]

const healingThemes = [
  { id: 'strawberry-cream', name: '草莓奶油', icon: '🍓' },
  { id: 'mint-choco', name: '薄荷巧克力', icon: '🍃' },
  { id: 'orange-soda', name: '香橙气泡', icon: '🍊' },
]

// 切换主题面板
const toggleThemePanel = () => {
  isThemePanelOpen.value = !isThemePanelOpen.value
}

// 关闭主题面板
const closeThemePanel = () => {
  isThemePanelOpen.value = false
}

// 设置主题
const setTheme = (themeId: string) => {
  themeStore.setTheme(themeId as Theme)
  currentTheme.value = themeId as Theme
  isThemePanelOpen.value = false
}

// 处理滚动
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

// 点击外部指令 - Vue3 自定义指令
const vClickOutside = {
  beforeMount(el: HTMLElement, binding: any) {
    el._clickOutside = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el: HTMLElement) {
    if (el._clickOutside) {
      document.removeEventListener('click', el._clickOutside)
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
  // 初始化认证状态
  authStore.initAuth()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 额外的scoped样式 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5%;
  transition: var(--transition-normal);
}

.navbar.scrolled {
  background: var(--bg-elevated);
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}

/* 用户入口样式 */
.nav-user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 6px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  text-decoration: none;
  transition: var(--transition-fast);
}

.nav-user:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 0 15px var(--glow-primary);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--bg-primary);
  overflow: hidden;
}

.nav-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
