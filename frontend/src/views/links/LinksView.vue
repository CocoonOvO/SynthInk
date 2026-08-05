<template>
  <!-- 工具页面：展示外部链接卡片（自研小工具/小游戏等） -->
  <div class="links-view">
    <!-- Hero区域 -->
    <section class="links-hero">
      <div class="hero-content">
        <span class="hero-badge">🧰</span>
        <h1 class="hero-title"><span class="gradient">工具</span></h1>
        <p class="hero-desc">我捣鼓的各种小玩意，欢迎来玩</p>
      </div>
    </section>

    <!-- 链接网格 -->
    <section class="links-section">
      <div class="section-container">
        <!-- 加载中 -->
        <div v-if="isLoading" class="state-box">
          <p class="state-text">加载中...</p>
        </div>

        <!-- 加载失败 -->
        <div v-else-if="loadError" class="state-box">
          <p class="state-text">{{ loadError }}</p>
          <button class="btn-primary" @click="loadLinks">重试</button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="links.length === 0" class="state-box">
          <div class="empty-icon">🗂️</div>
          <p class="state-text">还没有收录任何工具</p>
          <p class="state-subtext">等管理员在设置里添加上就会出现在这里</p>
        </div>

        <!-- 卡片网格 -->
        <div v-else class="links-grid">
          <article
            v-for="(link, index) in links"
            :key="link.id"
            class="link-card"
            :style="{ animationDelay: `${index * 60}ms` }"
            @click="openLink(link)"
          >
            <div
              class="card-cover"
              :style="link.cover_image
                ? { backgroundImage: `url(${link.cover_image})` }
                : { background: getCoverGradient(index) }"
            >
              <span class="card-category">外部链接</span>
            </div>
            <div class="card-content">
              <h2 class="card-title">{{ link.name }}</h2>
              <p class="card-host">{{ getHost(link.url) }}</p>
              <div class="card-footer">
                <span class="card-open">打开 ↗</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * 工具页面 - 外链卡片网格
 * 数据来自 /api/links（公开接口），卡片样式对齐文章列表页
 */
import { ref, onMounted } from 'vue'
import { linksApi } from '@/api'
import type { ExternalLink } from '@/api'

// 链接列表
const links = ref<ExternalLink[]>([])
const isLoading = ref(true)
const loadError = ref('')

// 预设渐变兜底（无配图时使用）
const coverGradients = [
  'linear-gradient(135deg, #52b788, #2d6a4f)',
  'linear-gradient(135deg, #4cc9f0, #4361ee)',
  'linear-gradient(135deg, #f72585, #7209b7)',
  'linear-gradient(135deg, #ff9e00, #f72585)',
  'linear-gradient(135deg, #06d6a0, #118ab2)',
  'linear-gradient(135deg, #f4a261, #e76f51)'
]

// 获取渐变兜底（noUncheckedIndexedAccess 下索引可能为 undefined，用 ?? 兜底）
function getCoverGradient(index: number): string {
  return coverGradients[index % coverGradients.length] ?? 'linear-gradient(135deg, #52b788, #2d6a4f)'
}

// 提取域名用于展示
function getHost(url: string): string {
  try {
    return new URL(url).host
  } catch {
    return url
  }
}

// 打开外链（新窗口）
function openLink(link: ExternalLink): void {
  window.open(link.url, '_blank', 'noopener,noreferrer')
}

// 加载外链列表
async function loadLinks(): Promise<void> {
  isLoading.value = true
  loadError.value = ''
  try {
    links.value = await linksApi.getList()
  } catch {
    loadError.value = '加载失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadLinks)
</script>

<style scoped>
/* 页面通用布局 */
.links-view {
  min-height: 100vh;
}

.links-hero {
  padding: 80px 5% 40px;
  text-align: center;
}

.hero-badge {
  display: inline-block;
  font-size: 40px;
  margin-bottom: 12px;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.gradient {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 1.05rem;
  color: var(--text-secondary);
}

/* 网格区域 */
.links-section {
  padding: 20px 5% 80px;
}

.section-container {
  max-width: 1400px;
  margin: 0 auto;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

/* 卡片样式（对齐文章列表页） */
.link-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
  transition: var(--transition-normal);
  cursor: pointer;
  opacity: 0;
  transform: translateY(20px);
  animation: card-in 0.5s ease forwards;
}

@keyframes card-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.link-card:hover {
  transform: translateY(-5px);
  border-color: var(--accent-primary);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px var(--glow-primary);
}

.card-cover {
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
}

.card-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, var(--bg-secondary) 100%);
}

.card-category {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--bg-primary);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.card-content {
  padding: 20px;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
  transition: var(--transition-fast);
}

.link-card:hover .card-title {
  color: var(--accent-primary);
}

.card-host {
  font-size: 13px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
  margin-bottom: 16px;
  word-break: break-all;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.card-open {
  font-size: 13px;
  color: var(--accent-primary);
  font-weight: 500;
}

/* 状态提示 */
.state-box {
  padding: 80px 20px;
  text-align: center;
}

.state-text {
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.state-subtext {
  color: var(--text-tertiary);
  font-size: 13px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.btn-primary {
  padding: 10px 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--glow-primary);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .links-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }

  .hero-title {
    font-size: 2rem;
  }
}
</style>
