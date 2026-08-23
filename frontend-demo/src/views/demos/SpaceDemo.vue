<template>
  <!-- 顶栏：始终可见的 Hub 返回 + 模式切换 -->
  <div class="space" :class="[`mode-${mode}`, { dragging: isDragging }]">
    <nav class="top mono">
      <div class="top-left">
        <!-- 需求：顶部必须有回到 Hub 的 router-link -->
        <router-link to="/" class="hub-link brutal-border">← Hub</router-link>
        <span class="top-title">SynthSpace — 3D 空间画廊</span>
        <span class="top-sub hide-mobile">拖拽漫游 · 滚轮缩放 · 悬停发光 · 点击推门</span>
      </div>
      <div class="top-right">
        <!-- 模式切换：星系 / 画廊 / 俯瞰，三种布局用 CSS transform 差异化 -->
        <div class="mode-switch brutal-border">
          <button
            class="mode-btn mono"
            :class="{ active: mode === 'galaxy' }"
            @click="mode = 'galaxy'"
            title="纵深环形 · 星系"
          >
            ⬢ 星系
          </button>
          <button
            class="mode-btn mono"
            :class="{ active: mode === 'gallery' }"
            @click="mode = 'gallery'"
            title="墙面网格 · 画廊"
          >
            ▦ 画廊
          </button>
          <button
            class="mode-btn mono"
            :class="{ active: mode === 'overlook' }"
            @click="mode = 'overlook'"
            title="俯瞰缩放 · 城市地图"
          >
            ◎ 俯瞰
          </button>
        </div>
        <button class="reset-btn mono brutal-border" @click="resetView">⟲ 复位</button>
        <span class="zoom-badge mono brutal-border">×{{ zoom.toFixed(2) }}</span>
      </div>
    </nav>

    <div class="layout">
      <!-- 左侧 HUD：分组过滤 + 标签云 + 统计，纯 Mock 鼠标点击 -->
      <aside class="hud brutal-border">
        <div class="hud-head mono">
          <span class="hud-title">HUD / 导航</span>
          <span class="hud-sub">{{ filteredPosts.length }} / {{ mockPosts.length }} 篇</span>
        </div>

        <!-- 分组芯片：点击仅显示该分组，带飞入动画（TransitionGroup） -->
        <section class="hud-section">
          <div class="sec-title mono">▣ Group · 分组过滤</div>
          <div class="chips">
            <button
              class="chip mono brutal-border"
              :class="{ active: selectedGroup === 'all' }"
              @click="selectedGroup = 'all'"
            >
              全部 <i>{{ mockPosts.length }}</i>
            </button>
            <button
              v-for="g in mockGroups"
              :key="g.id"
              class="chip mono brutal-border"
              :class="{ active: selectedGroup === g.id }"
              @click="selectedGroup = g.id === selectedGroup ? 'all' : g.id"
              :title="`只看 ${g.name}`"
            >
              <span>{{ g.icon }} {{ g.name }}</span>
              <i>{{ g.count }}</i>
            </button>
          </div>
          <div class="hud-hint mono">点芯片过滤 · 再次点击取消 · 带飞入动画</div>
        </section>

        <!-- 标签云：展示所有标签，点击可叠加过滤 -->
        <section class="hud-section">
          <div class="sec-title mono">◎ Tag Cloud · 标签云</div>
          <div class="tag-cloud">
            <button
              v-for="t in mockTags"
              :key="t.id"
              class="tag mono brutal-border"
              :class="{ active: selectedTagId === t.id }"
              :style="{ background: selectedTagId === t.id ? t.color : '#fff', borderColor: '#0a0a0f' }"
              @click="selectedTagId = selectedTagId === t.id ? null : t.id"
            >
              #{{ t.name }}
            </button>
          </div>
          <div class="hud-hint mono">标签叠加过滤 · 点亮即筛选</div>
        </section>

        <!-- 统计：基于 Mock，纯前端计算 -->
        <section class="hud-section stats">
          <div class="sec-title mono">◉ Stats · 统计</div>
          <div class="stat-grid mono">
            <div class="stat brutal-border"><span>POSTS</span><b>{{ mockPosts.length }}</b></div>
            <div class="stat brutal-border"><span>GROUP</span><b>{{ mockGroups.length }}</b></div>
            <div class="stat brutal-border"><span>TAGS</span><b>{{ mockTags.length }}</b></div>
            <div class="stat brutal-border"><span>VIEWS</span><b>{{ mockStats.total_views.toLocaleString() }}</b></div>
            <div class="stat brutal-border"><span>FILTERED</span><b>{{ filteredPosts.length }}</b></div>
            <div class="stat brutal-border"><span>MODE</span><b>{{ modeLabel }}</b></div>
          </div>
          <div class="scale-row mono">
            <span>缩放 {{ (zoom * 100).toFixed(0) }}% · 偏移 {{ offset.x.toFixed(0) }},{{ offset.y.toFixed(0) }}</span>
            <span class="muted">拖拽空白漫游·滚轮缩放</span>
          </div>
        </section>

        <div class="hud-foot mono">
          <span>GPU：transform3d · will-change</span>
          <span>粒子：Canvas 40 点 · RAF</span>
        </div>
      </aside>

      <!-- 主视口：全屏画布区，Canvas 星点 + CSS 3D 视差世界 -->
      <section
        ref="viewportRef"
        class="viewport brutal-border"
        @mousedown="onDown"
        @mousemove="onViewportMouse"
        @wheel="onWheel"
      >
        <!-- 背景：Canvas 粒子星点（30-50 点），RAF 驱动，不触发重排 -->
        <canvas ref="starCanvas" class="star-canvas" aria-hidden="true"></canvas>
        <!-- 装饰：晕影与网格地板，随模式微变 -->
        <div class="vignette" aria-hidden="true"></div>
        <div class="grid-floor" aria-hidden="true"></div>
        <div class="scan-glow" aria-hidden="true"></div>

        <!-- 世界容器：统一承载平移与缩放，GPU 加速 -->
        <div class="world" :style="worldStyle">
          <!-- 透视容器：星系/画廊/俯瞰的不同透视 -->
          <div class="perspective" :class="mode">
            <!-- 卡片舞台：TransitionGroup 实现过滤飞入动画 -->
            <TransitionGroup name="fly" tag="div" class="stage">
              <article
                v-for="(p, idx) in filteredPosts"
                :key="p.id"
                class="card brutal-border"
                :class="{ hovered: hoveredId === p.id }"
                :style="cardStyle(p, idx)"
                @mouseenter="hoveredId = p.id"
                @mouseleave="hoveredId = null"
                @click="openDetail(p)"
              >
                <!-- 卡片封面：保持比例，视差中保持清晰 -->
                <div class="card-cover brutal-border">
                  <img :src="p.cover" :alt="p.title" loading="lazy" draggable="false" />
                  <!-- 分组角标 -->
                  <span class="group-badge mono brutal-border" :style="{ background: p.tags[0]?.color || '#ffd700' }">
                    {{ p.group.icon }} {{ p.group.name }}
                  </span>
                  <!-- 悬停时显示的标签浮层 -->
                  <div class="cover-tags mono" :class="{ show: hoveredId === p.id }">
                    <span v-for="t in p.tags" :key="t.id" class="cover-tag brutal-border" :style="{ background: t.color }">{{ t.name }}</span>
                  </div>
                </div>
                <div class="card-body">
                  <h3 class="card-title display">{{ p.title }}</h3>
                  <p class="card-intro mono">{{ p.intro }}</p>
                  <div class="card-meta mono">
                    <span class="author"><span class="av" :style="{ background: p.author.color }">{{ p.author.avatar }}</span> {{ p.author.display_name }}</span>
                    <span class="meta-right">{{ p.createdAt }} · 👁 {{ p.views }}</span>
                  </div>
                  <!-- 标签行：默认可见，悬停发光增强 -->
                  <div class="card-tags mono">
                    <span v-for="t in p.tags" :key="t.id" class="card-tag brutal-border" :style="{ background: t.color }">#{{ t.name }}</span>
                  </div>
                  <div class="card-foot mono">
                    <span>♥ {{ getLikes(p.id) }} · 💬 {{ p.comments }}</span>
                    <span class="push-hint">点击推门 →</span>
                  </div>
                </div>
                <!-- 悬停发光层 -->
                <div class="glow" aria-hidden="true"></div>
              </article>
            </TransitionGroup>
          </div>
        </div>

        <!-- 视口浮动提示 -->
        <div class="viewport-hint mono">
          <span>拖拽空白处漫游 · 滚轮缩放 · 悬停发光 · 点击推门</span>
          <span class="hide-mobile">{{ modeHint }}</span>
        </div>

        <!-- 准星 / 中心点装饰 -->
        <div class="crosshair" aria-hidden="true">＋</div>
      </section>
    </div>

    <!-- 详情 Modal：点击推门，缩放动画，展示封面/正文/评论/点赞本地计数 -->
    <Transition name="modal">
      <div v-if="selected" class="modal-overlay" @click.self="closeDetail" @wheel.stop>
        <div class="modal brutal-border brutal-shadow">
          <button class="modal-close mono brutal-border" @click="closeDetail" title="关闭">× 关闭</button>
          <div class="modal-cover brutal-border">
            <img :src="selected.cover" :alt="selected.title" />
            <span class="modal-group mono brutal-border" :style="{ background: selected.tags[0]?.color || '#ffd700' }">
              {{ selected.group.icon }} {{ selected.group.name }} · {{ selected.group.slug }}
            </span>
          </div>
          <div class="modal-body">
            <h2 class="modal-title display">{{ selected.title }}</h2>
            <p class="modal-intro mono">{{ selected.intro }}</p>
            <div class="modal-meta mono brutal-border">
              <span class="author-line"><span class="av" :style="{ background: selected.author.color }">{{ selected.author.avatar }}</span> {{ selected.author.display_name }} @{{ selected.author.username }} · {{ selected.author.type }}</span>
              <span>{{ selected.createdAt }} · 👁 {{ selected.views }}</span>
            </div>
            <div class="modal-tags mono">
              <span v-for="t in selected.tags" :key="t.id" class="modal-tag brutal-border" :style="{ background: t.color }">{{ t.name }}</span>
            </div>
            <!-- 正文：保留换行与代码块质感 -->
            <pre class="modal-content mono brutal-border">{{ selected.content }}</pre>

            <!-- 操作：点赞本地计数 -->
            <div class="modal-actions mono">
              <button class="act-btn brutal-border" :class="{ liked: likedSet.has(selected.id) }" @click="toggleLike(selected.id)">
                {{ likedSet.has(selected.id) ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(selected.id) }}
              </button>
              <span class="muted">💬 {{ localComments.length }} 评论 · 本地 Mock 不会上传</span>
              <button class="act-btn brutal-border" @click="shareMock">↗ 分享（Mock）</button>
            </div>

            <!-- 评论区：本地输入与列表 -->
            <div class="comments">
              <div class="comments-head mono">评论 · {{ localComments.length }}</div>
              <div class="comment-input-row brutal-border">
                <input
                  v-model="newComment"
                  class="comment-input mono"
                  placeholder="写点什么… 回车发送（本地）"
                  @keydown.enter="addComment"
                />
                <button class="comment-send mono brutal-border" @click="addComment">发送</button>
              </div>
              <div v-for="c in localComments" :key="c.id" class="comment brutal-border">
                <div class="comment-head mono">
                  <span><b>{{ c.avatar }} {{ c.author }}</b> · {{ c.time }}</span>
                  <span>♥ {{ c.likes }}</span>
                </div>
                <p class="comment-body mono">{{ c.content }}</p>
                <div v-if="c.replies && c.replies.length" class="replies">
                  <div v-for="r in c.replies" :key="r.id" class="reply mono brutal-border">
                    <b>{{ r.avatar }} {{ r.author }}</b>：{{ r.content }} <span class="muted">· {{ r.time }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
/**
 * SynthSpace — 浏览器内 3D 空间画廊
 * 单文件 Vue SFC，中文注释，无新增依赖，纯 Mock 鼠标友好
 * 核心：HTML+CSS 3D 视差 + 单 Canvas 2D 星点，GPU 加速（transform3d / will-change）
 * 交互：拖拽平移（mousedown+mousemove）、滚轮缩放、悬停发光、点击推门 Modal
 * 状态：用 ref 管理 posts 位置、缩放、偏移、选中 等
 */
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { mockPosts, mockGroups, mockTags, mockStats, mockComments, type MockPost } from '@/mock/data'

// —— 模式：星系（纵深环形）/ 画廊（墙面网格）/ 俯瞰（等轴缩放） ——
type Mode = 'galaxy' | 'gallery' | 'overlook'
const mode = ref<Mode>('galaxy')
const modeLabel = computed(() => (mode.value === 'galaxy' ? '星系' : mode.value === 'gallery' ? '画廊' : '俯瞰'))
const modeHint = computed(() =>
  mode.value === 'galaxy'
    ? '星系：环形纵深 · 近大远小'
    : mode.value === 'gallery'
      ? '画廊：墙面网格 · 正视平铺'
      : '俯瞰：45° 轴测 · 地图感',
)

// —— 用 ref 管理：位置 / 缩放 / 偏移 / 选中 （满足题目要求） ——
const offset = ref({ x: 0, y: 0 }) // 视口平移偏移（拖拽产生）
const zoom = ref(1) // 缩放（滚轮产生），范围 0.6~2.2
const hoveredId = ref<string | null>(null) // 悬停卡片 id
const selected = ref<MockPost | null>(null) // 选中推门详情
const selectedGroup = ref<string>('all') // HUD 分组过滤
const selectedTagId = ref<number | null>(null) // 标签云过滤（可叠加）

// —— 视口与 Canvas 引用 ——
const viewportRef = ref<HTMLElement | null>(null)
const starCanvas = ref<HTMLCanvasElement | null>(null)

// —— 拖拽状态（鼠标友好） ——
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const startOffset = ref({ x: 0, y: 0 })

// —— 鼠标视差（RAF 驱动，不触发重排） ——
const mouse = ref({ x: 0, y: 0 }) // 视口内鼠标坐标
const smoothMouse = ref({ x: 0, y: 0 }) // 平滑后的视差偏移
const timeRef = ref(0) // RAF 时间，用于浮动与星点闪烁

// —— 点赞与评论（本地 Mock） ——
const likesMap = ref<Record<string, number>>({})
const likedSet = ref<Set<string>>(new Set())
const localComments = ref<typeof mockComments>([])
const newComment = ref('')

for (const p of mockPosts) likesMap.value[p.id] = p.likes
localComments.value = JSON.parse(JSON.stringify(mockComments))

function getLikes(id: string): number { return likesMap.value[id] ?? 0 }
function toggleLike(id: string): void {
  if (likedSet.value.has(id)) {
    likedSet.value.delete(id)
    likesMap.value[id] = Math.max(0, (likesMap.value[id] ?? 1) - 1)
  } else {
    likedSet.value.add(id)
    likesMap.value[id] = (likesMap.value[id] ?? 0) + 1
  }
  likedSet.value = new Set(likedSet.value)
}
function addComment(): void {
  const t = newComment.value.trim()
  if (!t) return
  localComments.value = [
    { id: `c-${Date.now()}`, author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 },
    ...localComments.value,
  ]
  newComment.value = ''
}
function shareMock(): void {
  // 仅本地提示，不请求后端
  // 使用临时 toast 效果：复用 hover 文案位置，简单 alert 替代
  if (typeof window !== 'undefined') window.alert('链接已复制（Mock）')
}

// —— 过滤后的文章（Group + Tag 双重过滤） ——
const filteredPosts = computed<MockPost[]>(() => {
  let arr = [...mockPosts]
  if (selectedGroup.value !== 'all') arr = arr.filter(p => p.group.id === selectedGroup.value)
  if (selectedTagId.value !== null) arr = arr.filter(p => p.tags.some(t => t.id === selectedTagId.value))
  return arr
})

// —— 世界容器样式：统一平移 + 缩放，GPU 加速 ——
const worldStyle = computed(() => ({
  transform: `translate3d(${offset.value.x}px, ${offset.value.y}px, 0) scale(${zoom.value})`,
  willChange: 'transform' as const,
}))

// —— 卡片布局计算：三种模式的 base 位置（x/y/z/scale/rotate） ——
interface Layout { x: number; y: number; z: number; scale: number; ry: number; rx: number }
function layoutFor(idx: number, total: number, m: Mode): Layout {
  // 星系：椭圆环形纵深，近大远小，带深度 z
  if (m === 'galaxy') {
    const angle = (idx / total) * Math.PI * 2 - Math.PI / 2
    const radiusX = 380
    const radiusY = 240
    const x = Math.cos(angle) * radiusX
    const y = Math.sin(angle) * radiusY
    const z = Math.cos(angle) * 160 // 纵深：正面大、背面小
    const scale = 0.88 + (z + 160) / 320 * 0.32 // 0.88~1.20
    const ry = -angle * 0.14 // 轻微朝向圆心
    return { x, y, z, scale, ry, rx: 2 }
  }
  // 画廊：墙面网格，正视平铺，z 微起伏
  if (m === 'gallery') {
    const cols = 3
    const col = idx % cols
    const row = Math.floor(idx / cols)
    const x = (col - 1) * 360
    const y = (row - 0.5) * 420 // 6 篇 = 2 行，居中
    const z = (idx % 2 === 0 ? 18 : -16) + (col === 1 ? 14 : 0)
    return { x, y, z, scale: 1, ry: 0, rx: 0 }
  }
  // 俯瞰：等轴 45° 俯视，间距收紧，整体缩小
  const cols = 3
  const col = idx % cols
  const row = Math.floor(idx / cols)
  const x = (col - 1) * 300
  const y = (row - 0.5) * 320
  const z = -30
  return { x, y, z, scale: 0.84, ry: 0, rx: 0 }
}

// —— 卡片内联样式：transform3d + 悬停放大发光 + 视差 + 浮动 ——
function cardStyle(post: MockPost, idx: number): Record<string, string> {
  const total = filteredPosts.value.length || 1
  const base = layoutFor(idx, total, mode.value)
  // 悬停：放大 1.08 并提升 z
  const isHover = hoveredId.value === post.id
  const hoverScale = isHover ? 1.08 : 1
  const hoverZ = isHover ? 28 : 0
  // 浮动：基于 RAF 时间的正弦上下浮动，深度越浅浮动越大
  const floatY = Math.sin(timeRef.value * 0.0012 + idx * 0.9) * (mode.value === 'galaxy' ? 10 : 6)
  const floatX = Math.cos(timeRef.value * 0.0009 + idx * 1.1) * 3
  // 视差：鼠标位置对每张卡片的微偏移，深度越大视差越强
  const depthFactor = (base.z + 160) / 320 // 0~1
  const parallaxX = smoothMouse.value.x * depthFactor * 0.045
  const parallaxY = smoothMouse.value.y * depthFactor * 0.045
  const finalScale = base.scale * hoverScale
  // 俯瞰模式下卡片轻微倾斜，模拟地图
  const tiltX = mode.value === 'overlook' ? 42 : base.rx
  const tiltY = base.ry
  // 组合 transform：全部用 3D，避免重排
  const transform = `translate3d(${base.x + parallaxX + floatX}px, ${base.y + parallaxY + floatY}px, ${base.z + hoverZ}px) scale3d(${finalScale}, ${finalScale}, 1) rotateY(${tiltY}rad) rotateX(${tiltX}deg)`
  // 视差深度对应的透明度与模糊：越远越淡（仅星系生效）
  const opacity = mode.value === 'galaxy' ? String(0.78 + depthFactor * 0.22) : '1'
  const zIndex = String(Math.round(100 + base.z))
  return {
    transform,
    opacity,
    zIndex,
    willChange: 'transform, opacity',
  }
}

// —— 交互：拖拽漫游（mousedown+mousemove 平移） ——
function onDown(e: MouseEvent): void {
  // 点击到卡片/按钮/HUD 不触发拖拽，直接推门或过滤
  const target = e.target as HTMLElement
  if (target.closest('.card') || target.closest('.hud') || target.closest('.top') || target.closest('.modal')) return
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
  startOffset.value = { x: offset.value.x, y: offset.value.y }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
  e.preventDefault()
}
function onMove(e: MouseEvent): void {
  if (!isDragging.value) return
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  // 直接更新 offset，触发 world transform，无重排
  offset.value = { x: startOffset.value.x + dx, y: startOffset.value.y + dy }
}
function onUp(): void {
  isDragging.value = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
}
function onViewportMouse(e: MouseEvent): void {
  const el = viewportRef.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  mouse.value = { x: e.clientX - cx, y: e.clientY - cy }
}

// —— 滚轮缩放（wheel 缩放，带阻尼与边界） ——
function onWheel(e: WheelEvent): void {
  // 在 Modal 内不缩放世界
  const target = e.target as HTMLElement
  if (target.closest('.modal')) return
  const delta = -e.deltaY * 0.0012
  const next = zoom.value + delta
  zoom.value = Math.min(2.2, Math.max(0.58, next))
}

// —— 推门详情（缩放动画由 Transition 完成） ——
function openDetail(post: MockPost): void { selected.value = post }
function closeDetail(): void { selected.value = null }
function resetView(): void {
  offset.value = { x: 0, y: 0 }
  zoom.value = 1
  mouse.value = { x: 0, y: 0 }
  smoothMouse.value = { x: 0, y: 0 }
}

// —— Canvas 星点粒子（30-50 点，RAF 驱动，纯 2D） ——
interface Star { x: number; y: number; r: number; alpha: number; tw: number; vx: number; vy: number; phase: number }
let stars: Star[] = []
let rafStar = 0
let rafMain = 0

function initStars(canvas: HTMLCanvasElement): void {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const rect = canvas.getBoundingClientRect()
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.scale(dpr, dpr)
  const w = rect.width
  const h = rect.height
  const count = 42 // 30-50 之间
  stars = Array.from({ length: count }, () => ({
    x: Math.random() * w,
    y: Math.random() * h,
    r: Math.random() * 1.6 + 0.4,
    alpha: Math.random() * 0.5 + 0.35,
    tw: Math.random() * 0.02 + 0.008,
    vx: (Math.random() - 0.5) * 0.18,
    vy: (Math.random() - 0.5) * 0.14,
    phase: Math.random() * Math.PI * 2,
  }))
}

function drawStars(): void {
  const canvas = starCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  const rect = canvas.getBoundingClientRect()
  const w = rect.width
  const h = rect.height
  // 清空：用半透明覆盖制造拖尾星云感
  ctx.clearRect(0, 0, w, h)
  // 背景渐变（深空）
  const grad = ctx.createRadialGradient(w * 0.72, h * 0.28, 0, w * 0.5, h * 0.5, Math.max(w, h) * 0.9)
  grad.addColorStop(0, 'rgba(255,0,110,0.10)')
  grad.addColorStop(0.35, 'rgba(0,245,212,0.06)')
  grad.addColorStop(1, 'rgba(10,10,15,0)')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, w, h)

  // 绘制星点与连线
  for (const s of stars) {
    // 闪烁 alpha
    s.phase += s.tw
    const a = s.alpha + Math.sin(s.phase) * 0.18
    // 漂移
    s.x += s.vx
    s.y += s.vy
    if (s.x < -6) s.x = w + 6
    if (s.x > w + 6) s.x = -6
    if (s.y < -6) s.y = h + 6
    if (s.y > h + 6) s.y = -6

    ctx.beginPath()
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(244,244,240,${Math.max(0, Math.min(1, a))})`
    // 发光外晕
    ctx.shadowColor = 'rgba(244,244,240,0.9)'
    ctx.shadowBlur = s.r * 3
    ctx.fill()
    ctx.shadowBlur = 0
  }
  // 轻量连线：距离 < 90 的星点连淡线，营造星系感
  ctx.strokeStyle = 'rgba(244,244,240,0.08)'
  ctx.lineWidth = 0.7
  for (let i = 0; i < stars.length; i++) {
    for (let j = i + 1; j < stars.length; j++) {
      const a = stars[i], b = stars[j]
      if (!a || !b) continue
      const dx = a.x - b.x
      const dy = a.y - b.y
      const dist = Math.hypot(dx, dy)
      if (dist < 92) {
        const op = (1 - dist / 92) * 0.18
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.globalAlpha = op
        ctx.stroke()
      }
    }
  }
  ctx.globalAlpha = 1
}

// —— 主 RAF：驱动视差平滑 + 时间浮动 + 星点 ——
function loopMain(now: number): void {
  timeRef.value = now
  // 平滑鼠标视差（lerp 0.08），避免抖动
  smoothMouse.value.x += (mouse.value.x - smoothMouse.value.x) * 0.08
  smoothMouse.value.y += (mouse.value.y - smoothMouse.value.y) * 0.08
  // 星点绘制（节流到每帧）
  drawStars()
  rafMain = requestAnimationFrame(loopMain)
}

function onResize(): void {
  const c = starCanvas.value
  if (c) initStars(c)
}

// —— 监听模式切换：重置视差，避免突变 ——
watch(mode, async () => {
  // 轻微复位缩放，保证三种布局都可见
  if (mode.value === 'overlook') zoom.value = 0.92
  else if (mode.value === 'gallery') zoom.value = 1
  else zoom.value = 1
  await nextTick()
})

// —— 生命周期：初始化 Canvas 与 RAF ——
onMounted(() => {
  const c = starCanvas.value
  if (c) initStars(c)
  window.addEventListener('resize', onResize)
  rafMain = requestAnimationFrame(loopMain)
  // 兼容：若用户直接滚轮，先阻止页面滚动穿透
  const vp = viewportRef.value
  if (vp) vp.addEventListener('wheel', (e) => e.preventDefault(), { passive: false } as AddEventListenerOptions)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', onUp)
  if (rafMain) cancelAnimationFrame(rafMain)
  if (rafStar) cancelAnimationFrame(rafStar)
})
</script>

<style scoped>
/* —— 页面骨架：全视口 + 暗色星空 —— */
.space {
  min-height: 100vh;
  background: #0a0a0f;
  color: #f4f4f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.space.dragging { cursor: grabbing; }
.space.dragging .viewport { cursor: grabbing; }

/* 顶栏 */
.top {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 14px;
  background: #0a0a0f;
  border-bottom: 3px solid #f4f4f0;
  flex-shrink: 0;
  z-index: 20;
}
.top-left, .top-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hub-link {
  background: #f4f4f0;
  color: #0a0a0f;
  padding: 6px 12px;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.06em;
  border-width: 2px;
}
.hub-link:hover { background: #ffd700; }
.top-title { font-weight: 800; font-size: 13px; letter-spacing: 0.06em; }
.top-sub { font-size: 11px; color: #bbb; letter-spacing: 0.04em; }
.mode-switch {
  display: flex;
  gap: 0;
  background: #f4f4f0;
  padding: 3px;
  border-width: 2px;
}
.mode-btn {
  background: transparent;
  color: #0a0a0f;
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 800;
  border: 2px solid transparent;
  cursor: pointer;
}
.mode-btn.active {
  background: #0a0a0f;
  color: #f4f4f0;
  border-color: #0a0a0f;
  box-shadow: 0 0 0 1px #f4f4f0 inset;
}
.reset-btn {
  background: #fff;
  color: #0a0a0f;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
}
.reset-btn:hover { background: #ffd700; }
.zoom-badge {
  background: #0a0a0f;
  color: #f4f4f0;
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 800;
  border-width: 2px;
  min-width: 54px;
  text-align: center;
}

/* 布局：左 HUD + 右视口 */
.layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 14px;
  padding: 14px;
  flex: 1;
  min-height: 0;
}
.hud {
  background: #f4f4f0;
  color: #0a0a0f;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: auto;
  border-width: 3px;
  max-height: calc(100vh - 72px);
}
.hud-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 3px solid #0a0a0f;
  padding-bottom: 8px;
}
.hud-title { font-weight: 800; font-size: 11px; letter-spacing: 0.12em; }
.hud-sub { font-size: 11px; color: #666; font-weight: 700; }
.hud-section { display: flex; flex-direction: column; gap: 8px; }
.sec-title { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  background: #fff;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.chip.active { background: #0a0a0f; color: #f4f4f0; }
.chip i {
  background: #ffd700;
  color: #0a0a0f;
  padding: 1px 5px;
  font-style: normal;
  font-size: 10px;
  border: 1.5px solid #0a0a0f;
}
.chip.active i { background: #ff006e; color: #fff; }
.hud-hint { font-size: 10px; color: #666; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-size: 10px;
  padding: 4px 8px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
}
.tag.active { color: #0a0a0f; box-shadow: 2px 2px 0 #0a0a0f; transform: translate(-1px, -1px); }
.stats .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.stat {
  background: #fff;
  padding: 8px;
  text-align: center;
  border-width: 2px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat span { font-size: 9px; letter-spacing: 0.08em; color: #666; font-weight: 800; }
.stat b { font-size: 14px; font-weight: 800; }
.scale-row { display: flex; flex-direction: column; gap: 4px; font-size: 10px; color: #333; border-top: 1.5px dashed #bbb; padding-top: 8px; }
.muted { color: #777; }
.hud-foot {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 9px;
  color: #666;
  letter-spacing: 0.06em;
  border-top: 2px solid #0a0a0f;
  padding-top: 8px;
}

/* 视口：透视舞台 + Canvas 星空 */
.viewport {
  position: relative;
  overflow: hidden;
  background: radial-gradient(120% 120% at 30% 20%, #1a1a2e 0%, #0a0a0f 55%, #050508 100%);
  border-width: 3px;
  cursor: grab;
  min-height: 560px;
  perspective: 1000px;
  perspective-origin: 50% 50%;
  transform-style: preserve-3d;
}
.viewport:active { cursor: grabbing; }
.star-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  pointer-events: none;
}
.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(85% 70% at 50% 50%, transparent 58%, rgba(0,0,0,0.55) 100%);
  pointer-events: none;
  z-index: 1;
}
.grid-floor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  opacity: 0.22;
  background-image:
    linear-gradient(rgba(244,244,240,0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(244,244,240,0.08) 1px, transparent 1px),
    radial-gradient(circle at 50% 85%, rgba(255,0,110,0.14), transparent 42%);
  background-size: 42px 42px, 42px 42px, auto;
  transform: translateZ(-120px) rotateX(62deg) scale(2.2);
  transform-origin: 50% 100%;
}
.scan-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(244,244,240,0.04) 3px, transparent 4px);
  mix-blend-mode: soft-light;
  opacity: 0.18;
}
.world {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 0;
  height: 0;
  overflow: visible;
  z-index: 2;
  transform-style: preserve-3d;
}
.perspective {
  position: absolute;
  left: 0;
  top: 0;
  transform-style: preserve-3d;
}
.perspective.galaxy { transform: translate3d(-0.5px, -0.5px, 0) rotateX(6deg); }
.perspective.gallery { transform: translate3d(-0.5px, -0.5px, 0) rotateX(0deg); }
.perspective.overlook { transform: translate3d(-0.5px, -80px, 0) rotateX(42deg); }
.stage {
  position: absolute;
  left: 0;
  top: 0;
  transform-style: preserve-3d;
}

/* 卡片：悬浮卡片，GPU 3D，悬停发光 */
.card {
  position: absolute;
  left: -160px;
  top: -210px;
  width: 320px;
  background: #fff;
  color: #0a0a0f;
  border-width: 3px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transform-style: preserve-3d;
  backface-visibility: hidden;
  box-shadow: 8px 8px 0 rgba(10,10,15,0.9);
  transition: box-shadow 0.2s, border-color 0.2s;
}
.card.hovered {
  border-color: #ffd700;
  box-shadow: 0 0 0 2px #ffd700, 0 0 28px rgba(255,215,0,0.55), 14px 14px 0 #0a0a0f;
}
.card-cover {
  height: 168px;
  overflow: hidden;
  position: relative;
  border-left: none;
  border-right: none;
  border-top: none;
  border-width: 3px;
  background: #f4f4f0;
}
.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s;
}
.card.hovered .card-cover img { transform: scale(1.06); }
.group-badge {
  position: absolute;
  left: 10px;
  bottom: 10px;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 800;
  border-width: 2px;
}
.cover-tags {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  opacity: 0;
  transform: translateY(-6px);
  transition: opacity 0.22s, transform 0.22s;
  pointer-events: none;
}
.cover-tags.show { opacity: 1; transform: translateY(0); }
.cover-tag {
  font-size: 9px;
  padding: 3px 6px;
  font-weight: 800;
  border-width: 1.5px;
}
.card-body { padding: 12px 12px 10px; display: flex; flex-direction: column; gap: 8px; background: #fff; }
.card-title { font-size: 16px; line-height: 1.08; font-weight: 800; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 34px; }
.card-intro { font-size: 11px; line-height: 1.6; color: #333; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 34px; background: #f4f4f0; border-left: 3px solid #0a0a0f; padding: 6px 8px; }
.card-meta { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #555; gap: 8px; }
.author { display: inline-flex; align-items: center; gap: 6px; font-weight: 800; }
.av { width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; border: 1.5px solid #0a0a0f; flex-shrink: 0; }
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.card-tag { font-size: 9px; padding: 3px 6px; font-weight: 800; border-width: 1.5px; }
.card-foot { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #666; border-top: 1.5px dashed #ddd; padding-top: 8px; }
.push-hint { font-weight: 800; color: #0a0a0f; text-decoration: underline; }
.glow {
  position: absolute;
  inset: -2px;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(400px 180px at 50% 0%, rgba(255,215,0,0.18), transparent 70%);
  transition: opacity 0.22s;
}
.card.hovered .glow { opacity: 1; }

/* 飞入动画（过滤时） */
.fly-enter-active { transition: transform 0.55s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s; }
.fly-leave-active { transition: transform 0.32s ease, opacity 0.22s ease; position: absolute; }
.fly-enter-from { opacity: 0; transform: translate3d(0, 40px, -120px) scale(0.86) !important; }
.fly-leave-to { opacity: 0; transform: translate3d(0, -30px, -80px) scale(0.9) !important; }
.fly-move { transition: transform 0.55s cubic-bezier(0.16, 1, 0.3, 1); }

/* 视口提示与准星 */
.viewport-hint {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 10px;
  color: #f4f4f0;
  z-index: 5;
  pointer-events: none;
  flex-wrap: wrap;
}
.viewport-hint span {
  background: rgba(10,10,15,0.82);
  border: 1.5px solid #f4f4f0;
  padding: 4px 8px;
}
.crosshair {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  font-size: 14px;
  color: rgba(244,244,240,0.28);
  pointer-events: none;
  z-index: 3;
}

/* Modal：缩放推门动画 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10,10,15,0.62);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  z-index: 40;
}
.modal {
  width: min(760px, 96vw);
  max-height: 92vh;
  overflow: auto;
  background: #fff;
  border-width: 3px;
  display: flex;
  flex-direction: column;
  position: relative;
}
.modal-close {
  position: sticky;
  top: 0;
  align-self: flex-end;
  margin: 10px 10px 0 0;
  background: #0a0a0f;
  color: #f4f4f0;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  z-index: 2;
  border-width: 2px;
}
.modal-cover {
  height: 260px;
  overflow: hidden;
  position: relative;
  border-left: none;
  border-right: none;
  border-top: none;
  border-width: 3px;
  flex-shrink: 0;
}
.modal-cover img { width: 100%; height: 100%; object-fit: cover; display: block; }
.modal-group {
  position: absolute;
  left: 12px;
  bottom: 12px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  border-width: 2px;
}
.modal-body { padding: 16px 16px 20px; display: flex; flex-direction: column; gap: 12px; }
.modal-title { font-size: 26px; line-height: 1.05; font-weight: 800; }
.modal-intro { font-size: 12px; line-height: 1.7; color: #333; background: #f4f4f0; border-left: 4px solid #0a0a0f; padding: 8px 10px; }
.modal-meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 10px;
  background: #fff;
  font-size: 11px;
  border-width: 2px;
}
.author-line { display: inline-flex; align-items: center; gap: 6px; font-weight: 800; }
.modal-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.modal-tag { font-size: 10px; padding: 4px 8px; font-weight: 800; border-width: 2px; }
.modal-content {
  background: #fcfcf8;
  padding: 14px 12px;
  font-size: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  border-width: 2px;
}
.modal-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 11px; }
.act-btn {
  background: #fff;
  padding: 7px 12px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
  font-size: 11px;
}
.act-btn:hover { background: #f4f4f0; }
.act-btn.liked { background: #0a0a0f; color: #fff; }
.comments { border-top: 3px solid #0a0a0f; padding-top: 12px; display: flex; flex-direction: column; gap: 10px; }
.comments-head { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; }
.comment-input-row { display: flex; gap: 8px; padding: 6px; background: #f4f4f0; border-width: 2px; }
.comment-input { flex: 1; border: 2px solid #0a0a0f; padding: 8px 10px; font-size: 11px; background: #fff; outline: none; }
.comment-send { background: #0a0a0f; color: #fff; padding: 6px 14px; font-weight: 800; cursor: pointer; border-width: 2px; font-size: 11px; }
.comment { background: #fff; padding: 10px; border-width: 2px; display: flex; flex-direction: column; gap: 6px; }
.comment-head { display: flex; justify-content: space-between; font-size: 11px; }
.comment-body { font-size: 12px; line-height: 1.6; }
.replies { display: flex; flex-direction: column; gap: 6px; padding-left: 10px; border-left: 3px solid #0a0a0f; }
.reply { background: #f4f4f0; padding: 6px 8px; font-size: 11px; border-width: 1.5px; }

.modal-enter-active { transition: opacity 0.22s, transform 0.32s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-leave-active { transition: opacity 0.18s, transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.92) translateY(14px); }

/* 响应式：窄屏 HUD 上置 */
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  .hud { max-height: none; order: 2; }
  .viewport { min-height: 520px; order: 1; }
}
@media (max-width: 560px) {
  .card { width: 280px; left: -140px; top: -190px; }
  .card-cover { height: 148px; }
  .top { height: auto; padding: 8px 10px; flex-wrap: wrap; }
  .mode-switch { order: 2; }
}
.hide-mobile { display: inline; }
@media (max-width: 720px) { .hide-mobile { display: none !important; } }
</style>
