<!--
  首页视图
  展示博客的主要内容和特色
  (´；ω；`) 虽然还没数据，但架子要好看
-->
<template>
  <div class="home-view">
    <!-- Hero区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">探索<span class="gradient-text"> SynthInk</span></h1>
        <p class="hero-subtitle">下一代博客体验，记录你的每一个灵感瞬间</p>
        <div class="hero-actions">
          <router-link to="/posts" class="btn-primary"> 浏览文章 </router-link>
          <router-link v-if="authStore.isLoggedIn" to="/user/posts/new" class="btn-secondary">
            开始写作
          </router-link>
        </div>
      </div>
      <div class="hero-decoration">
        <div class="glow-circle"></div>
      </div>
    </section>

    <!-- 特色功能 -->
    <section class="features-section">
      <h2 class="section-title">特色功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon :size="32"><EditPen /></el-icon>
          </div>
          <h3>优雅写作</h3>
          <p>简洁的编辑器，专注创作本身</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon :size="32"><Collection /></el-icon>
          </div>
          <h3>智能组织</h3>
          <p>标签与分组，轻松管理内容</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon :size="32"><Magic /></el-icon>
          </div>
          <h3>AI 辅助</h3>
          <p>智能建议，提升写作效率</p>
        </div>
      </div>
    </section>

    <!-- 最新文章占位 -->
    <section class="posts-section">
      <div class="section-header">
        <h2 class="section-title">最新文章</h2>
        <router-link to="/posts" class="view-all">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </router-link>
      </div>
      <div class="posts-placeholder">
        <el-empty description="文章列表开发中..." />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { EditPen, Collection, Magic, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.home-view {
  padding-bottom: var(--space-2xl);
}

/* Hero区域 */
.hero-section {
  position: relative;
  padding: var(--space-2xl) 0;
  text-align: center;
  overflow: hidden;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
}

.gradient-text {
  background: var(--gradient-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 20px;
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
}

.hero-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.btn-primary {
  padding: var(--space-md) var(--space-xl);
  background: var(--gradient-border);
  color: var(--bg-primary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 16px;
  transition: var(--transition-normal);
}

.btn-primary:hover {
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

.btn-secondary {
  padding: var(--space-md) var(--space-xl);
  background: var(--bg-card);
  color: var(--text-primary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 16px;
  border: 1px solid var(--border-color);
  transition: var(--transition-normal);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.hero-decoration {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 0;
}

.glow-circle {
  width: 400px;
  height: 400px;
  background: var(--gradient-hero);
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
}

/* 特色功能 */
.features-section {
  padding: var(--space-2xl) 0;
}

.section-title {
  font-size: 32px;
  font-weight: 600;
  text-align: center;
  margin-bottom: var(--space-xl);
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-lg);
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  text-align: center;
  transition: var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

.feature-icon {
  width: 64px;
  height: 64px;
  background: var(--gradient-hero);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-md);
  color: var(--accent-primary);
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 文章区域 */
.posts-section {
  padding: var(--space-2xl) 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

.view-all {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition-normal);
}

.view-all:hover {
  gap: var(--space-sm);
}

.posts-placeholder {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl);
}
</style>
