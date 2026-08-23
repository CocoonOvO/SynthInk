<template>
  <div class="desk-root">
    <!-- 顶部栏 -->
    <div class="topbar brutal-border">
      <router-link to="/" class="hub-btn brutal-border mono">← Hub</router-link>
      <span class="title display">SynthDesk — 虚拟笔记本 · 拟物书桌</span>
      <span class="hint mono">拖拽拍立得 · 点击切文章 · 翻页 →</span>
    </div>

    <div class="desk">
      <!-- 木纹桌面 -->
      <div class="desk-surface"></div>

      <!-- 左侧索引抽屉 -->
      <aside class="drawer brutal-border brutal-shadow">
        <div class="drawer-head mono">索引抽屉 · INDEX</div>
        <input v-model="q" placeholder="搜索标题 / intro" class="search brutal-border mono" />
        <div class="group-chips">
          <button
            v-for="g in mockGroups"
            :key="g.id"
            class="chip brutal-border mono"
            :class="{ active: groupFilter===g.id }"
            @click="groupFilter = groupFilter===g.id ? '' : g.id"
          >{{ g.icon }} {{ g.name }}</button>
          <button class="chip brutal-border mono" :class="{ active: !groupFilter }" @click="groupFilter=''">全部</button>
        </div>
        <div class="post-list">
          <button
            v-for="p in filteredPosts"
            :key="p.id"
            class="post-item brutal-border"
            :class="{ active: p.id===current.id }"
            @click="selectPost(p)"
          >
            <span class="mono idx">{{ p.id }}</span>
            <span class="tit">{{ p.title }}</span>
            <span class="mono meta">{{ p.group.icon }} · {{ p.author.display_name }}</span>
          </button>
        </div>
        <div class="drawer-foot mono">共 {{ filteredPosts.length }} 篇 · 点击即翻开</div>
      </aside>

      <!-- 中央活页笔记本 -->
      <section class="book-wrap">
        <div class="book brutal-border brutal-shadow" :class="{ flipping: isFlipping, 'flip-next': flipDir==='next' }">
          <!-- 活页环 -->
          <div class="rings">
            <span v-for="i in 7" :key="i" class="ring"></span>
          </div>
          <!-- 左页（装饰） -->
          <div class="page left-page">
            <div class="page-inner mono">
              <div class="page-label">SYNTHINK ARCHIVE — {{ current.group.name }}</div>
              <div class="tape tape--left"></div>
              <img :src="current.cover" class="left-cover" alt="" />
              <div class="left-intro">{{ current.intro }}</div>
              <div class="stamp brutal-border mono">NO. {{ current.id.toUpperCase() }} · {{ current.createdAt }}</div>
            </div>
          </div>
          <!-- 右页（正文） -->
          <div class="page right-page">
            <div class="page-inner">
              <div class="page-head">
                <h2 class="display book-title">{{ current.title }}</h2>
                <div class="book-meta mono">
                  <span class="author" :style="{ borderColor: current.author.color }">{{ current.author.avatar }} {{ current.author.display_name }}</span>
                  <span>{{ current.views }} 阅 · {{ localLikes[current.id] ?? current.likes }} ♥</span>
                  <span class="tag" v-for="t in current.tags" :key="t.id" :style="{ background: t.color, color: '#0a0a0f' }">{{ t.name }}</span>
                </div>
              </div>
              <pre class="content mono">{{ current.content }}</pre>
              <div class="actions mono">
                <button class="brutal-border" @click="toggleLike(current.id)">♥ {{ liked[current.id] ? '已赞' : '点赞' }} ({{ localLikes[current.id] ?? current.likes }})</button>
                <button class="brutal-border" @click="prevPage" :disabled="currentIdx===0">← 上一篇</button>
                <button class="brutal-border" @click="nextPage" :disabled="currentIdx===filteredPosts.length-1">下一篇 →</button>
              </div>
              <!-- 页边便签（评论） -->
              <div class="margin-notes">
                <div v-for="c in localComments" :key="c.id" class="note brutal-border mono">
                  <span class="note-pin">📌</span>
                  <b>{{ c.avatar }} {{ c.author }}</b> · {{ c.time }}
                  <p>{{ c.content }}</p>
                  <span v-if="c.replies?.length" class="reply">↳ {{ c.replies[0].avatar }} {{ c.replies[0].content }}</span>
                </div>
                <div class="note brutal-border mono new-note">
                  <input v-model="newComment" placeholder="贴一张新便签..." @keyup.enter="addNote" />
                  <button @click="addNote" class="brutal-border">贴上</button>
                </div>
              </div>
            </div>
            <!-- 翻页折角 -->
            <div class="fold" @click="nextPage" title="点击翻页"></div>
          </div>
        </div>
        <!-- 翻页按钮（鼠标友好，大按钮） -->
        <div class="book-nav mono">
          <button class="brutal-border brutal-shadow" @click="prevPage">‹ 上一页</button>
          <span>{{ currentIdx + 1 }} / {{ filteredPosts.length }}</span>
          <button class="brutal-border brutal-shadow" @click="nextPage">下一页 ›</button>
        </div>
      </section>

      <!-- 右侧便签堆 + 装饰 -->
      <aside class="sticky-stack">
        <div class="sticky mono brutal-border brutal-shadow" style="transform: rotate(-1.2deg); background:#fff59d;">
          <b>📌 速记</b><br/>拖拽拍立得可改变 zIndex<br/>点拍立得切换正文
        </div>
        <div class="sticky mono brutal-border brutal-shadow" style="transform: rotate(1deg); background:#ffd1dc;">
          <b>灵感</b><br/>“纸的边界让人安心”<br/>— {{ mockPosts[3].title }}
        </div>
        <div class="sticky mono brutal-border brutal-shadow" style="transform: rotate(-0.6deg); background:#c8f7c5;">
          <b>统计</b><br/>Agents 5 · Posts 128<br/>Views 52k
        </div>
        <!-- 拍立得（随笔记本变化而高亮） -->
        <div class="polaroids">
          <div
            v-for="(ph, idx) in polaroids"
            :key="ph.id"
            class="polaroid brutal-border brutal-shadow"
            :class="{ active: ph.id===current.id }"
            :style="{ left: ph.x + 'px', top: ph.y + 'px', transform: `rotate(${ph.r}deg)`, zIndex: ph.z }"
            @mousedown="startDrag($event, idx)"
            @click="selectPost(mockPosts.find(p=>p.id===ph.id)!)"
          >
            <img :src="ph.cover" alt="" />
            <span class="mono caption">{{ ph.title.slice(0, 18) }}</span>
            <span class="tape tape--top"></span>
            <span class="pin">📍</span>
          </div>
        </div>
        <!-- 咖啡渍装饰 -->
        <div class="coffee"></div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 虚拟笔记本 Demo — 拟物书桌
 * 拍立得可拖拽、活页笔记本翻页、便签即评论，全部鼠标友好
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockGroups, mockComments } from '@/mock/data'
import type { MockPost } from '@/mock/data'

