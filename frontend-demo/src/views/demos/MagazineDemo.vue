<template>
  <div class="magazine">
    <!-- ========== 顶部 Masthead：杂志刊头 + Hub 返回入口 ========== -->
    <header class="masthead">
      <!-- 顶栏信息条：Hub 链接 / 期号 / 日期 / 地点 -->
      <div class="masthead-meta">
        <router-link to="/" class="hub-link">← Hub</router-link>
        <span class="meta-item mono">VOL. III — No. 08</span>
        <span class="meta-item mono hide-mobile">SYNTHINK EDITORIAL</span>
        <span class="meta-date mono">{{ todayStr }}</span>
        <span class="meta-item mono hide-mobile">PARIS · TOKYO · REMOTE</span>
      </div>
      <!-- 大标题 SYNTHINK：Cormorant Garamond 超大字号，字距压缩 -->
      <h1 class="masthead-title">SYNTHINK</h1>
      <div class="masthead-rule">
        <span class="rule-red"></span>
        <span class="rule-hair"></span>
        <span class="masthead-kicker mono">后现代交互 · 纸上杂志 · 纯前端 Mock · 鼠标友好</span>
        <span class="rule-hair"></span>
        <span class="rule-red"></span>
      </div>
      <!-- 副刊头：价格 / 标语 -->
      <div class="masthead-sub mono">
        <span>PRICE: FREE / OPEN ACCESS</span>
        <span class="sub-center">“把博客重新排成一本可触摸的杂志” — SYNTHINK EDITORIAL — August 2026</span>
        <span>EDITION: DEMO</span>
      </div>
    </header>

    <!-- ========== 工具条：搜索 + 结果统计 + 清除过滤 ========== -->
    <div class="toolbar">
      <label class="search-box">
        <span class="search-icon">⌕</span>
        <input v-model="search" type="text" placeholder="搜索标题 / 导语 / 标签 / 作者 …" class="search-input" />
        <span v-if="search" class="clear-btn mono" @click="search = ''">✕ 清除</span>
      </label>
      <div class="toolbar-right mono">
        <span class="count">{{ filteredGrid.length + (heroVisible ? 1 : 0) }} 篇 · {{ activeFilterLabel }}</span>
        <button v-if="hasActiveFilter" class="reset-btn" @click="clearFilters">重置过滤</button>
      </div>
    </div>

    <!-- ========== 主布局：左侧主内容 + 右侧吸顶目录 ========== -->
    <div class="layout">
      <!-- 主内容区 -->
      <main class="main">
        <!-- Hero 跨栏大图：固定取 mockPosts[1] 作主打，受搜索/过滤联动 -->
        <section v-if="heroVisible && heroPost" class="hero" @click="openPost(heroPost)">
          <div class="hero-media">
            <img :src="heroPost.cover" :alt="heroPost.title" class="hero-img" />
            <span class="hero-badge mono">COVER STORY — {{ heroPost.group.icon }} {{ heroPost.group.name }}</span>
            <span class="hero-kicker mono">FEATURED · 主打</span>
          </div>
          <div class="hero-body">
            <div class="hero-eyebrow mono">
              <span class="eyebrow-red">— No. {{ heroPost.id.toUpperCase() }}</span>
              <span>{{ heroPost.createdAt }} · {{ heroPost.author.display_name }}</span>
              <span class="views mono">{{ getLikes(heroPost.id) }} ♥ · {{ heroPost.views }} 阅读</span>
            </div>
            <h2 class="hero-title">{{ heroPost.title }}</h2>
            <p class="hero-intro">{{ heroPost.intro }}</p>
            <!-- 分栏正文预览：首字下沉 + 双栏排版 -->
            <div class="hero-columns">
              <p class="dropcap">{{ heroPost.content.slice(0, 220) }}…</p>
            </div>
            <div class="hero-tags mono">
              <span v-for="t in heroPost.tags" :key="t.id" class="tag" :style="{ borderColor: t.color }">
                <span class="tag-dot" :style="{ background: t.color }"></span>{{ t.name }}
              </span>
            </div>
            <div class="hero-foot mono">
              <span class="read-more">阅读全文 →</span>
              <span class="hero-hint">点击拉页展开</span>
            </div>
          </div>
        </section>

        <!-- Hero 被过滤时的占位提示 -->
        <section v-else-if="search.trim() || selectedGroup || selectedTag" class="hero-empty mono">
          <span class="empty-icon">⊘</span>
          <span>主打文章不在当前筛选范围内 — 下方仍有 {{ filteredGrid.length }} 篇结果</span>
          <button class="empty-btn" @click="clearFilters">查看全部</button>
        </section>

        <!-- 分隔细线：红线 accent -->
        <div class="section-rule">
          <span class="section-label mono">CONTENTS · 目录 / 本期文章</span>
          <span class="rule-line"></span>
          <span class="rule-red-sm"></span>
        </div>

        <!-- 3 栏 Editorial Grid：卡片分栏排版 -->
        <section class="grid">
          <article
            v-for="post in filteredGrid"
            :key="post.id"
            class="card"
            @click="openPost(post)"
          >
            <div class="card-media">
              <img :src="post.cover" :alt="post.title" class="card-img" loading="lazy" />
              <span class="card-num mono">{{ post.id.toUpperCase() }}</span>
              <span class="card-group mono">{{ post.group.icon }} {{ post.group.name }}</span>
            </div>
            <div class="card-body">
              <div class="card-meta mono">
                <span class="card-date">{{ post.createdAt }}</span>
                <span class="card-dot">·</span>
                <span class="card-author">{{ post.author.avatar }} {{ post.author.display_name }}</span>
              </div>
              <h3 class="card-title">{{ post.title }}</h3>
              <p class="card-intro">{{ post.intro }}</p>
              <!-- 卡片内分栏：模拟杂志小栏排版，column-count -->
              <div class="card-columns mono">
                <p>{{ post.content.replace(/[#`>\\-]/g, '').slice(0, 120) }}…</p>
              </div>
              <div class="card-tags mono">
                <span v-for="t in post.tags" :key="t.id" class="mini-tag" :style="{ background: t.color }">{{ t.name }}</span>
              </div>
              <div class="card-foot mono">
                <span class="like-btn" :class="{ liked: likedSet.has(post.id) }" @click.stop="toggleLike(post.id)">
                  {{ likedSet.has(post.id) ? '♥' : '♡' }} {{ getLikes(post.id) }}
                </span>
                <span>💬 {{ post.comments }}</span>
                <span>👁 {{ post.views }}</span>
                <span class="open-hint">打开 →</span>
              </div>
            </div>
            <!-- 卡片底部红线 hover 显现 -->
            <span class="card-accent"></span>
          </article>
        </section>

        <!-- 空状态 -->
        <div v-if="filteredGrid.length === 0 && !heroVisible" class="empty mono">
          <p class="empty-title">没有匹配的文章</p>
          <p class="empty-desc">试试清空搜索或切换分组 / 标签</p>
          <button class="empty-btn" @click="clearFilters">重置过滤 ✕</button>
        </div>

        <!-- 期末 colophon -->
        <footer class="colophon mono">
          <span>— FIN —</span>
          <span>SYNTHINK MAGAZINE · 编辑部排版实验室 · 2026</span>
          <span>PRINTED IN THE BROWSER · #faf9f6 · #e8e0cc · #c1121f</span>
        </footer>
      </main>

      <!-- ========== 右侧目录（吸顶）：Group / Tag 过滤 + 订阅卡 ========== -->
      <aside class="sidebar">
        <div class="sidebar-inner">
          <!-- 目录标题 -->
          <div class="toc-head">
            <span class="toc-title">目录 · INDEX</span>
            <span class="toc-issue mono">ISSUE 08 / AUG 2026</span>
          </div>

          <div class="toc-rule"></div>

          <!-- 分组过滤 -->
          <div class="toc-section">
            <span class="toc-label mono">分组 / GROUPS</span>
            <div class="group-list">
              <button
                v-for="g in mockGroups"
                :key="g.id"
                class="group-btn"
                :class="{ active: selectedGroup === g.id }"
                @click="selectedGroup = selectedGroup === g.id ? '' : g.id"
              >
                <span class="group-icon">{{ g.icon }}</span>
                <span class="group-name">{{ g.name }}</span>
                <span class="group-count mono">{{ g.count }}</span>
                <span v-if="selectedGroup === g.id" class="group-check">✓</span>
              </button>
              <button class="group-btn all" :class="{ active: !selectedGroup }" @click="selectedGroup = ''">
                <span>—</span><span>全部</span><span class="group-count mono">{{ mockPosts.length }}</span>
              </button>
            </div>
          </div>

          <!-- 标签过滤 -->
          <div class="toc-section">
            <span class="toc-label mono">标签 / TAGS</span>
            <div class="tag-cloud">
              <button
                v-for="t in mockTags"
                :key="t.id"
                class="cloud-tag mono"
                :class="{ active: selectedTag === t.slug }"
                :style="selectedTag === t.slug ? { background: t.color, borderColor: t.color, color: '#fff' } : { borderColor: t.color }"
                @click="selectedTag = selectedTag === t.slug ? '' : t.slug"
              >
                # {{ t.name }}
              </button>
            </div>
          </div>

          <div class="toc-rule dashed"></div>

          <!-- 本期速览：小目录列表 -->
          <div class="toc-section">
            <span class="toc-label mono">本期篇目 · {{ filteredGrid.length + (heroVisible ? 1 : 0) }}</span>
            <ul class="toc-list mono">
              <li v-if="heroVisible && heroPost" class="toc-item hero-item" @click="openPost(heroPost!)">
                <span class="toc-num">{{ heroPost!.id.toUpperCase() }}</span>
                <span class="toc-tit">{{ heroPost!.title }}</span>
                <span class="toc-arrow">↗</span>
              </li>
              <li v-for="p in filteredGrid" :key="p.id" class="toc-item" @click="openPost(p)">
                <span class="toc-num">{{ p.id.toUpperCase() }}</span>
                <span class="toc-tit">{{ p.title }}</span>
                <span class="toc-meta">{{ p.group.name }}</span>
              </li>
            </ul>
          </div>

          <!-- 订阅卡：红底 accent -->
          <div class="subscribe-card">
            <span class="sub-label mono">SUBSCRIBE</span>
            <p class="sub-title">订阅 SYNTHINK<br>纸上杂志</p>
            <p class="sub-desc mono">每月一期 · 排版即内容<br>点击右下角任意文章拉页阅读</p>
            <button class="sub-btn mono" @click="showToast('已订阅（Mock）')">立即订阅 — 免费</button>
          </div>

          <!-- 底部小注 -->
          <div class="sidebar-foot mono">
            <span>图片悬停恢复彩色 · 拉页用 transform</span>
            <span>正文分栏 column-count · 首字下沉</span>
          </div>
        </div>
      </aside>
    </div>

    <!-- ========== 文章 Modal：拉页效果（transform + 遮罩） ========== -->
    <transition name="magazine-modal">
      <div v-if="selectedPost" class="modal-overlay" @click.self="closePost">
        <!-- 拉页面板：perspective 旋转 + 滑入 -->
        <div class="modal-sheet">
          <!-- 顶栏控制 -->
          <div class="modal-top mono">
            <span class="modal-kicker">SYNTHINK — {{ selectedPost.group.icon }} {{ selectedPost.group.name }} — {{ selectedPost.createdAt }}</span>
            <button class="modal-close" @click="closePost">✕ 关闭</button>
          </div>
          <div class="modal-rule">
            <span class="rule-red"></span><span class="rule-hair"></span>
          </div>

          <div class="modal-body">
            <!-- 大字标题区 -->
            <div class="modal-head">
              <h2 class="modal-title">{{ selectedPost.title }}</h2>
              <p class="modal-intro">{{ selectedPost.intro }}</p>
              <div class="modal-meta mono">
                <span class="author-line">{{ selectedPost.author.avatar }} {{ selectedPost.author.display_name }} · {{ selectedPost.author.type }}</span>
                <span>{{ selectedPost.views }} 阅读 · {{ getLikes(selectedPost.id) }} ♥</span>
                <span v-for="t in selectedPost.tags" :key="t.id" class="modal-tag" :style="{ background: t.color }">{{ t.name }}</span>
              </div>
            </div>

            <img :src="selectedPost.cover" :alt="selectedPost.title" class="modal-cover" />

            <!-- 分栏正文：column-count + 首字下沉 + 大留白 -->
            <div class="modal-columns">
              <!-- Markdown 渲染：editorial 主题，替换原文插值以支持富文本 -->
              <MarkdownRenderer :content="selectedPost.content" theme="editorial" />
              <p class="modal-more">
                这是一期纸上杂志的排版实验。所有正文均采用分栏流动（column-count）、首字下沉（::first-letter）与大留白，
                图像默认黑白滤镜，鼠标悬停恢复彩色，交互完全依赖鼠标点击。内容来自 Mock，无需后端。
              </p>
              <p class="modal-more mono small">
                —— 编辑部按 · 2026.08 · #c1121f 红线是本期的唯一强调色。hairline 边框 #e8e0cc 贯穿所有分割线。
                标题使用 Cormorant Garamond，正文与数据使用 Helvetica / 系统无衬线，分栏间隙 2.2rem。
              </p>
            </div>

            <!-- 操作区：本地点赞 + 分享 Mock -->
            <div class="modal-actions mono">
              <button class="action-btn primary" :class="{ liked: likedSet.has(selectedPost.id) }" @click="toggleLike(selectedPost.id)">
                <span class="heart" :class="{ liked: likedSet.has(selectedPost.id) }">♥</span>
                {{ likedSet.has(selectedPost.id) ? '已赞' : '点赞' }} · {{ getLikes(selectedPost.id) }}
              </button>
              <button class="action-btn" @click="showToast('链接已复制（Mock）')">复制链接 ↗</button>
              <button class="action-btn" @click="closePost">继续浏览</button>
              <span class="action-hint hide-mobile">拉页可按 ESC 关闭</span>
            </div>

            <!-- 拉页折角装饰 -->
            <div class="modal-fold" aria-hidden="true"></div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 轻提示 Toast -->
    <transition name="fade">
      <div v-if="toast" class="toast mono">{{ toast }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * MagazineDemo — Editorial 杂志排版
 * 设计语言：米白 #faf9f6 + hairline #e8e0cc + 红线 #c1121f
 * 字体：标题 Cormorant Garamond / 正文与数据 Helvetica Now（回退 Helvetica/Inter）
 * 交互：Masthead 刊头、Hero 跨栏、3 栏 Grid、分栏 column-count、侧栏吸顶目录、拉页 Modal、搜索过滤、本地点赞
 * 约束：纯 Mock（@/mock/data.ts），单文件 SFC，中文注释，ref 管理状态，鼠标友好
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { mockPosts, mockGroups, mockTags } from '@/mock/data'
import type { MockPost } from '@/mock/data'
// 引入 Markdown 渲染器，用于杂志长文 Editorial 主题渲染
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

// —— 响应式状态：搜索 / 过滤 / 选中文章 ——
const search = ref('') // 搜索框，双向绑定，过滤 hero + grid
const selectedGroup = ref('') // 分组过滤（group.id），空字符串为全部
const selectedTag = ref('') // 标签过滤（tag.slug）
const selectedPost = ref<MockPost | null>(null) // 当前拉页的文章，null 则关闭 Modal

// —— 本地点赞：likesMap 存可变点赞数，likedSet 记录已赞 ——
const likesMap = ref<Record<string, number>>({})
const likedSet = ref<Set<string>>(new Set())
// 初始化 Mock 点赞数到本地可变表
for (const p of mockPosts) likesMap.value[p.id] = p.likes

// —— 轻提示 ——
const toast = ref('')
let toastTimer: number | null = null
function showToast(msg: string) {
  toast.value = msg
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => (toast.value = ''), 1600)
}

// —— 日期：Masthead 刊头日期 ——
const todayStr = computed(() => {
  const d = new Date()
  const w = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'][d.getDay()] ?? 'MON'
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} — ${w}`
})

// —— Hero 主打：固定 mockPosts[1]（野蛮网络） ——
const heroPost = computed<MockPost | undefined>(() => mockPosts[1])

// —— 过滤命中判定：标题 / 导语 / 标签 / 作者 / 分组 / 内容 ——
function matchesFilter(post: MockPost): boolean {
  // 分组过滤
  if (selectedGroup.value && post.group.id !== selectedGroup.value) return false
  // 标签过滤
  if (selectedTag.value && !post.tags.some(t => t.slug === selectedTag.value)) return false
  // 关键词搜索（大小写不敏感，覆盖 hero+grid）
  const k = search.value.trim().toLowerCase()
  if (!k) return true
  const hay = `${post.title} ${post.intro} ${post.content} ${post.author.display_name} ${post.group.name} ${post.tags.map(t => t.name).join(' ')}`.toLowerCase()
  return hay.includes(k)
}

// —— Hero 是否可见：受同一套过滤逻辑控制 ——
const heroVisible = computed(() => {
  const h = heroPost.value
  if (!h) return false
  return matchesFilter(h)
})

// —— Grid 列表：除 Hero 外的其余文章，按过滤结果展示（避免与 Hero 重复） ——
const filteredGrid = computed<MockPost[]>(() => {
  return mockPosts.filter(p => {
    if (p.id === heroPost.value?.id && heroVisible.value) return false // Hero 已单独展示则 Grid 去重
    return matchesFilter(p)
  })
})

// —— 过滤标签文案 ——
const activeFilterLabel = computed(() => {
  const parts: string[] = []
  if (selectedGroup.value) {
    const g = mockGroups.find(x => x.id === selectedGroup.value)
    if (g) parts.push(g.name)
  }
  if (selectedTag.value) {
    const t = mockTags.find(x => x.slug === selectedTag.value)
    if (t) parts.push(`#${t.name}`)
  }
  if (search.value.trim()) parts.push(`“${search.value.trim()}”`)
  return parts.length ? parts.join(' · ') : '全部文章'
})
const hasActiveFilter = computed(() => !!(selectedGroup.value || selectedTag.value || search.value.trim()))
function clearFilters() {
  selectedGroup.value = ''
  selectedTag.value = ''
  search.value = ''
}

// —— 点赞与 Modal 控制 ——
function getLikes(id: string): number {
  return likesMap.value[id] ?? 0
}
function toggleLike(id: string) {
  if (likedSet.value.has(id)) {
    likedSet.value.delete(id)
    likesMap.value[id] = Math.max(0, (likesMap.value[id] ?? 1) - 1)
  } else {
    likedSet.value.add(id)
    likesMap.value[id] = (likesMap.value[id] ?? 0) + 1
  }
  // Set 需重建以触发响应式
  likedSet.value = new Set(likedSet.value)
}
function openPost(post: MockPost) {
  selectedPost.value = post
}
function closePost() {
  selectedPost.value = null
}

// —— 锁定 body 滚动：Modal 打开时禁止背景滚动 ——
watch(selectedPost, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
})
// ESC 关闭 Modal
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') closePost()
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ========== 字体引入（标题衬线 + 数据无衬线） ========== */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Inter:wght@400;600;700;800&display=swap');

/* ========== 整体：米白背景 #faf9f6 + 大留白 + hairline #e8e0cc ========== */
.magazine {
  min-height: 100vh;
  background: #faf9f6;
  color: #1a1a18;
  /* 默认无衬线：Helvetica Now → Helvetica → Inter → 系统回退 */
  font-family: 'Helvetica Now Text', Helvetica, 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 0 0 32px;
}

/* 等宽/数据字体辅助 */
.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* ————— Masthead 刊头 ————— */
.masthead {
  border-bottom: 1px solid #e8e0cc;
  background: #faf9f6;
  /* 顶部吸顶时保留刊头气质，但不遮挡吸顶侧栏 */
  position: sticky;
  top: 0;
  z-index: 20;
}
.masthead-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 3%;
  border-bottom: 1px solid #e8e0cc;
  font-size: 10px;
  letter-spacing: 0.08em;
  color: #6b6b60;
  flex-wrap: wrap;
}
/* Hub 入口：必须保留 router-link，hairline 胶囊 */
.hub-link {
  background: #fff;
  color: #1a1a18;
  border: 1px solid #e8e0cc;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-decoration: none;
  transition: transform 0.16s, box-shadow 0.16s, background 0.16s, border-color 0.16s;
}
.hub-link:hover {
  transform: translateY(-1px);
  background: #fff;
  border-color: #d8cfb8;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}
.meta-item {
  padding: 4px 8px;
  background: #fff;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
}
.meta-date {
  margin-left: auto;
  font-weight: 800;
  color: #c1121f;
  letter-spacing: 0.06em;
}
/* 大标题 SYNTHINK */
.masthead-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-weight: 800;
  font-size: clamp(48px, 11vw, 132px);
  line-height: 0.82;
  letter-spacing: -0.04em;
  text-align: center;
  padding: 18px 2% 6px;
  color: #0f0f0e;
}
.masthead-rule {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 3%;
}
.rule-red {
  height: 2px;
  flex: none;
  width: 56px;
  background: #c1121f;
}
.rule-hair {
  height: 1px;
  flex: 1;
  background: #e8e0cc;
}
.masthead-kicker {
  font-size: 10px;
  letter-spacing: 0.14em;
  color: #8a8a7e;
  white-space: nowrap;
  font-weight: 700;
}
.masthead-sub {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 3% 12px;
  font-size: 10px;
  letter-spacing: 0.06em;
  color: #8a8a7e;
  border-top: 1px solid #e8e0cc;
  flex-wrap: wrap;
}
.sub-center {
  text-align: center;
  flex: 1;
  color: #1a1a18;
  font-weight: 600;
}

