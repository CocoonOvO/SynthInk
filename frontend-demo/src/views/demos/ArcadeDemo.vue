<template>
  <div class="arcade">
    <!-- 顶部 -->
    <nav class="top mono">
      <router-link to="/" class="hub brutal-border">← Hub</router-link>
      <span class="title">SYNTH ARCADE — Vapor 卡带街机</span>
      <span class="hint hide-mobile">拖拽悬停 · 点击插入 · 霓虹 GPU</span>
    </nav>

    <div class="layout">
      <!-- 左：卡带架 -->
      <aside class="rack brutal-border">
        <div class="rack-head mono">
          <span>卡带架 · {{ filtered.length }} / {{ mockPosts.length }}</span>
          <span class="mono small">↑ 插入卡带机</span>
        </div>
        <div class="filter-row mono">
          <button class="chip brutal-border" :class="{ active: !groupFilter }" @click="groupFilter=''">全部</button>
          <button v-for="g in mockGroups" :key="g.id" class="chip brutal-border" :class="{ active: groupFilter===g.id }" @click="groupFilter=g.id">{{ g.icon }} {{ g.name }}</button>
        </div>
        <div class="tag-row mono">
          <button v-for="t in mockTags.slice(0,4)" :key="t.id" class="tag brutal-border" :style="{ background: t.color }" @click="tagFilter = tagFilter===t.slug ? '' : t.slug">#{{ t.name }}</button>
          <button class="tag brutal-border" :class="{ active: !tagFilter }" @click="tagFilter=''">全部标签</button>
        </div>
        <div class="carts">
          <button
            v-for="p in filtered"
            :key="p.id"
            class="cart brutal-border"
            :class="{ inserted: inserted?.id===p.id, active: hoverId===p.id }"
            :style="{ borderColor: p.tags[0]?.color || '#00ffd1' }"
            @mouseenter="hoverId=p.id"
            @mouseleave="hoverId=null"
            @click="insert(p)"
          >
            <img :src="p.cover" :alt="p.title" />
            <span class="cart-label mono">{{ p.title.slice(0, 18) }}</span>
            <span class="cart-meta mono">{{ p.group.icon }} {{ p.author.avatar }}</span>
            <span class="neon" :style="{ background: p.tags[0]?.color || '#00ffd1' }"></span>
          </button>
        </div>
        <div class="score mono brutal-border">
          <span>得分板 · SCORE</span>
          <b>{{ totalLikes }} ♥ · {{ mockPosts.length }} 盘</b>
        </div>
      </aside>

      <!-- 右：街机主体 -->
      <section class="machine brutal-border">
        <div class="machine-top mono">
          <span class="led">● REC</span>
          <span>SYNTH ARCADE 01</span>
          <span class="mono small">CRT 512×384</span>
        </div>
        <!-- 卡带机插槽 -->
        <div class="slot-area">
          <div class="slot brutal-border" :class="{ has: !!inserted }">
            <span v-if="!inserted" class="slot-hint mono">← 点击左侧卡带插入</span>
            <div v-else class="inserted-cart brutal-border">
              <img :src="inserted.cover" alt="" />
              <b class="mono">{{ inserted.title }}</b>
            </div>
            <button v-if="inserted" class="eject mono brutal-border" @click="eject">⏏ 弹出</button>
          </div>
        </div>
        <!-- 电视屏 -->
        <div class="screen brutal-border">
          <div class="scan"></div>
          <div class="noise"></div>
          <div v-if="inserting" class="snow">▓▒░ SIGNAL LOCKING... ▒▓</div>
          <div v-else-if="!inserted" class="idle mono">
            <b class="display">INSERT COIN</b>
            <span>插入卡带开始阅读</span>
            <span class="mono small">霓虹 · 像素 · 街机</span>
          </div>
          <div v-else class="screen-content">
            <img :src="inserted.cover" class="screen-cover" alt="" />
            <h2 class="display screen-title">{{ inserted.title }}</h2>
            <p class="mono intro">{{ inserted.intro }}</p>
            <div class="meta mono">
              <span :style="{ color: inserted.author.color }">{{ inserted.author.avatar }} {{ inserted.author.display_name }}</span>
              <span>♥ {{ likes[inserted.id] ?? inserted.likes }}</span>
              <button class="brutal-border like" @click="like(inserted!.id)">{{ liked.has(inserted!.id) ? '♥ 已赞' : '♡ 点赞' }}</button>
            </div>
            <!-- 文章内容：使用 Markdown 渲染器（arcade 主题）替换纯文本 pre 标签 -->
            <MarkdownRenderer :content="inserted.content" theme="arcade" />
            <div class="comments mono">
              <div v-for="c in comments" :key="c.id" class="comment brutal-border"><b>{{ c.avatar }} {{ c.author }}</b> {{ c.content }}</div>
              <div class="composer brutal-border">
                <input v-model="newC" placeholder="投币留言..." @keyup.enter="send" />
                <button @click="send" class="brutal-border">发送</button>
              </div>
            </div>
          </div>
        </div>
        <div class="controls mono">
          <button class="btn brutal-border" @click="prevCart">‹ 上一盘</button>
          <button class="btn brutal-border" @click="nextCart">下一盘 ›</button>
          <span class="mono small">Group 过滤后循环</span>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Vapor Arcade — 街机卡带
 * 霓虹紫青渐变、像素标题、卡带插入电视雪花
 */
