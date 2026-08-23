<template>
  <!-- 顶栏：始终可见的 Hub 返回 + 模式切换 -->
  <div class="space" :class="[`mode-${mode}`, { dragging: isDragging }]">
    <nav class="top mono">
      <div class="top-left">
        <!-- 需求：顶部必须有回到 Hub 的 router-link，极简细描边 -->
        <router-link to="/" class="hub-link">← Hub</router-link>
        <span class="top-title">SynthSpace — 3D 空间画廊</span>
        <span class="top-sub hide-mobile">拖拽漫游 · 滚轮缩放 · 悬停发光 · 点击推门</span>
      </div>
      <div class="top-right">
        <!-- 模式切换：星系 / 画廊 / 俯瞰，三种布局用 CSS transform 差异化 -->
        <div class="mode-switch">
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
        <button class="reset-btn mono" @click="resetView">⟲ 复位</button>
        <span class="zoom-badge mono">×{{ zoom.toFixed(2) }}</span>
      </div>
    </nav>

    <div class="layout">
      <!-- 左侧 HUD：分组过滤 + 标签云 + 统计，纯 Mock 鼠标点击，极简毛玻璃 -->
      <aside class="hud">
        <div class="hud-head mono">
          <span class="hud-title">HUD / 导航</span>
          <span class="hud-sub">{{ filteredPosts.length }} / {{ mockPosts.length }} 篇</span>
        </div>

        <!-- 分组芯片：点击仅显示该分组，带飞入动画（TransitionGroup） -->
        <section class="hud-section">
          <div class="sec-title mono">▣ Group · 分组过滤</div>
          <div class="chips">
            <button
              class="chip mono"
              :class="{ active: selectedGroup === 'all' }"
              @click="selectedGroup = 'all'"
            >
              全部 <i>{{ mockPosts.length }}</i>
            </button>
            <button
              v-for="g in mockGroups"
              :key="g.id"
              class="chip mono"
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
              class="tag mono"
              :class="{ active: selectedTagId === t.id }"
              :style="tagStyle(t)"
              @click="selectedTagId = selectedTagId === t.id ? null : t.id"
            >
              <span class="tag-dot" :style="{ background: t.color }"></span>
              #{{ t.name }}
            </button>
          </div>
          <div class="hud-hint mono">标签叠加过滤 · 点亮即筛选</div>
        </section>

        <!-- 统计：基于 Mock，纯前端计算 -->
        <section class="hud-section stats">
          <div class="sec-title mono">◉ Stats · 统计</div>
          <div class="stat-grid mono">
            <div class="stat"><span>POSTS</span><b>{{ mockPosts.length }}</b></div>
            <div class="stat"><span>GROUP</span><b>{{ mockGroups.length }}</b></div>
            <div class="stat"><span>TAGS</span><b>{{ mockTags.length }}</b></div>
            <div class="stat"><span>VIEWS</span><b>{{ mockStats.total_views.toLocaleString() }}</b></div>
            <div class="stat"><span>FILTERED</span><b>{{ filteredPosts.length }}</b></div>
            <div class="stat"><span>MODE</span><b>{{ modeLabel }}</b></div>
          </div>
          <div class="scale-row mono">
            <span>缩放 {{ (zoom * 100).toFixed(0) }}% · 偏移 {{ offset.x.toFixed(0) }},{{ offset.y.toFixed(0) }}</span>
            <span class="muted">拖拽空白漫游 · 滚轮缩放</span>
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
        class="viewport"
        @mousedown="onDown"
        @mousemove="onViewportMouse"
        @wheel="onWheel"
      >
        <!-- 背景：Canvas 粒子星点（30-50 点），RAF 驱动，不触发重排 -->
        <canvas ref="starCanvas" class="star-canvas" aria-hidden="true"></canvas>
        <!-- 装饰：晕影与点阵地板，随模式微变 -->
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
                class="card"
                :class="{ hovered: hoveredId === p.id }"
                :style="cardStyle(p, idx)"
                @mouseenter="hoveredId = p.id"
                @mouseleave="hoveredId = null"
                @click="openDetail(p)"
              >
                <!-- 卡片封面：保持比例，视差中保持清晰 -->
                <div class="card-cover">
                  <img :src="p.cover" :alt="p.title" loading="lazy" draggable="false" />
                  <!-- 分组角标：极简毛玻璃 pill -->
                  <span class="group-badge mono" :style="{ borderColor: 'rgba(255,255,255,.18)' }">
                    <span class="badge-dot" :style="{ background: p.tags[0]?.color || '#fff' }"></span>
                    {{ p.group.icon }} {{ p.group.name }}
                  </span>
                  <!-- 悬停时显示的标签浮层 -->
                  <div class="cover-tags mono" :class="{ show: hoveredId === p.id }">
                    <span v-for="t in p.tags" :key="t.id" class="cover-tag" :style="{ background: 'rgba(10,10,15,.55)', borderColor: 'rgba(255,255,255,.18)', backdropFilter: 'blur(8px)' }"><span class="tag-dot" :style="{ background: t.color }"></span>{{ t.name }}</span>
                  </div>
                  <div class="cover-vignette" aria-hidden="true"></div>
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
                    <span v-for="t in p.tags" :key="t.id" class="card-tag" :style="tagPillStyle(t)">#{{ t.name }}</span>
                  </div>
                  <div class="card-foot mono">
                    <span>♥ {{ getLikes(p.id) }} · 💬 {{ p.comments }}</span>
                    <span class="push-hint">点击推门 →</span>
                  </div>
                </div>
                <!-- 悬停柔光层：细白描边 + 柔光 -->
                <div class="glow" aria-hidden="true"></div>
                <div class="card-hairline" aria-hidden="true"></div>
              </article>
            </TransitionGroup>
          </div>
        </div>

        <!-- 视口浮动提示 -->
        <div class="viewport-hint mono">
          <span>拖拽空白处漫游 · 滚轮缩放 · 悬停发光 · 点击推门</span>
          <span class="hide-mobile">{{ modeHint }}</span>
        </div>

        <!-- 准星 / 中心点装饰：极简细线 -->
        <div class="crosshair" aria-hidden="true"><span class="cross-v"></span><span class="cross-h"></span></div>
      </section>
    </div>

    <!-- 详情 Modal：点击推门，缩放动画，展示封面/正文/评论/点赞本地计数 -->
    <Transition name="modal">
      <div v-if="selected" class="modal-overlay" @click.self="closeDetail" @wheel.stop>
        <div class="modal">
          <button class="modal-close mono" @click="closeDetail" title="关闭">× 关闭</button>
          <div class="modal-cover">
            <img :src="selected.cover" :alt="selected.title" />
            <span class="modal-group mono" :style="{ background: 'rgba(10,10,15,.52)', backdropFilter: 'blur(10px)', borderColor: 'rgba(255,255,255,.18)' }">
              <span class="badge-dot" :style="{ background: selected.tags[0]?.color || '#fff' }"></span>
              {{ selected.group.icon }} {{ selected.group.name }} · {{ selected.group.slug }}
            </span>
            <div class="cover-vignette" aria-hidden="true"></div>
          </div>
          <div class="modal-body">
            <h2 class="modal-title display">{{ selected.title }}</h2>
            <p class="modal-intro mono">{{ selected.intro }}</p>
            <div class="modal-meta mono">
              <span class="author-line"><span class="av" :style="{ background: selected.author.color }">{{ selected.author.avatar }}</span> {{ selected.author.display_name }} @{{ selected.author.username }} · {{ selected.author.type }}</span>
              <span>{{ selected.createdAt }} · 👁 {{ selected.views }}</span>
            </div>
            <div class="modal-tags mono">
              <span v-for="t in selected.tags" :key="t.id" class="modal-tag" :style="tagPillStyle(t)">{{ t.name }}</span>
            </div>
            <!-- 正文：Markdown 渲染（深空极简主题） -->
            <MarkdownRenderer :content="selected.content" theme="space" />

            <!-- 操作：点赞本地计数 -->
            <div class="modal-actions mono">
              <button class="act-btn" :class="{ liked: likedSet.has(selected.id) }" @click="toggleLike(selected.id)">
                {{ likedSet.has(selected.id) ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(selected.id) }}
              </button>
              <span class="muted">💬 {{ localComments.length }} 评论 · 本地 Mock 不会上传</span>
              <button class="act-btn" @click="shareMock">↗ 分享（Mock）</button>
            </div>

            <!-- 评论区：本地输入与列表 -->
            <div class="comments">
              <div class="comments-head mono">评论 · {{ localComments.length }}</div>
              <div class="comment-input-row">
                <input
                  v-model="newComment"
                  class="comment-input mono"
                  placeholder="写点什么… 回车发送（本地）"
                  @keydown.enter="addComment"
                />
                <button class="comment-send mono" @click="addComment">发送</button>
              </div>
              <div v-for="c in localComments" :key="c.id" class="comment">
                <div class="comment-head mono">
                  <span><b>{{ c.avatar }} {{ c.author }}</b> · {{ c.time }}</span>
                  <span>♥ {{ c.likes }}</span>
                </div>
                <p class="comment-body mono">{{ c.content }}</p>
                <div v-if="c.replies && c.replies.length" class="replies">
                  <div v-for="r in c.replies" :key="r.id" class="reply mono">
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
 * SynthSpace — 深空极简画廊
 * 单文件 Vue SFC，中文注释，无新增依赖
 * 设计语言「深空极简」：#0a0a0f 背景 + 毛玻璃 HUD/卡片 + 细白描边柔光 + 点阵地板
 * 核心：HTML+CSS 3D 视差 + 单 Canvas 2D 星点，GPU 加速（transform3d / will-change）
 * 交互：拖拽平移（mousedown+mousemove）、滚轮缩放、悬停发光、点击推门 Modal
 * 状态：用 ref 管理 posts 位置、缩放、偏移、选中 等，保持原 TS 逻辑仅替换样式
 */
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
// 引入 Markdown 渲染器（深空主题）
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import { mockPosts, mockGroups, mockTags, mockStats, mockComments, type MockPost, type MockTag } from '@/mock/data'

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

