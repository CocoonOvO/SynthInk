<!--
  主布局组件
  包含导航栏、页脚，中间是内容区
  老大说要精致，我就整了个玻璃拟态效果
  (´；ω；`) 虽然还没内容，但架子要好看
-->
<template>
  <div class="main-layout">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="nav-container">
        <!-- Logo -->
        <router-link to="/" class="logo">
          <span class="logo-text">SynthInk</span>
        </router-link>
        
        <!-- 导航链接 -->
        <div class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">
            首页
          </router-link>
          <router-link to="/posts" class="nav-link" active-class="active">
            文章
          </router-link>
        </div>
        
        <!-- 右侧操作区 -->
        <div class="nav-actions">
          <!-- 主题切换 -->
          <button class="action-btn" @click="toggleTheme" title="切换主题">
            <el-icon><Moon v-if="themeStore.appliedTheme === 'cyber'" /><Sunny v-else /></el-icon>
          </button>
          
          <!-- 用户菜单 -->
          <template v-if="authStore.isLoggedIn">
            <el-dropdown>
              <span class="user-menu">
                <el-avatar :size="32" :src="authStore.user?.avatar">
                  {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ authStore.user?.username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/user/profile')">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/user/settings')">
                    <el-icon><Setting /></el-icon>账号设置
                  </el-dropdown-item>
                  <el-dropdown-item v-if="authStore.isAdmin" @click="$router.push('/admin')">
                    <el-icon><Management /></el-icon>管理后台
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          
          <template v-else>
            <router-link to="/auth/login" class="login-btn">
              登录
            </router-link>
          </template>
        </div>
      </div>
    </nav>
    
    <!-- 主内容区 -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p class="copyright">
          © 2026 SynthInk. All rights reserved.
        </p>
        <p class="powered">
          Powered by Vue3 + FastAPI
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Moon, Sunny, User, Setting, Management, SwitchButton } from '@element-plus/icons-vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()

// 切换主题
const toggleTheme = () => {
  const themes: Array<'cyber' | 'aurora' | 'sunset'> = ['cyber', 'aurora', 'sunset']
  const currentIndex = themes.indexOf(themeStore.appliedTheme as 'cyber' | 'aurora' | 'sunset')
  const nextTheme = themes[(currentIndex + 1) % themes.length]
  themeStore.setTheme(nextTheme)
}

// 退出登录
const handleLogout = () => {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* 导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 64px;
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  text-decoration: none;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  background: var(--gradient-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: var(--space-lg);
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-glass);
}

.nav-link.active {
  color: var(--accent-primary);
  background: rgba(0, 245, 255, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--bg-glass);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-normal);
}

.action-btn:hover {
  background: var(--bg-card);
  color: var(--accent-primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.user-menu:hover {
  background: var(--bg-glass);
}

.username {
  color: var(--text-secondary);
  font-size: 14px;
}

.login-btn {
  padding: var(--space-sm) var(--space-lg);
  background: var(--gradient-border);
  color: var(--bg-primary);
  text-decoration: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition-normal);
}

.login-btn:hover {
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-top: 64px;
  padding: var(--space-xl);
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

/* 页脚 */
.footer {
  padding: var(--space-xl);
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
}

.copyright {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: var(--space-sm);
}

.powered {
  color: var(--text-secondary);
  font-size: 12px;
}
</style>
