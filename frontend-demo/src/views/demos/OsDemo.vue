<template>
  <div class="os">
    <!-- 顶部菜单栏：SynthOS + Hub 入口 + Spotlight + 时间 -->
    <nav class="menubar">
      <div class="menu-left">
        <span class="logo display"> SynthOS</span>
        <router-link to="/" class="hub-link">← Hub</router-link>
        <span class="menu-item hide-mobile">文件</span>
        <span class="menu-item hide-mobile">编辑</span>
        <span class="menu-item hide-mobile">窗口</span>
        <span class="menu-item hide-mobile">帮助</span>
      </div>
      <div class="menu-center mono hide-mobile">
        <span class="menu-title">{{ topTitle }}</span>
      </div>
      <div class="menu-right">
        <button class="spotlight-trigger mono" @click="spotlightOpen = !spotlightOpen" title="Spotlight 搜索 (⌘K)">
          ⌕ 搜索
        </button>
        <span class="time mono">{{ now }}</span>
        <span class="battery mono hide-mobile">◧ 86%</span>
      </div>
    </nav>

    <!-- 桌面主区域 -->
    <div class="desktop" ref="desktopRef" @click="onDesktopClick">
      <!-- 桌面壁纸柔和渐变 -->
      <div class="wallpaper-grid" />

      <!-- Spotlight 搜索覆盖层 -->
      <div v-if="spotlightOpen" class="spotlight-overlay" @click.self="spotlightOpen = false">
        <div class="spotlight">
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
                <button v-for="k in quickKeys" :key="k" class="quick-chip" @click="spotlightQuery = k">{{ k }}</button>
              </div>
            </div>
            <template v-else>
              <div v-if="spotlightResults.length === 0" class="spot-empty mono">无结果 — 换个关键词试试</div>
              <button
                v-for="p in spotlightResults"
                :key="p.id"
                class="spot-item"
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
        <div class="desk-icon-img" :style="{ background: icon.bg }">
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
        class="window"
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
              class="side-item mono"
              :class="{ active: win.groupFilter === g.id }"
              @click="win.groupFilter = g.id"
            >
              <span>{{ g.icon }} {{ g.name }}</span>
              <span class="side-count">{{ g.count }}</span>
            </button>
            <div class="side-divider"></div>
            <div class="side-title mono">标签</div>
            <div class="side-tags">
              <span v-for="t in mockTags" :key="t.id" class="side-tag mono" :style="{ background: t.color }">{{ t.name }}</span>
            </div>
            <div class="side-foot mono">共 {{ filteredPosts(win).length }} 项</div>
          </aside>
          <section class="finder-main">
            <div class="finder-toolbar mono">
              <span>▦ 网格</span>
              <span class="muted">{{ win.groupFilter === 'all' ? '全部文件' : (mockGroups.find(g=>g.id===win.groupFilter)?.name || '文件夹') }}</span>
              <button class="toolbar-btn" @click="openEditor">＋ 新建文档</button>
            </div>
            <div class="file-grid">
              <button
                v-for="p in filteredPosts(win)"
                :key="p.id"
                class="file-card"
                @click="openPost(p)"
                @dblclick="openPost(p)"
              >
                <div class="file-thumb" :style="{ background: p.tags[0]?.color || '#fff' }">
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
            <div class="post-cover-wrap">
              <img :src="getPostById(win.postId!)!.cover" :alt="getPostById(win.postId!)!.title" />
              <span class="post-cover-tag mono" :style="{ background: getPostById(win.postId!)!.tags[0]?.color || '#5ac8fa' }">{{ getPostById(win.postId!)!.group.icon }} {{ getPostById(win.postId!)!.group.name }}</span>
            </div>
            <div class="post-inner">
              <h2 class="post-title display">{{ getPostById(win.postId!)!.title }}</h2>
              <p class="post-intro mono">{{ getPostById(win.postId!)!.intro }}</p>
              <div class="post-meta mono">
                <span class="author-line"><span class="avatar">{{ getPostById(win.postId!)!.author.avatar }}</span> {{ getPostById(win.postId!)!.author.display_name }} · {{ getPostById(win.postId!)!.author.type }}</span>
                <span>{{ getPostById(win.postId!)!.createdAt }} · 👁 {{ getPostById(win.postId!)!.views }}</span>
              </div>
              <div class="post-tags mono">
                <span v-for="t in getPostById(win.postId!)!.tags" :key="t.id" class="post-tag" :style="{ background: t.color }">{{ t.name }}</span>
              </div>
              <!-- 正文：Markdown 渲染（glass 玻璃拟态主题，适配毛玻璃卡片） -->
              <MarkdownRenderer :content="getPostById(win.postId!)!.content" theme="glass" />
              <!-- 额外图片：若存在 images/extraImages 则补充展示（Markdown 内已可通过 ![ ](url) 渲染，此处可选兜底） -->
              <div v-if="(getPostById(win.postId!) as any)?.images?.length || (getPostById(win.postId!) as any)?.extraImages?.length" class="post-extra-images mono">
                <template v-if="(getPostById(win.postId!) as any)?.images?.length">
                  <img v-for="(img, idx) in (getPostById(win.postId!) as any).images" :key="`img-${idx}`" :src="img" loading="lazy" :alt="`image-${Number(idx)+1}`" />
                </template>
                <template v-if="(getPostById(win.postId!) as any)?.extraImages?.length">
                  <img v-for="(img, idx) in (getPostById(win.postId!) as any).extraImages" :key="`extra-${idx}`" :src="img" loading="lazy" :alt="`extra-${Number(idx)+1}`" />
                </template>
              </div>

              <!-- 操作栏：点赞 -->
              <div class="post-actions mono">
                <button class="action-btn" :class="{ liked: isLiked(win.postId!) }" @click="toggleLike(win.postId!)">
                  {{ isLiked(win.postId!) ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(win.postId!) }}
                </button>
                <span class="muted">💬 {{ localComments.length }} 评论 · 分享 ↗</span>
                <button class="action-btn" @click="showToast('链接已复制（Mock）')">复制链接</button>
              </div>

              <!-- 评论区 -->
              <div class="comments">
                <div class="comments-title mono">评论 · {{ localComments.length }}</div>
                <div class="comment-input-row">
                  <input v-model="newCommentText" class="comment-input mono" placeholder="写点什么…（本地 Mock，不会上传）" @keydown.enter="addComment" />
                  <button class="comment-send mono" @click="addComment">发送</button>
                </div>
                <div v-for="c in localComments" :key="c.id" class="comment">
                  <div class="comment-head mono">
                    <span><b>{{ c.avatar }} {{ c.author }}</b> · {{ c.time }}</span>
                    <span>♥ {{ c.likes }}</span>
                  </div>
                  <p class="comment-body mono">{{ c.content }}</p>
                  <div v-if="c.replies && c.replies.length" class="comment-replies">
                    <div v-for="r in c.replies" :key="r.id" class="reply mono">
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
          <input v-model="editorTitle" class="editor-title-input display" placeholder="无标题文档…" />
          <textarea v-model="editorContent" class="editor-textarea mono" placeholder="在此输入正文… 支持 Markdown，保存仅在本地 localStorage，不会请求后端。"></textarea>
          <div class="editor-foot mono">
            <span>{{ editorContent.length }} 字 · {{ editorTitle ? '有标题' : '无标题' }}</span>
            <div class="editor-actions">
              <button class="action-btn" @click="clearEditor">清空</button>
              <button class="action-btn primary" @click="saveEditor">💾 保存到本地</button>
              <button class="action-btn" @click="publishAsPost">发布为新文件 → Finder</button>
            </div>
          </div>
        </div>

        <!-- 缩放手柄 -->
        <div class="resize-handle" @mousedown.stop="startResize($event, win)" title="拖动缩放"></div>
      </div>

      <!-- 轻提示 Toast -->
      <div v-if="toastMsg" class="toast mono">{{ toastMsg }}</div>
    </div>

    <!-- 底部 Dock -->
    <div class="dock-wrap">
      <div class="dock">
        <button
          v-for="d in dockItems"
          :key="d.id"
          class="dock-item"
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
        <button class="dock-item trash" title="废纸篓" @click="showToast('废纸篓是空的（Mock）')">
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
 * SynthOS — 浏览器内伪操作系统 (Glass Aqua 拟态)
 * 纯前端 Mock，无后端；所有数据来自 frontend-demo/src/mock/data.ts
 * 交互：拖拽/缩放/层叠窗口、Finder 过滤、Post 阅读、Editor 本地保存、Spotlight 全局搜索
 * 设计语言：Glass Aqua — 毛玻璃 + 淡蓝灰 + 柔和阴影 + Inter/SF Mono
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockGroups, mockTags, mockComments, type MockPost } from '@/mock/data'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

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
  const bgs = ['#ffffff', '#e0f2fe', '#fce7f3', '#e0fdf4']
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
      bg: '#dcfce7',
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
      bg: '#ffedd5',
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
  { id: 'finder', icon: '🗂️', label: '访达', bg: 'rgba(255,255,255,0.85)' },
  { id: 'post', icon: '📄', label: '文章', bg: 'rgba(255,255,255,0.85)' },
  { id: 'editor', icon: '✎', label: '编辑器', bg: 'rgba(255,255,255,0.85)' },
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
/* ========== Glass Aqua 设计语言 ========== */
/* 背景 #eef2f7 淡蓝灰 · 窗口 rgba(255,255,255,.72) blur18 · 边框 rgba(0,0,0,.08) · 圆角12 · 阴影 0 8 32 / inset 高光 */
/* 字体 Inter + SF Mono · Dock 放大 scale · 菜单栏毛玻璃 · 彻底无 brutal 粗黑边 */

