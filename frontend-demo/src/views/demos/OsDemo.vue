<template>
  <div class="os">
    <!-- 顶部菜单栏：SynthOS + Hub 入口 + Spotlight + 时间 -->
    <nav class="menubar">
      <div class="menu-left">
        <span class="logo display"> SynthOS</span>
        <router-link to="/" class="hub-link brutal-border">← Hub</router-link>
        <span class="menu-item hide-mobile">文件</span>
        <span class="menu-item hide-mobile">编辑</span>
        <span class="menu-item hide-mobile">窗口</span>
        <span class="menu-item hide-mobile">帮助</span>
      </div>
      <div class="menu-center mono hide-mobile">
        <span class="menu-title">{{ topTitle }}</span>
      </div>
      <div class="menu-right">
        <button class="spotlight-trigger mono brutal-border" @click="spotlightOpen = !spotlightOpen" title="Spotlight 搜索 (⌘K)">
          ⌕ 搜索
        </button>
        <span class="time mono">{{ now }}</span>
        <span class="battery mono hide-mobile">◧ 86%</span>
      </div>
    </nav>

    <!-- 桌面主区域 -->
    <div class="desktop" ref="desktopRef" @click="onDesktopClick">
      <!-- 桌面壁纸网格 -->
      <div class="wallpaper-grid" />

      <!-- Spotlight 搜索覆盖层 -->
      <div v-if="spotlightOpen" class="spotlight-overlay" @click.self="spotlightOpen = false">
        <div class="spotlight brutal-border brutal-shadow">
          <div class="spotlight-input-row">
            <span class="spot-icon">⌕</span>
            <input
              v-model="spotlightQuery"
              class="spot-input mono"
              placeholder="搜索文章、标签、作者、分组…"
              autofocus
              @keydown.escape="spotlightOpen = false"
              @keydown.enter="onSpotlightEnter"
            />
            <span class="spot-esc mono" @click="spotlightOpen = false">ESC</span>
          </div>
          <div class="spotlight-results">
            <div v-if="!spotlightQuery.trim()" class="spot-hint mono">
              <p>试试输入「野蛮」「终端」「Agent」「MCP」…</p>
              <div class="spot-quick mono">
                <button v-for="k in quickKeys" :key="k" class="quick-chip brutal-border" @click="spotlightQuery = k">{{ k }}</button>
              </div>
            </div>
            <template v-else>
              <div v-if="spotlightResults.length === 0" class="spot-empty mono">无结果 — 换个关键词试试</div>
              <button
                v-for="p in spotlightResults"
                :key="p.id"
                class="spot-item brutal-border"
                @click="openPost(p)"
              >
                <span class="spot-item-icon">📄</span>
                <span class="spot-item-main">
                  <b class="display">{{ p.title }}</b>
                  <span class="mono">{{ p.intro.slice(0, 56) }}…</span>
                  <span class="mono spot-tags">
                    <i v-for="t in p.tags" :key="t.id" class="spot-tag" :style="{ background: t.color }">{{ t.name }}</i>
                    <i class="spot-group">{{ p.group.icon }} {{ p.group.name }}</i>
                  </span>
                </span>
                <span class="spot-arrow">↗</span>
              </button>
            </template>
          </div>
          <div class="spot-foot mono">↵ 打开 · ESC 关闭 · {{ spotlightResults.length }} 结果</div>
        </div>
      </div>

      <!-- 桌面图标：4 篇 mockPosts + 2 文件夹，散落排布 -->
      <div
        v-for="icon in desktopIcons"
        :key="icon.id"
        class="desk-icon"
        :class="{ selected: selectedIcon === icon.id }"
        :style="{ left: icon.x + 'px', top: icon.y + 'px' }"
        @click.stop="selectIcon(icon.id)"
        @dblclick.stop="openFromIcon(icon)"
      >
        <div class="desk-icon-img brutal-border" :style="{ background: icon.bg }">
          <span class="desk-emoji">{{ icon.emoji }}</span>
          <!-- 文件夹叠层效果 -->
          <span v-if="icon.type === 'folder'" class="folder-tab"></span>
        </div>
        <div class="desk-icon-label mono">{{ icon.label }}</div>
        <div v-if="icon.sub" class="desk-icon-sub mono">{{ icon.sub }}</div>
      </div>

      <!-- 窗口层：可拖拽 / 缩放 / 层叠 -->
      <div
        v-for="win in windows"
        :key="win.id"
        v-show="!win.minimized"
        class="window brutal-border brutal-shadow"
        :style="{ left: win.x + 'px', top: win.y + 'px', width: win.w + 'px', height: win.h + 'px', zIndex: win.z }"
        @mousedown="bringToFront(win.id)"
      >
        <!-- 窗口标题栏：拖拽手柄 + 红黄绿 -->
        <div class="win-titlebar" @mousedown="startDrag($event, win)">
          <div class="traffic">
            <span class="dot red" title="关闭" @click.stop="closeWindow(win.id)"></span>
            <span class="dot yellow" title="最小化" @click.stop="minimizeWindow(win.id)"></span>
            <span class="dot green" title="最大化/还原" @click.stop="toggleMax(win)"></span>
          </div>
          <div class="win-title mono">{{ win.title }}</div>
          <div class="win-title-actions mono hide-mobile">
            <span class="win-type-pill">{{ win.type }}</span>
          </div>
        </div>

        <!-- Finder 窗口 -->
        <div v-if="win.type === 'finder'" class="win-body finder-body">
          <aside class="finder-side">
            <div class="side-title mono">位置</div>
            <button
              v-for="g in finderGroups"
              :key="g.id"
              class="side-item mono brutal-border"
              :class="{ active: win.groupFilter === g.id }"
              @click="win.groupFilter = g.id"
            >
              <span>{{ g.icon }} {{ g.name }}</span>
              <span class="side-count">{{ g.count }}</span>
            </button>
            <div class="side-divider"></div>
            <div class="side-title mono">标签</div>
            <div class="side-tags">
              <span v-for="t in mockTags" :key="t.id" class="side-tag mono brutal-border" :style="{ background: t.color }">{{ t.name }}</span>
            </div>
            <div class="side-foot mono">共 {{ filteredPosts(win).length }} 项</div>
          </aside>
          <section class="finder-main">
            <div class="finder-toolbar mono">
              <span>▦ 网格</span>
              <span class="muted">{{ win.groupFilter === 'all' ? '全部文件' : (mockGroups.find(g=>g.id===win.groupFilter)?.name || '文件夹') }}</span>
              <button class="toolbar-btn brutal-border" @click="openEditor">＋ 新建文档</button>
            </div>
            <div class="file-grid">
              <button
                v-for="p in filteredPosts(win)"
                :key="p.id"
                class="file-card brutal-border"
                @click="openPost(p)"
                @dblclick="openPost(p)"
              >
                <div class="file-thumb brutal-border" :style="{ background: p.tags[0]?.color || '#fff' }">
                  <img :src="p.cover" :alt="p.title" loading="lazy" />
                  <span class="file-ext mono">{{ p.group.slug }}</span>
                </div>
                <div class="file-name display">{{ p.title }}</div>
                <div class="file-meta mono">{{ p.author.display_name }} · {{ p.createdAt }}</div>
                <div class="file-stats mono">♥ {{ getLikes(p.id) }} · 💬 {{ p.comments }} · 👁 {{ p.views }}</div>
              </button>
            </div>
          </section>
        </div>

        <!-- Post 窗口：标题作者封面正文标签评论点赞 -->
        <div v-else-if="win.type === 'post'" class="win-body post-body">
          <template v-if="getPostById(win.postId!)">
            <div class="post-cover-wrap brutal-border">
              <img :src="getPostById(win.postId!)!.cover" :alt="getPostById(win.postId!)!.title" />
              <span class="post-cover-tag mono brutal-border" :style="{ background: getPostById(win.postId!)!.tags[0]?.color || '#ffd700' }">{{ getPostById(win.postId!)!.group.icon }} {{ getPostById(win.postId!)!.group.name }}</span>
            </div>
            <div class="post-inner">
              <h2 class="post-title display">{{ getPostById(win.postId!)!.title }}</h2>
              <p class="post-intro mono">{{ getPostById(win.postId!)!.intro }}</p>
              <div class="post-meta mono brutal-border">
                <span class="author-line"><span class="avatar">{{ getPostById(win.postId!)!.author.avatar }}</span> {{ getPostById(win.postId!)!.author.display_name }} · {{ getPostById(win.postId!)!.author.type }}</span>
                <span>{{ getPostById(win.postId!)!.createdAt }} · 👁 {{ getPostById(win.postId!)!.views }}</span>
              </div>
              <div class="post-tags mono">
                <span v-for="t in getPostById(win.postId!)!.tags" :key="t.id" class="post-tag brutal-border" :style="{ background: t.color }">{{ t.name }}</span>
              </div>
              <!-- 正文：保留换行与代码块样式 -->
              <pre class="post-content mono brutal-border">{{ getPostById(win.postId!)!.content }}</pre>

              <!-- 操作栏：点赞 -->
              <div class="post-actions mono">
                <button class="action-btn brutal-border" :class="{ liked: isLiked(win.postId!) }" @click="toggleLike(win.postId!)">
                  {{ isLiked(win.postId!) ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(win.postId!) }}
                </button>
                <span class="muted">💬 {{ localComments.length }} 评论 · 分享 ↗</span>
                <button class="action-btn brutal-border" @click="showToast('链接已复制（Mock）')">复制链接</button>
              </div>

              <!-- 评论区 -->
              <div class="comments">
                <div class="comments-title mono">评论 · {{ localComments.length }}</div>
                <div class="comment-input-row brutal-border">
                  <input v-model="newCommentText" class="comment-input mono" placeholder="写点什么…（本地 Mock，不会上传）" @keydown.enter="addComment" />
                  <button class="comment-send mono brutal-border" @click="addComment">发送</button>
                </div>
                <div v-for="c in localComments" :key="c.id" class="comment brutal-border">
                  <div class="comment-head mono">
                    <span><b>{{ c.avatar }} {{ c.author }}</b> · {{ c.time }}</span>
                    <span>♥ {{ c.likes }}</span>
                  </div>
                  <p class="comment-body mono">{{ c.content }}</p>
                  <div v-if="c.replies && c.replies.length" class="comment-replies">
                    <div v-for="r in c.replies" :key="r.id" class="reply mono brutal-border">
                      <b>{{ r.avatar }} {{ r.author }}</b>：{{ r.content }} <span class="muted">· {{ r.time }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
          <div v-else class="mono empty-tip">文章不存在或已被移除</div>
        </div>

        <!-- Editor 窗口：标题+内容保存本地 -->
        <div v-else-if="win.type === 'editor'" class="win-body editor-body">
          <div class="editor-toolbar mono">
            <span>✎ SynthPad — 本地草稿自动保存</span>
            <span class="muted hide-mobile">{{ saveStatus }}</span>
          </div>
          <input v-model="editorTitle" class="editor-title-input display brutal-border" placeholder="无标题文档…" />
          <textarea v-model="editorContent" class="editor-textarea mono brutal-border" placeholder="在此输入正文… 支持 Markdown，保存仅在本地 localStorage，不会请求后端。"></textarea>
          <div class="editor-foot mono">
            <span>{{ editorContent.length }} 字 · {{ editorTitle ? '有标题' : '无标题' }}</span>
            <div class="editor-actions">
              <button class="action-btn brutal-border" @click="clearEditor">清空</button>
              <button class="action-btn primary brutal-border" @click="saveEditor">💾 保存到本地</button>
              <button class="action-btn brutal-border" @click="publishAsPost">发布为新文件 → Finder</button>
            </div>
          </div>
        </div>

        <!-- 缩放手柄 -->
        <div class="resize-handle" @mousedown.stop="startResize($event, win)" title="拖动缩放"></div>
      </div>

      <!-- 轻提示 Toast -->
      <div v-if="toastMsg" class="toast mono brutal-border brutal-shadow">{{ toastMsg }}</div>
    </div>

    <!-- 底部 Dock -->
    <div class="dock-wrap">
      <div class="dock brutal-border brutal-shadow">
        <button
          v-for="d in dockItems"
          :key="d.id"
          class="dock-item brutal-border"
          :class="{ active: isDockActive(d.id) }"
          :style="{ background: d.bg }"
          :title="d.label"
          @click="handleDock(d.id)"
        >
          <span class="dock-icon">{{ d.icon }}</span>
          <span class="dock-label mono">{{ d.label }}</span>
          <span v-if="isDockActive(d.id)" class="dock-dot"></span>
        </button>
        <span class="dock-divider"></span>
        <button class="dock-item brutal-border trash" title="废纸篓" @click="showToast('废纸篓是空的（Mock）')">
          <span class="dock-icon">🗑️</span>
          <span class="dock-label mono">废纸篓</span>
        </button>
      </div>
      <div class="dock-hint mono hide-mobile">双击桌面图标打开 · 拖拽标题栏移动 · 右下角拖动缩放 · Dock 快速启动</div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SynthOS — 浏览器内伪操作系统
 * 纯前端 Mock，无后端；所有数据来自 frontend-demo/src/mock/data.ts
 * 交互：拖拽/缩放/层叠窗口、Finder 过滤、Post 阅读、Editor 本地保存、Spotlight 全局搜索
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockGroups, mockTags, mockComments, type MockPost } from '@/mock/data'

