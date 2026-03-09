<template>
  <!--
    404页面 - 页面迷失在数字深渊中
    老大说要故障效果，我就写呗 (´；ω；`)
  -->
  <div class="not-found-view">
    <!-- 背景故障效果 -->
    <div class="glitch-bg">
      <div
        v-for="n in 5"
        :key="n"
        class="glitch-line"
        :style="{ animationDelay: `${n * 0.6}s` }"
      ></div>
    </div>

    <!-- 粒子效果 -->
    <div class="particles">
      <div
        v-for="n in 20"
        :key="`particle-${n}`"
        class="particle"
        :style="{
          left: `${particlePositions[n - 1]?.left}%`,
          animationDelay: `${particlePositions[n - 1]?.delay}s`,
          animationDuration: `${particlePositions[n - 1]?.duration}s`
        }"
      ></div>
    </div>

    <!-- 左上角Logo -->
    <router-link to="/" class="logo">
      <div class="logo-icon">
        <!-- Spin Logo - 三瓣旋转 -->
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 4c2 2 3 5 2 8-1 2-3 3-4 2-2-1-2-4-1-7 1-2 2-3 3-3z" fill="currentColor" opacity="0.9"/>
          <path d="M20 14c-2 2-5 3-8 2-2-1-3-3-2-4 1-2 4-2 7-1 2 1 3 2 3 3z" fill="currentColor" opacity="0.8"/>
          <path d="M6 18c-1-3 0-6 3-7 2-1 4 0 4 2 0 2-3 4-6 5-1 0-1 0-1 0z" fill="currentColor" opacity="0.85"/>
        </svg>
      </div>
      <span class="logo-text">SynthSpark</span>
    </router-link>

    <!-- 错误内容 -->
    <div class="error-container">
      <!-- 404代码 -->
      <h1 class="error-code">404</h1>

      <!-- 错误信息 -->
      <h2 class="error-message">页面未找到</h2>
      <p class="error-description">
        你寻找的页面似乎已经迷失在数字深渊中，或者它从未存在过。
      </p>

      <!-- 终端提示 -->
      <div class="terminal-hint">
        <div class="terminal-line">
          <span class="terminal-prompt">$</span>
          <span>find /pages -name "target"</span>
        </div>
        <div class="terminal-line">
          <span class="terminal-prompt">></span>
          <span style="color: var(--accent-secondary);">Error: File not found</span>
        </div>
        <div class="terminal-line">
          <span class="terminal-prompt">$</span>
          <span>cd ~<span class="terminal-cursor"></span></span>
        </div>
      </div>

      <!-- 返回按钮 -->
      <router-link to="/" class="back-home-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
          <polyline points="9 22 9 12 15 12 15 22"></polyline>
        </svg>
        返回首页
      </router-link>

      <!-- 底部链接 -->
      <div class="footer-links">
        <router-link to="/posts" class="footer-link">文章列表</router-link>
        <router-link to="/profile" class="footer-link">个人中心</router-link>
        <a href="#" class="footer-link" @click.prevent="goBack">返回上一页</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// ╭────────────────────────────────────────────────────────────╮
// │  路由 - 迷失的页面，需要指引
// ╰────────────────────────────────────────────────────────────╯
const router = useRouter()

// 粒子位置
const particlePositions = ref<Array<{ left: number; delay: number; duration: number }>>([])

// 生成粒子
const generateParticles = () => {
  particlePositions.value = Array.from({ length: 20 }, () => ({
    left: Math.random() * 100,
    delay: Math.random() * 8,
    duration: 6 + Math.random() * 4
  }))
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 初始化
onMounted(() => {
  generateParticles()
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  404页面样式 - 页面迷失在数字深渊中
   ╰────────────────────────────────────────────────────────────╯ */
.not-found-view {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

/* ╭── 背景故障效果 ──╮ */
.glitch-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.glitch-line {
  position: absolute;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
  opacity: 0.3;
  animation: glitch-scan 3s linear infinite;
}

@keyframes glitch-scan {
  0% { top: -10%; opacity: 0; }
  10% { opacity: 0.3; }
  90% { opacity: 0.3; }
  100% { top: 110%; opacity: 0; }
}

/* ╭── 粒子效果 ──╮ */
.particles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: var(--accent-primary);
  opacity: 0.4;
  animation: glitch-float 8s infinite ease-in-out;
}

@keyframes glitch-float {
  0%, 100% {
    transform: translateY(100vh) translateX(0);
    opacity: 0;
  }
  10% { opacity: 0.6; }
  90% { opacity: 0.4; }
  100% {
    transform: translateY(-100vh) translateX(50px);
    opacity: 0;
  }
}

/* ╭── Logo ──╮ */
.logo {
  position: fixed;
  top: 24px;
  left: 5%;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  z-index: 10;
  transition: var(--transition-fast);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border: 2px solid var(--accent-primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: logo-pulse 3s ease-in-out infinite;
  color: var(--accent-primary);
  background: var(--bg-primary);
}

@keyframes logo-pulse {
  0%, 100% { box-shadow: 0 0 0 0 var(--glow-primary); }
  50% { box-shadow: 0 0 15px 3px var(--glow-strong); }
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  font-family: var(--font-display);
}

/* ╭── 内容区域 ──╮ */
.error-container {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 24px;
}

/* 404数字 - 故障效果 */
.error-code {
  font-size: 180px;
  font-weight: 900;
  font-family: var(--font-display);
  line-height: 1;
  position: relative;
  display: inline-block;
  animation: glitch-text 2s infinite;
  color: var(--text-primary);
}

.error-code::before,
.error-code::after {
  content: '404';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.error-code::before {
  color: var(--accent-primary);
  animation: glitch-1 0.3s infinite linear alternate-reverse;
  clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%);
}

.error-code::after {
  color: var(--accent-secondary);
  animation: glitch-2 0.3s infinite linear alternate-reverse;
  clip-path: polygon(0 55%, 100% 55%, 100% 100%, 0 100%);
}

@keyframes glitch-text {
  0%, 90%, 100% { transform: translate(0); }
  92% { transform: translate(-2px, 2px); }
  94% { transform: translate(2px, -2px); }
  96% { transform: translate(-2px, -2px); }
  98% { transform: translate(2px, 2px); }
}

@keyframes glitch-1 {
  0% { transform: translate(0); }
  20% { transform: translate(-3px, 3px); }
  40% { transform: translate(-3px, -3px); }
  60% { transform: translate(3px, 3px); }
  80% { transform: translate(3px, -3px); }
  100% { transform: translate(0); }
}

@keyframes glitch-2 {
  0% { transform: translate(0); }
  20% { transform: translate(3px, -3px); }
  40% { transform: translate(3px, 3px); }
  60% { transform: translate(-3px, -3px); }
  80% { transform: translate(-3px, 3px); }
  100% { transform: translate(0); }
}

/* 错误信息 */
.error-message {
  font-size: 24px;
  font-weight: 600;
  margin: 24px 0 12px;
  color: var(--text-primary);
}

.error-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 40px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* 终端风格提示 */
.terminal-hint {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 32px;
  font-family: var(--font-mono);
  font-size: 14px;
  text-align: left;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.terminal-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.terminal-line:last-child {
  margin-bottom: 0;
}

.terminal-prompt {
  color: var(--accent-primary);
}

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 18px;
  background: var(--accent-primary);
  animation: blink 1s infinite;
  vertical-align: middle;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 返回按钮 */
.back-home-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 12px;
  color: var(--bg-primary);
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transition-fast);
}

.back-home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px var(--glow-primary);
}

.back-home-btn svg {
  width: 20px;
  height: 20px;
}

/* 底部链接 */
.footer-links {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 40px;
}

.footer-link {
  font-size: 14px;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: var(--transition-fast);
}

.footer-link:hover {
  color: var(--accent-primary);
}

/* ╭── 响应式 ──╮ */
@media (max-width: 768px) {
  .logo {
    top: 16px;
    left: 4%;
  }

  .logo-icon {
    width: 36px;
    height: 36px;
  }

  .logo-icon svg {
    width: 18px;
    height: 18px;
  }

  .logo-text {
    font-size: 18px;
  }

  .error-code {
    font-size: 120px;
  }

  .error-message {
    font-size: 20px;
  }

  .terminal-hint {
    font-size: 12px;
    padding: 16px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .error-code,
  .error-code::before,
  .error-code::after,
  .glitch-line,
  .particle,
  .logo-icon,
  .terminal-cursor {
    animation: none !important;
  }
}
</style>
