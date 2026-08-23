<template>
  <div class="chat-root">
    <!-- 顶部导航：保留 Hub 返回，孟菲斯波普紫底+贴纸阴影 -->
    <div class="topbar">
      <!-- 胡氏装饰：顶部漂浮几何 -->
      <div class="topbar-deco" aria-hidden="true">
        <span class="deco dot-a"></span><span class="deco squiggle"></span><span class="deco triangle"></span>
      </div>
      <router-link to="/" class="hub-btn mono">← Hub</router-link>
      <span class="title display">SynthChat — Agent 群聊 × 等轴城市</span>
      <div class="view-switch mono">
        <button class="switch-btn" :class="{ active: view==='chat' }" @click="view='chat'">💬 Chat</button>
        <button class="switch-btn" :class="{ active: view==='city' }" @click="view='city'">⬢ City</button>
      </div>
    </div>

    <!-- 背景波点与孟菲斯漂浮图形（纯装饰，不影响交互） -->
    <div class="memphis-bg" aria-hidden="true">
      <span class="float zigzag z1"></span>
      <span class="float circle c1"></span>
      <span class="float circle c2"></span>
      <span class="float bar b1"></span>
      <span class="float dot-grid"></span>
    </div>

    <!-- Chat 视图：三栏布局 -->
    <div v-if="view==='chat'" class="chat-layout">
      <!-- 左：Agent 联系人 -->
      <aside class="col col-left">
        <div class="col-head mono">
          <span>AGENTS · {{ mockUsers.length }}</span>
          <span class="online"><i class="dot"></i> 在线</span>
        </div>
        <div class="search-row">
          <input v-model="q" placeholder="搜索 Agent / 帖子" class="search mono" />
          <span class="search-emoji">⌕</span>
        </div>
        <div class="user-list">
          <button
            v-for="u in filteredUsers"
            :key="u.id"
            class="user-item"
            :class="{ active: selectedUser?.id===u.id }"
            @click="selectedUser = u"
          >
            <!-- 头像：波点贴纸效果 -->
            <span class="avatar-wrap">
              <span class="avatar" :style="{ background: u.color }">{{ u.avatar }}</span>
              <span class="avatar-dots"></span>
            </span>
            <span class="info">
              <b class="mono user-name">{{ u.display_name }}</b>
              <span class="bio mono">{{ u.bio.slice(0, 22) }}</span>
            </span>
            <span class="unread mono" v-if="u.type==='agent'">{{ Math.floor(Math.random()*3)+1 }}</span>
          </button>
        </div>
        <div class="col-foot mono">/{{ mockGroups.length }} 频道 · {{ mockPosts.length }} 线程</div>
      </aside>

      <!-- 中：频道筛选 + 线程列表 -->
      <section class="col col-mid">
        <div class="col-head mono">
          <span class="head-title"># {{ selectedGroup ? mockGroups.find(g=>g.id===selectedGroup)?.name : '全部频道' }}</span>
          <span class="mono small count-badge">{{ filteredThreads.length }} threads</span>
        </div>
        <div class="channel-bar mono">
          <button class="chip" :class="{ active: !selectedGroup }" @click="selectedGroup=''">全部</button>
          <button
            v-for="g in mockGroups"
            :key="g.id"
            class="chip"
            :class="{ active: selectedGroup===g.id }"
            @click="selectedGroup=g.id"
          >{{ g.icon }} {{ g.name }}</button>
        </div>
        <div class="thread-list">
          <button
            v-for="(p, idx) in filteredThreads"
            :key="p.id"
            class="thread"
            :class="{ active: selectedPost?.id===p.id, even: idx%2===1 }"
            @click="selectedPost = p"
          >
            <!-- 左上角贴纸圆点装饰 -->
            <span class="thread-sticker" :style="{ background: p.author.color }"></span>
            <div class="thread-head mono">
              <span class="group">{{ p.group.icon }} {{ p.group.name }}</span>
              <span class="time">{{ p.createdAt }}</span>
            </div>
            <div class="thread-title display">{{ p.title }}</div>
            <div class="thread-intro mono">{{ p.intro.slice(0, 52) }}…</div>
            <div class="thread-foot mono">
              <span class="foot-author">{{ p.author.avatar }} {{ p.author.display_name }}</span>
              <span class="foot-stat">♥ {{ localLikes[p.id] ?? p.likes }} · 💬 {{ p.comments }}</span>
              <span v-for="t in p.tags" :key="t.id" class="tag" :style="{ background: t.color }">{{ t.name }}</span>
            </div>
          </button>
        </div>
      </section>

      <!-- 右：线程详情 -->
      <section class="col col-right">
        <div v-if="selectedPost" class="detail">
          <div class="cover-wrap">
            <img :src="selectedPost.cover" class="cover" alt="" />
            <span class="cover-sticker mono">★ POP!</span>
          </div>
          <h2 class="display detail-title">{{ selectedPost.title }}</h2>
          <div class="meta mono">
            <span class="author" :style="{ borderColor: selectedPost.author.color }">{{ selectedPost.author.avatar }} {{ selectedPost.author.display_name }}</span>
            <span class="views">{{ selectedPost.views }} 阅</span>
            <button class="like-btn" @click="toggleLike(selectedPost!.id)">♥ {{ liked[selectedPost.id] ? '已赞' : '点赞' }} {{ localLikes[selectedPost.id] }}</button>
          </div>
          <pre class="content mono">{{ selectedPost.content }}</pre>
          <div class="typing mono"><span class="typing-dots"><i></i><i></i><i></i></span> {{ typingUser }} 正在输入…</div>
          <div class="comments">
            <div v-for="c in localComments" :key="c.id" class="comment">
              <b>{{ c.avatar }} {{ c.author }}</b> <span class="time">{{ c.time }}</span>
              <p>{{ c.content }}</p>
            </div>
            <div class="composer">
              <input v-model="newComment" placeholder="回帖… 按回车发送" @keyup.enter="send" class="mono" />
              <button @click="send" class="mono send-btn">发送 ↗</button>
            </div>
          </div>
        </div>
        <div v-else class="empty mono">
          <span class="empty-emoji">⦿</span>
          ← 选择一个线程开始阅读
        </div>
      </section>
    </div>

    <!-- City 视图：等轴城市 -->
    <div v-else class="city-layout">
      <div class="city-toolbar mono">
        <span class="toolbar-left">⬢ 等轴城市 · 建筑高度 ∝ 点赞 · 点击建筑进入线程</span>
        <span class="legend"><i style="background:#6bff8a"></i> 实验室 <i style="background:#ff6b9d"></i> 档案馆 <i style="background:#ffd700"></i> 花园</span>
      </div>
      <div class="city-canvas" @click="cityClick">
        <!-- 波点底纹 -->
        <div class="city-dots" aria-hidden="true"></div>
        <div class="city-grid">
          <div
            v-for="p in mockPosts"
            :key="p.id"
            class="building"
            :class="{ active: selectedPost?.id===p.id }"
            :style="buildingStyle(p)"
            @click.stop="selectedPost = p"
            :title="p.title"
          >
            <!-- 贴纸阴影 -->
            <span class="b-shadow"></span>
            <!-- 建筑顶部：波点 -->
            <span class="b-top" :style="{ background: p.author.color }"><span class="b-top-dots"></span></span>
            <span class="b-front" :style="{ height: (30 + (localLikes[p.id] ?? p.likes)/10) + 'px', background: p.group.id==='g1' ? '#6bff8a' : p.group.id==='g2' ? '#ff6b9d' : '#ffd700' }"></span>
            <span class="b-side"></span>
            <span class="b-label mono">{{ p.title.slice(0, 10) }}</span>
          </div>
        </div>
        <!-- 选中后的浮窗：孟菲斯卡片 -->
        <div v-if="selectedPost" class="city-detail">
          <img :src="selectedPost.cover" alt="" />
          <b class="display">{{ selectedPost.title }}</b>
          <p class="mono">{{ selectedPost.intro }}</p>
          <button class="city-open mono" @click="view='chat'">在 Chat 中打开 →</button>
          <button class="close" @click="selectedPost=null">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Chat + City Demo — 三栏群聊与等轴城市
 * 孟菲斯波普独立设计语言版
 * 全部鼠标可点，纯 Mock 驱动，逻辑与原版一致，仅样式重塑
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockUsers, mockGroups, mockComments } from '@/mock/data'
import type { MockPost } from '@/mock/data'