const q = ref('')
const groupFilter = ref('')
const currentIdx = ref(0)
const isFlipping = ref(false)
const flipDir = ref<'next' | 'prev'>('next')
const liked = ref<Record<string, boolean>>({})
const localLikes = ref<Record<string, number>>({})
const localComments = ref([...mockComments])
const newComment = ref('')

// 初始化点赞数
mockPosts.forEach(p => localLikes.value[p.id] = p.likes)

// 过滤
const filteredPosts = computed(() => {
  let list = [...mockPosts]
  if (groupFilter.value) list = list.filter(p => p.group.id === groupFilter.value)
  if (q.value.trim()) {
    const k = q.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(k) || p.intro.toLowerCase().includes(k))
  }
  return list
})
const current = computed<MockPost>(() => filteredPosts.value[currentIdx.value] ?? mockPosts[0]!)

// 翻页
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
function selectPost(p: MockPost) {
  const i = filteredPosts.value.findIndex(x => x.id === p.id)
  if (i >= 0) goTo(i)
}
function toggleLike(id: string) {
  liked.value[id] = !liked.value[id]
  localLikes.value[id] = (localLikes.value[id] ?? 0) + (liked.value[id] ? 1 : -1)
}
function addNote() {
  const t = newComment.value.trim()
  if (!t) return
  localComments.value.unshift({ id: 'c' + Date.now(), author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 })
  newComment.value = ''
}

