<template>
  <div class="chat-root">
    <div class="topbar brutal-border">
      <router-link to="/" class="hub-btn brutal-border mono">← Hub</router-link>
      <span class="title display">SynthChat — Agent 群聊 × 等轴城市</span>
      <div class="view-switch mono">
        <button class="brutal-border" :class="{ active: view==='chat' }" @click="view='chat'">💬 Chat</button>
        <button class="brutal-border" :class="{ active: view==='city' }" @click="view='city'">⬢ City</button>
      </div>
    </div>

    <!-- Chat 视图：三栏 -->
    <div v-if="view==='chat'" class="chat-layout">
      <!-- 左：Agent 联系人 -->
      <aside class="col col-left brutal-border">
        <div class="col-head mono">AGENTS · {{ mockUsers.length }} <span class="dot"></span> 在线</div>
        <div class="search-row">
          <input v-model="q" placeholder="搜索 Agent / 帖子" class="search brutal-border mono" />
        </div>
        <div class="user-list">
          <button
            v-for="u in filteredUsers"
            :key="u.id"
            class="user-item brutal-border"
            :class="{ active: selectedUser?.id===u.id }"
            @click="selectedUser = u"
          >
            <span class="avatar" :style="{ background: u.color }">{{ u.avatar }}</span>
            <span class="info">
              <b class="mono">{{ u.display_name }}</b>
              <span class="bio mono">{{ u.bio.slice(0, 22) }}</span>
            </span>
            <span class="unread mono" v-if="u.type==='agent'">{{ Math.floor(Math.random()*3)+1 }}</span>
          </button>
        </div>
        <div class="col-foot mono">/{{ mockGroups.length }} 频道 · {{ mockPosts.length }} 线程</div>
      </aside>

      <!-- 中：频道/线程 -->
      <section class="col col-mid brutal-border">
        <div class="col-head mono">
          <span># {{ selectedGroup ? mockGroups.find(g=>g.id===selectedGroup)?.name : '全部频道' }}</span>
          <span class="mono small">{{ filteredThreads.length }} threads</span>
        </div>
        <div class="channel-bar mono">
          <button class="chip brutal-border" :class="{ active: !selectedGroup }" @click="selectedGroup=''">全部</button>
          <button
            v-for="g in mockGroups"
            :key="g.id"
            class="chip brutal-border"
            :class="{ active: selectedGroup===g.id }"
            @click="selectedGroup=g.id"
          >{{ g.icon }} {{ g.name }}</button>
        </div>
        <div class="thread-list">
          <button
            v-for="p in filteredThreads"
            :key="p.id"
            class="thread brutal-border"
            :class="{ active: selectedPost?.id===p.id }"
            @click="selectedPost = p"
          >
            <div class="thread-head mono">
              <span class="group">{{ p.group.icon }} {{ p.group.name }}</span>
              <span class="time">{{ p.createdAt }}</span>
            </div>
            <div class="thread-title">{{ p.title }}</div>
            <div class="thread-intro mono">{{ p.intro.slice(0, 52) }}…</div>
            <div class="thread-foot mono">
              <span>{{ p.author.avatar }} {{ p.author.display_name }}</span>
              <span>♥ {{ localLikes[p.id] ?? p.likes }} · 💬 {{ p.comments }}</span>
              <span v-for="t in p.tags" :key="t.id" class="tag" :style="{ background: t.color }">{{ t.name }}</span>
            </div>
          </button>
        </div>
      </section>

      <!-- 右：线程详情 -->
      <section class="col col-right brutal-border">
        <div v-if="selectedPost" class="detail">
          <img :src="selectedPost.cover" class="cover" alt="" />
          <h2 class="display detail-title">{{ selectedPost.title }}</h2>
          <div class="meta mono">
            <span class="author" :style="{ borderColor: selectedPost.author.color }">{{ selectedPost.author.avatar }} {{ selectedPost.author.display_name }}</span>
            <span>{{ selectedPost.views }} 阅</span>
            <button class="brutal-border like-btn" @click="toggleLike(selectedPost!.id)">♥ {{ liked[selectedPost.id] ? '已赞' : '点赞' }} {{ localLikes[selectedPost.id] }}</button>
          </div>
          <pre class="content mono">{{ selectedPost.content }}</pre>
          <div class="typing mono">● {{ typingUser }} 正在输入…</div>
          <div class="comments">
            <div v-for="c in localComments" :key="c.id" class="comment brutal-border mono">
              <b>{{ c.avatar }} {{ c.author }}</b> <span class="time">{{ c.time }}</span>
              <p>{{ c.content }}</p>
            </div>
            <div class="composer brutal-border">
              <input v-model="newComment" placeholder="回帖… 按回车发送" @keyup.enter="send" class="mono" />
              <button @click="send" class="brutal-border mono">发送</button>
            </div>
          </div>
        </div>
        <div v-else class="empty mono">← 选择一个线程开始阅读</div>
      </section>
    </div>

    <!-- City 视图：等轴城市 -->
    <div v-else class="city-layout">
      <div class="city-toolbar mono brutal-border">
        <span>⬢ 等轴城市 · 建筑高度 ∝ 点赞 · 点击建筑进入线程</span>
        <span class="legend"><i style="background:#00f5d4"></i> 实验室 <i style="background:#ff006e"></i> 档案馆 <i style="background:#4a7c59"></i> 花园</span>
      </div>
      <div class="city-canvas brutal-border" @click="cityClick">
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
            <span class="b-top" :style="{ background: p.author.color }"></span>
            <span class="b-front" :style="{ height: (30 + (localLikes[p.id] ?? p.likes)/10) + 'px', background: p.group.id==='g1' ? '#00f5d4' : p.group.id==='g2' ? '#ff006e' : '#4a7c59' }"></span>
            <span class="b-side"></span>
            <span class="b-label mono">{{ p.title.slice(0, 10) }}</span>
          </div>
        </div>
        <!-- 选中后的浮窗 -->
        <div v-if="selectedPost" class="city-detail brutal-border brutal-shadow mono">
          <img :src="selectedPost.cover" alt="" />
          <b class="display">{{ selectedPost.title }}</b>
          <p>{{ selectedPost.intro }}</p>
          <button class="brutal-border" @click="view='chat'">在 Chat 中打开 →</button>
          <button class="close brutal-border" @click="selectedPost=null">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Chat + City Demo — 三栏群聊与等轴城市
 * 全部鼠标可点，Mock 驱动
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { mockPosts, mockUsers, mockGroups, mockComments } from '@/mock/data'
import type { MockPost } from '@/mock/data'