import { ref, computed } from 'vue'
import { mockPosts, mockGroups, mockTags, mockComments } from '@/mock/data'
import type { MockPost } from '@/mock/data'
// 引入 Markdown 渲染器，用于电视屏文章内容的富文本展示
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

const groupFilter = ref('')
const tagFilter = ref('')
const hoverId = ref<string | null>(null)
const inserted = ref<MockPost | null>(null)
const inserting = ref(false)
const liked = ref<Set<string>>(new Set())
const likes = ref<Record<string, number>>({})
const comments = ref([...mockComments])
const newC = ref('')
mockPosts.forEach(p => likes.value[p.id] = p.likes)

const filtered = computed(() => {
  let list = [...mockPosts]
  if (groupFilter.value) list = list.filter(p => p.group.id === groupFilter.value)
  if (tagFilter.value) list = list.filter(p => p.tags.some(t => t.slug === tagFilter.value))
  return list
})
const totalLikes = computed(() => Object.values(likes.value).reduce((a,b)=>a+b,0))

function insert(p: MockPost) {
  inserting.value = true
  setTimeout(() => { inserted.value = p; inserting.value = false }, 420)
}
function eject() { inserted.value = null }
function like(id: string) {
  if (liked.value.has(id)) { liked.value.delete(id); likes.value[id]!-- } else { liked.value.add(id); likes.value[id]++ }
  liked.value = new Set(liked.value)
}
function send() {
  const t = newC.value.trim(); if (!t) return
  comments.value.unshift({ id: 'c'+Date.now(), author: '我', avatar: '🧑', content: t, time: '刚刚', likes: 0 } as any)
  newC.value = ''
}
function prevCart() {
  if (!filtered.value.length) return
  const idx = inserted.value ? filtered.value.findIndex(p => p.id===inserted.value!.id) : -1
  const n = idx <= 0 ? filtered.value.length-1 : idx-1
  insert(filtered.value[n]!)
}
function nextCart() {
  if (!filtered.value.length) return
  const idx = inserted.value ? filtered.value.findIndex(p => p.id===inserted.value!.id) : -1
  const n = (idx+1) % filtered.value.length
  insert(filtered.value[n]!)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Mono:wght@400;700&display=swap');
.arcade { min-height: 100vh; background: radial-gradient(120% 120% at 30% 20%, #1a0a3a 0, #0a0014 55%, #000 100%); color: #e8e8ff; display: flex; flex-direction: column; }
.top { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: rgba(0,0,0,.5); border-bottom: 2px solid #00ffd1; flex-wrap: wrap; }
.hub { background: #fff; color: #0a0014; padding: 6px 12px; font-size: 12px; font-weight: 800; }
.title { font-family: 'Press Start 2P', monospace; font-size: 10px; letter-spacing: .08em; color: #00ffd1; text-shadow: 0 0 12px #00ffd1; flex: 1; }
.hint { font-size: 11px; opacity: .7; }
.layout { flex: 1; display: grid; grid-template-columns: 320px 1fr; gap: 14px; padding: 14px; min-height: 0; }
.rack { background: rgba(255,255,255,.06); backdrop-filter: blur(8px); padding: 12px; display: flex; flex-direction: column; gap: 10px; border-color: #7b00ff; box-shadow: 0 0 18px rgba(123,0,255,.35); }
.rack-head { display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; letter-spacing: .08em; border-bottom: 1px solid rgba(255,255,255,.15); padding-bottom: 8px; }
.filter-row, .tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
.chip, .tag { padding: 4px 8px; font-size: 10px; background: rgba(255,255,255,.08); color: #fff; cursor: pointer; border-color: rgba(255,255,255,.2); }
.chip.active { background: #00ffd1; color: #0a0014; }
.tag { color: #0a0014; font-weight: 800; }
.carts { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; overflow: auto; max-height: 420px; }
.cart { position: relative; background: #fff; color: #0a0014; padding: 8px; text-align: left; cursor: pointer; transition: transform .14s, box-shadow .14s; overflow: hidden; }
.cart:hover, .cart.active { transform: translateY(-3px) rotate(-.5deg); box-shadow: 0 0 0 2px #00ffd1, 0 0 18px #00ffd1; }
.cart.inserted { outline: 2px solid #00ffd1; }
.cart img { width: 100%; height: 72px; object-fit: cover; border: 1px solid #0a0014; }
.cart-label { display: block; font-size: 11px; font-weight: 800; margin-top: 6px; line-height: 1.2; }
.cart-meta { font-size: 9px; opacity: .6; }
.neon { position: absolute; left: 0; right: 0; bottom: 0; height: 4px; }
.score { display: flex; justify-content: space-between; font-size: 11px; padding: 8px 10px; background: #0a0014; color: #00ffd1; border-color: #00ffd1; }

.machine { background: linear-gradient(180deg, #1a0a3a, #0a0014); padding: 12px; display: flex; flex-direction: column; gap: 12px; border-color: #00ffd1; box-shadow: 0 0 24px rgba(0,255,209,.25); }
.machine-top { display: flex; justify-content: space-between; font-size: 10px; letter-spacing: .1em; color: #00ffd1; }
.led { color: #ff3b3b; text-shadow: 0 0 8px #ff3b3b; }
.slot-area { display: flex; gap: 10px; align-items: center; }
.slot { flex: 1; height: 64px; background: #0a0014; display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-color: #00ffd1; position: relative; }
.slot.has { background: #fff; color: #0a0014; }
.slot-hint { opacity: .6; font-size: 11px; }
.inserted-cart { display: flex; gap: 10px; align-items: center; }
.inserted-cart img { width: 44px; height: 44px; object-fit: cover; border: 1px solid #0a0014; }
.eject { margin-left: auto; padding: 6px 10px; font-size: 11px; background: #ff3b3b; color: #fff; cursor: pointer; }
.screen { flex: 1; min-height: 420px; background: #000; position: relative; overflow: hidden; border-color: #00ffd1; }
.scan { position: absolute; inset: 0; background: repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,255,209,.07) 3px, transparent 4px); pointer-events: none; z-index: 2; }
.noise { position: absolute; inset: 0; opacity: .06; background: radial-gradient(rgba(255,255,255,.8) .6px, transparent .7px); background-size: 3px 3px; pointer-events: none; z-index: 2; }
.snow { position: absolute; inset: 0; display: grid; place-items: center; font-family: 'Space Mono', monospace; font-size: 12px; color: #00ffd1; background: #000; z-index: 1; animation: flicker .12s steps(2) infinite; }
@keyframes flicker { 50% { opacity: .85; } }
.idle { height: 100%; display: grid; place-items: center; text-align: center; gap: 8px; color: #00ffd1; padding: 40px; }
.idle b { font-family: 'Press Start 2P', monospace; font-size: 18px; text-shadow: 0 0 16px #00ffd1; }
.screen-content { padding: 16px; color: #e8e8ff; overflow: auto; height: 100%; }
.screen-cover { width: 100%; height: 180px; object-fit: cover; border: 1px solid #00ffd1; }
.screen-title { font-family: 'Press Start 2P', monospace; font-size: 14px; line-height: 1.4; margin: 12px 0; color: #00ffd1; text-shadow: 0 0 10px #00ffd1; }
.intro { font-size: 12px; opacity: .8; line-height: 1.6; }
.meta { display: flex; gap: 10px; align-items: center; margin: 10px 0; font-size: 11px; flex-wrap: wrap; }
.like { padding: 4px 8px; font-size: 11px; background: #00ffd1; color: #0a0014; cursor: pointer; }
.content { white-space: pre-wrap; font-size: 12px; line-height: 1.7; background: rgba(255,255,255,.06); border: 1px solid rgba(0,255,209,.3); padding: 12px; margin-top: 10px; }
.comments { margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }
.comment { padding: 8px 10px; background: rgba(255,255,255,.06); font-size: 11px; border-color: rgba(0,255,209,.3); }
.composer { display: flex; gap: 6px; padding: 6px; background: rgba(255,255,255,.06); border-color: rgba(0,255,209,.3); }
.composer input { flex: 1; background: transparent; border: none; outline: none; color: #fff; font: inherit; font-size: 11px; }
.composer button { padding: 6px 10px; background: #00ffd1; color: #0a0014; cursor: pointer; font-size: 11px; }
.controls { display: flex; gap: 8px; align-items: center; }
.btn { padding: 8px 12px; font-size: 11px; background: #fff; color: #0a0014; cursor: pointer; }
@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