/* —— 整体 OS 布局 —— */
.os {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #eef2f7;
  overflow: hidden;
  /* 主字体 Inter，中文回退 */
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  color: #1d1d1f;
}
/* 等宽辅助 */
.mono {
  font-family: 'SF Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
.display {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* —— 顶部菜单栏：半透明毛玻璃 —— */
.menubar {
  height: 28px;
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(18px) saturate(180%);
  -webkit-backdrop-filter: blur(18px) saturate(180%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  flex-shrink: 0;
  gap: 12px;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.6) inset, 0 1px 8px rgba(0, 0, 0, 0.04);
  z-index: 50;
}
.menu-left,
.menu-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo {
  font-weight: 800;
  font-size: 13px;
  letter-spacing: -0.02em;
  white-space: nowrap;
  color: #1d1d1f;
}
.hub-link {
  background: rgba(0, 122, 255, 0.08);
  border: 1px solid rgba(0, 122, 255, 0.18);
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #007aff;
  text-decoration: none;
  transition: background 0.2s, transform 0.15s;
}
.hub-link:hover {
  background: rgba(0, 122, 255, 0.16);
  transform: translateY(-0.5px);
}
.menu-item {
  font-size: 11px;
  font-weight: 500;
  color: #3a3a3c;
  opacity: 0.85;
  cursor: default;
  padding: 2px 6px;
  border-radius: 6px;
}
.menu-item:hover {
  background: rgba(0, 0, 0, 0.05);
}
.menu-title {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #6e6e73;
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.spotlight-trigger {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  color: #3a3a3c;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}
.spotlight-trigger:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}
.time,
.battery {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.01em;
  white-space: nowrap;
  color: #1d1d1f;
}

/* —— 桌面：淡蓝灰 + 柔和水色光斑 —— */
.desktop {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #eef2f7;
  /* 淡蓝灰基底 + 水波光晕 */
  background-image:
    radial-gradient(ellipse 820px 520px at 18% 12%, rgba(125, 211, 252, 0.18) 0%, transparent 62%),
    radial-gradient(ellipse 680px 480px at 82% 78%, rgba(167, 139, 250, 0.14) 0%, transparent 64%),
    radial-gradient(ellipse 540px 360px at 55% 45%, rgba(255, 255, 255, 0.9) 0%, transparent 66%),
    linear-gradient(180deg, #eef2f7 0%, #e8ecf3 100%);
}
.wallpaper-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  /* 极淡的网格纹理，营造纸感但不抢戏 */
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.55) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.45) 1px, transparent 1px);
  background-size: 28px 28px;
  opacity: 0.35;
}

