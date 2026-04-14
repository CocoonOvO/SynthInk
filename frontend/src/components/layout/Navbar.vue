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

    <!-- 移动端汉堡菜单按钮 -->
    <button 
      class="mobile-menu-toggle"
      :class="{ active: isMobileMenuOpen }"
      @click="toggleMobileMenu"
      aria-label="切换菜单"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>

    <!-- 桌面端导航链接 -->
    <ul class="nav-links desktop-only">
      <li v-for="item in cw.navItems" :key="item.path">
        <router-link :to="item.path">{{ item.label }}</router-link>
      </li>
    </ul>

    <!-- 移动端菜单 - 包含导航链接和操作按钮 -->
    <div class="mobile-menu" :class="{ open: isMobileMenuOpen }">
      <!-- 移动端导航链接 - 统一为按钮样式 -->
      <div class="mobile-nav-links">
        <router-link 
          v-for="item in cw.navItems" 
          :key="item.path"
          :to="item.path" 
          class="mobile-nav-btn"
          @click="closeMobileMenu"
        >
          <!-- 首页图标 -->
          <svg v-if="item.path === '/'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          <!-- 文章图标 -->
          <svg v-else-if="item.path === '/posts'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          <!-- 关于图标 -->
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>{{ item.label }}</span>
        </router-link>
      </div>
      
      <!-- 移动端操作区 -->
      <div class="mobile-actions">
        <!-- 写作按钮 - 只有登录后才显示 -->
        <router-link v-if="authStore.isLoggedIn" to="/write" class="mobile-action-btn" @click="closeMobileMenu">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
          </svg>
          <span>开始创作</span>
        </router-link>

        <!-- 主题选择器 -->
        <button class="mobile-action-btn" @click.stop="toggleThemePanel">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          <span>切换主题</span>
        </button>

        <!-- 登录/用户入口 -->
        <router-link v-if="!authStore.isLoggedIn" to="/login" class="mobile-action-btn mobile-login" @click="closeMobileMenu">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
            <polyline points="10 17 15 12 10 7"/>
            <line x1="15" y1="12" x2="3" y2="12"/>
          </svg>
          <span>登录</span>
        </router-link>
        <router-link v-else to="/profile" class="mobile-action-btn" @click="closeMobileMenu">
          <span class="user-avatar-small">
            <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" alt="头像">
            <span v-else>{{ authStore.user?.username?.[0]?.toUpperCase() || 'U' }}</span>
          </span>
          <span>{{ authStore.user?.username || '用户' }}</span>
        </router-link>
      </div>
    </div>

    <!-- 桌面端右侧操作区 -->
    <div class="nav-actions desktop-only">
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

// 移动端菜单状态
const isMobileMenuOpen = ref(false)

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// 处理窗口大小变化
const handleResize = () => {
  if (window.innerWidth > 768) {
    isMobileMenuOpen.value = false
  }
}

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
  window.addEventListener('resize', handleResize)
  handleScroll()
  // 初始化认证状态
  authStore.initAuth()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
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

/* 桌面端/移动端显示控制 */
.desktop-only {
  display: flex;
}

.mobile-menu {
  display: none;
}

/* 移动端汉堡菜单按钮 */
.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  gap: 5px;
  z-index: 1001;
  margin-left: auto;
}

.mobile-menu-toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--text-primary);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.mobile-menu-toggle.active span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.mobile-menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.mobile-menu-toggle.active span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* 响应式样式 - 移动端 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 4%;
  }

  .desktop-only {
    display: none !important;
  }

  .mobile-menu-toggle {
    display: flex;
  }

  /* 移动端菜单 */
  .mobile-menu {
    display: block;
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    background: var(--bg-elevated);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-subtle);
    transform: translateY(-150%);
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 999;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    max-height: calc(100vh - 70px);
    overflow-y: auto;
  }

  .mobile-menu.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  /* 移动端导航链接 - 列表样式 */
  .mobile-nav-links {
    display: flex;
    flex-direction: column;
    margin: 0;
    padding: 0;
  }

  .mobile-nav-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 5%;
    color: var(--text-primary);
    font-size: 16px;
    text-decoration: none;
    cursor: pointer;
    transition: var(--transition-fast);
    border-bottom: 1px solid var(--border-subtle);
  }

  .mobile-nav-btn:last-child {
    border-bottom: none;
  }

  .mobile-nav-btn:hover {
    background: var(--bg-secondary);
  }

  .mobile-nav-btn svg {
    flex-shrink: 0;
    opacity: 0.7;
  }

  /* 移动端操作区 - 列表样式 */
  .mobile-actions {
    display: flex;
    flex-direction: column;
    padding: 0;
    border-top: 8px solid var(--bg-secondary);
  }

  .mobile-action-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 5%;
    background: transparent;
    border: none;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-primary);
    font-size: 16px;
    text-decoration: none;
    cursor: pointer;
    transition: var(--transition-fast);
    width: 100%;
    text-align: left;
  }

  .mobile-action-btn:last-child {
    border-bottom: none;
  }

  .mobile-action-btn:hover {
    background: var(--bg-secondary);
  }

  .mobile-action-btn svg {
    flex-shrink: 0;
    opacity: 0.7;
  }

  .mobile-login {
    color: var(--accent-primary);
    font-weight: 500;
  }

  .user-avatar-small {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 600;
    color: var(--bg-primary);
    overflow: hidden;
    flex-shrink: 0;
  }

  .user-avatar-small img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* 移动端主题面板调整 */
  .theme-panel {
    position: fixed;
    top: 70px;
    left: 0;
    right: 0;
    width: 100%;
    max-height: calc(100vh - 80px);
    overflow-y: auto;
    border-radius: 0;
    border: none;
    border-bottom: 1px solid var(--border-subtle);
  }
}

/* 小屏幕手机额外优化 */
@media (max-width: 375px) {
  .nav-logo-text {
    font-size: 16px;
  }
}
</style>
