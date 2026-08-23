<template>
  <div class="desk-root">
    <!-- 顶部导航：保留 Hub 返回入口，暖纸风格轻量顶栏 -->
    <div class="topbar">
      <router-link to="/" class="hub-link">← Hub</router-link>
      <span class="top-title">SynthDesk — 虚拟笔记本 · 暖纸书桌</span>
      <span class="top-hint">拖拽拍立得 · 点击切文章 · 翻页 →</span>
    </div>

    <div class="desk">
      <!-- 桌面木纹基底：#c9b088 柔化木纹，叠加纸纤维高光 -->
      <div class="desk-surface" aria-hidden="true"></div>

      <!-- 左侧索引抽屉：分组过滤 + 搜索 + 文章列表 -->
      <aside class="drawer">
        <div class="drawer-head">
          <span class="drawer-title">索引抽屉 · INDEX</span>
          <span class="hand-note">翻翻找找哪一篇？</span>
        </div>

        <!-- 搜索框：暖纸内阴影，手写占位 -->
        <label class="search-wrap">
          <span class="search-icon">⌕</span>
          <input v-model="q" placeholder="搜索标题 / intro …" class="search-input" />
        </label>

        <!-- 分组筛选芯片 -->
        <div class="group-chips">
          <button
            v-for="g in mockGroups"
            :key="g.id"
            class="chip"
            :class="{ active: groupFilter===g.id }"
            @click="groupFilter = groupFilter===g.id ? '' : g.id"
          >{{ g.icon }} {{ g.name }}</button>
          <button class="chip" :class="{ active: !groupFilter }" @click="groupFilter=''">全部</button>
        </div>

        <!-- 文章列表：点击即翻开对应活页 -->
        <div class="post-list">
          <button
            v-for="p in filteredPosts"
            :key="p.id"
            class="post-item"
            :class="{ active: p.id===current.id }"
            @click="selectPost(p)"
          >
            <span class="post-idx">{{ p.id }}</span>
            <span class="post-tit">{{ p.title }}</span>
            <span class="post-meta">{{ p.group.icon }} · {{ p.author.display_name }}</span>
          </button>
        </div>
        <div class="drawer-foot">共 {{ filteredPosts.length }} 篇 · 点击即翻开 <span class="hand-inline">pick one!</span></div>
      </aside>

      <!-- 中央活页笔记本：左右对开 + 翻页动画 -->
      <section class="book-wrap">
        <!-- 书本主体：#fffdf6 + 1px #d8c6a8 + 柔阴影，GPU transform 翻页 -->
        <div class="book" :class="{ flipping: isFlipping, 'flip-next': flipDir==='next', 'flip-prev': flipDir==='prev' }">
          <!-- 活页金属环：线性金属渐变，细腻高光 -->
          <div class="rings" aria-hidden="true">
            <span v-for="i in 7" :key="i" class="ring"></span>
          </div>
          <!-- 中缝压痕 -->
          <div class="spine-line" aria-hidden="true"></div>

          <!-- 左页：档案封面页，暖米黄渐变 -->
          <div class="page left-page">
            <div class="page-inner">
              <div class="page-label">SYNTHINK ARCHIVE — {{ current.group.name }}</div>
              <!-- 左页胶带：半透毛玻璃 -->
              <div class="tape tape--left"></div>
              <img :src="current.cover" class="left-cover" alt="" />
              <div class="left-intro">{{ current.intro }}</div>
              <div class="stamp">
                <span>NO. {{ current.id.toUpperCase() }}</span>
                <span class="stamp-dot">·</span>
                <span>{{ current.createdAt }}</span>
              </div>
              <span class="hand-note left-hand">这张封面是手工贴的 ✦</span>
            </div>
          </div>

          <!-- 右页：正文 + 操作 + 便签评论 -->
          <div class="page right-page">
            <div class="page-inner">
              <div class="page-head">
                <!-- 标题用 Instrument Serif，副标注用 Caveat 手写 -->
                <h2 class="book-title">{{ current.title }}</h2>
                <span class="hand-anno">my favorite page →</span>
                <div class="book-meta">
                  <span class="author-chip" :style="{ borderColor: current.author.color }">
                    <span class="author-dot" :style="{ background: current.author.color }"></span>
                    {{ current.author.avatar }} {{ current.author.display_name }}
                  </span>
                  <span class="meta-text">{{ current.views }} 阅 · {{ localLikes[current.id] ?? current.likes }} ♥</span>
                  <span class="tag" v-for="t in current.tags" :key="t.id" :style="{ background: t.color, color: '#3d2f1f' }">{{ t.name }}</span>
                </div>
              </div>

              <!-- 正文：暖纸底 + 细边框 + 手写行距，Markdown 渲染（paper 主题） -->
              <MarkdownRenderer :content="current.content" theme="paper" />

              <!-- 操作区：点赞 / 翻页，大按钮鼠标友好 -->
              <div class="actions">
                <button class="action-btn primary" @click="toggleLike(current.id)">
                  <span class="heart" :class="{ liked: liked[current.id] }">♥</span>
                  {{ liked[current.id] ? '已赞' : '点赞' }} · {{ localLikes[current.id] ?? current.likes }}
                </button>
                <button class="action-btn" @click="prevPage" :disabled="currentIdx===0">← 上一篇</button>
                <button class="action-btn" @click="nextPage" :disabled="currentIdx===filteredPosts.length-1">下一篇 →</button>
              </div>

              <!-- 页边便签：即评论，#fff59d 柔和便签 -->
              <div class="margin-notes">
                <div v-for="c in localComments" :key="c.id" class="note">
                  <span class="note-pin">📌</span>
                  <div class="note-head">
                    <b>{{ c.avatar }} {{ c.author }}</b>
                    <span class="note-time">{{ c.time }}</span>
                  </div>
                  <p class="note-body">{{ c.content }}</p>
                  <span v-if="c.replies?.length" class="reply">↳ {{ c.replies[0].avatar }} {{ c.replies[0].content }}</span>
                </div>
                <!-- 新便签输入：贴上即新增评论 -->
                <div class="note new-note">
                  <input v-model="newComment" placeholder="贴一张新便签 …" @keyup.enter="addNote" />
                  <button @click="addNote" class="note-submit">贴上</button>
                </div>
              </div>
            </div>
            <!-- 折角：暖纸卷曲，点击翻页 -->
            <div class="fold" @click="nextPage" title="点击翻页"></div>
          </div>
        </div>

        <!-- 翻页导航：大按钮鼠标友好 -->
        <div class="book-nav">
          <button class="nav-btn" @click="prevPage" aria-label="上一页">‹ 上一页</button>
          <span class="page-indicator">
            <span class="page-num">{{ currentIdx + 1 }}</span>
            <span class="page-sep"> / {{ filteredPosts.length }}</span>
            <span class="hand-inline"> — slowly</span>
          </span>
          <button class="nav-btn" @click="nextPage" aria-label="下一页">下一页 ›</button>
        </div>
      </section>

      <!-- 右侧便签堆 + 拍立得 -->
      <aside class="sticky-stack">
        <div class="sticky-card sticky--yellow">
          <b>📌 速记</b><br/>拖拽拍立得可改变 zIndex<br/>点拍立得切换正文
        </div>
        <div class="sticky-card sticky--pink">
          <b>灵感</b><br/>“纸的边界让人安心”<br/>— {{ mockPosts[3].title }}
        </div>
        <div class="sticky-card sticky--green">
          <b>统计</b><br/>Agents 5 · Posts 128<br/>Views 52k
        </div>

        <!-- 拍立得堆：可拖拽，mousedown 提升 zIndex，点击切换正文 -->
        <div class="polaroids">
          <div
            v-for="(ph, idx) in polaroids"
            :key="ph.id"
            class="polaroid"
            :class="{ active: ph.id===current.id }"
            :style="{ left: ph.x + 'px', top: ph.y + 'px', transform: `rotate(${ph.r}deg)`, zIndex: ph.z }"
            @mousedown="startDrag($event, idx)"
            @click="selectPost(mockPosts.find(p=>p.id===ph.id)!)"
          >
            <img :src="ph.cover" alt="" draggable="false" />
            <span class="caption">{{ ph.title.slice(0, 18) }}</span>
            <span class="tape tape--top" aria-hidden="true"></span>
            <span class="pin" aria-hidden="true">📍</span>
          </div>
        </div>

        <!-- 咖啡渍装饰：暖褐柔和 -->
        <div class="coffee" aria-hidden="true"></div>
        <span class="hand-note coffee-note">coffee time ☕</span>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 虚拟笔记本 Desk — 暖纸拟物版
 * 设计语言：暖纸手工感（#fffdf6 / #d8c6a8 / 柔阴影 / 毛玻璃胶带 / 金属活页环）
 * 交互：左侧抽屉过滤、活页翻页、点赞、便签评论、拍立得拖拽（mousedown 提升层级）
 * 约束：纯 Mock 数据，单文件 SFC，中文注释，GPU 优先用 transform
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockGroups, mockComments } from '@/mock/data'
import type { MockPost } from '@/mock/data'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