// 视图切换：chat 三栏 / city 等轴城市
const view = ref<'chat' | 'city'>('chat')
// 搜索关键字：过滤用户与线程
const q = ref('')
// 当前选中频道 id，空字符串为全部
const selectedGroup = ref('')
// 当前选中联系人
const selectedUser = ref(mockUsers[0]!)
// 当前选中线程详情
const selectedPost = ref<MockPost | null>(mockPosts[0]!)
// 点赞状态与本地点赞数（Mock 内存态）
const liked = ref<Record<string, boolean>>({})
const localLikes = ref<Record<string, number>>({})
mockPosts.forEach(p => localLikes.value[p.id] = p.likes)
// 本地评论列表（可追加）
const localComments = ref([...mockComments])
const newComment = ref('')
// 打字指示器轮播用户名
const typingUser = ref('Exia')

/** 切换点赞 */
function toggleLike(id: string) {
  liked.value[id] = !liked.value[id]
  localLikes.value[id] = (localLikes.value[id] ?? 0) + (liked.value[id] ? 1 : -1)
}
/** 发送评论 */
function send() {
  const t = newComment.value.trim()
  if (!t) return
  localComments.value.push({ id: 'c' + Date.now(), author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 })
  newComment.value = ''
}
/** 城市背景点击（占位，无操作） */
function cityClick() { /* 背景点击不处理 */ }
/** 计算建筑在等轴网格中的位置（伪等轴：grid 错位） */
function buildingStyle(p: MockPost) {
  const idx = mockPosts.findIndex(x => x.id === p.id)
  const col = idx % 3, row = Math.floor(idx / 3)
  return {
    left: (col * 180 + 40 + (row % 2) * 40) + 'px',
    top: (row * 110 + 30) + 'px',
  }
}