// —— 类型定义 ——
interface OsWindow {
  id: string
  title: string
  type: 'finder' | 'post' | 'editor'
  x: number
  y: number
  w: number
  h: number
  z: number
  minimized: boolean
  maximized: boolean
  prev?: { x: number; y: number; w: number; h: number }
  postId?: string
  groupFilter?: string
}
interface DeskIcon {
  id: string
  type: 'post' | 'folder'
  label: string
  sub?: string
  emoji: string
  bg: string
  x: number
  y: number
  postId?: string
  groupId?: string
}
type DockId = 'finder' | 'post' | 'editor' | 'trash'

// —— 响应式状态 ——
const now = ref('')
const spotlightOpen = ref(false)
const spotlightQuery = ref('')
const selectedIcon = ref<string | null>(null)
const desktopRef = ref<HTMLDivElement | null>(null)
const zCounter = ref(40)
const saveStatus = ref('未保存')
const toastMsg = ref('')
const newCommentText = ref('')
let toastTimer: number | null = null
let timeTimer: number | null = null

// 编辑器本地草稿
const editorTitle = ref('')
const editorContent = ref('')

// 点赞与评论（本地 Mock 状态）
const likesMap = ref<Record<string, number>>({})
const likedSet = ref<Set<string>>(new Set())
const localComments = ref<typeof mockComments>([])