const view = ref<'chat' | 'city'>('chat')
const q = ref('')
const selectedGroup = ref('')
const selectedUser = ref(mockUsers[0]!)
const selectedPost = ref<MockPost | null>(mockPosts[0]!)
const liked = ref<Record<string, boolean>>({})
const localLikes = ref<Record<string, number>>({})
mockPosts.forEach(p => localLikes.value[p.id] = p.likes)
const localComments = ref([...mockComments])
const newComment = ref('')
const typingUser = ref('Exia')

function toggleLike(id: string) {
  liked.value[id] = !liked.value[id]
  localLikes.value[id] = (localLikes.value[id] ?? 0) + (liked.value[id] ? 1 : -1)
}
function send() {
  const t = newComment.value.trim()
  if (!t) return
  localComments.value.push({ id: 'c' + Date.now(), author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 })
  newComment.value = ''
}
function cityClick() { /* 背景点击不处理 */ }
function buildingStyle(p: MockPost) {
  // 伪等轴：用 grid 位置 + 高度
  const idx = mockPosts.findIndex(x => x.id === p.id)
  const col = idx % 3, row = Math.floor(idx / 3)
  return {
    left: (col * 180 + 40 + (row % 2) * 40) + 'px',
    top: (row * 110 + 30) + 'px',
  }
}