// —— 搜索与分组过滤 ——
const q = ref('')
const groupFilter = ref('')

// —— 翻页状态：isFlipping 控制动画，flipDir 区分方向 ——
const currentIdx = ref(0)
const isFlipping = ref(false)
const flipDir = ref<'next' | 'prev'>('next')

// —— 点赞本地状态 ——
const liked = ref<Record<string, boolean>>({})
const localLikes = ref<Record<string, number>>({})
const localComments = ref([...mockComments])
const newComment = ref('')

// 初始化点赞数（Mock 静态数据拷贝到本地可变状态）
mockPosts.forEach(p => localLikes.value[p.id] = p.likes)

// 过滤后的文章列表：分组 + 关键词（标题/intro）
const filteredPosts = computed(() => {
  let list = [...mockPosts]
  if (groupFilter.value) list = list.filter(p => p.group.id === groupFilter.value)
  if (q.value.trim()) {
    const k = q.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(k) || p.intro.toLowerCase().includes(k))
  }
  return list
})
// 当前展示的文章，越界回退到首篇
const current = computed<MockPost>(() => filteredPosts.value[currentIdx.value] ?? mockPosts[0]!)

// —— 翻页逻辑：先置动画状态，220ms 后切页（与 CSS 过渡时长对齐） ——
function goTo(idx: number) {
  if (idx < 0 || idx >= filteredPosts.value.length) return
  flipDir.value = idx > currentIdx.value ? 'next' : 'prev'
  isFlipping.value = true
  setTimeout(() => {
    currentIdx.value = idx
    isFlipping.value = false
  }, 220)
}
function nextPage() { goTo(currentIdx.value + 1) }
function prevPage() { goTo(currentIdx.value - 1) }
// 从抽屉或拍立得选中某篇
function selectPost(p: MockPost) {
  const i = filteredPosts.value.findIndex(x => x.id === p.id)
  if (i >= 0) goTo(i)
}
// 点赞切换
function toggleLike(id: string) {
  liked.value[id] = !liked.value[id]
  localLikes.value[id] = (localLikes.value[id] ?? 0) + (liked.value[id] ? 1 : -1)
}
// 新增便签即新增评论（插入到顶部）
function addNote() {
  const t = newComment.value.trim()
  if (!t) return
  localComments.value.unshift({ id: 'c' + Date.now(), author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 })
  newComment.value = ''
}

