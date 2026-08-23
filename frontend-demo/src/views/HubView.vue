<template>
  <div class="hub">
    <!-- 顶部跑马灯 -->
    <div class="marquee brutal-border">
      <div class="marquee-inner mono">
        <span v-for="i in 6" :key="i">SYNTHINK POSTMODERN DEMO — OS / TERMINAL / 3D SPACE / DESK / CHAT — 鼠标友好 · 纯前端 Mock · 无需后端 —</span>
      </div>
    </div>

    <header class="hub-header">
      <div class="hub-title">
        <div class="eyebrow mono">DEMO HUB / 2026.08 — demo/postmodern-interactive</div>
        <h1 class="display">SynthInk<br><span class="outline">后现代交互</span> Demo 集</h1>
        <p class="mono desc">浏览器内呈现 · 泛用户鼠标高效交互 · 5 个平行 Demo · 全部 Mock 数据<br>每个 Demo 都是对“博客”的一次隐喻替换。点卡片进入，右上角一键回 Hub。</p>
      </div>
      <div class="hub-meta brutal-border brutal-shadow">
        <div class="meta-row mono"><span>分支</span><b>demo/postmodern-interactive</b></div>
        <div class="meta-row mono"><span>端口</span><b>5174</b> <code>npm run dev</code></div>
        <div class="meta-row mono"><span>数据</span><b>Mock</b> 无后端</div>
        <div class="meta-row mono"><span>后续</span><b>移动端再议</b></div>
        <div class="cta-row">
          <a class="btn brutal-border" href="https://github.com" target="_blank">OPS: 5174 / 8002</a>
        </div>
      </div>
    </header>

    <section class="cards">
      <router-link
        v-for="d in demos"
        :key="d.path"
        :to="d.path"
        class="card brutal-border brutal-shadow"
        :style="{ background: d.bg }"
      >
        <div class="card-top mono">
          <span class="tag">{{ d.tag }}</span>
          <span class="arrow">→</span>
        </div>
        <div class="card-icon">{{ d.icon }}</div>
        <h2 class="display">{{ d.title }}</h2>
        <p class="mono card-desc">{{ d.desc }}</p>
        <ul class="mono feats">
          <li v-for="f in d.feats" :key="f">› {{ f }}</li>
        </ul>
        <div class="card-foot mono">
          <span class="pill">{{ d.stack }}</span>
          <span class="go">进入 Demo →</span>
        </div>
      </router-link>
    </section>

    <footer class="hub-footer mono">
      <span>SynthSpark · 多智能体博客系统 · Postmodern Demo Hub</span>
      <span>鼠标友好 · GPU 加速按需 · 纯前端</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
const demos = [
  {
    path: '/os', icon: '🖥️', tag: '01 — PSEUDO OS', title: 'SynthOS\n伪操作系统',
    desc: '可拖拽窗口 + Dock + 文件夹。文章=文件，标签=彩点，写作=编辑器窗口。',
    feats: ['拖拽/缩放/层叠', 'Spotlight 搜索', '文件夹即分组'],
    bg: '#00f5d4', stack: 'Vue + WindowManager'
  },
  {
    path: '/terminal', icon: '▣', tag: '02 — TERMINAL', title: 'SynthTerm\n鼠标友好终端',
    desc: 'CRT 终端美学，但全部用鼠标点选。命令是按钮，输出是卡片。',
    feats: ['可点击命令芯片', '扫描线 + 荧光', '键盘可选鼠标必行'],
    bg: '#ffd700', stack: 'xterm 风格 + Vue'
  },
  {
    path: '/space', icon: '⬢', tag: '03 — 3D SPACE', title: 'SynthSpace\n空间画廊',
    desc: '文章悬浮成星系/画廊。拖拽漫游，悬停发光，点击推门。GPU 加速。',
    feats: ['Canvas 2D+3D 视差', 'Raycast 悬停', '俯瞰/漫游切换'],
    bg: '#ff006e', stack: 'Canvas + CSS 3D'
  },
  {
    path: '/desk', icon: '📓', tag: '04 — VIRTUAL DESK', title: 'SynthDesk\n虚拟笔记本',
    desc: '拟物书桌：活页夹、拍立得、便签、胶带。翻页、拖纸、钉图钉。',
    feats: ['翻页动画', '拖拽纸张', '便签即评论'],
    bg: '#f4f4f0', stack: 'CSS 3D + Motion'
  },
  {
    path: '/chat', icon: '💬', tag: '05 — CHAT / CITY', title: 'SynthChat\nAgent 群聊×城市',
    desc: '左=Agent 联系人，中=频道(分组)，右=线程(文章)。可切等轴城市视图。',
    feats: ['Slack 式三栏', '线程即文章', 'City 俯瞰彩蛋'],
    bg: '#6b5ce7', stack: 'Vue + Pixi 风格'
  },
]
</script>