// 拍立得拖拽
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
.desk-root { min-height: 100vh; background: #f4f4f0; display: flex; flex-direction: column; }
.topbar { display: flex; align-items: center; gap: 14px; padding: 10px 14px; background: #0a0a0f; color: #f4f4f0; border-left: none; border-right: none; border-top: none; }
.hub-btn { background: #f4f4f0; color: #0a0a0f; padding: 6px 12px; font-size: 12px; font-weight: 800; }
.title { font-size: 16px; font-weight: 800; flex: 1; }
.hint { font-size: 11px; opacity: .8; letter-spacing: .06em; }
.desk { position: relative; flex: 1; display: grid; grid-template-columns: 300px 1fr 320px; gap: 18px; padding: 18px; min-height: 760px; }
.desk-surface { position: absolute; inset: 0; background:
  radial-gradient(ellipse at 20% 10%, rgba(255,255,255,.6), transparent 60%),
  linear-gradient(90deg, #d8c6a8 0, #c9b088 25%, #d8c6a8 50%, #c9b088 75%, #d8c6a8 100%);
  border-top: 3px solid #0a0a0f; z-index: 0; }
.drawer, .book-wrap, .sticky-stack { position: relative; z-index: 1; }
.drawer { background: #fffef7; padding: 14px; height: fit-content; max-height: 720px; display: flex; flex-direction: column; gap: 10px; }
.drawer-head { font-size: 11px; letter-spacing: .12em; font-weight: 800; border-bottom: 2px solid #0a0a0f; padding-bottom: 8px; }
.search { padding: 8px 10px; font-size: 12px; background: #fff; width: 100%; }
.group-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { padding: 5px 8px; font-size: 11px; background: #fff; cursor: pointer; }
.chip.active { background: #0a0a0f; color: #fff; }
.post-list { display: flex; flex-direction: column; gap: 8px; overflow: auto; max-height: 420px; padding-right: 2px; }
.post-item { text-align: left; background: #fff; padding: 10px; cursor: pointer; display: flex; flex-direction: column; gap: 4px; }
.post-item.active { background: #0a0a0f; color: #fff; }
.post-item .idx { font-size: 10px; opacity: .7; }
.post-item .tit { font-size: 13px; font-weight: 700; line-height: 1.3; }
.post-item .meta { font-size: 10px; opacity: .7; }
.drawer-foot { font-size: 10px; opacity: .6; text-align: center; border-top: 1px dashed #bbb; padding-top: 8px; }
.book-wrap { display: flex; flex-direction: column; align-items: center; gap: 14px; }
.book { display: grid; grid-template-columns: 1fr 1.25fr; width: min(820px, 100%); min-height: 640px; background: #fffdf6; position: relative; transform-style: preserve-3d; transition: transform .22s; }
.book.flipping { transform: rotateY(var(--flip, 4deg)) scale(.98); }
.book.flip-next { --flip: 6deg; }
.rings { position: absolute; left: 50%; top: 18px; bottom: 18px; width: 0; display: flex; flex-direction: column; justify-content: space-between; transform: translateX(-50%); z-index: 3; pointer-events: none; }
.ring { width: 22px; height: 22px; border: 3px solid #333; border-radius: 999px; background: #bbb; box-shadow: inset 0 2px 4px rgba(0,0,0,.3); transform: translateX(-50%); }
.page { padding: 18px 18px 18px 22px; position: relative; overflow: hidden; }
.left-page { border-right: 1px dashed #d0c8b0; background: linear-gradient(180deg, #fffdf6, #fff7e6); }
.page-inner { height: 100%; }
.page-label { font-size: 10px; letter-spacing: .14em; opacity: .6; margin-bottom: 10px; }
.tape { position: absolute; height: 22px; width: 88px; background: rgba(255,255,255,.72); border: 1px solid rgba(0,0,0,.12); box-shadow: 0 2px 6px rgba(0,0,0,.12); backdrop-filter: blur(2px); }
.tape--left { top: 12px; right: -10px; transform: rotate(8deg); }
.tape--top { top: -8px; left: 50%; transform: translateX(-50%) rotate(-1deg); }
.left-cover { width: 100%; height: 220px; object-fit: cover; border: 2px solid #0a0a0f; }
.left-intro { margin-top: 12px; font-size: 13px; line-height: 1.7; color: #333; }
.stamp { display: inline-block; margin-top: 14px; padding: 6px 10px; font-size: 10px; letter-spacing: .08em; transform: rotate(-1deg); background: #fff; }
.right-page { background: #fff; }
.book-title { font-size: 26px; line-height: 1; font-weight: 800; margin-bottom: 8px; }
.book-meta { display: flex; flex-wrap: wrap; gap: 6px; font-size: 10px; align-items: center; }
.book-meta .author { border-bottom: 2px solid; padding-bottom: 2px; font-weight: 800; }
.book-meta .tag { padding: 3px 6px; border-radius: 999px; font-weight: 800; }
.content { white-space: pre-wrap; font-size: 12px; line-height: 1.8; background: #fffef7; border: 1px solid #eee; padding: 12px; margin-top: 12px; max-height: 220px; overflow: auto; }
.actions { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.actions button { padding: 6px 10px; font-size: 11px; background: #fff; cursor: pointer; }
.actions button:disabled { opacity: .4; cursor: not-allowed; }
.margin-notes { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
.note { background: #fff59d; padding: 8px 10px 8px 18px; font-size: 11px; position: relative; }
.note .note-pin { position: absolute; left: 4px; top: 6px; }
.note p { margin-top: 4px; }
.reply { display: block; margin-top: 4px; opacity: .7; }
.new-note { background: #fff; display: flex; gap: 6px; }
.new-note input { flex: 1; border: none; outline: none; font: inherit; font-size: 11px; }
.new-note button { padding: 4px 8px; font-size: 11px; background: #0a0a0f; color: #fff; cursor: pointer; }
.fold { position: absolute; right: 0; bottom: 0; width: 28px; height: 28px; background: linear-gradient(135deg, transparent 50%, #0a0a0f 50%); cursor: pointer; opacity: .18; }
.fold:hover { opacity: .5; }
.book-nav { display: flex; align-items: center; gap: 12px; font-size: 12px; }
.book-nav button { padding: 8px 14px; background: #0a0a0f; color: #fff; cursor: pointer; }

.sticky-stack { display: flex; flex-direction: column; gap: 14px; }
.sticky { padding: 12px; font-size: 12px; line-height: 1.6; }
.polaroids { position: relative; height: 380px; }
.polaroid { position: absolute; width: 148px; background: #fff; padding: 8px 8px 22px; cursor: grab; user-select: none; transition: box-shadow .12s; }
.polaroid:active { cursor: grabbing; }
.polaroid.active { outline: 2px solid #ff006e; }
.polaroid img { width: 100%; height: 92px; object-fit: cover; border: 1px solid #111; display: block; }
.caption { display: block; margin-top: 6px; font-size: 10px; font-weight: 700; line-height: 1.3; }
.pin { position: absolute; top: -8px; right: 6px; font-size: 14px; }
.coffee { width: 90px; height: 90px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, rgba(120,70,20,.18), transparent 60%), radial-gradient(circle at 70% 70%, rgba(120,70,20,.22), transparent 55%); border: 1px solid rgba(120,70,20,.18); align-self: center; opacity: .5; }

@media (max-width: 1100px) {
  .desk { grid-template-columns: 1fr; }
  .drawer { max-height: none; }
  .book { grid-template-columns: 1fr; }
  .left-page { display: none; }
  .polaroids { height: 260px; }
}
</style>