/* —— 桌面图标：玻璃拟态 + 悬浮感 —— */
.desk-icon {
  position: absolute;
  width: 96px;
  text-align: center;
  cursor: pointer;
  user-select: none;
  padding: 8px 4px;
  border-radius: 12px;
  border: 1px solid transparent;
  transition: background 0.2s, border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.desk-icon:hover {
  transform: translateY(-1px);
}
.desk-icon.selected {
  background: rgba(255, 255, 255, 0.58);
  border-color: rgba(0, 122, 255, 0.18);
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06), 0 1px 0 rgba(255, 255, 255, 0.7) inset;
}
.desk-icon-img {
  width: 60px;
  height: 60px;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.75);
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.85) inset;
  backdrop-filter: blur(8px);
  transition: transform 0.18s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.18s;
}
.desk-icon:hover .desk-icon-img {
  transform: scale(1.06) translateY(-1px);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.1),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
}
.desk-icon.selected .desk-icon-img {
  box-shadow:
    0 8px 24px rgba(0, 122, 255, 0.18),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
  border-color: rgba(0, 122, 255, 0.2);
}
.desk-emoji {
  font-size: 26px;
  line-height: 1;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.08));
}
.folder-tab {
  position: absolute;
  top: -5px;
  left: 10px;
  width: 22px;
  height: 6px;
  background: inherit;
  border-radius: 4px 4px 0 0;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-bottom: none;
  filter: brightness(1.04);
  opacity: 0.9;
}
.desk-icon-label {
  font-size: 10px;
  font-weight: 600;
  line-height: 1.3;
  color: #1d1d1f;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 3px 6px;
  border-radius: 7px;
  display: inline-block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
}
.desk-icon.selected .desk-icon-label {
  background: #007aff;
  color: #fff;
  border-color: rgba(0, 122, 255, 0.4);
  box-shadow: 0 2px 10px rgba(0, 122, 255, 0.28);
}
.desk-icon-sub {
  font-size: 9px;
  color: #6e6e73;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* —— 窗口：核心玻璃拟态 ==  */
.window {
  position: absolute;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(18px) saturate(175%);
  -webkit-backdrop-filter: blur(18px) saturate(175%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 1px 0 rgba(255, 255, 255, 0.6) inset,
    0 0 0 0.5px rgba(255, 255, 255, 0.4) inset;
  min-width: 320px;
  min-height: 240px;
  transition: box-shadow 0.2s;
}
.window:active {
  box-shadow:
    0 12px 40px rgba(0, 0, 0, 0.14),
    0 1px 0 rgba(255, 255, 255, 0.65) inset;
}
.win-titlebar {
  height: 36px;
  background: rgba(255, 255, 255, 0.42);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
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
  gap: 7px;
  align-items: center;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  display: inline-block;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 1px 0 rgba(255, 255, 255, 0.6) inset;
  transition: transform 0.15s, filter 0.15s;
}
.dot.red { background: #ff5f56; }
.dot.yellow { background: #ffbd2e; }
.dot.green { background: #27c93f; }
.dot:hover { filter: brightness(0.96); transform: scale(1.12); }
.win-title {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #1d1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  text-align: center;
}
.win-type-pill {
  font-size: 9px;
  font-weight: 700;
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
  padding: 3px 7px;
  border-radius: 999px;
  border: 1px solid rgba(0, 122, 255, 0.14);
  letter-spacing: 0.04em;
}
.win-body {
  flex: 1;
  overflow: auto;
  background: rgba(255, 255, 255, 0.18);
  position: relative;
}
/* 滚动条柔和 */
.win-body::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.win-body::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: content-box;
}
.win-body::-webkit-scrollbar-track {
  background: transparent;
}
.resize-handle {
  position: absolute;
  right: 6px;
  bottom: 6px;
  width: 14px;
  height: 14px;
  cursor: nwse-resize;
  opacity: 0.5;
  background:
    linear-gradient(135deg, transparent 40%, rgba(0, 0, 0, 0.18) 40%, rgba(0, 0, 0, 0.18) 48%, transparent 48%),
    linear-gradient(135deg, transparent 60%, rgba(0, 0, 0, 0.18) 60%, rgba(0, 0, 0, 0.18) 68%, transparent 68%);
  border-radius: 2px;
  transition: opacity 0.2s;
}
.resize-handle:hover { opacity: 0.85; }

/* —— Finder —— */
.finder-body {
  display: grid;
  grid-template-columns: 176px 1fr;
  overflow: hidden;
}
.finder-side {
  background: rgba(255, 255, 255, 0.38);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  padding: 12px 8px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.side-title {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #86868b;
  margin-top: 6px;
  text-transform: uppercase;
}
.side-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 10px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  color: #1d1d1f;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.side-item:hover {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(0, 0, 0, 0.04);
}
.side-item.active {
  background: #007aff;
  color: #fff;
  border-color: rgba(0, 122, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.28);
}
.side-item.active .side-count { color: rgba(255, 255, 255, 0.85); }
.side-count {
  font-size: 10px;
  color: #86868b;
  font-weight: 500;
}
.side-divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.06);
  margin: 8px 4px;
}
.side-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.side-tag {
  font-size: 9px;
  padding: 4px 7px;
  font-weight: 700;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  color: #1d1d1f;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.side-foot {
  margin-top: auto;
  font-size: 10px;
  color: #86868b;
  padding-top: 10px;
  border-top: 1px dashed rgba(0, 0, 0, 0.08);
}
.finder-main {
  overflow: auto;
  background: rgba(255, 255, 255, 0.22);
  display: flex;
  flex-direction: column;
}
.finder-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(10px);
  font-size: 11px;
  font-weight: 600;
  color: #1d1d1f;
}
.finder-toolbar .muted {
  color: #86868b;
  font-weight: 400;
  margin-left: 6px;
}
.toolbar-btn {
  margin-left: auto;
  background: #007aff;
  color: #fff;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(0, 122, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.28), 0 1px 0 rgba(255, 255, 255, 0.4) inset;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}
.toolbar-btn:hover { background: #0a84ff; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,122,255,0.32); }
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 14px;
  padding: 16px;
}
.file-card {
  background: rgba(255, 255, 255, 0.68);
  backdrop-filter: blur(12px);
  padding: 10px;
  text-align: left;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06), 0 1px 0 rgba(255, 255, 255, 0.7) inset;
  transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s, border-color 0.2s;
}
.file-card:hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.1), 0 1px 0 rgba(255, 255, 255, 0.85) inset;
  border-color: rgba(0, 122, 255, 0.12);
}
.file-thumb {
  height: 92px;
  overflow: hidden;
  position: relative;
  background: #f5f7fb;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  margin-bottom: 10px;
}
.file-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.file-ext {
  position: absolute;
  bottom: 6px;
  right: 6px;
  background: rgba(29, 29, 31, 0.82);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 8px;
  padding: 3px 6px;
  border-radius: 6px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.file-name {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.25;
  color: #1d1d1f;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 30px;
}
.file-meta,
.file-stats {
  font-size: 10px;
  color: #86868b;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* —— Post —— */
.post-body {
  padding: 0;
  background: rgba(255, 255, 255, 0.32);
}
.post-cover-wrap {
  height: 176px;
  overflow: hidden;
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
.post-cover-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.post-cover-tag {
  position: absolute;
  bottom: 12px;
  left: 12px;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  color: #1d1d1f;
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12), 0 1px 0 rgba(255, 255, 255, 0.6) inset;
  backdrop-filter: blur(8px);
}
.post-inner {
  padding: 16px 18px 22px;
}
.post-title {
  font-size: 21px;
  line-height: 1.15;
  font-weight: 800;
  color: #1d1d1f;
  letter-spacing: -0.03em;
}
.post-intro {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.65;
  color: #3a3a3c;
  background: rgba(255, 255, 255, 0.58);
  border-left: 3px solid rgba(0, 122, 255, 0.32);
  padding: 10px 12px;
  border-radius: 8px;
  backdrop-filter: blur(8px);
}
.post-meta {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  font-size: 11px;
  color: #3a3a3c;
  gap: 8px;
  flex-wrap: wrap;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
}
.avatar {
  font-size: 14px;
}
.author-line {
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.post-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 12px;
}
.post-tag {
  font-size: 10px;
  padding: 4px 9px;
  font-weight: 700;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.post-content {
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  padding: 16px 14px;
  font-size: 12px;
  line-height: 1.78;
  white-space: pre-wrap;
  word-break: break-word;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}
/* Markdown 容器：沿用 post-content 卡片质感，适配 glass 玻璃拟态 */
.post-inner .md {
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  padding: 16px 14px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}
/* 额外图片网格：images/extraImages 兜底展示（Markdown 内已可通过 ![ ](url) 渲染） */
.post-extra-images {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}
.post-extra-images img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}
.post-actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 11px;
}
.action-btn {
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(10px);
  padding: 7px 14px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 999px;
  font-size: 11px;
  color: #1d1d1f;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05), 0 1px 0 rgba(255, 255, 255, 0.7) inset;
  transition: all 0.18s;
}
.action-btn:hover { background: #fff; transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,0.08); }
.action-btn.liked {
  background: #ff3b30;
  color: #fff;
  border-color: rgba(255, 59, 48, 0.3);
  box-shadow: 0 4px 14px rgba(255, 59, 48, 0.28);
}
.action-btn.primary {
  background: #007aff;
  color: #fff;
  border-color: rgba(0, 122, 255, 0.32);
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.28);
}
.action-btn.primary:hover { background: #0a84ff; }
.comments {
  margin-top: 18px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  padding-top: 14px;
}
.comments-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #1d1d1f;
  margin-bottom: 10px;
}
.comment-input-row {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.56);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  margin-bottom: 14px;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
}
.comment-input {
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 8px 12px;
  font-size: 11px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.comment-input:focus {
  border-color: rgba(0, 122, 255, 0.32);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12);
}
.comment-send {
  background: #007aff;
  color: #fff;
  padding: 7px 16px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(0, 122, 255, 0.3);
  border-radius: 999px;
  font-size: 11px;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.28);
  transition: all 0.15s;
}
.comment-send:hover { background: #0a84ff; transform: translateY(-0.5px); }
.comment {
  background: rgba(255, 255, 255, 0.66);
  backdrop-filter: blur(10px);
  padding: 12px 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  margin-bottom: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}
.comment-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 6px;
  color: #3a3a3c;
}
.comment-body {
  font-size: 12px;
  line-height: 1.6;
  color: #1d1d1f;
}
.comment-replies {
  margin-top: 10px;
  padding-left: 12px;
  border-left: 2px solid rgba(0, 122, 255, 0.16);
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.reply {
  background: rgba(255, 255, 255, 0.72);
  padding: 7px 10px;
  font-size: 11px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}
.empty-tip {
  padding: 32px;
  text-align: center;
  color: #86868b;
  font-size: 12px;
}

/* —— Editor —— */
.editor-body {
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 10px;
  background: rgba(255, 255, 255, 0.24);
}
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  color: #1d1d1f;
  padding: 4px 2px;
}
.editor-toolbar .muted { color: #86868b; font-weight: 500; }
.editor-title-input {
  padding: 12px 14px;
  font-size: 17px;
  font-weight: 800;
  letter-spacing: -0.02em;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(10px);
  outline: none;
  color: #1d1d1f;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.editor-title-input:focus,
.editor-textarea:focus {
  border-color: rgba(0, 122, 255, 0.28);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12), 0 2px 12px rgba(0, 0, 0, 0.06);
}
.editor-textarea {
  flex: 1;
  min-height: 180px;
  padding: 14px;
  font-size: 12px;
  line-height: 1.72;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(10px);
  outline: none;
  resize: none;
  color: #1d1d1f;
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
}
.editor-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #86868b;
  gap: 10px;
  flex-wrap: wrap;
}
.editor-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* —— Spotlight：玻璃拟态居中弹窗 —— */
.spotlight-overlay {
  position: absolute;
  inset: 0;
  background: rgba(238, 242, 247, 0.42);
  backdrop-filter: blur(10px) saturate(150%);
  -webkit-backdrop-filter: blur(10px) saturate(150%);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 56px;
  z-index: 9999;
}
.spotlight {
  width: 560px;
  max-width: 92%;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
  box-shadow:
    0 16px 48px rgba(0, 0, 0, 0.14),
    0 1px 0 rgba(255, 255, 255, 0.7) inset;
  animation: spotIn 0.22s cubic-bezier(0.175, 0.885, 0.32, 1.2);
}
@keyframes spotIn {
  from { opacity: 0; transform: translateY(8px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.spotlight-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.42);
}
.spot-icon {
  font-size: 16px;
  font-weight: 800;
  color: #86868b;
}
.spot-input {
  flex: 1;
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 9px 12px;
  font-size: 13px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  outline: none;
  color: #1d1d1f;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.spot-input:focus {
  border-color: rgba(0, 122, 255, 0.32);
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.12);
}
.spot-esc {
  font-size: 10px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.06);
  color: #3a3a3c;
  padding: 5px 8px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: background 0.15s;
}
.spot-esc:hover { background: rgba(0, 0, 0, 0.1); }
.spotlight-results {
  overflow: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 120px;
}
.spotlight-results::-webkit-scrollbar { width: 6px; }
.spotlight-results::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 999px; }
.spot-hint {
  text-align: center;
  padding: 22px 10px;
  font-size: 11px;
  color: #86868b;
  line-height: 1.6;
}
.spot-quick {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 12px;
}
.quick-chip {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(0, 0, 0, 0.06);
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #1d1d1f;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04);
  transition: all 0.15s;
}
.quick-chip:hover { background: #007aff; color: #fff; border-color: rgba(0,122,255,0.3); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,122,255,0.2); }
.spot-empty {
  text-align: center;
  padding: 24px;
  font-size: 11px;
  color: #86868b;
}
.spot-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 11px 12px;
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  text-align: left;
  cursor: pointer;
  width: 100%;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.03);
  transition: all 0.18s;
}
.spot-item:hover {
  background: rgba(255, 255, 255, 0.92);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: rgba(0, 122, 255, 0.14);
}
.spot-item-icon {
  font-size: 18px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 122, 255, 0.1);
  border: 1px solid rgba(0, 122, 255, 0.12);
  border-radius: 8px;
  flex-shrink: 0;
}
.spot-item-main {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 0;
}
.spot-item-main b {
  font-size: 12px;
  color: #1d1d1f;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.spot-item-main span {
  font-size: 10px;
  color: #86868b;
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
  padding: 2px 6px;
  color: #1d1d1f;
  font-weight: 700;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}