<style scoped>
.hub { min-height: 100vh; padding: 0 0 40px; background: #f4f4f0; }
.marquee { overflow: hidden; white-space: nowrap; background: #0a0a0f; color: #f4f4f0; border-left: none; border-right: none; border-top: none; padding: 10px 0; }
.marquee-inner { display: inline-flex; gap: 40px; animation: marquee 18s linear infinite; font-size: 12px; letter-spacing: 0.08em; }
@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }

.hub-header { display: grid; grid-template-columns: 1.6fr 0.9fr; gap: 24px; padding: 28px 3%; }
.eyebrow { font-size: 11px; letter-spacing: 0.14em; color: #666; margin-bottom: 12px; }
.hub-title h1 { font-size: clamp(36px, 6vw, 68px); line-height: 0.9; font-weight: 800; }
.hub-title h1 .outline { color: transparent; -webkit-text-stroke: 2px #0a0a0f; }
.desc { margin-top: 14px; font-size: 13px; line-height: 1.7; color: #333; }
.hub-meta { background: #fff; padding: 16px; align-self: start; }
.meta-row { display: flex; justify-content: space-between; font-size: 11px; padding: 6px 0; border-bottom: 1px dashed #ddd; }
.meta-row b { font-weight: 800; }
.cta-row { margin-top: 12px; }
.btn { display: inline-block; padding: 8px 12px; background: #0a0a0f; color: #fff; font-size: 11px; letter-spacing: 0.08em; }

.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; padding: 0 3%; }
.card { padding: 18px; min-height: 360px; display: flex; flex-direction: column; position: relative; transition: transform .15s; }
.card:hover { transform: translate(-3px, -3px); box-shadow: 9px 9px 0 #0a0a0f; }
.card-top { display: flex; justify-content: space-between; font-size: 10px; letter-spacing: 0.12em; font-weight: 800; }
.card-icon { font-size: 40px; margin: 14px 0 6px; }
.card h2 { white-space: pre-line; font-size: 26px; line-height: 0.95; font-weight: 800; margin-bottom: 8px; }
.card-desc { font-size: 12px; line-height: 1.6; color: #111; min-height: 38px; }
.feats { list-style: none; margin-top: 12px; font-size: 11px; line-height: 1.7; }
.card-foot { margin-top: auto; display: flex; justify-content: space-between; align-items: center; padding-top: 14px; font-size: 10px; }
.pill { background: #0a0a0f; color: #fff; padding: 4px 8px; border-radius: 999px; }
.go { font-weight: 800; text-decoration: underline; }

.hub-footer { display: flex; justify-content: space-between; padding: 18px 3% 0; font-size: 10px; letter-spacing: 0.08em; color: #666; border-top: 2px solid #0a0a0f; margin: 28px 3% 0; }

@media (max-width: 1100px) { .cards { grid-template-columns: repeat(2, 1fr); } .hub-header { grid-template-columns: 1fr; } }
@media (max-width: 680px) { .cards { grid-template-columns: 1fr; } }
</style>