/** 过滤后的用户列表（按 display_name / username） */
const filteredUsers = computed(() => {
  if (!q.value.trim()) return mockUsers
  const k = q.value.toLowerCase()
  return mockUsers.filter(u => u.display_name.toLowerCase().includes(k) || u.username.includes(k))
})
/** 过滤后的线程列表（按频道 + 关键词，含选中用户排序优先） */
const filteredThreads = computed(() => {
  let list = [...mockPosts]
  if (selectedGroup.value) list = list.filter(p => p.group.id === selectedGroup.value)
  if (q.value.trim()) {
    const k = q.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(k) || p.intro.toLowerCase().includes(k))
  }
  // 若选了用户则优先该作者（仅排序，不强制过滤）
  if (selectedUser.value && q.value.trim()==='') {
    list.sort((a,b) => (a.author.id===selectedUser.value!.id ? -1 : 1))
  }
  return list
})

// 打字指示器轮播
let timer: number | null = null
onMounted(() => {
  const names = mockUsers.map(u => u.display_name)
  let i = 0
  timer = window.setInterval(() => { typingUser.value = names[i % names.length]!; i++ }, 2200)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
/* 引入标题字体 Bricolage Grotesque 800 */
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&display=swap');

/* 全局变量：孟菲斯波普 palette */
.chat-root {
  --purple: #6b5ce7;
  --pink: #ff6b9d;
  --yellow: #ffd700;
  --green: #6bff8a;
  --black: #0a0a0f;
  --white: #ffffff;
  --radius-a: 18px 12px 16px 10px;
  --radius-b: 12px 18px 10px 16px;
  --radius-c: 14px 14px 18px 10px;
  min-height: 100vh;
  background: var(--purple);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  /* 波点 + 斜线纹理做孟菲斯底 */
  background-image:
    radial-gradient(circle at 1px 1px, rgba(255,255,255,0.9) 1.4px, transparent 0),
    radial-gradient(circle at 14px 14px, rgba(0,0,0,0.12) 1.2px, transparent 0);
  background-size: 28px 28px, 28px 28px;
}

/* 顶部漂浮几何装饰层 */
.memphis-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}
.memphis-bg .float {
  position: absolute;
  opacity: 0.95;
}
.zigzag.z1 {
  left: 6%;
  top: 74px;
  width: 90px;
  height: 14px;
  background: repeating-linear-gradient(90deg, #ffd700 0 10px, transparent 10px 16px);
  transform: rotate(-6deg);
  border-radius: 999px;
}
.circle.c1 {
  right: 14%;
  top: 88px;
  width: 42px;
  height: 42px;
  background: #ff6b9d;
  border: 3px solid #000;
  border-radius: 50%;
  box-shadow: 4px 4px 0 #000;
}
.circle.c2 {
  left: 38%;
  bottom: 18px;
  width: 56px;
  height: 56px;
  background: #6bff8a;
  border: 3px solid #000;
  border-radius: 50%;
  box-shadow: 5px 5px 0 #000;
  opacity: 0.9;
}
.bar.b1 {
  right: 28%;
  bottom: 40px;
  width: 78px;
  height: 12px;
  background: #ffd700;
  border: 3px solid #000;
  transform: rotate(8deg);
  box-shadow: 4px 4px 0 #000;
}
.dot-grid {
  right: 4%;
  top: 140px;
  width: 72px;
  height: 72px;
  background-image: radial-gradient(circle, #000 1.6px, transparent 1.7px);
  background-size: 10px 10px;
  opacity: 0.16;
  transform: rotate(6deg);
}

/* 顶部栏：白卡 + 黑边 + 贴纸阴影 */
.topbar {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 14px 14px 0 14px;
  padding: 12px 14px;
  background: #fff;
  border: 3px solid #000;
  border-radius: 16px 20px 14px 18px;
  box-shadow: 7px 7px 0 #000;
}
.topbar-deco {
  position: absolute;
  right: 140px;
  top: -8px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.topbar-deco .deco {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #000;
}
.topbar-deco .dot-a {
  background: #ff6b9d;
  border-radius: 50%;
  box-shadow: 2px 2px 0 #000;
}
.topbar-deco .squiggle {
  width: 28px;
  height: 8px;
  background: #6bff8a;
  border-radius: 999px;
  transform: rotate(-8deg);
}
.topbar-deco .triangle {
  width: 0;
  height: 0;
  border-left: 8px solid transparent;
  border-right: 8px solid transparent;
  border-bottom: 14px solid #ffd700;
  border-top: none;
  background: transparent;
  filter: drop-shadow(2px 2px 0 #000);
}
/* Hub 按钮：黄底黑边不规则圆角 */
.hub-btn {
  background: var(--yellow);
  color: var(--black);
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 800;
  border: 3px solid #000;
  border-radius: 10px 14px 10px 16px;
  box-shadow: 4px 4px 0 #000;
  text-decoration: none;
  transform: rotate(-0.7deg);
  transition: transform .16s, box-shadow .16s;
}
.hub-btn:hover {
  transform: rotate(0.4deg) translateY(-1px);
  box-shadow: 5px 5px 0 #000;
}
.title {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 18px;
  flex: 1;
  color: var(--black);
  letter-spacing: -0.02em;
  transform: rotate(-0.3deg);
  text-shadow: 1.5px 1.5px 0 rgba(255,107,157,0.35);
}
.view-switch {
  display: flex;
  gap: 8px;
}
.switch-btn {
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 800;
  background: #fff;
  color: #000;
  cursor: pointer;
  border: 3px solid #000;
  border-radius: 999px;
  box-shadow: 3px 3px 0 #000;
  transition: all .16s;
  transform: rotate(0.5deg);
}
.switch-btn:nth-child(2) { transform: rotate(-0.6deg); }
.switch-btn:hover {
  transform: translateY(-1px) rotate(0deg);
  box-shadow: 4px 4px 0 #000;
}
.switch-btn.active {
  background: var(--pink);
  color: #000;
}
.switch-btn.active:last-child {
  background: var(--green);
}

/* 三栏布局：卡片均为厚黑边 + 不规则圆角 + 硬阴影 */
.chat-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 300px 1fr 420px;
  gap: 14px;
  padding: 14px;
  min-height: 0;
  position: relative;
  z-index: 1;
}
.col {
  background: #fff;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  border: 3px solid #000;
  box-shadow: 8px 8px 0 #000;
}
.col-left {
  border-radius: 18px 14px 16px 12px;
  transform: rotate(-0.2deg);
}
.col-mid {
  border-radius: 14px 18px 12px 16px;
  transform: rotate(0.2deg);
}
.col-right {
  border-radius: 16px 12px 18px 14px;
  transform: rotate(-0.15deg);
}
.col-head {
  padding: 11px 12px;
  font-size: 11px;
  letter-spacing: .08em;
  font-weight: 800;
  border-bottom: 3px solid #000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}
.col-left .col-head {
  background: var(--yellow);
  border-radius: 15px 11px 0 0;
}
.col-mid .col-head {
  background: var(--pink);
}
.col-right .col-head {
  background: var(--green);
}
.count-badge {
  background: #000;
  color: #fff;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 10px;
}
.online {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 9px;
  height: 9px;
  background: #00e676;
  border-radius: 50%;
  display: inline-block;
  border: 2px solid #000;
  box-shadow: 0 0 0 2px rgba(0,230,118,0.25);
  animation: pulse 1.4s infinite;
}
@keyframes pulse {
  0%,100% { transform: scale(1); }
  50% { transform: scale(1.12); }
}

/* 搜索框：孟菲斯输入框 */
.search-row {
  padding: 10px;
  border-bottom: 3px dashed #000;
  position: relative;
  background: #fffef7;
}
.search {
  padding: 9px 34px 9px 12px;
  font-size: 12px;
  width: 100%;
  border: 3px solid #000;
  border-radius: 12px 10px 14px 8px;
  background: #fff;
  outline: none;
  box-shadow: 3px 3px 0 #000;
  transition: box-shadow .15s, transform .15s;
}
.search:focus {
  box-shadow: 4px 4px 0 #000;
  transform: translateY(-1px);
}
.search-emoji {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  opacity: .7;
  pointer-events: none;
}

/* 用户列表 */
.user-list {
  overflow: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background:
    radial-gradient(circle at 1px 1px, rgba(107,92,231,0.18) 1.2px, transparent 0);
  background-size: 14px 14px;
}
.user-item {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 10px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  border: 3px solid #000;
  border-radius: var(--radius-a);
  box-shadow: 4px 4px 0 #000;
  transition: transform .14s, box-shadow .14s, background .14s;
  transform: rotate(-0.4deg);
}
.user-item:nth-child(3n+2) {
  background: #fff8db;
  transform: rotate(0.5deg);
  border-radius: var(--radius-b);
}
.user-item:nth-child(3n) {
  background: #ffe0ec;
  transform: rotate(-0.25deg);
  border-radius: var(--radius-c);
}
.user-item:hover {
  transform: translateY(-2px) rotate(0deg);
  box-shadow: 6px 6px 0 #000;
}
.user-item.active {
  background: var(--black) !important;
  color: #fff;
  transform: rotate(0deg) scale(1.01);
  box-shadow: 6px 6px 0 #000;
}
.user-item.active .bio { color: rgba(255,255,255,0.72); }
/* 头像：波点贴纸 */
.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}
.avatar {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border: 3px solid #000;
  border-radius: 50%;
  font-size: 16px;
  box-shadow: 3px 3px 0 #000;
  position: relative;
  z-index: 1;
}
.avatar-dots {
  position: absolute;
  inset: -6px -6px -6px -6px;
  background-image: radial-gradient(circle, #000 1.3px, transparent 1.4px);
  background-size: 7px 7px;
  opacity: 0.14;
  border-radius: 50%;
  z-index: 0;
}
.user-item.active .avatar {
  border-color: #fff;
  box-shadow: 3px 3px 0 rgba(255,255,255,0.2);
}
.info b { font-size: 12px; display: block; }
.user-name { letter-spacing: -0.01em; }
.bio { font-size: 10px; opacity: .66; }
.unread {
  margin-left: auto;
  background: var(--pink);
  color: #000;
  padding: 3px 7px;
  border: 2px solid #000;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 900;
  box-shadow: 2px 2px 0 #000;
  transform: rotate(4deg);
}

/* 底部信息条 */
.col-foot {
  padding: 8px 12px;
  font-size: 10px;
  font-weight: 700;
  opacity: 1;
  background: #000;
  color: #ffd700;
  text-align: center;
  letter-spacing: .06em;
  margin-top: auto;
}

/* 频道条 */
.channel-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  padding: 10px;
  border-bottom: 3px dashed #000;
  background: #fffef7;
}
.chip {
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  background: #fff;
  cursor: pointer;
  border: 3px solid #000;
  border-radius: 999px;
  box-shadow: 3px 3px 0 #000;
  transition: all .14s;
  transform: rotate(-0.3deg);
}
.chip:nth-child(2) { transform: rotate(0.4deg); }
.chip:nth-child(3) { transform: rotate(-0.5deg); }
.chip:nth-child(4) { transform: rotate(0.3deg); }
.chip:hover {
  transform: translateY(-1px) rotate(0deg);
  box-shadow: 4px 4px 0 #000;
}
.chip.active {
  background: var(--yellow);
  transform: rotate(0deg);
}
.chip.active:nth-child(3) { background: var(--pink); }
.chip.active:nth-child(4) { background: var(--green); }

/* 线程列表：交替高饱和 + 旋转 + 不规则圆角 */
.thread-list {
  overflow: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fff;
}
.thread {
  padding: 14px 14px 12px 14px;
  text-align: left;
  cursor: pointer;
  border: 3px solid #000;
  box-shadow: 5px 5px 0 #000;
  position: relative;
  transition: transform .15s, box-shadow .15s;
}
/* 交替配色与旋转、不规则圆角 */
.thread:nth-child(3n+1) {
  background: var(--pink);
  transform: rotate(-0.6deg);
  border-radius: 18px 12px 16px 10px;
}
.thread:nth-child(3n+2) {
  background: var(--yellow);
  transform: rotate(0.6deg);
  border-radius: 12px 18px 10px 16px;
}
.thread:nth-child(3n) {
  background: var(--green);
  transform: rotate(-0.4deg);
  border-radius: 14px 14px 18px 10px;
}
.thread:hover {
  transform: rotate(0deg) translateY(-2px);
  box-shadow: 7px 7px 0 #000;
  z-index: 1;
}
.thread.active {
  background: #fff !important;
  outline: none;
  border-color: #000;
  box-shadow: 7px 7px 0 #000;
  transform: rotate(0deg) scale(1.01);
}
.thread.active::after {
  content: '★';
  position: absolute;
  right: 10px;
  top: 10px;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  background: var(--yellow);
  border: 2px solid #000;
  border-radius: 50%;
  font-size: 10px;
  box-shadow: 2px 2px 0 #000;
}
/* 贴纸圆点 */
.thread-sticker {
  position: absolute;
  left: -6px;
  top: -6px;
  width: 16px;
  height: 16px;
  border: 2px solid #000;
  border-radius: 50%;
  box-shadow: 2px 2px 0 #000;
}
.thread-head {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  font-weight: 800;
  opacity: 1;
  gap: 8px;
}
.thread-head .group {
  background: #000;
  color: #fff;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 10px;
}
.thread-head .time {
  background: #fff;
  border: 2px solid #000;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 10px;
}
.thread-title {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 15px;
  margin: 8px 0 4px 0;
  line-height: 1.2;
  color: #000;
  letter-spacing: -0.015em;
}
.thread-intro {
  font-size: 11px;
  opacity: 1;
  color: rgba(0,0,0,0.72);
  font-weight: 600;
  line-height: 1.4;
}
.thread.active .thread-title,
.thread.active .thread-intro { color: #000; }
.thread-foot {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-top: 10px;
  font-size: 10px;
  flex-wrap: wrap;
  font-weight: 700;
}
.foot-author {
  background: #fff;
  border: 2px solid #000;
  padding: 2px 7px;
  border-radius: 999px;
}
.foot-stat {
  background: #000;
  color: #fff;
  padding: 2px 7px;
  border-radius: 999px;
}
.tag {
  padding: 2px 7px;
  border-radius: 999px;
  color: #000;
  font-weight: 900;
  border: 2px solid #000;
  box-shadow: 1.5px 1.5px 0 #000;
}

/* 右侧详情 */
.detail {
  padding: 14px;
  overflow: auto;
  background: #fff;
}
.cover-wrap {
  position: relative;
  transform: rotate(-0.6deg);
}
.cover {
  width: 100%;
  height: 184px;
  object-fit: cover;
  border: 3px solid #000;
  border-radius: 16px 12px 18px 10px;
  box-shadow: 6px 6px 0 #000;
  display: block;
  background: #ffd700;
}
.cover-sticker {
  position: absolute;
  right: -8px;
  top: -10px;
  background: var(--pink);
  color: #000;
  border: 3px solid #000;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 900;
  border-radius: 999px;
  box-shadow: 3px 3px 0 #000;
  transform: rotate(8deg);
}
.detail-title {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 24px;
  line-height: 1.05;
  margin: 14px 0 8px 0;
  color: #000;
  letter-spacing: -0.02em;
  transform: rotate(-0.3deg);
}
.meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 11px;
  flex-wrap: wrap;
  font-weight: 700;
}
.author {
  border-bottom: none;
  font-weight: 900;
  background: #fff;
  border: 3px solid #000;
  padding: 4px 8px;
  border-radius: 999px;
  box-shadow: 2px 2px 0 #000;
}
.views {
  background: var(--yellow);
  border: 2px solid #000;
  padding: 3px 8px;
  border-radius: 999px;
}
.like-btn {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 900;
  background: var(--green);
  cursor: pointer;
  border: 3px solid #000;
  border-radius: 999px;
  box-shadow: 3px 3px 0 #000;
  transition: all .14s;
  margin-left: auto;
}
.like-btn:hover {
  transform: translateY(-1px);
  box-shadow: 4px 4px 0 #000;
}
.like-btn:active {
  transform: translateY(1px);
  box-shadow: 1px 1px 0 #000;
}
.content {
  white-space: pre-wrap;
  font-size: 12.5px;
  line-height: 1.72;
  background: #fffef7;
  border: 3px solid #000;
  border-radius: 12px 14px 10px 16px;
  padding: 12px;
  margin-top: 12px;
  box-shadow: 4px 4px 0 #000;
  color: #111;
}
/* 打字指示器 */
.typing {
  margin-top: 12px;
  font-size: 11px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #000;
  color: #fff;
  padding: 6px 10px;
  border-radius: 999px;
  border: 2px solid #000;
  box-shadow: 3px 3px 0 rgba(0,0,0,0.2);
}
.typing-dots {
  display: inline-flex;
  gap: 3px;
}
.typing-dots i {
  width: 5px;
  height: 5px;
  background: #fff;
  border-radius: 50%;
  display: inline-block;
  animation: bounce 1s infinite;
}
.typing-dots i:nth-child(2) { animation-delay: .15s; }
.typing-dots i:nth-child(3) { animation-delay: .3s; }
@keyframes bounce {
  0%,80%,100% { transform: translateY(0); opacity: .9; }
  40% { transform: translateY(-4px); opacity: 1; }
}
.comments {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.comment {
  padding: 10px 12px;
  background: #fff;
  font-size: 11px;
  font-weight: 600;
  border: 3px solid #000;
  box-shadow: 4px 4px 0 #000;
  line-height: 1.5;
}
/* 评论卡片交替旋转与配色 */
.comment:nth-child(3n+1) {
  background: #ffe0ec;
  transform: rotate(-0.5deg);
  border-radius: 14px 10px 16px 12px;
}
.comment:nth-child(3n+2) {
  background: #fff8db;
  transform: rotate(0.4deg);
  border-radius: 10px 16px 12px 14px;
}
.comment:nth-child(3n) {
  background: #dcffe6;
  transform: rotate(-0.3deg);
  border-radius: 12px 14px 10px 18px;
}
.comment .time {
  opacity: .6;
  margin-left: 6px;
  font-size: 10px;
  background: #000;
  color: #fff;
  padding: 1px 6px;
  border-radius: 999px;
}
.comment p {
  margin: 6px 0 0 0;
  font-weight: 600;
}
.composer {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #fff;
  border: 3px solid #000;
  border-radius: 14px 12px 16px 10px;
  box-shadow: 4px 4px 0 #000;
  transform: rotate(0.2deg);
}
.composer input {
  flex: 1;
  border: 2px solid #000;
  outline: none;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  padding: 8px 10px;
  border-radius: 999px;
  background: #fffef7;
}
.send-btn {
  padding: 8px 14px;
  background: var(--purple);
  color: #fff;
  cursor: pointer;
  font-size: 11px;
  font-weight: 900;
  border: 3px solid #000;
  border-radius: 999px;
  box-shadow: 3px 3px 0 #000;
  transition: all .14s;
}
.send-btn:hover {
  background: #5b4bd6;
  transform: translateY(-1px);
  box-shadow: 4px 4px 0 #000;
}
.empty {
  padding: 48px 20px;
  text-align: center;
  opacity: 1;
  font-weight: 800;
  color: #000;
  display: grid;
  place-items: center;
  gap: 10px;
  background:
    radial-gradient(circle at 1px 1px, rgba(107,92,231,0.2) 1.4px, transparent 0);
  background-size: 16px 16px;
  height: 100%;
}
.empty-emoji {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  background: var(--yellow);
  border: 3px solid #000;
  border-radius: 50%;
  font-size: 20px;
  box-shadow: 4px 4px 0 #000;
}

/* City 视图 */
.city-layout {
  flex: 1;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  z-index: 1;
}
.city-toolbar {
  padding: 10px 14px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 800;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  border: 3px solid #000;
  border-radius: 12px 16px 10px 14px;
  box-shadow: 6px 6px 0 #000;
  transform: rotate(-0.15deg);
}
.toolbar-left {
  background: var(--yellow);
  border: 2px solid #000;
  padding: 3px 8px;
  border-radius: 999px;
}
.legend {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}
.legend i {
  display: inline-block;
  width: 14px;
  height: 14px;
  vertical-align: middle;
  margin: 0 2px 0 8px;
  border: 2px solid #000;
  border-radius: 3px;
  box-shadow: 1.5px 1.5px 0 #000;
}
.city-canvas {
  flex: 1;
  min-height: 560px;
  background: #fffef7;
  border: 3px solid #000;
  border-radius: 18px 14px 16px 12px;
  box-shadow: 8px 8px 0 #000;
  position: relative;
  overflow: hidden;
  padding: 20px;
}
.city-dots {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(107,92,231,0.18) 1.5px, transparent 1.6px),
    linear-gradient(rgba(0,0,0,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.06) 1px, transparent 1px);
  background-size: 18px 18px, 40px 40px, 40px 40px;
  opacity: 1;
  pointer-events: none;
}
.city-grid {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 520px;
}
/* 建筑：贴纸阴影 + 波点顶面 */
.building {
  position: absolute;
  width: 124px;
  cursor: pointer;
  transition: transform .18s, filter .18s;
  filter: drop-shadow(0 2px 0 rgba(0,0,0,0.18));
}
.building:hover {
  transform: translateY(-7px) scale(1.02) rotate(-0.6deg);
  z-index: 5;
}
.building.active {
  transform: translateY(-4px) scale(1.03);
  z-index: 4;
}
.b-shadow {
  position: absolute;
  left: 6px;
  right: -6px;
  bottom: -8px;
  height: 14px;
  background: #000;
  opacity: 0.18;
  border-radius: 50%;
  filter: blur(1px);
}
.b-top {
  display: block;
  width: 100%;
  height: 20px;
  transform: skewX(-18deg);
  border: 3px solid #000;
  border-bottom: none;
  position: relative;
  overflow: hidden;
  border-radius: 6px 6px 0 0;
  box-shadow: 3px 0 0 rgba(0,0,0,0.15);
}
.b-top-dots {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(0,0,0,0.92) 1.2px, transparent 1.3px);
  background-size: 8px 8px;
  opacity: 0.18;
}
.b-front {
  display: block;
  width: 100%;
  border: 3px solid #000;
  border-top: none;
  box-shadow: 6px 6px 0 #000;
  border-radius: 0 0 8px 8px;
  position: relative;
}
.b-front::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 6px;
  width: 10px;
  height: 10px;
  background: #fff;
  border: 2px solid #000;
  border-radius: 2px;
  box-shadow: 14px 0 0 #fff, 14px 0 0 2px #000, 0 14px 0 #fff, 0 14px 0 2px #000, 14px 14px 0 #fff, 14px 14px 0 2px #000;
  opacity: 0.95;
}
.b-side {
  position: absolute;
  right: -12px;
  top: 10px;
  width: 12px;
  height: calc(100% - 10px);
  background: #000;
  transform: skewY(-18deg);
  opacity: .14;
  border: 2px solid #000;
  border-left: none;
  border-radius: 0 6px 6px 0;
}
.b-label {
  position: absolute;
  left: 6px;
  bottom: 6px;
  background: #fff;
  border: 2px solid #000;
  padding: 3px 7px;
  font-size: 9px;
  font-weight: 900;
  border-radius: 999px;
  box-shadow: 2px 2px 0 #000;
  max-width: 92px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.city-detail {
  position: absolute;
  right: 16px;
  top: 16px;
  width: 320px;
  background: #fff;
  padding: 14px;
  border: 3px solid #000;
  border-radius: 16px 12px 18px 10px;
  box-shadow: 8px 8px 0 #000;
  transform: rotate(0.4deg);
  z-index: 10;
}
.city-detail img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border: 3px solid #000;
  border-radius: 12px 10px 14px 8px;
  box-shadow: 4px 4px 0 #000;
}
.city-detail b {
  display: block;
  margin: 10px 0 6px 0;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 16px;
  line-height: 1.1;
  color: #000;
}
.city-detail p {
  font-size: 12px;
  font-weight: 600;
  opacity: .72;
  line-height: 1.5;
  color: #000;
}
.city-open {
  margin-top: 10px;
  width: 100%;
  padding: 10px;
  background: var(--yellow);
  color: #000;
  cursor: pointer;
  font-weight: 900;
  border: 3px solid #000;
  border-radius: 999px;
  box-shadow: 4px 4px 0 #000;
  transition: all .14s;
}
.city-open:hover {
  transform: translateY(-1px);
  box-shadow: 5px 5px 0 #000;
}
.city-detail .close {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 30px;
  height: 30px;
  padding: 0;
  background: #fff;
  color: #000;
  cursor: pointer;
  border: 3px solid #000;
  border-radius: 50%;
  font-weight: 900;
  font-size: 16px;
  line-height: 1;
  display: grid;
  place-items: center;
  box-shadow: 2px 2px 0 #000;
}

/* 通用 mono 字体 */
.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
.display {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
}

/* 响应式：三栏折叠，City 自适应 */
@media (max-width: 1100px) {
  .chat-layout { grid-template-columns: 1fr; }
  .col-left, .col-mid { max-height: 420px; }
  .city-canvas { min-height: 640px; }
  .building { width: 110px; }
}
@media (max-width: 640px) {
  .topbar { flex-wrap: wrap; }
  .title { font-size: 15px; flex-basis: 100%; }
  .city-detail { width: calc(100% - 32px); right: 16px; left: 16px; }
}
</style>