/* ————— 工具条：搜索 + 统计 ————— */
.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 3%;
  border-bottom: 1px solid #e8e0cc;
  background: rgba(250, 249, 246, 0.92);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 19;
  flex-wrap: wrap;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 260px;
  max-width: 640px;
  background: #fff;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
  padding: 8px 14px;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
  transition: border-color 0.16s, box-shadow 0.16s;
}
.search-box:focus-within {
  border-color: #c1121f;
  box-shadow: 0 0 0 3px rgba(193, 18, 31, 0.08), inset 0 1px 2px rgba(0,0,0,0.03);
}
.search-icon {
  font-size: 14px;
  color: #b8b0a0;
  font-weight: 800;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 13px;
  background: transparent;
  color: #1a1a18;
}
.search-input::placeholder {
  color: #b8b0a0;
}
.clear-btn {
  font-size: 11px;
  font-weight: 700;
  color: #8a8a7e;
  cursor: pointer;
  padding: 4px 8px;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
  background: #faf9f6;
  transition: all 0.15s;
}
.clear-btn:hover {
  color: #c1121f;
  border-color: #c1121f;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: #6b6b60;
  margin-left: auto;
}
.count {
  letter-spacing: 0.04em;
  font-weight: 600;
}
.reset-btn {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  background: #c1121f;
  color: #fff;
  border: 1px solid #a80f1a;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.14s, box-shadow 0.14s;
}
.reset-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(193, 18, 31, 0.22);
}

