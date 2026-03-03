<!--
  404页面
  页面找不到时显示
  (´；ω；`) 虽然没人想看到这个页面
-->
<template>
  <div class="not-found-view">
    <div class="error-content">
      <div class="error-code">
        <span class="digit">4</span>
        <span class="digit glitch">0</span>
        <span class="digit">4</span>
      </div>
      <h1 class="error-title">页面不存在</h1>
      <p class="error-message">抱歉，您访问的页面可能已经搬家了，或者从未存在过</p>
      <div class="error-actions">
        <router-link to="/" class="btn-primary">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </router-link>
        <button class="btn-secondary" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </button>
      </div>
    </div>

    <!-- 装饰元素 -->
    <div class="decoration">
      <div class="grid"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled, ArrowLeft } from '@element-plus/icons-vue'
</script>

<style scoped>
.not-found-view {
  min-height: calc(100vh - 64px - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.error-content {
  text-align: center;
  z-index: 1;
}

.error-code {
  font-size: 120px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: var(--space-md);
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
}

.digit {
  background: var(--gradient-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.digit.glitch {
  animation: glitch 2s infinite;
}

@keyframes glitch {
  0%,
  100% {
    transform: translate(0);
  }
  20% {
    transform: translate(-2px, 2px);
  }
  40% {
    transform: translate(2px, -2px);
  }
  60% {
    transform: translate(-2px, -2px);
  }
  80% {
    transform: translate(2px, 2px);
  }
}

.error-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.error-message {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
}

.error-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  background: var(--gradient-border);
  color: var(--bg-primary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition-normal);
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition-normal);
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 装饰背景 */
.decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  mask-image: radial-gradient(ellipse at center, black 0%, transparent 70%);
}
</style>