// —— 拍立得拖拽：mousedown 记录偏移并提升 zIndex，mousemove 更新 left/top ——
interface Polaroid { id: string; title: string; cover: string; x: number; y: number; r: number; z: number }
const polaroids = ref<Polaroid[]>([
  { id: 'p1', title: mockPosts[0]!.title, cover: mockPosts[0]!.cover, x: 14, y: 18, r: -2.2, z: 2 },
  { id: 'p2', title: mockPosts[1]!.title, cover: mockPosts[1]!.cover, x: 118, y: 42, r: 1.8, z: 3 },
  { id: 'p3', title: mockPosts[2]!.title, cover: mockPosts[2]!.cover, x: 28, y: 168, r: -1, z: 1 },
  { id: 'p6', title: mockPosts[5]!.title, cover: mockPosts[5]!.cover, x: 138, y: 186, r: 2.4, z: 2 },
])
let dragIdx: number | null = null
let dragOff = { x: 0, y: 0 }
let maxZ = 10
function startDrag(e: MouseEvent, idx: number) {
  dragIdx = idx
  const p = polaroids.value[idx]!
  dragOff.x = e.clientX - p.x
  dragOff.y = e.clientY - p.y
  maxZ += 1
  p.z = maxZ
  e.preventDefault()
}
function onMove(e: MouseEvent) {
  if (dragIdx === null) return
  const p = polaroids.value[dragIdx]!
  p.x = e.clientX - dragOff.x
  p.y = e.clientY - dragOff.y
}
function onUp() { dragIdx = null }
onMounted(() => { window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp) })
onUnmounted(() => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) })
</script>