/* ————— 主布局：main + 吸顶侧栏 ————— */
.layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 28px;
  padding: 24px 3%;
  align-items: start;
}
.main {
  min-width: 0;
}

/* ————— Hero 跨栏大图：左右分栏，hairline 分割 ————— */
.hero {
  display: grid;
  grid-template-columns: 1.25fr 0.95fr;
  gap: 0;
  background: #fff;
  border: 1px solid #e8e0cc;
  cursor: pointer;
  overflow: hidden;
  transition: box-shadow 0.18s, transform 0.18s;
  will-change: transform;
}
.hero:hover {
  box-shadow: 0 10px 32px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}
.hero-media {
  position: relative;
  overflow: hidden;
  background: #f0ece2;
  min-height: 100%;
}
/* 图片黑白滤镜，悬停恢复彩色 */
.hero-img {
  width: 100%;
  height: 100%;
  min-height: 420px;
  object-fit: cover;
  display: block;
  filter: grayscale(100%) contrast(1.04);
  transition: filter 0.45s ease, transform 0.6s ease;
  will-change: filter, transform;
}
.hero:hover .hero-img {
  filter: grayscale(0%) contrast(1);
  transform: scale(1.02);
}
.hero-badge {
  position: absolute;
  left: 12px;
  bottom: 12px;
  background: #fff;
  border: 1px solid #e8e0cc;
  padding: 6px 10px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.hero-kicker {
  position: absolute;
  top: 12px;
  left: 12px;
  background: #c1121f;
  color: #fff;
  padding: 5px 9px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}
.hero-body {
  padding: 22px 22px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-left: 1px solid #e8e0cc;
}
.hero-eyebrow {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 10px;
  letter-spacing: 0.06em;
  color: #8a8a7e;
}
.eyebrow-red {
  color: #c1121f;
  font-weight: 800;
}
.views {
  margin-left: auto;
  background: #faf9f6;
  border: 1px solid #e8e0cc;
  padding: 3px 7px;
  border-radius: 999px;
}
.hero-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(28px, 3.2vw, 38px);
  line-height: 0.95;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #0f0f0e;
}
.hero-intro {
  font-size: 13px;
  line-height: 1.6;
  color: #3a3a36;
  border-left: 3px solid #c1121f;
  padding-left: 12px;
}
.hero-columns {
  margin-top: 4px;
  font-size: 12.5px;
  line-height: 1.75;
  color: #2b2b28;
  /* 正文分栏：双栏杂志感 */
  column-count: 2;
  column-gap: 1.6rem;
  column-rule: 1px solid #e8e0cc;
  text-align: justify;
  hyphens: auto;
}
/* 首字下沉：首字母超大衬线 */
.dropcap::first-letter {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 3.2em;
  font-weight: 800;
  float: left;
  line-height: 0.78;
  margin: 0.08em 0.12em 0 0;
  color: #c1121f;
}
.dropcap {
  margin: 0;
}
.hero-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: #fff;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
}
.tag-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}
.hero-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid #e8e0cc;
  font-size: 11px;
}
.read-more {
  font-weight: 800;
  letter-spacing: 0.06em;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.hero-hint {
  color: #b8b0a0;
  font-style: italic;
}

/* Hero 空状态 */
.hero-empty {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 16px;
  background: #fff;
  border: 1px solid #e8e0cc;
  font-size: 12px;
  color: #6b6b60;
  flex-wrap: wrap;
}
.empty-icon {
  color: #c1121f;
  font-weight: 800;
}

/* 分隔规则线 */
.section-rule {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 28px 0 18px;
}
.section-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  color: #1a1a18;
  white-space: nowrap;
}
.rule-line {
  flex: 1;
  height: 1px;
  background: #e8e0cc;
}
.rule-red-sm {
  width: 32px;
  height: 2px;
  background: #c1121f;
  flex: none;
}

