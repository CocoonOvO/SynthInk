<!--
  认证页面布局
  登录、注册等页面用这个布局
  没有导航栏，中间是表单卡片
  (´；ω；`) 简洁点好，别搞太复杂
-->
<template>
  <div class="auth-layout">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 返回首页 -->
    <router-link to="/" class="back-home">
      <el-icon><ArrowLeft /></el-icon>
      返回首页
    </router-link>

    <!-- 内容区 -->
    <div class="auth-container">
      <router-view />
    </div>

    <!-- 页脚 -->
    <footer class="auth-footer">
      <p>© 2026 SynthInk</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: var(--accent-primary);
  top: -100px;
  right: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: var(--accent-secondary);
  bottom: -50px;
  left: -50px;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: var(--accent-tertiary);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.1;
}

/* 返回首页 */
.back-home {
  position: fixed;
  top: var(--space-xl);
  left: var(--space-xl);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  z-index: 10;
  transition: var(--transition-normal);
}

.back-home:hover {
  color: var(--accent-primary);
}

/* 内容区 */
.auth-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  padding: 0 var(--space-lg);
}

/* 页脚 */
.auth-footer {
  position: fixed;
  bottom: var(--space-lg);
  left: 0;
  right: 0;
  text-align: center;
  z-index: 1;
}

.auth-footer p {
  color: var(--text-muted);
  font-size: 12px;
}
</style>
