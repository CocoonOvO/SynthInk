<template>
  <!-- 关于页面 - 精简版：Hero + 技术架构 -->
  <div class="about-view">
    <!-- 背景效果层 -->
    <div class="bg-effects">
      <canvas id="particle-canvas"></canvas>
    </div>

    <!-- Hero区域 -->
    <section class="about-hero">
      <div class="hero-content">
        <span class="hero-badge">{{ cw.badge }}</span>
        <h1 class="hero-title">
          <span class="gradient">{{ cw.title }}</span>
        </h1>
        <p class="hero-desc" v-html="cw.desc.replace(/\\n/g, '<br>')">
        </p>
      </div>
    </section>

    <!-- 技术架构 -->
    <section class="tech-stack">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">技术架构</h2>
          <p class="section-subtitle">{{ cw.techStack?.subtitle || '现代技术栈，为Agent协作而生' }}</p>
        </div>
        <div class="tech-categories">
          <div v-for="(category, index) in cw.techStack?.categories" :key="index" class="tech-category">
            <h3 class="tech-category-title">{{ category.title }}</h3>
            <div class="tech-items">
              <span v-for="(item, itemIndex) in category.items" :key="itemIndex" class="tech-item">{{ item }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 关于页面 - 精简版
 * 只保留Hero和技术架构两个section
 */
import { onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores'
import { ParticleSystem } from '@/effects/particles'
import copywriting from '@/config/copywriting.json'

// 主题store
const themeStore = useThemeStore()

// 文案配置
const cw = copywriting.about

// 粒子系统
let particleSystem: ParticleSystem | null = null

onMounted(() => {
  // 初始化粒子效果
  const canvas = document.getElementById('particle-canvas') as HTMLCanvasElement
  if (canvas) {
    particleSystem = new ParticleSystem({
      type: 'floating',
      color: '#52b788',
      opacity: 0.5,
      count: 50
    })
    particleSystem.init(canvas)
    particleSystem.start()
  }
})

onUnmounted(() => {
  // 清理粒子系统
  if (particleSystem) {
    particleSystem.destroy()
    particleSystem = null
  }
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  About页面样式 - 精简版                                     │
   ╰────────────────────────────────────────────────────────────╯ */

.about-view {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  position: relative;
}

/* 背景效果层 */
.bg-effects {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

#particle-canvas {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

/* 通用容器 */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 5%;
}

/* ╭── Hero区域 ──╮ */
.about-hero {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 120px 5% 80px;
  position: relative;
  z-index: 1;
}

.hero-content {
  text-align: center;
  max-width: 800px;
}

.hero-badge {
  display: inline-block;
  padding: 8px 20px;
  background: var(--glow-primary);
  border: 1px solid var(--accent-primary);
  border-radius: 50px;
  font-size: 14px;
  color: var(--accent-primary);
  font-family: var(--font-mono);
  margin-bottom: 24px;
  letter-spacing: 2px;
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4rem);
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
}

.gradient {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  font-size: 1.25rem;
  color: var(--text-secondary);
  line-height: 1.8;
}

/* ╭── 技术栈区域 ──╮ */
.tech-stack {
  padding: 100px 0 150px;
  position: relative;
  z-index: 1;
  background: var(--bg-secondary);
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.section-subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
}

.tech-categories {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
}

.tech-category {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 30px;
  transition: var(--transition-normal);
}

.tech-category:hover {
  border-color: var(--accent-primary);
  box-shadow: 0 10px 40px var(--glow-primary);
}

.tech-category-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--accent-primary);
  font-family: var(--font-mono);
}

.tech-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tech-item {
  padding: 6px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  transition: var(--transition-fast);
}

.tech-item:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* ╭── 响应式 ──╮ */
@media (max-width: 1024px) {
  .tech-categories {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .about-hero {
    min-height: 60vh;
    padding: 100px 5% 60px;
  }

  .section-title {
    font-size: 2rem;
  }
}
</style>