/* ————— 3 栏 Editorial Grid ————— */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.card {
  background: #fff;
  border: 1px solid #e8e0cc;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.18s, box-shadow 0.18s;
  will-change: transform;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(0,0,0,0.07);
}
.card-media {
  position: relative;
  overflow: hidden;
  background: #f0ece2;
  height: 178px;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  /* 黑白滤镜，悬停恢复彩色 */
  filter: grayscale(100%) contrast(1.05);
  transition: filter 0.4s ease, transform 0.55s ease;
  will-change: filter, transform;
}
.card:hover .card-img {
  filter: grayscale(0%) contrast(1);
  transform: scale(1.04);
}
.card-num {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(255,255,255,0.92);
  border: 1px solid #e8e0cc;
  padding: 3px 7px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
}
.card-group {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: #1a1a18;
  color: #fff;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.card-body {
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.card-meta {
  display: flex;
  gap: 6px;
  align-items: center;
  font-size: 10px;
  letter-spacing: 0.04em;
  color: #8a8a7e;
}
.card-dot {
  opacity: 0.5;
}
.card-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 19px;
  line-height: 1.05;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f0f0e;
}
.card-intro {
  font-size: 12px;
  line-height: 1.55;
  color: #3a3a36;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-columns {
  margin-top: 2px;
  font-size: 11px;
  line-height: 1.6;
  color: #5a5a56;
  /* 卡片内小分栏排版 */
  column-count: 2;
  column-gap: 1rem;
  text-align: left;
  border-top: 1px dashed #e8e0cc;
  padding-top: 8px;
}
.card-columns p {
  margin: 0;
}
.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.mini-tag {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 7px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,0.06);
  color: #1a1a18;
}
.card-foot {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid #e8e0cc;
  font-size: 10px;
  color: #8a8a7e;
}
.like-btn {
  cursor: pointer;
  padding: 3px 8px;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
  background: #faf9f6;
  font-weight: 700;
  transition: all 0.14s;
}
.like-btn:hover {
  border-color: #c1121f;
  color: #c1121f;
}
.like-btn.liked {
  background: #c1121f;
  color: #fff;
  border-color: #a80f1a;
}
.open-hint {
  margin-left: auto;
  font-weight: 800;
  color: #1a1a18;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.card-accent {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  background: #c1121f;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.28s ease;
}
.card:hover .card-accent {
  transform: scaleX(1);
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 32px 16px;
  border: 1px dashed #e8e0cc;
  background: #fff;
  margin-top: 18px;
}
.empty-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 22px;
  font-weight: 700;
}
.empty-desc {
  margin-top: 6px;
  font-size: 12px;
  color: #8a8a7e;
}
.empty-btn {
  margin-top: 12px;
  padding: 8px 14px;
  background: #1a1a18;
  color: #fff;
  border: 1px solid #1a1a18;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 999px;
}
.empty-btn:hover {
  background: #c1121f;
  border-color: #a80f1a;
}