// 额外本地文章（由编辑器发布）
const extraPosts = ref<MockPost[]>([])

// 初始化点赞表与评论
for (const p of mockPosts) likesMap.value[p.id] = p.likes
localComments.value = JSON.parse(JSON.stringify(mockComments))

// 窗口列表：默认打开 Finder
const windows = ref<OsWindow[]>([
  {
    id: 'win-finder-root',
    title: 'Finder — SynthInk 文件',
    type: 'finder',
    x: 280,
    y: 28,
    w: 740,
    h: 440,
    z: 10,
    minimized: false,
    maximized: false,
    groupFilter: 'all',
  },
])

// Finder 侧边分组（含全部）
const finderGroups = computed(() => [
  { id: 'all', name: '全部', icon: '⌂', count: allPosts.value.length },
  ...mockGroups,
])

// 全部文章（含本地新增）
const allPosts = computed<MockPost[]>(() => [...mockPosts, ...extraPosts.value])

// 顶部标题随置顶窗口变化
const topTitle = computed(() => {
  const top = [...windows.value].filter(w => !w.minimized).sort((a, b) => b.z - a.z)[0]
  return top ? top.title : 'SynthOS — 就绪'
})

// 桌面图标：4 篇 mockPosts + 2 文件夹，散落排布
const desktopIcons = computed<DeskIcon[]>(() => {
  const posts = mockPosts.slice(0, 4)
  const bgs = ['#fff', '#ffd700', '#ff006e', '#00f5d4']
  const icons: DeskIcon[] = posts.map((p, i) => ({
    id: `icon-${p.id}`,
    type: 'post',
    label: p.title.slice(0, 14),
    sub: `${p.group.name} · ${p.author.display_name}`,
    emoji: '📄',
    bg: bgs[i % bgs.length],
    x: [36, 170, 36, 180][i] ?? 36,
    y: [18, 86, 216, 268][i] ?? 18,
    postId: p.id,
  }))
  // 两个文件夹对应实验室/档案馆
  icons.push(
    {
      id: 'icon-folder-lab',
      type: 'folder',
      label: mockGroups[0].name,
      sub: `${mockGroups[0].count} 项`,
      emoji: '📁',
      bg: '#00f5d4',
      x: 420,
      y: 24,
      groupId: mockGroups[0].id,
    },
    {
      id: 'icon-folder-archive',
      type: 'folder',
      label: mockGroups[1].name,
      sub: `${mockGroups[1].count} 项`,
      emoji: '📁',
      bg: '#ff8c42',
      x: 420,
      y: 168,
      groupId: mockGroups[1].id,
    },
  )
  return icons
})