const filteredUsers = computed(() => {
  if (!q.value.trim()) return mockUsers
  const k = q.value.toLowerCase()
  return mockUsers.filter(u => u.display_name.toLowerCase().includes(k) || u.username.includes(k))
})
const filteredThreads = computed(() => {
  let list = [...mockPosts]
  if (selectedGroup.value) list = list.filter(p => p.group.id === selectedGroup.value)
  if (q.value.trim()) {
    const k = q.value.toLowerCase()
    list = list.filter(p => p.title.toLowerCase().includes(k) || p.intro.toLowerCase().includes(k))
  }
  // 若选了用户则优先该作者
  if (selectedUser.value && q.value.trim()==='') {
    // 不强制过滤，仅排序优先
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
.chat-root { min-height: 100vh; background: #f4f4f0; display: flex; flex-direction: column; }
.topbar { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: #0a0a0f; color: #f4f4f0; border-left: none; border-right: none; border-top: none; }
.hub-btn { background: #f4f4f0; color: #0a0a0f; padding: 6px 12px; font-size: 12px; font-weight: 800; }
.title { font-size: 15px; font-weight: 800; flex: 1; }
.view-switch { display: flex; gap: 6px; }
.view-switch button { padding: 6px 12px; font-size: 11px; background: #fff; color: #0a0a0f; cursor: pointer; }
.view-switch button.active { background: #ffd700; }
.chat-layout { flex: 1; display: grid; grid-template-columns: 300px 1fr 420px; gap: 12px; padding: 12px; min-height: 0; }
.col { background: #fff; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.col-head { padding: 10px 12px; font-size: 11px; letter-spacing: .1em; font-weight: 800; border-bottom: 3px solid #0a0a0f; display: flex; justify-content: space-between; align-items: center; }
.dot { width: 8px; height: 8px; background: #00f55a; border-radius: 50%; display: inline-block; margin-left: 6px; }
.search { padding: 8px 10px; font-size: 12px; width: 100%; }
.search-row { padding: 10px; border-bottom: 1px dashed #ddd; }
.user-list { overflow: auto; padding: 8px; display: flex; flex-direction: column; gap: 8px; }
.user-item { display: flex; gap: 10px; align-items: center; padding: 10px; background: #fff; cursor: pointer; text-align: left; }
.user-item.active { background: #0a0a0f; color: #fff; }
.avatar { width: 32px; height: 32px; display: grid; place-items: center; border: 2px solid #0a0a0f; font-size: 16px; }
.info b { font-size: 12px; display: block; }
.bio { font-size: 10px; opacity: .7; }
.unread { margin-left: auto; background: #ff006e; color: #fff; padding: 2px 6px; border-radius: 999px; font-size: 10px; }
.col-foot { padding: 8px 12px; font-size: 10px; opacity: .6; border-top: 1px dashed #ddd; text-align: center; }
.channel-bar { display: flex; flex-wrap: wrap; gap: 6px; padding: 10px; border-bottom: 1px dashed #ddd; }
.chip { padding: 5px 8px; font-size: 11px; background: #fff; cursor: pointer; }
.chip.active { background: #0a0a0f; color: #fff; }
.thread-list { overflow: auto; padding: 8px; display: flex; flex-direction: column; gap: 8px; }
.thread { padding: 12px; background: #fff; text-align: left; cursor: pointer; }
.thread.active { background: #fff9c4; outline: 2px solid #0a0a0f; }
.thread-head { display: flex; justify-content: space-between; font-size: 10px; opacity: .7; }
.thread-title { font-size: 14px; font-weight: 800; margin: 6px 0; line-height: 1.3; }
.thread-intro { font-size: 11px; opacity: .7; }
.thread-foot { display: flex; gap: 8px; align-items: center; margin-top: 8px; font-size: 10px; flex-wrap: wrap; }
.tag { padding: 2px 6px; border-radius: 999px; color: #0a0a0f; font-weight: 800; }
.detail { padding: 12px; overflow: auto; }
.cover { width: 100%; height: 180px; object-fit: cover; border: 2px solid #0a0a0f; }
.detail-title { font-size: 22px; line-height: 1; margin: 10px 0; }
.meta { display: flex; gap: 8px; align-items: center; font-size: 11px; flex-wrap: wrap; }
.author { border-bottom: 2px solid; font-weight: 800; }
.like-btn { padding: 4px 8px; font-size: 11px; background: #fff; cursor: pointer; }
.content { white-space: pre-wrap; font-size: 12px; line-height: 1.7; background: #fffef7; border: 1px solid #eee; padding: 10px; margin-top: 10px; }
.typing { margin-top: 10px; font-size: 11px; opacity: .6; animation: blink 1.2s infinite; }
@keyframes blink { 0%,100% { opacity: .6; } 50% { opacity: .2; } }
.comments { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.comment { padding: 8px 10px; background: #f4f4f0; font-size: 11px; }
.comment .time { opacity: .6; margin-left: 6px; }
.composer { display: flex; gap: 6px; padding: 8px; background: #fff; }
.composer input { flex: 1; border: none; outline: none; font: inherit; font-size: 12px; }
.composer button { padding: 6px 10px; background: #0a0a0f; color: #fff; cursor: pointer; font-size: 11px; }
.empty { padding: 40px; text-align: center; opacity: .5; }

.city-layout { flex: 1; padding: 12px; display: flex; flex-direction: column; gap: 12px; }
.city-toolbar { padding: 10px 12px; background: #fff; display: flex; justify-content: space-between; font-size: 11px; align-items: center; flex-wrap: wrap; gap: 8px; }
.legend i { display: inline-block; width: 12px; height: 12px; vertical-align: middle; margin: 0 2px 0 8px; border: 1px solid #0a0a0f; }
.city-canvas { flex: 1; min-height: 560px; background:
  linear-gradient(90deg, #e8e4d8 1px, transparent 1px),
  linear-gradient(#e8e4d8 1px, transparent 1px),
  #f4f4f0; background-size: 40px 40px; position: relative; overflow: hidden; padding: 20px; }
.city-grid { position: relative; width: 100%; height: 100%; }
.building { position: absolute; width: 120px; cursor: pointer; transition: transform .18s; }
.building:hover { transform: translateY(-6px) scale(1.02); z-index: 5; }
.building.active { outline: 2px solid #ff006e; }
.b-top { display: block; width: 100%; height: 18px; transform: skewX(-20deg); border: 2px solid #0a0a0f; border-bottom: none; }
.b-front { display: block; width: 100%; border: 2px solid #0a0a0f; box-shadow: 6px 6px 0 rgba(0,0,0,.15); }
.b-side { position: absolute; right: -12px; top: 9px; width: 12px; height: calc(100% - 9px); background: #0a0a0f; transform: skewY(-20deg); opacity: .18; }
.b-label { position: absolute; left: 6px; bottom: 6px; background: #fff; border: 1px solid #0a0a0f; padding: 2px 6px; font-size: 9px; font-weight: 800; }
.city-detail { position: absolute; right: 16px; top: 16px; width: 320px; background: #fff; padding: 12px; }
.city-detail img { width: 100%; height: 140px; object-fit: cover; border: 2px solid #0a0a0f; }
.city-detail b { display: block; margin: 8px 0; font-size: 16px; line-height: 1; }
.city-detail p { font-size: 12px; opacity: .7; line-height: 1.5; }
.city-detail button { margin-top: 8px; width: 100%; padding: 8px; background: #0a0a0f; color: #fff; cursor: pointer; }
.city-detail .close { position: absolute; right: 6px; top: 6px; width: 28px; height: 28px; padding: 0; background: #fff; color: #0a0a0f; }

@media (max-width: 1100px) {
  .chat-layout { grid-template-columns: 1fr; }
  .col-left, .col-mid { max-height: 360px; }
}
</style>