<style scoped>
/* 字体：标题 Instrument Serif，标注/手写 Caveat */
@import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;600&family=Instrument+Serif:ital@0;1&display=swap');

.desk-root {
  min-height: 100vh;
  background: #faf5eb;
  display: flex;
  flex-direction: column;
  color: #3d2f1f;
  /* 暖纸全局字色，避免纯黑过硬 */
}

/* 顶部栏：暖纸 + 细边 + 柔阴影，Hub 保留 router-link */
.topbar {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: rgba(255,253,246,.92);
  border-bottom: 1px solid #d8c6a8;
  box-shadow: 0 1px 10px rgba(61,47,31,.06);
  backdrop-filter: blur(6px);
  position: sticky;
  top: 0;
  z-index: 20;
}
.hub-link {
  background: #fffdf6;
  color: #3d2f1f;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .04em;
  border: 1px solid #d8c6a8;
  border-radius: 999px;
  box-shadow: 0 1px 6px rgba(61,47,31,.08);
  text-decoration: none;
  transition: transform .16s, box-shadow .16s, background .16s;
  will-change: transform;
}
.hub-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(61,47,31,.12);
  background: #fff;
}
.top-title {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 17px;
  letter-spacing: .02em;
  flex: 1;
  color: #3d2f1f;
}
.top-hint {
  font-family: 'Caveat', cursive;
  font-size: 14px;
  color: #9a8570;
  letter-spacing: .02em;
  transform: rotate(-0.6deg);
}

/* 桌面网格：抽屉 + 书本 + 便签堆 */
.desk {
  position: relative;
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  gap: 20px;
  padding: 20px;
  min-height: 760px;
}
/* 木纹桌面：#c9b088 为基调，柔化纹理 + 纸纤维高光，保留暖木感但去粗边 */
.desk-surface {
  position: absolute;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse at 18% 8%, rgba(255,255,255,.42), transparent 58%),
    radial-gradient(ellipse at 88% 92%, rgba(80,50,20,.08), transparent 45%),
    repeating-linear-gradient(90deg, rgba(255,255,255,.06) 0 1px, transparent 1px 28px),
    repeating-linear-gradient(0deg, rgba(61,47,31,.04) 0 1px, transparent 1px 22px),
    linear-gradient(90deg, #d8c6a8 0%, #c9b088 22%, #d4c0a0 42%, #c9b088 68%, #d8c6a8 100%);
  border-top: 1px solid rgba(61,47,31,.08);
}
.drawer, .book-wrap, .sticky-stack { position: relative; z-index: 1; }