/* 期末 colophon */
.colophon {
  margin-top: 28px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 0 0;
  border-top: 1px solid #e8e0cc;
  font-size: 10px;
  letter-spacing: 0.06em;
  color: #8a8a7e;
  flex-wrap: wrap;
  text-align: center;
}

/* ————— 侧栏：吸顶目录 ————— */
.sidebar {
  position: relative;
}
.sidebar-inner {
  position: sticky;
  top: 88px; /* 避开 masthead + toolbar 吸顶高度 */
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.toc-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
}
.toc-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.toc-issue {
  font-size: 10px;
  letter-spacing: 0.08em;
  color: #c1121f;
  font-weight: 800;
  background: #fff;
  border: 1px solid #e8e0cc;
  padding: 4px 8px;
  border-radius: 999px;
}
.toc-rule {
  height: 1px;
  background: #e8e0cc;
}
.toc-rule.dashed {
  background: none;
  border-top: 1px dashed #e8e0cc;
  height: 0;
}
.toc-section {
  background: #fff;
  border: 1px solid #e8e0cc;
  padding: 12px 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.toc-label {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #1a1a18;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e0cc;
}
.group-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.group-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #faf9f6;
  border: 1px solid #e8e0cc;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  text-align: left;
  transition: all 0.14s;
  will-change: transform;
}
.group-btn:hover {
  transform: translateY(-1px);
  border-color: #d8cfb8;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.group-btn.active {
  background: #1a1a18;
  color: #fff;
  border-color: #1a1a18;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.group-btn.active .group-count {
  color: rgba(255,255,255,0.7);
}
.group-btn.all {
  border-style: dashed;
}
.group-icon {
  font-size: 13px;
}
.group-name {
  flex: 1;
}
.group-count {
  font-size: 10px;
  color: #8a8a7e;
  background: rgba(0,0,0,0.04);
  padding: 2px 6px;
  border-radius: 999px;
}
.group-btn.active .group-count {
  background: rgba(255,255,255,0.12);
}
.group-check {
  color: #c1121f;
  font-weight: 800;
}
.group-btn.active .group-check {
  color: #fff;
}
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.cloud-tag {
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  background: #fff;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.14s, background 0.14s, color 0.14s, box-shadow 0.14s;
  will-change: transform;
}
.cloud-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.cloud-tag.active {
  box-shadow: 0 3px 10px rgba(193, 18, 31, 0.2);
}
.toc-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #e8e0cc;
  border: 1px solid #e8e0cc;
}
.toc-item {
  display: grid;
  grid-template-columns: 42px 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 9px 10px;
  background: #fff;
  cursor: pointer;
  transition: background 0.14s;
}
.toc-item:hover {
  background: #faf9f6;
}
.toc-item.hero-item {
  background: #1a1a18;
  color: #fff;
}
.toc-item.hero-item:hover {
  background: #242422;
}
.toc-num {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #c1121f;
}
.toc-item.hero-item .toc-num {
  color: #ff6b6b;
}
.toc-tit {
  font-size: 11px;
  font-weight: 700;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.toc-meta, .toc-arrow {
  font-size: 10px;
  color: #8a8a7e;
}
.toc-item.hero-item .toc-meta,
.toc-item.hero-item .toc-arrow {
  color: rgba(255,255,255,0.6);
}

/* 订阅卡：红底强调，hairline 内描边 */
.subscribe-card {
  background: #c1121f;
  color: #fff;
  padding: 16px;
  border: 1px solid #a80f1a;
  position: relative;
  overflow: hidden;
}
.subscribe-card::after {
  content: '';
  position: absolute;
  inset: 8px;
  border: 1px solid rgba(255,255,255,0.18);
  pointer-events: none;
}
.sub-label {
  font-size: 10px;
  letter-spacing: 0.14em;
  font-weight: 800;
  opacity: 0.9;
}
.sub-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 22px;
  line-height: 0.95;
  font-weight: 800;
  margin-top: 8px;
}
.sub-desc {
  margin-top: 8px;
  font-size: 11px;
  line-height: 1.6;
  opacity: 0.9;
}
.sub-btn {
  margin-top: 14px;
  width: 100%;
  padding: 10px 12px;
  background: #fff;
  color: #c1121f;
  border: 1px solid #fff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: transform 0.14s, box-shadow 0.14s;
}
.sub-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.18);
}
.sidebar-foot {
  font-size: 10px;
  line-height: 1.6;
  color: #8a8a7e;
  text-align: center;
  border-top: 1px dashed #e8e0cc;
  padding-top: 10px;
}