// Spotlight 搜索
const quickKeys = ['野蛮', 'Agent', 'MCP', '终端', '后现代']
const spotlightResults = computed(() => {
  const q = spotlightQuery.value.trim().toLowerCase()
  if (!q) return []
  return allPosts.value.filter(p => {
    const hay = `${p.title} ${p.intro} ${p.content} ${p.author.display_name} ${p.group.name} ${p.tags.map(t => t.name).join(' ')}`.toLowerCase()
    return hay.includes(q)
  }).slice(0, 8)
})

// Dock 配置
const dockItems: { id: DockId; icon: string; label: string; bg: string }[] = [
  { id: 'finder', icon: '🗂️', label: '访达', bg: '#00f5d4' },
  { id: 'post', icon: '📄', label: '文章', bg: '#ffd700' },
  { id: 'editor', icon: '✎', label: '编辑器', bg: '#fff' },
]

// —— 工具函数 ——
function nextZ(): number {
  zCounter.value += 1
  return zCounter.value
}
function bringToFront(id: string): void {
  const w = windows.value.find(v => v.id === id)
  if (w) w.z = nextZ()
}
function getPostById(id: string): MockPost | undefined {
  return allPosts.value.find(p => p.id === id)
}
function getLikes(id: string): number {
  return likesMap.value[id] ?? 0
}
function isLiked(id: string): boolean {
  return likedSet.value.has(id)
}
function filteredPosts(win: OsWindow): MockPost[] {
  if (!win.groupFilter || win.groupFilter === 'all') return allPosts.value
  return allPosts.value.filter(p => p.group.id === win.groupFilter)
}
function isDockActive(id: DockId): boolean {
  if (id === 'finder') return windows.value.some(w => w.type === 'finder' && !w.minimized)
  if (id === 'editor') return windows.value.some(w => w.type === 'editor' && !w.minimized)
  if (id === 'post') return windows.value.some(w => w.type === 'post' && !w.minimized)
  return false
}
function showToast(msg: string): void {
  toastMsg.value = msg
  if (toastTimer) window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => (toastMsg.value = ''), 1800)
}

// —— 窗口操作 ——
function openFinder(groupId: string = 'all'): void {
  const exist = windows.value.find(w => w.type === 'finder' && !w.minimized)
  if (exist) {
    exist.groupFilter = groupId
    bringToFront(exist.id)
    return
  }
  // 若已被最小化则还原
  const min = windows.value.find(w => w.type === 'finder' && w.minimized)
  if (min) {
    min.minimized = false
    min.groupFilter = groupId
    bringToFront(min.id)
    return
  }
  windows.value.push({
    id: `win-finder-${Date.now()}`,
    title: 'Finder — SynthInk 文件',
    type: 'finder',
    x: 260 + Math.random() * 60,
    y: 22 + Math.random() * 40,
    w: 740,
    h: 440,
    z: nextZ(),
    minimized: false,
    maximized: false,
    groupFilter: groupId,
  })
}
function openPost(post: MockPost): void {
  spotlightOpen.value = false
  // 若已打开同一文章则置顶
  const exist = windows.value.find(w => w.type === 'post' && w.postId === post.id && !w.minimized)
  if (exist) {
    bringToFront(exist.id)
    return
  }
  // 已最小化的同文章还原
  const min = windows.value.find(w => w.type === 'post' && w.postId === post.id && w.minimized)
  if (min) {
    min.minimized = false
    bringToFront(min.id)
    return
  }
  windows.value.push({
    id: `win-post-${post.id}-${Date.now()}`,
    title: post.title,
    type: 'post',
    x: 120 + Math.random() * 160,
    y: 48 + Math.random() * 60,
    w: 560,
    h: 480,
    z: nextZ(),
    minimized: false,
    maximized: false,
    postId: post.id,
  })
}
function openEditor(): void {
  const exist = windows.value.find(w => w.type === 'editor' && !w.minimized)
  if (exist) {
    bringToFront(exist.id)
    return
  }
  const min = windows.value.find(w => w.type === 'editor' && w.minimized)
  if (min) {
    min.minimized = false
    bringToFront(min.id)
    return
  }
  windows.value.push({
    id: `win-editor-${Date.now()}`,
    title: 'SynthPad — 编辑器',
    type: 'editor',
    x: 200 + Math.random() * 80,
    y: 80 + Math.random() * 40,
    w: 520,
    h: 420,
    z: nextZ(),
    minimized: false,
    maximized: false,
  })
}
function openFromIcon(icon: DeskIcon): void {
  if (icon.type === 'post' && icon.postId) {
    const p = getPostById(icon.postId)
    if (p) openPost(p)
  } else if (icon.type === 'folder' && icon.groupId) {
    openFinder(icon.groupId)
  }
}
function closeWindow(id: string): void {
  const idx = windows.value.findIndex(w => w.id === id)
  if (idx !== -1) windows.value.splice(idx, 1)
}
function minimizeWindow(id: string): void {
  const w = windows.value.find(v => v.id === id)
  if (w) w.minimized = true
}
function toggleMax(win: OsWindow): void {
  if (!win.maximized) {
    win.prev = { x: win.x, y: win.y, w: win.w, h: win.h }
    const dw = desktopRef.value?.clientWidth ?? 1000
    const dh = desktopRef.value?.clientHeight ?? 600
    win.x = 6
    win.y = 6
    win.w = dw - 12
    win.h = dh - 12
    win.maximized = true
  } else {
    if (win.prev) {
      win.x = win.prev.x
      win.y = win.prev.y
      win.w = win.prev.w
      win.h = win.prev.h
    }
    win.maximized = false
  }
  bringToFront(win.id)
}
function handleDock(id: DockId): void {
  if (id === 'finder') openFinder('all')
  else if (id === 'editor') openEditor()
  else if (id === 'post') {
    // 依次打开第一篇未打开的文章，若全部已开则置顶第一篇
    const first = allPosts.value[0]
    if (first) openPost(first)
  } else if (id === 'trash') showToast('废纸篓是空的（Mock）')
}