// —— 用 ref 管理：位置 / 缩放 / 偏移 / 选中 ——
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
  if (typeof window !== 'undefined') window.alert('链接已复制（Mock）')
}

// —— 标签胶囊样式：极简冷感，保留原色作点缀而非整块实色 ——
function tagStyle(t: MockTag): Record<string, string> {
  const active = selectedTagId.value === t.id
  return {
    background: active ? 'rgba(255,255,255,.10)' : 'rgba(255,255,255,.06)',
    borderColor: active ? 'rgba(255,255,255,.28)' : 'rgba(255,255,255,.12)',
    color: active ? '#fff' : 'rgba(244,244,240,.82)',
    boxShadow: active ? '0 0 0 1px rgba(255,255,255,.08), 0 4px 16px rgba(255,255,255,.06)' : 'none',
  }
}
function tagPillStyle(t: MockTag): Record<string, string> {
  // 卡片内标签：极简毛玻璃 + 彩色圆点
  return {
    background: 'rgba(255,255,255,.06)',
    borderColor: 'rgba(255,255,255,.12)',
    color: 'rgba(244,244,240,.88)',
  }
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
  // 悬停：放大 1.06 并提升 z（极简仅微放大，避免 brutal）
  const isHover = hoveredId.value === post.id
  const hoverScale = isHover ? 1.06 : 1
  const hoverZ = isHover ? 22 : 0
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

// —— Canvas 星点粒子（30-50 点，RAF 驱动，纯 2D，深空极简配色） ——
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
    r: Math.random() * 1.4 + 0.35,
    alpha: Math.random() * 0.42 + 0.28,
    tw: Math.random() * 0.018 + 0.007,
    vx: (Math.random() - 0.5) * 0.16,
    vy: (Math.random() - 0.5) * 0.12,
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
  ctx.clearRect(0, 0, w, h)
  // 背景渐变（深空冷感，仅极淡蓝灰晕）
  const grad = ctx.createRadialGradient(w * 0.68, h * 0.26, 0, w * 0.5, h * 0.5, Math.max(w, h) * 0.92)
  grad.addColorStop(0, 'rgba(180,190,210,0.07)')
  grad.addColorStop(0.38, 'rgba(120,130,150,0.03)')
  grad.addColorStop(0.72, 'rgba(20,22,28,0.0)')
  grad.addColorStop(1, 'rgba(10,10,15,0)')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, w, h)

  // 绘制星点与极淡连线
  for (const s of stars) {
    s.phase += s.tw
    const a = s.alpha + Math.sin(s.phase) * 0.16
    s.x += s.vx
    s.y += s.vy
    if (s.x < -6) s.x = w + 6
    if (s.x > w + 6) s.x = -6
    if (s.y < -6) s.y = h + 6
    if (s.y > h + 6) s.y = -6

    ctx.beginPath()
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(244,244,240,${Math.max(0, Math.min(1, a))})`
    ctx.shadowColor = 'rgba(244,244,240,0.55)'
    ctx.shadowBlur = s.r * 2.6
    ctx.fill()
    ctx.shadowBlur = 0
  }
  // 轻量连线：冷白极淡
  ctx.strokeStyle = 'rgba(244,244,240,0.06)'
  ctx.lineWidth = 0.6
  for (let i = 0; i < stars.length; i++) {
    for (let j = i + 1; j < stars.length; j++) {
      const a = stars[i], b = stars[j]
      if (!a || !b) continue
      const dx = a.x - b.x
      const dy = a.y - b.y
      const dist = Math.hypot(dx, dy)
      if (dist < 92) {
        const op = (1 - dist / 92) * 0.14
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
  smoothMouse.value.x += (mouse.value.x - smoothMouse.value.x) * 0.08
  smoothMouse.value.y += (mouse.value.y - smoothMouse.value.y) * 0.08
  drawStars()
  rafMain = requestAnimationFrame(loopMain)
}

function onResize(): void {
  const c = starCanvas.value
  if (c) initStars(c)
}

// —— 监听模式切换：重置视差，避免突变 ——
watch(mode, async () => {
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
/* 引入标题衬线字体 Instrument Serif，深空极简标题用 */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap');

/* —— 字体工具类 —— */
.mono {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.display {
  font-family: 'Instrument Serif', 'Times New Roman', serif;
  letter-spacing: .14em; /* 需求：标题 letter-spacing .14em */
  font-weight: 400;
}

/* —— 页面骨架：深空极简 #0a0a0f —— */
.space {
  min-height: 100vh;
  background: #0a0a0f;
  /* 深空基底 + 极淡冷晕，避免纯黑死寂 */
  background-image:
    radial-gradient(900px 560px at 68% 8%, rgba(180,190,210,.06), transparent 62%),
    radial-gradient(700px 480px at 12% 82%, rgba(120,130,150,.04), transparent 62%);
  color: #f4f4f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.space.dragging { cursor: grabbing; }
.space.dragging .viewport { cursor: grabbing; }

/* ——————————————————————————— 顶栏：毛玻璃 + 细描边 ——————————————————————————— */
.top {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 14px;
  background: rgba(255,255,255,.06); /* 需求 HUD 同款玻璃 */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,.12);
  flex-shrink: 0;
  z-index: 20;
}
.top-left, .top-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hub-link {
  /* 极简冷感：毛玻璃 pill + 细白描边 */
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: #f4f4f0;
  padding: 7px 14px;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-decoration: none;
  transition: background .18s, border-color .18s, box-shadow .18s;
}
.hub-link:hover {
  background: rgba(255,255,255,.10);
  border-color: rgba(255,255,255,.22);
  box-shadow: 0 0 0 1px rgba(255,255,255,.06), 0 8px 20px rgba(0,0,0,.24);
}
.top-title {
  font-family: 'Instrument Serif', serif;
  font-weight: 400;
  font-size: 15px;
  letter-spacing: .14em; /* 标题统一字距 */
  color: #f4f4f0;
}
.top-sub { font-size: 11px; color: rgba(244,244,240,.56); letter-spacing: 0.04em; }
.mode-switch {
  display: flex;
  gap: 6px;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  padding: 4px;
}
.mode-btn {
  background: transparent;
  color: rgba(244,244,240,.72);
  padding: 6px 14px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid transparent;
  border-radius: 999px;
  cursor: pointer;
  transition: background .18s, color .18s, border-color .18s, box-shadow .18s;
}
.mode-btn:hover { color: #fff; background: rgba(255,255,255,.06); }
.mode-btn.active {
  background: rgba(255,255,255,.14);
  color: #ffffff;
  border-color: rgba(255,255,255,.18);
  box-shadow: 0 0 0 1px rgba(255,255,255,.06), 0 4px 16px rgba(0,0,0,.16);
}
.reset-btn {
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: #f4f4f0;
  padding: 7px 12px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: background .18s, border-color .18s;
}
.reset-btn:hover { background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.20); }
.zoom-badge {
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: rgba(244,244,240,.84);
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  min-width: 54px;
  text-align: center;
}

/* ——————————————————————————— 布局：左 HUD + 右视口 ——————————————————————————— */
.layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 16px;
  padding: 16px;
  flex: 1;
  min-height: 0;
}

/* HUD：毛玻璃极简，深空悬浮 */
.hud {
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 16px;
  color: #f4f4f0;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: auto;
  max-height: calc(100vh - 84px);
  box-shadow: 0 8px 32px rgba(0,0,0,.24);
}
.hud-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,.12);
  padding-bottom: 10px;
}
.hud-title { font-weight: 700; font-size: 11px; letter-spacing: 0.12em; color: #f4f4f0; }
.hud-sub { font-size: 11px; color: rgba(244,244,240,.56); font-weight: 600; }
.hud-section { display: flex; flex-direction: column; gap: 10px; }
.sec-title { font-size: 10px; font-weight: 700; letter-spacing: 0.10em; color: rgba(244,244,240,.62); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  /* 极简芯片：毛玻璃 + 细描边 */
  background: rgba(255,255,255,.06);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(244,244,240,.86);
  transition: background .16s, border-color .16s, color .16s, box-shadow .16s;
}
.chip:hover { background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.18); color: #fff; }
.chip.active { background: rgba(255,255,255,.12); color: #fff; border-color: rgba(255,255,255,.22); box-shadow: 0 0 0 1px rgba(255,255,255,.06), 0 4px 16px rgba(255,255,255,.06); }
.chip i {
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 999px;
  color: rgba(244,244,240,.84);
  padding: 1px 6px;
  font-style: normal;
  font-size: 10px;
}
.chip.active i { background: rgba(255,255,255,.16); color: #fff; border-color: rgba(255,255,255,.18); }
.hud-hint { font-size: 10px; color: rgba(244,244,240,.42); }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 7px; }
.tag {
  font-size: 11px;
  padding: 5px 10px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background .16s, border-color .16s, box-shadow .16s, transform .16s;
}
.tag:hover { background: rgba(255,255,255,.08); transform: translateY(-1px); }
.tag.active { transform: translateY(-1px); }
.tag-dot {
  width: 7px; height: 7px; border-radius: 999px; display: inline-block; flex-shrink: 0;
  box-shadow: 0 0 8px currentColor;
}
.stats .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.stat {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08); /* 卡片描边同款 0 0 0 1px rgba(.08) 的视觉 */
  border-radius: 12px;
  padding: 10px 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat span { font-size: 9px; letter-spacing: 0.08em; color: rgba(244,244,240,.52); font-weight: 700; }
.stat b { font-size: 14px; font-weight: 700; color: #f4f4f0; }
.scale-row { display: flex; flex-direction: column; gap: 4px; font-size: 10px; color: rgba(244,244,240,.56); border-top: 1px solid rgba(255,255,255,.08); padding-top: 10px; }
.muted { color: rgba(244,244,240,.48); }
.hud-foot {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 9px;
  color: rgba(244,244,240,.38);
  letter-spacing: 0.06em;
  border-top: 1px solid rgba(255,255,255,.08);
  padding-top: 10px;
}

/* ——————————————————————————— 视口：透视舞台 + Canvas 星空 ——————————————————————————— */
.viewport {
  position: relative;
  overflow: hidden;
  /* 深空画廊背景：冷渐变 + 极淡晕 */
  background:
    radial-gradient(820px 520px at 62% 18%, rgba(180,190,210,.07), transparent 66%),
    radial-gradient(120% 120% at 30% 20%, #15151d 0%, #0a0a0f 58%, #07070a 100%);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  cursor: grab;
  min-height: 560px;
  perspective: 1000px;
  perspective-origin: 50% 50%;
  transform-style: preserve-3d;
  box-shadow: 0 12px 40px rgba(0,0,0,.28);
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
  background: radial-gradient(85% 70% at 50% 50%, transparent 58%, rgba(0,0,0,0.52) 100%);
  pointer-events: none;
  z-index: 1;
}
.grid-floor {
  /* 需求：细点阵地板，替代 brutal 网格 */
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  opacity: 0.30;
  /* 细点阵：1px 实点 + 透明，28px 间距 */
  background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,.22) 1.05px, transparent 1.7px);
  background-size: 28px 28px;
  background-position: -1px -1px;
  /* 透视压平：像美术馆地板向远处延伸 */
  transform: translateZ(-120px) rotateX(62deg) scale(2.2);
  transform-origin: 50% 100%;
  /* 边缘羽化 + 深度衰减 */
  -webkit-mask-image: radial-gradient(74% 62% at 50% 88%, black 28%, transparent 74%);
  mask-image: radial-gradient(74% 62% at 50% 88%, black 28%, transparent 74%);
}
.scan-glow {
  /* 极简仅保留极淡扫描线，冷感 */
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(244,244,240,0.02) 3px, transparent 4px);
  opacity: 0.10;
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

/* ——————————————————————————— 卡片：深空极简，无阴影仅细描边 + 柔光 ——————————————————————————— */
.card {
  position: absolute;
  left: -160px;
  top: -210px;
  width: 320px;
  /* 极简卡片：半透明深底 + 毛玻璃，边仅 0 0 0 1px rgba(.08) */
  background: rgba(18,18,24,.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #f4f4f0;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
  transform-style: preserve-3d;
  backface-visibility: hidden;
  /* 需求：无阴影，仅 0 0 0 1px rgba(255,255,255,.08) */
  box-shadow: 0 0 0 1px rgba(255,255,255,.08);
  transition: box-shadow .22s ease, background .22s ease, transform .22s ease;
}
.card:hover,
.card.hovered {
  /* 需求：悬停仅细白描边 + 柔光 */
  background: rgba(22,22,28,.82);
  border-color: transparent;
  box-shadow:
    0 0 0 1px rgba(255,255,255,.92), /* 细白描边 */
    0 12px 40px rgba(0,0,0,.36), /* 柔和落地阴影，仅为层次非 brutal */
    0 0 28px rgba(255,255,255,.08); /* 柔光外晕 */
}
/* 细发丝高光线 */
.card-hairline {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(255,255,255,.08), transparent 42%);
  opacity: .7;
}
.card-cover {
  height: 168px;
  overflow: hidden;
  position: relative;
  background: #0a0a0f;
  flex-shrink: 0;
}
.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform .45s cubic-bezier(.16,1,.3,1), filter .28s;
  filter: saturate(.9) contrast(1.02);
}
.card.hovered .card-cover img { transform: scale(1.04); filter: saturate(1) contrast(1.02); }
.cover-vignette {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, transparent 46%, rgba(10,10,15,.52) 100%),
    linear-gradient(180deg, rgba(10,10,15,.14), transparent 36%);
  pointer-events: none;
}
.group-badge {
  position: absolute;
  left: 10px;
  bottom: 10px;
  padding: 5px 10px;
  font-size: 10px;
  font-weight: 700;
  background: rgba(10,10,15,.55);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: #f4f4f0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.badge-dot { width: 7px; height: 7px; border-radius: 999px; display: inline-block; flex-shrink: 0; box-shadow: 0 0 10px currentColor; }
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
  font-size: 10px;
  padding: 4px 8px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: #f4f4f0;
}
.card-body { padding: 14px 14px 12px; display: flex; flex-direction: column; gap: 9px; background: transparent; }
.card-title {
  /* 需求：标题 Instrument Serif 32px，这里卡片内适度缩小至 19px，Modal 保持 32px，二者同字族同字距 */
  font-size: 19px;
  line-height: 1.08;
  font-weight: 400;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 42px;
  color: #ffffff;
}
.card-intro {
  font-size: 11px;
  line-height: 1.64;
  color: rgba(244,244,240,.62);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 36px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 10px;
  padding: 8px 10px;
}
.card-meta { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: rgba(244,244,240,.56); gap: 8px; }
.author { display: inline-flex; align-items: center; gap: 6px; font-weight: 700; color: rgba(244,244,240,.84); }
.av { width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; border: 1px solid rgba(255,255,255,.14); border-radius: 999px; flex-shrink: 0; }
.card-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.card-tag {
  font-size: 10px;
  padding: 4px 8px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(255,255,255,.06);
}
.card-foot { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: rgba(244,244,240,.52); border-top: 1px solid rgba(255,255,255,.08); padding-top: 10px; }
.push-hint { font-weight: 700; color: rgba(244,244,240,.72); letter-spacing: .02em; transition: color .18s, letter-spacing .18s; }
.card.hovered .push-hint { color: #fff; letter-spacing: .03em; }
.glow {
  /* 悬停柔光：极淡白晕，非金色 brutal */
  position: absolute;
  inset: -1px;
  border-radius: 16px;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(420px 180px at 50% 0%, rgba(255,255,255,0.09), transparent 68%);
  transition: opacity 0.24s;
}
.card.hovered .glow { opacity: 1; }

/* ——————————————————————————— 飞入动画（过滤时） ——————————————————————————— */
.fly-enter-active { transition: transform 0.55s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s; }
.fly-leave-active { transition: transform 0.32s ease, opacity 0.22s ease; position: absolute; }
.fly-enter-from { opacity: 0; transform: translate3d(0, 40px, -120px) scale(0.86) !important; }
.fly-leave-to { opacity: 0; transform: translate3d(0, -30px, -80px) scale(0.9) !important; }
.fly-move { transition: transform 0.55s cubic-bezier(0.16, 1, 0.3, 1); }

/* ——————————————————————————— 视口提示与准星（极简细线） ——————————————————————————— */
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
  background: rgba(10,10,15,.52);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  padding: 5px 10px;
  color: rgba(244,244,240,.76);
}
.crosshair {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  pointer-events: none;
  z-index: 3;
  opacity: .45;
}
.cross-v, .cross-h {
  position: absolute;
  background: rgba(244,244,240,.28);
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
}
.cross-v { width: 1px; height: 14px; }
.cross-h { width: 14px; height: 1px; }

/* ——————————————————————————— Modal：深空极简推门 ——————————————————————————— */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10,10,15,0.58);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
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
  background: rgba(18,18,24,.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,.42), 0 0 0 1px rgba(255,255,255,.06);
  color: #f4f4f0;
  /* 滚动条极简 */
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,.14) transparent;
}
.modal::-webkit-scrollbar { width: 6px; }
.modal::-webkit-scrollbar-thumb { background: rgba(255,255,255,.14); border-radius: 999px; }
.modal-close {
  position: sticky;
  top: 10px;
  align-self: flex-end;
  margin: 10px 10px 0 0;
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: #f4f4f0;
  padding: 7px 12px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  z-index: 2;
  transition: background .16s, border-color .16s;
}
.modal-close:hover { background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.18); }
.modal-cover {
  height: 260px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
  background: #0a0a0f;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.modal-cover img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(.92); }
.modal-group {
  position: absolute;
  left: 12px;
  bottom: 12px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  color: #fff;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.modal-body { padding: 18px 18px 20px; display: flex; flex-direction: column; gap: 14px; }
.modal-title {
  /* 需求：标题 Instrument Serif 32px letter-spacing .14em */
  font-size: 32px;
  line-height: 1.02;
  font-weight: 400;
  letter-spacing: .14em;
  color: #ffffff;
}
.modal-intro {
  font-size: 12px;
  line-height: 1.72;
  color: rgba(244,244,240,.70);
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-left: 1px solid rgba(255,255,255,.18);
  border-radius: 12px;
  padding: 10px 12px;
}
.modal-meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 12px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
  font-size: 11px;
  color: rgba(244,244,240,.68);
}
.author-line { display: inline-flex; align-items: center; gap: 6px; font-weight: 700; }
.modal-tags { display: flex; flex-wrap: wrap; gap: 7px; }
.modal-tag {
  font-size: 10px;
  padding: 5px 9px;
  font-weight: 700;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  background: rgba(255,255,255,.06);
  color: rgba(244,244,240,.88);
}
.modal-content {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
  padding: 14px 12px;
  font-size: 12px;
  line-height: 1.84;
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(244,244,240,.78);
}
.modal-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 11px; color: rgba(244,244,240,.68); }
.act-btn {
  background: rgba(255,255,255,.06);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: 11px;
  color: #f4f4f0;
  transition: background .16s, border-color .16s, box-shadow .16s, color .16s;
}
.act-btn:hover { background: rgba(255,255,255,.10); border-color: rgba(255,255,255,.18); }
.act-btn.liked { background: rgba(255,255,255,.14); color: #fff; border-color: rgba(255,255,255,.22); box-shadow: 0 0 18px rgba(255,255,255,.08); }
.comments { border-top: 1px solid rgba(255,255,255,.08); padding-top: 14px; display: flex; flex-direction: column; gap: 10px; }
.comments-head { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; color: rgba(244,244,240,.72); }
.comment-input-row {
  display: flex;
  gap: 8px;
  padding: 6px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
}
.comment-input {
  flex: 1;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  padding: 8px 12px;
  font-size: 11px;
  background: rgba(255,255,255,.06);
  color: #f4f4f0;
  outline: none;
}
.comment-input::placeholder { color: rgba(244,244,240,.42); }
.comment-input:focus { border-color: rgba(255,255,255,.22); background: rgba(255,255,255,.08); }
.comment-send {
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 999px;
  color: #fff;
  padding: 7px 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: 11px;
  transition: background .16s;
}
.comment-send:hover { background: rgba(255,255,255,.16); }
.comment {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comment-head { display: flex; justify-content: space-between; font-size: 11px; color: rgba(244,244,240,.62); }
.comment-body { font-size: 12px; line-height: 1.64; color: rgba(244,244,240,.82); }
.replies { display: flex; flex-direction: column; gap: 6px; padding-left: 10px; border-left: 1px solid rgba(255,255,255,.10); }
.reply {
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 10px;
  padding: 7px 9px;
  font-size: 11px;
  color: rgba(244,244,240,.74);
}

.modal-enter-active { transition: opacity 0.24s, transform 0.32s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-leave-active { transition: opacity 0.18s, transform 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal, .modal-leave-to .modal { transform: scale(0.96) translateY(12px); }

/* ——————————————————————————— 响应式：窄屏 HUD 上置 ——————————————————————————— */
@media (max-width: 980px) {
  .layout { grid-template-columns: 1fr; }
  .hud { max-height: none; order: 2; }
  .viewport { min-height: 520px; order: 1; }
}
@media (max-width: 560px) {
  .card { width: 280px; left: -140px; top: -190px; }
  .card-cover { height: 148px; }
  .top { height: auto; padding: 10px 10px; flex-wrap: wrap; }
  .mode-switch { order: 2; }
  .modal-title { font-size: 26px; }
}
.hide-mobile { display: inline; }
@media (max-width: 720px) { .hide-mobile { display: none !important; } }

/* 滚动条极简：HUD */
.hud { scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.12) transparent; }
.hud::-webkit-scrollbar { width: 6px; }
.hud::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 999px; }
</style>