/* ————— Modal 拉页：遮罩 + transform 滑入 ————— */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(26, 26, 24, 0.38);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 28px 3% 32px;
  overflow: auto;
  z-index: 60;
}
.modal-sheet {
  width: min(860px, 100%);
  background: #fffefb;
  border: 1px solid #e8e0cc;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18), 0 1px 0 rgba(255,255,255,0.8) inset;
  overflow: hidden;
  /* 拉页 transform 入场：由 transition 控制 */
  transform-origin: top center;
}
.modal-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  font-size: 10px;
  letter-spacing: 0.06em;
  color: #8a8a7e;
  background: #faf9f6;
  border-bottom: 1px solid #e8e0cc;
}
.modal-kicker {
  font-weight: 700;
  color: #1a1a18;
}
.modal-close {
  padding: 6px 12px;
  background: #1a1a18;
  color: #fff;
  border: 1px solid #1a1a18;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 999px;
  transition: background 0.14s;
}
.modal-close:hover {
  background: #c1121f;
  border-color: #a80f1a;
}
.modal-rule {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 0 18px;
  background: #faf9f6;
}
.modal-body {
  padding: 22px 22px 26px;
  position: relative;
}
.modal-head {
  max-width: 680px;
  margin: 0 auto;
  text-align: center;
}
.modal-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(32px, 4.5vw, 48px);
  line-height: 0.9;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #0f0f0e;
}
.modal-intro {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #3a3a36;
  border-top: 1px solid #e8e0cc;
  border-bottom: 1px solid #e8e0cc;
  padding: 12px 0;
}
.modal-meta {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 12px;
  font-size: 11px;
  color: #6b6b60;
}
.modal-tag {
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid rgba(0,0,0,0.06);
  font-weight: 700;
  color: #1a1a18;
}
.author-line {
  font-weight: 800;
  color: #1a1a18;
}
.modal-cover {
  width: 100%;
  height: 360px;
  object-fit: cover;
  display: block;
  margin-top: 18px;
  border: 1px solid #e8e0cc;
  /* Modal 封面亦用黑白滤镜，悬停恢复 */
  filter: grayscale(100%) contrast(1.04);
  transition: filter 0.4s;
}
.modal-cover:hover {
  filter: grayscale(0%) contrast(1);
}
.modal-columns {
  margin-top: 20px;
  font-size: 14px;
  line-height: 1.85;
  color: #1a1a18;
  /* 分栏：双栏 magazine 排版，大留白 */
  column-count: 2;
  column-gap: 2.2rem;
  column-rule: 1px solid #e8e0cc;
  text-align: justify;
  hyphens: auto;
}
.modal-columns p {
  margin: 0 0 1em;
}
.modal-dropcap::first-letter {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 3.6em;
  font-weight: 800;
  float: left;
  line-height: 0.78;
  margin: 0.08em 0.14em 0 0;
  color: #c1121f;
}
.modal-more {
  break-inside: avoid;
}
.modal-more.small {
  font-size: 11px;
  line-height: 1.7;
  color: #6b6b60;
  background: #faf9f6;
  border: 1px solid #e8e0cc;
  padding: 10px 12px;
}
.modal-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid #e8e0cc;
  font-size: 11px;
}
.action-btn {
  padding: 8px 14px;
  font-size: 11px;
  font-weight: 700;
  background: #fff;
  color: #1a1a18;
  border: 1px solid #e8e0cc;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.14s, box-shadow 0.14s, background 0.14s, color 0.14s;
}
.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-color: #d8cfb8;
}
.action-btn.primary {
  background: #faf9f6;
  border-color: #e8e0cc;
}
.action-btn.primary.liked {
  background: #c1121f;
  color: #fff;
  border-color: #a80f1a;
}
.heart {
  color: #d8cfb8;
  transition: color 0.14s, transform 0.14s;
  display: inline-block;
}
.heart.liked {
  color: #fff;
  transform: scale(1.1);
}
.action-hint {
  margin-left: auto;
  color: #b8b0a0;
  font-style: italic;
}
/* 折角：暖纸卷曲，transform 轻微立体 */
.modal-fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, transparent 50%, #e8ddd0 50%, #d8c6a8 64%, #fffefb 64%);
  border-top-left-radius: 8px;
  box-shadow: -1px -1px 8px rgba(0,0,0,0.06);
  pointer-events: none;
}