// —— 桌面交互 ——
function selectIcon(id: string): void {
  selectedIcon.value = id
}
function onDesktopClick(): void {
  selectedIcon.value = null
}
function onSpotlightEnter(): void {
  if (spotlightResults.value.length > 0) openPost(spotlightResults.value[0])
}

// —— 点赞 / 评论 ——
function toggleLike(postId: string): void {
  if (likedSet.value.has(postId)) {
    likedSet.value.delete(postId)
    likesMap.value[postId] = Math.max(0, (likesMap.value[postId] ?? 1) - 1)
  } else {
    likedSet.value.add(postId)
    likesMap.value[postId] = (likesMap.value[postId] ?? 0) + 1
  }
  // 触发响应式（Set 需重新赋值）
  likedSet.value = new Set(likedSet.value)
}
function addComment(): void {
  const t = newCommentText.value.trim()
  if (!t) return
  localComments.value = [
    { id: `c-${Date.now()}`, author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 },
    ...localComments.value,
  ]
  newCommentText.value = ''
  showToast('评论已添加（本地）')
}

// —— 编辑器本地持久化 ——
function loadEditorDraft(): void {
  try {
    const tt = localStorage.getItem('synthos_editor_title')
    const cc = localStorage.getItem('synthos_editor_content')
    const ex = localStorage.getItem('synthos_extra_posts')
    if (tt) editorTitle.value = tt
    if (cc) editorContent.value = cc
    if (ex) {
      const arr = JSON.parse(ex) as MockPost[]
      if (Array.isArray(arr)) extraPosts.value = arr
      // 同步点赞表
      for (const p of extraPosts.value) if (!(p.id in likesMap.value)) likesMap.value[p.id] = p.likes
    }
  } catch {
    // 忽略本地存储异常
  }
}
function saveEditor(): void {
  try {
    localStorage.setItem('synthos_editor_title', editorTitle.value)
    localStorage.setItem('synthos_editor_content', editorContent.value)
    saveStatus.value = `已保存 ${new Date().toLocaleTimeString()}`
    showToast('已保存到本地 ✓')
  } catch {
    showToast('保存失败（存储受限）')
  }
}
function clearEditor(): void {
  editorTitle.value = ''
  editorContent.value = ''
  saveEditor()
}
function publishAsPost(): void {
  const title = editorTitle.value.trim() || '无标题文档'
  const content = editorContent.value.trim() || '（空文档）'
  const newPost: MockPost = {
    id: `local-${Date.now()}`,
    slug: `local-${Date.now()}`,
    title,
    intro: content.slice(0, 60),
    content,
    cover: `https://picsum.photos/seed/local${Date.now()}/800/500`,
    author: mockPosts[0].author,
    group: mockGroups[0],
    tags: [mockTags[0]],
    views: 0,
    likes: 0,
    comments: 0,
    createdAt: new Date().toISOString().slice(0, 10),
  }
  extraPosts.value = [newPost, ...extraPosts.value]
  likesMap.value[newPost.id] = 0
  try {
    localStorage.setItem('synthos_extra_posts', JSON.stringify(extraPosts.value))
  } catch {
    // 忽略
  }
  showToast('已发布到 Finder ✓')
  openPost(newPost)
  openFinder('all')
}

// —— 拖拽与缩放（鼠标友好，纯前端） ——
let dragState: { win: OsWindow; offX: number; offY: number } | null = null
let resizeState: { win: OsWindow; startX: number; startY: number; startW: number; startH: number } | null = null

function startDrag(e: MouseEvent, win: OsWindow): void {
  // 点击红黄绿不触发拖拽
  const target = e.target as HTMLElement
  if (target.closest('.dot')) return
  bringToFront(win.id)
  dragState = { win, offX: e.clientX - win.x, offY: e.clientY - win.y }
  window.addEventListener('mousemove', onDragMove)
  window.addEventListener('mouseup', onDragEnd)
  e.preventDefault()
}
function onDragMove(e: MouseEvent): void {
  if (!dragState) return
  const { win, offX, offY } = dragState
  if (win.maximized) return
  const dw = desktopRef.value?.clientWidth ?? 1200
  const dh = desktopRef.value?.clientHeight ?? 700
  let nx = e.clientX - offX
  let ny = e.clientY - offY
  // 边界 clamp，保留标题栏可见
  nx = Math.max(-win.w + 80, Math.min(nx, dw - 80))
  ny = Math.max(0, Math.min(ny, dh - 40))
  win.x = nx
  win.y = ny
}
function onDragEnd(): void {
  dragState = null
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
}
function startResize(e: MouseEvent, win: OsWindow): void {
  bringToFront(win.id)
  resizeState = { win, startX: e.clientX, startY: e.clientY, startW: win.w, startH: win.h }
  window.addEventListener('mousemove', onResizeMove)
  window.addEventListener('mouseup', onResizeEnd)
  e.preventDefault()
}
function onResizeMove(e: MouseEvent): void {
  if (!resizeState) return
  const { win, startX, startY, startW, startH } = resizeState
  if (win.maximized) return
  const dw = desktopRef.value?.clientWidth ?? 1200
  const dh = desktopRef.value?.clientHeight ?? 700
  let nw = startW + (e.clientX - startX)
  let nh = startH + (e.clientY - startY)
  nw = Math.max(320, Math.min(nw, dw - win.x - 6))
  nh = Math.max(240, Math.min(nh, dh - win.y - 6))
  win.w = nw
  win.h = nh
}
function onResizeEnd(): void {
  resizeState = null
  window.removeEventListener('mousemove', onResizeMove)
  window.removeEventListener('mouseup', onResizeEnd)
}