.spot-group {
  font-size: 9px;
  background: rgba(0, 0, 0, 0.06);
  color: #3a3a3c;
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}
.spot-arrow {
  font-size: 14px;
  font-weight: 700;
  color: #86868b;
}
.spot-foot {
  padding: 8px 14px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.42);
  font-size: 10px;
  color: #86868b;
  text-align: center;
}

/* —— Dock：毛玻璃 + 放大动效 —— */
.dock-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0 14px;
  background: transparent;
  gap: 6px;
  pointer-events: none;
}
.dock {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.64);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 18px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    0 1px 0 rgba(255, 255, 255, 0.65) inset;
  pointer-events: auto;
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
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  position: relative;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px;
  box-shadow:
    0 2px 10px rgba(0, 0, 0, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
  transition: transform 0.24s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.2s, background 0.2s, border-color 0.2s;
  transform-origin: bottom center;
}
.dock-item:hover {
  transform: scale(1.28) translateY(-6px);
  box-shadow:
    0 10px 28px rgba(0, 0, 0, 0.14),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
  border-color: rgba(0, 122, 255, 0.16);
  background: #fff;
  z-index: 2;
}
.dock-item.active {
  border-color: rgba(0, 122, 255, 0.18);
  box-shadow:
    0 4px 16px rgba(0, 122, 255, 0.18),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
  background: #fff;
}
.dock-icon {
  font-size: 20px;
  line-height: 1;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.06));
}
.dock-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.03em;
  white-space: nowrap;
  color: #3a3a3c;
}
.dock-dot {
  position: absolute;
  bottom: -7px;
  width: 4px;
  height: 4px;
  background: #007aff;
  border-radius: 50%;
  box-shadow: 0 1px 4px rgba(0, 122, 255, 0.4);
}
.dock-divider {
  width: 1px;
  height: 32px;
  background: rgba(0, 0, 0, 0.08);
  margin: 0 4px;
}
.dock-item.trash {
  background: rgba(255, 255, 255, 0.72);
}
.dock-hint {
  font-size: 9px;
  color: #86868b;
  letter-spacing: 0.04em;
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
}

/* —— Toast：玻璃胶囊 —— */
.toast {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(29, 29, 31, 0.88);
  backdrop-filter: blur(14px);
  color: #f5f5f7;
  padding: 9px 16px;
  font-size: 11px;
  font-weight: 700;
  z-index: 99999;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  white-space: nowrap;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18), 0 1px 0 rgba(255, 255, 255, 0.08) inset;
  animation: toastIn 0.2s ease;
}
@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-6px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
.muted { color: #86868b; }

/* —— 响应式：窄屏优化 —— */
@media (max-width: 860px) {
  .finder-body { grid-template-columns: 1fr; }
  .finder-side { border-right: none; border-bottom: 1px solid rgba(0,0,0,0.06); max-height: 160px; }
  .hide-mobile { display: none !important; }
  .desk-icon { transform: scale(0.92); }
  .window { min-width: 280px; }
}
@media (max-width: 560px) {
  .desktop { padding-bottom: 20px; }
  .desk-icon { width: 84px; }
  .desk-icon-img { width: 56px; height: 56px; border-radius: 12px; }
  .spotlight { max-width: 96%; }
  .dock-item { width: 46px; height: 46px; }
  .dock-item:hover { transform: scale(1.16) translateY(-4px); }
}
</style>