/* ————— 过渡动画：Modal 拉页用 transform ————— */
.magazine-modal-enter-active {
  transition: opacity 0.22s ease;
}
.magazine-modal-leave-active {
  transition: opacity 0.18s ease;
}
.magazine-modal-enter-from,
.magazine-modal-leave-to {
  opacity: 0;
}
.magazine-modal-enter-active .modal-sheet {
  animation: sheetIn 0.42s cubic-bezier(0.16, 1, 0.3, 1);
}
.magazine-modal-leave-active .modal-sheet {
  animation: sheetOut 0.22s ease forwards;
}
@keyframes sheetIn {
  from {
    opacity: 0;
    transform: perspective(1200px) rotateX(10deg) translateY(32px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: perspective(1200px) rotateX(0deg) translateY(0) scale(1);
  }
}
@keyframes sheetOut {
  from {
    opacity: 1;
    transform: perspective(1200px) rotateX(0deg) translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: perspective(1200px) rotateX(4deg) translateY(16px) scale(0.98);
  }
}

/* ————— Toast ————— */
.toast {
  position: fixed;
  left: 50%;
  bottom: 26px;
  transform: translateX(-50%);
  background: #1a1a18;
  color: #fff;
  padding: 10px 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: 999px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  z-index: 80;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 6px);
}

/* ————— 响应式 ————— */
@media (max-width: 1100px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .sidebar-inner {
    position: static;
  }
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-body {
    border-left: none;
    border-top: 1px solid #e8e0cc;
  }
  .hero-img {
    min-height: 320px;
  }
  .hero-columns,
  .modal-columns {
    column-count: 1;
  }
  .card-columns {
    column-count: 1;
  }
}
@media (max-width: 640px) {
  .masthead-title {
    font-size: 52px;
  }
  .masthead-kicker {
    display: none;
  }
  .meta-date {
    margin-left: 0;
  }
  .toolbar {
    position: static;
  }
  .grid {
    grid-template-columns: 1fr;
  }
  .modal-overlay {
    padding: 0;
    align-items: flex-start;
  }
  .modal-sheet {
    border-left: none;
    border-right: none;
  }
  .modal-cover {
    height: 220px;
  }
  .hide-mobile {
    display: none !important;
  }
}
</style>