// —— 时间与生命周期 ——
function tick(): void {
  const d = new Date()
  const w = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
  now.value = `${d.getMonth() + 1}月${d.getDate()}日 周${w} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
onMounted(() => {
  tick()
  timeTimer = window.setInterval(tick, 1000 * 30)
  loadEditorDraft()
  // 全局快捷键 ⌘K / Ctrl+K 打开 Spotlight
  const onKey = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault()
      spotlightOpen.value = !spotlightOpen.value
    }
    if (e.key === 'Escape') spotlightOpen.value = false
  }
  window.addEventListener('keydown', onKey)
  onUnmounted(() => window.removeEventListener('keydown', onKey))
})
onUnmounted(() => {
  if (timeTimer) window.clearInterval(timeTimer)
  window.removeEventListener('mousemove', onDragMove)
  window.removeEventListener('mouseup', onDragEnd)
  window.removeEventListener('mousemove', onResizeMove)
  window.removeEventListener('mouseup', onResizeEnd)
})
</script>

<style scoped>
/* —— 整体 OS 布局 —— */
.os {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #e8e4d8;
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
}
.menubar {
  height: 32px;
  background: #0a0a0f;
  color: #f4f4f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  border-bottom: 3px solid #0a0a0f;
  flex-shrink: 0;
  gap: 12px;
}
.menu-left,
.menu-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo {
  font-weight: 800;
  font-size: 14px;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.hub-link {
  background: #f4f4f0;
  color: #0a0a0f;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  border-width: 2px;
}
.hub-link:hover {
  background: #ffd700;
}
.menu-item {
  font-size: 11px;
  opacity: 0.9;
  cursor: default;
}
.menu-title {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.spotlight-trigger {
  background: #f4f4f0;
  color: #0a0a0f;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-width: 2px;
}
.spotlight-trigger:hover {
  background: #ffd700;
}
.time,
.battery {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

/* —— 桌面 —— */
.desktop {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #d9d6cc;
  /* 拟物网格壁纸 */
  background-image:
    linear-gradient(rgba(10, 10, 15, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(10, 10, 15, 0.06) 1px, transparent 1px),
    radial-gradient(circle at 70% 30%, rgba(255, 0, 110, 0.12), transparent 40%),
    radial-gradient(circle at 20% 80%, rgba(0, 245, 212, 0.18), transparent 45%);
  background-size: 28px 28px, 28px 28px, auto, auto;
}
.wallpaper-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* —— 桌面图标 —— */
.desk-icon {
  position: absolute;
  width: 96px;
  text-align: center;
  cursor: pointer;
  user-select: none;
  padding: 6px 4px;
  border: 2px solid transparent;
}
.desk-icon.selected {
  background: rgba(10, 10, 15, 0.08);
  border-color: #0a0a0f;
}
.desk-icon-img {
  width: 64px;
  height: 64px;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-width: 3px;
  box-shadow: 4px 4px 0 #0a0a0f;
  transition: transform 0.12s;
}
.desk-icon:hover .desk-icon-img {
  transform: translate(-1px, -1px);
  box-shadow: 6px 6px 0 #0a0a0f;
}
.desk-icon.selected .desk-icon-img {
  background: #0a0a0f !important;
  color: #f4f4f0;
}
.desk-emoji {
  font-size: 28px;
  line-height: 1;
}
.folder-tab {
  position: absolute;
  top: -6px;
  left: 6px;
  width: 28px;
  height: 8px;
  background: inherit;
  border: 2px solid #0a0a0f;
  border-bottom: none;
  filter: brightness(0.92);
}
.desk-icon-label {
  font-size: 10px;
  font-weight: 800;
  line-height: 1.3;
  color: #0a0a0f;
  background: #f4f4f0;
  border: 1.5px solid #0a0a0f;
  padding: 2px 4px;
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.desk-icon.selected .desk-icon-label {
  background: #0a0a0f;
  color: #f4f4f0;
}
.desk-icon-sub {
  font-size: 9px;
  color: #333;
  margin-top: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* —— 窗口 —— */
.window {
  position: absolute;
  background: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-width: 3px;
  box-shadow: 8px 8px 0 #0a0a0f;
  min-width: 320px;
  min-height: 240px;
}
.win-titlebar {
  height: 34px;
  background: #f4f4f0;
  border-bottom: 3px solid #0a0a0f;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
  gap: 8px;
}
.win-titlebar:active {
  cursor: grabbing;
}
.traffic {
  display: flex;
  gap: 6px;
  align-items: center;
}
.dot {
  width: 13px;
  height: 13px;
  border: 2px solid #0a0a0f;
  border-radius: 50%;
  cursor: pointer;
  display: inline-block;
}
.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }
.dot:hover { filter: brightness(0.9); transform: scale(1.05); }
.win-title {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.04em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  text-align: center;
}
.win-type-pill {
  font-size: 9px;
  background: #0a0a0f;
  color: #fff;
  padding: 2px 6px;
  border-radius: 999px;
}
.win-body {
  flex: 1;
  overflow: auto;
  background: #fff;
  position: relative;
}
.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 18px;
  height: 18px;
  cursor: nwse-resize;
  background:
    linear-gradient(135deg, transparent 50%, #0a0a0f 50%, #0a0a0f 55%, transparent 55%),
    linear-gradient(135deg, transparent 65%, #0a0a0f 65%, #0a0a0f 70%, transparent 70%);
  background-repeat: no-repeat;
  background-position: right bottom;
  opacity: 0.9;
}

/* —— Finder —— */
.finder-body {
  display: grid;
  grid-template-columns: 176px 1fr;
  overflow: hidden;
}
.finder-side {
  background: #f4f4f0;
  border-right: 3px solid #0a0a0f;
  padding: 10px 8px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.side-title {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #666;
  margin-top: 4px;
}
.side-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 8px;
  background: #fff;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border-width: 2px;
  text-align: left;
  width: 100%;
}
.side-item.active {
  background: #0a0a0f;
  color: #f4f4f0;
}
.side-count {
  font-size: 10px;
  opacity: 0.7;
}
.side-divider {
  height: 2px;
  background: #0a0a0f;
  margin: 6px 0;
  opacity: 0.12;
}
.side-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.side-tag {
  font-size: 9px;
  padding: 3px 6px;
  font-weight: 800;
  border-width: 2px;
}
.side-foot {
  margin-top: auto;
  font-size: 10px;
  color: #666;
  padding-top: 8px;
  border-top: 1px dashed #bbb;
}
.finder-main {
  overflow: auto;
  background: #fff;
  display: flex;
  flex-direction: column;
}
.finder-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-bottom: 2px solid #0a0a0f;
  background: #f4f4f0;
  font-size: 11px;
  font-weight: 700;
}
.finder-toolbar .muted {
  color: #666;
  font-weight: 400;
  margin-left: 6px;
}
.toolbar-btn {
  margin-left: auto;
  background: #0a0a0f;
  color: #fff;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
}
.toolbar-btn:hover { background: #1a1a22; }
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(138px, 1fr));
  gap: 12px;
  padding: 14px;
}
.file-card {
  background: #fff;
  padding: 8px;
  text-align: left;
  cursor: pointer;
  border-width: 2px;
  transition: transform 0.12s, box-shadow 0.12s;
}
.file-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 4px 4px 0 #0a0a0f;
}
.file-thumb {
  height: 92px;
  overflow: hidden;
  position: relative;
  background: #f4f4f0;
  border-width: 2px;
  margin-bottom: 8px;
}
.file-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.file-ext {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: #0a0a0f;
  color: #fff;
  font-size: 8px;
  padding: 2px 5px;
  font-weight: 800;
}
.file-name {
  font-size: 12px;
  font-weight: 800;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 28px;
}
.file-meta,
.file-stats {
  font-size: 10px;
  color: #666;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* —— Post —— */
.post-body {
  padding: 0;
  background: #fff;
}
.post-cover-wrap {
  height: 176px;
  overflow: hidden;
  position: relative;
  border-left: none;
  border-right: none;
  border-top: none;
  border-width: 3px;
}
.post-cover-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.post-cover-tag {
  position: absolute;
  bottom: 10px;
  left: 10px;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 800;
  border-width: 2px;
}
.post-inner {
  padding: 14px 16px 20px;
}
.post-title {
  font-size: 22px;
  line-height: 1.05;
  font-weight: 800;
}
.post-intro {
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.6;
  color: #333;
  background: #f4f4f0;
  border-left: 4px solid #0a0a0f;
  padding: 8px 10px;
}
.post-meta {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #fff;
  font-size: 11px;
  border-width: 2px;
  gap: 8px;
  flex-wrap: wrap;
}
.avatar {
  font-size: 14px;
}
.author-line {
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}
.post-tag {
  font-size: 10px;
  padding: 3px 8px;
  font-weight: 800;
  border-width: 2px;
}
.post-content {
  margin-top: 14px;
  background: #fcfcf8;
  padding: 14px 12px;
  font-size: 12px;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
  border-width: 2px;
  max-height: none;
}
.post-actions {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 11px;
}
.action-btn {
  background: #fff;
  padding: 6px 12px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
  font-size: 11px;
}
.action-btn:hover { background: #f4f4f0; }
.action-btn.liked {
  background: #0a0a0f;
  color: #fff;
}
.action-btn.primary {
  background: #ffd700;
}
.comments {
  margin-top: 16px;
  border-top: 3px solid #0a0a0f;
  padding-top: 12px;
}
.comments-title {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}
.comment-input-row {
  display: flex;
  gap: 8px;
  padding: 6px;
  background: #f4f4f0;
  border-width: 2px;
  margin-bottom: 12px;
}
.comment-input {
  flex: 1;
  border: 2px solid #0a0a0f;
  padding: 7px 10px;
  font-size: 11px;
  background: #fff;
  outline: none;
}
.comment-send {
  background: #0a0a0f;
  color: #fff;
  padding: 6px 14px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
  font-size: 11px;
}
.comment {
  background: #fff;
  padding: 10px 10px;
  border-width: 2px;
  margin-bottom: 8px;
}
.comment-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 6px;
}
.comment-body {
  font-size: 12px;
  line-height: 1.6;
}
.comment-replies {
  margin-top: 8px;
  padding-left: 10px;
  border-left: 3px solid #0a0a0f;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.reply {
  background: #f4f4f0;
  padding: 6px 8px;
  font-size: 11px;
  border-width: 1.5px;
}
.empty-tip {
  padding: 24px;
  text-align: center;
  color: #666;
  font-size: 12px;
}

/* —— Editor —— */
.editor-body {
  display: flex;
  flex-direction: column;
  padding: 10px;
  gap: 8px;
  background: #f4f4f0;
}
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 800;
  padding: 6px 0;
}
.editor-title-input {
  padding: 10px 12px;
  font-size: 18px;
  font-weight: 800;
  border-width: 3px;
  background: #fff;
  outline: none;
}
.editor-textarea {
  flex: 1;
  min-height: 180px;
  padding: 12px;
  font-size: 12px;
  line-height: 1.7;
  border-width: 3px;
  background: #fff;
  outline: none;
  resize: none;
}
.editor-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  gap: 10px;
  flex-wrap: wrap;
}
.editor-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* —— Spotlight —— */
.spotlight-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 15, 0.22);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 56px;
  z-index: 9999;
}
.spotlight {
  width: 560px;
  max-width: 92%;
  background: #fff;
  border-width: 3px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
}
.spotlight-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 12px;
  border-bottom: 3px solid #0a0a0f;
  background: #f4f4f0;
}
.spot-icon {
  font-size: 16px;
  font-weight: 800;
}
.spot-input {
  flex: 1;
  border: 2px solid #0a0a0f;
  padding: 8px 10px;
  font-size: 13px;
  background: #fff;
  outline: none;
}
.spot-esc {
  font-size: 10px;
  background: #0a0a0f;
  color: #fff;
  padding: 4px 7px;
  cursor: pointer;
}
.spotlight-results {
  overflow: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 120px;
}
.spot-hint {
  text-align: center;
  padding: 18px 10px;
  font-size: 11px;
  color: #666;
  line-height: 1.6;
}
.spot-quick {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 10px;
}
.quick-chip {
  background: #fff;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
  border-width: 2px;
}
.quick-chip:hover { background: #ffd700; }
.spot-empty {
  text-align: center;
  padding: 20px;
  font-size: 11px;
  color: #666;
}
.spot-item {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 10px;
  background: #fff;
  text-align: left;
  cursor: pointer;
  border-width: 2px;
  width: 100%;
}
.spot-item:hover {
  background: #f4f4f0;
  transform: translate(-1px, -1px);
  box-shadow: 3px 3px 0 #0a0a0f;
}
.spot-item-icon {
  font-size: 20px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffd700;
  border: 2px solid #0a0a0f;
  flex-shrink: 0;
}
.spot-item-main {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}
.spot-item-main b {
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.spot-item-main span {
  font-size: 10px;
  color: #555;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.spot-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.spot-tag {
  font-size: 9px;
  padding: 1px 5px;
  color: #0a0a0f;
  font-weight: 800;
  border: 1px solid #0a0a0f;
}
.spot-group {
  font-size: 9px;
  background: #0a0a0f;
  color: #fff;
  padding: 1px 5px;
}
.spot-arrow {
  font-size: 14px;
  font-weight: 800;
}
.spot-foot {
  padding: 7px 12px;
  border-top: 2px solid #0a0a0f;
  background: #f4f4f0;
  font-size: 10px;
  color: #666;
  text-align: center;
}

/* —— Dock —— */
.dock-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0 12px;
  background: transparent;
  gap: 6px;
}
.dock {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(244, 244, 240, 0.96);
  padding: 8px 10px;
  border-width: 3px;
  backdrop-filter: blur(6px);
}
.dock-item {
  width: 52px;
  height: 52px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
  cursor: pointer;
  border-width: 2px;
  position: relative;
  background: #fff;
  padding: 2px;
}
.dock-item:hover {
  transform: translateY(-3px);
  box-shadow: 3px 3px 0 #0a0a0f;
}
.dock-item.active {
  border-color: #0a0a0f;
  box-shadow: 3px 3px 0 #0a0a0f;
}
.dock-icon {
  font-size: 20px;
  line-height: 1;
}
.dock-label {
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.dock-dot {
  position: absolute;
  bottom: -6px;
  width: 5px;
  height: 5px;
  background: #0a0a0f;
  border-radius: 50%;
}
.dock-divider {
  width: 2px;
  height: 36px;
  background: #0a0a0f;
  opacity: 0.2;
  margin: 0 2px;
}
.dock-item.trash {
  background: #f4f4f0;
}
.dock-hint {
  font-size: 9px;
  color: #666;
  letter-spacing: 0.06em;
}

/* —— Toast —— */
.toast {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  background: #0a0a0f;
  color: #f4f4f0;
  padding: 8px 14px;
  font-size: 11px;
  font-weight: 800;
  z-index: 99999;
  border-width: 2px;
  border-color: #f4f4f0;
  white-space: nowrap;
}
.muted { color: #666; }

/* —— 响应式：窄屏优化 —— */
@media (max-width: 860px) {
  .finder-body { grid-template-columns: 1fr; }
  .finder-side { border-right: none; border-bottom: 3px solid #0a0a0f; max-height: 160px; }
  .hide-mobile { display: none !important; }
  .desk-icon { transform: scale(0.92); }
  .window { min-width: 280px; }
}
@media (max-width: 560px) {
  .desktop { padding-bottom: 20px; }
  .desk-icon { width: 84px; }
  .desk-icon-img { width: 56px; height: 56px; }
  .spotlight { max-width: 96%; }
}
</style>