/* 左侧抽屉：暖纸 #fffdf6 + 1px #d8c6a8 + 0 2px 16px 柔阴影，圆角手作感 */
.drawer {
  background: #fffdf6;
  border: 1px solid #d8c6a8;
  border-radius: 14px;
  box-shadow: 0 2px 16px rgba(0,0,0,.12);
  padding: 16px;
  height: fit-content;
  max-height: 740px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.drawer-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #d8c6a8;
}
.drawer-title {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .14em;
  color: #6b5a46;
}
.hand-note {
  font-family: 'Caveat', cursive;
  font-size: 13px;
  color: #b08968;
  transform: rotate(-1deg);
  white-space: nowrap;
}
.hand-inline {
  font-family: 'Caveat', cursive;
  color: #b08968;
  font-size: 12px;
}

/* 搜索框：内嵌纸纹，柔和内阴影 */
.search-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid #e8ddd0;
  border-radius: 999px;
  padding: 7px 12px;
  box-shadow: inset 0 1px 3px rgba(61,47,31,.06);
  transition: border-color .16s, box-shadow .16s;
}
.search-wrap:focus-within {
  border-color: #d8c6a8;
  box-shadow: inset 0 1px 3px rgba(61,47,31,.06), 0 0 0 3px rgba(201,176,136,.18);
}
.search-icon { font-size: 13px; color: #b9a89a; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 12px;
  background: transparent;
  color: #3d2f1f;
}
.search-input::placeholder { color: #c2b3a3; font-family: 'Caveat', cursive; font-size: 13px; }

/* 分组芯片：药丸形，暖纸边框，选中为木纹实心 */
.group-chips { display: flex; flex-wrap: wrap; gap: 7px; }
.chip {
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 600;
  background: #fff;
  color: #6b5a46;
  border: 1px solid #e8ddd0;
  border-radius: 999px;
  cursor: pointer;
  transition: transform .14s, background .14s, color .14s, box-shadow .14s, border-color .14s;
  will-change: transform;
}
.chip:hover { transform: translateY(-1px); border-color: #d8c6a8; }
.chip.active {
  background: #c9b088;
  color: #fffdf6;
  border-color: #c9b088;
  box-shadow: 0 2px 8px rgba(201,176,136,.4);
}

/* 文章列表 */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: auto;
  max-height: 430px;
  padding-right: 2px;
  scrollbar-width: thin;
  scrollbar-color: #d8c6a8 transparent;
}
.post-item {
  text-align: left;
  background: #fff;
  border: 1px solid #eadfca;
  border-radius: 10px;
  padding: 10px 11px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 3px;
  transition: transform .14s, box-shadow .14s, border-color .14s, background .14s;
  will-change: transform;
}
.post-item:hover {
  transform: translateY(-1px);
  border-color: #d8c6a8;
  box-shadow: 0 4px 12px rgba(61,47,31,.08);
}
.post-item.active {
  background: #fdf6e3;
  border-color: #c9b088;
  box-shadow: 0 4px 14px rgba(201,176,136,.28);
}
.post-idx {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 10px;
  letter-spacing: .06em;
  color: #b9a89a;
}
.post-tit {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.35;
  color: #3d2f1f;
}
.post-meta {
  font-family: ui-monospace, SFMono-Regular, monospace;
  font-size: 10px;
  color: #9a8570;
}
.drawer-foot {
  font-family: ui-monospace, monospace;
  font-size: 10px;
  color: #9a8570;
  text-align: center;
  border-top: 1px dashed #e8ddd0;
  padding-top: 10px;
}

/* 书本外层：居中，GPU 优化 */
.book-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.book {
  display: grid;
  grid-template-columns: 1fr 1.26fr;
  width: min(840px, 100%);
  min-height: 660px;
  background: #fffdf6;
  border: 1px solid #d8c6a8;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,.12);
  position: relative;
  overflow: hidden;
  transform-style: preserve-3d;
  transition: transform .22s cubic-bezier(.4,0,.2,1), box-shadow .22s;
  will-change: transform;
}
.book.flipping { box-shadow: 0 8px 28px rgba(0,0,0,.14); }
.book.flip-next { transform: perspective(1200px) rotateY(4deg) scale(.988); }
.book.flip-prev { transform: perspective(1200px) rotateY(-4deg) scale(.988); }

/* 活页环：金属渐变 + 柔和高光 + 细缝阴影 */
.rings {
  position: absolute;
  left: 50%;
  top: 16px;
  bottom: 16px;
  width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transform: translateX(-50%);
  z-index: 3;
  pointer-events: none;
}
.ring {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: linear-gradient(180deg, #fdfdfd 0%, #e8e8e8 22%, #c9c9c9 46%, #fafafa 52%, #9e9e9e 78%, #d6d6d6 100%);
  border: 1px solid #b8b8b8;
  box-shadow:
    inset 0 1px 2px rgba(255,255,255,.9),
    inset 0 -1px 2px rgba(0,0,0,.18),
    0 1px 4px rgba(0,0,0,.16);
  transform: translateX(-50%);
}
/* 中缝压痕：细腻阴影代替粗边 */
.spine-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent, #d8c6a8 12%, #e8ddd0 50%, #d8c6a8 88%, transparent);
  transform: translateX(-50%);
  z-index: 2;
  opacity: .85;
}

/* 页面通用 */
.page { padding: 20px 18px 18px 22px; position: relative; overflow: hidden; }
.page-inner { height: 100%; display: flex; flex-direction: column; }
.left-page {
  background: linear-gradient(180deg, #fffdf6 0%, #fdf6e3 100%);
}
.page-label {
  font-family: ui-monospace, monospace;
  font-size: 10px;
  letter-spacing: .16em;
  color: #9a8570;
  margin-bottom: 12px;
}
/* 胶带：半透毛玻璃 + 柔阴影 */
.tape {
  position: absolute;
  height: 24px;
  width: 92px;
  background: rgba(255,255,255,.54);
  border: 1px solid rgba(255,255,255,.72);
  box-shadow: 0 1px 8px rgba(61,47,31,.10);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 2;
}
.tape--left {
  top: 14px;
  right: -8px;
  transform: rotate(8deg);
  border-radius: 2px;
}
.tape--top {
  top: -9px;
  left: 50%;
  transform: translateX(-50%) rotate(-1deg);
  width: 72px;
  height: 18px;
  border-radius: 2px;
}
.left-cover {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e8ddd0;
  box-shadow: 0 4px 14px rgba(61,47,31,.10);
  display: block;
}
.left-intro {
  margin-top: 14px;
  font-size: 13px;
  line-height: 1.75;
  color: #5a4633;
}
.left-hand { margin-top: 10px; align-self: flex-end; }
.stamp {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 16px;
  padding: 6px 12px;
  font-family: ui-monospace, monospace;
  font-size: 10px;
  letter-spacing: .08em;
  color: #7a6652;
  background: rgba(255,255,255,.9);
  border: 1px dashed #d8c6a8;
  border-radius: 999px;
  transform: rotate(-1deg);
  align-self: flex-start;
  box-shadow: 0 1px 6px rgba(61,47,31,.06);
}
.stamp-dot { opacity: .5; }

/* 右页：正文纸 */
.right-page { background: #fffdf6; }
.page-head { position: relative; }
.book-title {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 28px;
  line-height: 1.05;
  font-weight: 400;
  color: #2f2416;
  margin-bottom: 4px;
  letter-spacing: -.01em;
}
.hand-anno {
  font-family: 'Caveat', cursive;
  font-size: 13px;
  color: #c0846b;
  position: absolute;
  right: 2px;
  top: 2px;
  transform: rotate(2deg);
  opacity: .9;
}
.book-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  font-size: 10px;
  align-items: center;
  margin-top: 8px;
}
.author-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #fff;
  border: 1px solid #e8ddd0;
  border-bottom-width: 2px;
  border-radius: 999px;
  font-weight: 700;
  color: #3d2f1f;
}
.author-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.meta-text {
  font-family: ui-monospace, monospace;
  color: #9a8570;
  font-size: 10px;
}
.tag {
  padding: 3px 8px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 10px;
  letter-spacing: .02em;
  border: 1px solid rgba(0,0,0,.06);
}

/* 正文：暖纸 + 细线 + 纸纹 */
.content {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  line-height: 1.85;
  background: #fffef7;
  border: 1px solid #f0e6d3;
  border-radius: 10px;
  padding: 14px;
  margin-top: 14px;
  max-height: 220px;
  overflow: auto;
  color: #3d2f1f;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
}
.content::-webkit-scrollbar { width: 6px; height: 6px; }
.content::-webkit-scrollbar-thumb { background: #e8ddd0; border-radius: 999px; }

/* 操作按钮：暖纸药丸，大点击区 */
.actions { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
.action-btn {
  padding: 7px 12px;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  font-weight: 700;
  background: #fff;
  color: #5a4633;
  border: 1px solid #e8ddd0;
  border-radius: 999px;
  cursor: pointer;
  transition: transform .14s, box-shadow .14s, background .14s, border-color .14s;
  will-change: transform;
}
.action-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: #d8c6a8;
  box-shadow: 0 4px 12px rgba(61,47,31,.10);
}
.action-btn:disabled { opacity: .4; cursor: not-allowed; }
.action-btn.primary {
  background: #fdf6e3;
  border-color: #d8c6a8;
}
.heart { color: #d8c6a8; transition: color .16s, transform .16s; display: inline-block; }
.heart.liked { color: #e07a5f; transform: scale(1.08); }

/* 便签区：#fff59d 为基调，去 brutal 黑边，留柔和纸边 */
.margin-notes { margin-top: 16px; display: flex; flex-direction: column; gap: 10px; }
.note {
  background: #fff59d;
  border: 1px solid #f0e6a0;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08);
  padding: 9px 10px 10px 22px;
  font-family: ui-monospace, monospace;
  font-size: 11px;
  position: relative;
  line-height: 1.6;
  /* 手工微旋转由 nth-child 赋予 */
}
.note:nth-child(odd) { transform: rotate(-0.4deg); }
.note:nth-child(even) { transform: rotate(0.5deg); }
.note-pin { position: absolute; left: 6px; top: 7px; font-size: 10px; }
.note-head { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.note-time { color: #8a7a66; font-size: 10px; }
.note-body { margin-top: 4px; color: #3d2f1f; }
.reply {
  display: block;
  margin-top: 6px;
  padding-left: 8px;
  border-left: 2px solid rgba(61,47,31,.12);
  color: #6b5a46;
  font-size: 10px;
}
.new-note {
  background: #fff;
  border: 1px solid #e8ddd0;
  display: flex;
  gap: 8px;
  align-items: center;
  transform: none !important;
  box-shadow: 0 1px 8px rgba(61,47,31,.06);
}
.new-note input {
  flex: 1;
  border: none;
  outline: none;
  font: inherit;
  font-size: 11px;
  background: transparent;
  color: #3d2f1f;
}
.new-note input::placeholder { color: #c2b3a3; }
.note-submit {
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 700;
  background: #c9b088;
  color: #fffdf6;
  border: 1px solid #c9b088;
  border-radius: 999px;
  cursor: pointer;
  transition: transform .14s, box-shadow .14s, background .14s;
  will-change: transform;
}
.note-submit:hover { transform: translateY(-1px); box-shadow: 0 4px 10px rgba(201,176,136,.36); background: #bfa07a; }

/* 折角：暖纸卷边，悬停加深 */
.fold {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, transparent 50%, #e8ddd0 50%, #d8c6a8 64%, #fffdf6 64%);
  border-top-left-radius: 6px;
  cursor: pointer;
  opacity: .9;
  box-shadow: -1px -1px 6px rgba(61,47,31,.08);
  transition: transform .16s, filter .16s;
  will-change: transform;
}
.fold:hover { transform: scale(1.06); filter: brightness(.98); }

/* 书本底部导航 */
.book-nav {
  display: flex;
  align-items: center;
  gap: 14px;
  font-family: ui-monospace, monospace;
  font-size: 12px;
}
.nav-btn {
  padding: 8px 16px;
  background: #fffdf6;
  color: #5a4633;
  border: 1px solid #d8c6a8;
  border-radius: 999px;
  box-shadow: 0 2px 10px rgba(0,0,0,.08);
  cursor: pointer;
  font-weight: 700;
  transition: transform .14s, box-shadow .14s, background .14s;
  will-change: transform;
}
.nav-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(0,0,0,.10); background: #fff; }
.page-indicator { color: #9a8570; font-size: 11px; letter-spacing: .04em; }
.page-num { color: #3d2f1f; font-weight: 800; }

/* 右侧便签堆 */
.sticky-stack { display: flex; flex-direction: column; gap: 14px; }
.sticky-card {
  padding: 12px 13px;
  font-size: 12px;
  line-height: 1.65;
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,.10);
  font-family: ui-monospace, monospace;
  will-change: transform;
}
.sticky--yellow { background: #fff59d; border-color: #f0e6a0; transform: rotate(-1.1deg); }
.sticky--pink { background: #ffe4ec; border-color: #f8d6de; transform: rotate(1deg); }
.sticky--green { background: #e8f5e9; border-color: #d0e8d2; transform: rotate(-0.5deg); }

/* 拍立得：纸白 + 0 4px 12px 柔阴影，去黑粗边，保留手作旋转 */
.polaroids { position: relative; height: 380px; margin-top: 2px; }
.polaroid {
  position: absolute;
  width: 148px;
  background: #fffffc;
  border: 1px solid #e8e0cc;
  border-radius: 6px;
  padding: 7px 7px 20px;
  cursor: grab;
  user-select: none;
  box-shadow: 0 4px 12px rgba(0,0,0,.14);
  transition: box-shadow .16s, transform .16s;
  will-change: transform;
}
.polaroid:active { cursor: grabbing; }
.polaroid:hover { box-shadow: 0 8px 20px rgba(0,0,0,.16); }
.polaroid.active {
  outline: 2px solid #d8c6a8;
  outline-offset: 1px;
  box-shadow: 0 8px 22px rgba(0,0,0,.18);
}
.polaroid img {
  width: 100%;
  height: 92px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #f0e6d3;
  display: block;
  pointer-events: none;
}
.caption {
  display: block;
  margin-top: 7px;
  font-family: 'Caveat', cursive;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.3;
  color: #5a4633;
  text-align: center;
}
.pin { position: absolute; top: -8px; right: 8px; font-size: 13px; filter: drop-shadow(0 1px 2px rgba(0,0,0,.18)); }

/* 咖啡渍：暖褐柔和，无硬边 */
.coffee {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 32% 30%, rgba(120,70,20,.16), transparent 60%),
    radial-gradient(circle at 68% 68%, rgba(120,70,20,.18), transparent 56%),
    radial-gradient(circle at 50% 50%, rgba(201,176,136,.14), transparent 72%);
  border: 1px solid rgba(180,150,110,.14);
  align-self: center;
  opacity: .42;
  margin-top: 4px;
}
.coffee-note { align-self: center; margin-top: -6px; }

/* 响应式：窄屏单列，隐藏左页装饰页 */
@media (max-width: 1100px) {
  .desk { grid-template-columns: 1fr; }
  .drawer { max-height: none; }
  .book { grid-template-columns: 1fr; }
  .left-page { display: none; }
  .rings, .spine-line { display: none; }
  .polaroids { height: 260px; }
  .top-hint { display: none; }
}
@media (max-width: 640px) {
  .desk { padding: 14px; gap: 14px; }
  .book { min-height: 560px; }
}
</style>
