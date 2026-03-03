<!--
  后台管理布局
  包含侧边栏和顶部栏
  老大说后台要专业点，我就整了个侧边导航
  (´；ω；`) 虽然还没内容，但看起来要像那么回事
-->
<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <!-- Logo -->
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-logo">
          <span v-if="!isCollapsed" class="logo-text">SynthInk</span>
          <span v-else class="logo-short">S</span>
        </router-link>
        <button class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon :size="20">
            <component :is="item.icon" />
          </el-icon>
          <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 底部 -->
      <div class="sidebar-footer">
        <router-link to="/" class="back-link">
          <el-icon><HomeFilled /></el-icon>
          <span v-if="!isCollapsed">返回前台</span>
        </router-link>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="admin-main" :class="{ expanded: isCollapsed }">
      <!-- 顶部栏 -->
      <header class="admin-header">
        <h1 class="page-title">{{ pageTitle }}</h1>
        <div class="header-actions">
          <span class="admin-name">{{ authStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout"> 退出 </el-button>
        </div>
      </header>

      <!-- 内容 -->
      <main class="admin-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Fold,
  Expand,
  HomeFilled,
  DataLine,
  Document,
  User,
  PriceTag,
  FolderOpened,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)

// 菜单项
const menuItems = [
  { path: '/admin', label: '概览', icon: DataLine },
  { path: '/admin/posts', label: '文章管理', icon: Document },
  { path: '/admin/users', label: '用户管理', icon: User },
  { path: '/admin/tags', label: '标签管理', icon: PriceTag },
  { path: '/admin/groups', label: '分组管理', icon: FolderOpened },
]

// 页面标题
const pageTitle = computed(() => {
  const item = menuItems.find((i) => i.path === route.path)
  return item?.label || '管理后台'
})

// 退出登录
const handleLogout = () => {
  authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-md);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-logo {
  text-decoration: none;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-short {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent-primary);
}

.collapse-btn {
  width: 32px;
  height: 32px;
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

.collapse-btn:hover {
  background: var(--bg-card);
  color: var(--accent-primary);
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-md) 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  color: var(--text-secondary);
  text-decoration: none;
  transition: var(--transition-normal);
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--bg-glass);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(0, 245, 255, 0.1);
  color: var(--accent-primary);
  border-left-color: var(--accent-primary);
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
}

.sidebar-footer {
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
}

.back-link {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  transition: var(--transition-normal);
}

.back-link:hover {
  color: var(--accent-primary);
}

/* 主内容区 */
.admin-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  transition: margin-left var(--transition-normal);
}

.admin-main.expanded {
  margin-left: 64px;
}

.admin-header {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  position: sticky;
  top: 0;
  z-index: 10;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.admin-name {
  color: var(--text-secondary);
  font-size: 14px;
}

.admin-content {
  flex: 1;
  padding: var(--space-xl);
  overflow-y: auto;
}
</style>
