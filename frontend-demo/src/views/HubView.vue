<template>
  <div class="hub">
    <!-- 中性索引墙：细线 + 大留白，Hub 本身不预设风格偏见 -->
    <div class="top-rule"></div>
    <div class="marquee mono">
      <div class="marquee-inner">
        <span v-for="i in 6" :key="i">SYNTHSPARK POSTMODERN 8 DEMOS — GLASS / CRT / VOID / PAPER / POP / EDITORIAL / NEWSPAPER / ARCADE — MOUSE FRIENDLY · GPU · MOCK —</span>
      </div>
    </div>

    <header class="hub-header">
      <div class="hub-title">
        <div class="eyebrow mono">INDEX WALL / 2026.08 — demo/postmodern-interactive — 8 WORLDS</div>
        <h1 class="title">SynthSpark<br><span class="thin">后现代交互</span> Demo 集</h1>
        <p class="mono desc">一景一语 · 每 Demo 独立设计语言 · 浏览器内 · 鼠标高效 · 纯 Mock<br>Hub 为中性画廊，仅作索引；进入 Demo 即进入该世界完整材质。</p>
        <div class="legend mono">
          <span class="leg"><i style="background:rgba(0,122,255,.18)"></i> Glass</span>
          <span class="leg"><i style="background:#050508"></i> CRT</span>
          <span class="leg"><i style="background:#0a0a0f"></i> Void</span>
          <span class="leg"><i style="background:#d8c6a8"></i> Paper</span>
          <span class="leg"><i style="background:#ff6b9d"></i> Pop</span>
          <span class="leg"><i style="background:#faf9f6"></i> Editorial</span>
          <span class="leg"><i style="background:#e8e4d8"></i> Newspaper</span>
          <span class="leg"><i style="background:#0a0014"></i> Arcade</span>
        </div>
      </div>
      <div class="hub-meta">
        <div class="meta-row mono"><span>分支</span><b>demo/postmodern-interactive</b></div>
        <div class="meta-row mono"><span>端口</span><b>5174</b> <code>npm run dev</code></div>
        <div class="meta-row mono"><span>数据</span><b>Mock</b> 无后端</div>
        <div class="meta-row mono"><span>总数</span><b>8 Demos</b></div>
        <div class="mono note">Hub 为中性索引墙，Demo 内才进入完整世界材质。</div>
      </div>
    </header>

    <section class="cards">
      <router-link
        v-for="d in demos"
        :key="d.path"
        :to="d.path"
        class="card"
        :style="cardStyle(d)"
      >
        <div class="card-top mono">
          <span class="tag">{{ d.tag }}</span>
          <span class="arrow">→</span>
        </div>
        <div class="card-icon" :style="{ fontFamily: d.font }">{{ d.icon }}</div>
        <h2 :style="{ fontFamily: d.font }">{{ d.title }}</h2>
        <p class="mono card-desc">{{ d.desc }}</p>
        <ul class="mono feats">
          <li v-for="f in d.feats" :key="f">› {{ f }}</li>
        </ul>
        <div class="card-foot mono">
          <span class="pill" :style="{ background: d.accent, color: d.accentText }">{{ d.stack }}</span>
          <span class="go">进入 →</span>
        </div>
      </router-link>
    </section>

    <footer class="hub-footer mono">
      <span>SynthSpark · 8 独立世界 · 鼠标友好 · GPU 加速</span>
      <span>demo/postmodern-interactive · frontend-demo 5174</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
const demos = [
  {
    path: '/os', icon: '◐', tag: '01 — GLASS OS', title: 'SynthOS\n玻璃拟态 OS',
    desc: '毛玻璃窗口 + 柔阴影圆角。文章=文件，Spotlight 搜索。',
    feats: ['backdrop-blur 18px', '1px 细线 + 12px 圆角', 'Dock 放大'],
    bg: '#eef2f7', accent: '#007aff', accentText: '#fff', font: 'Inter, system-ui, sans-serif', stack: 'Glass · 12px'
  },
  {
    path: '/terminal', icon: '▣', tag: '02 — CRT', title: 'SynthTerm\n磷光终端',
    desc: '纯黑磷光 + 扫描线。芯片即命令，输出为卡片。',
    feats: ['磷光 glow', '1px 细线', '仅等宽'],
    bg: '#050508', accent: '#ffb000', accentText: '#0a0a0f', font: '"JetBrains Mono", monospace', stack: 'CRT · Phosphor'
  },
  {
    path: '/space', icon: '⬢', tag: '03 — VOID', title: 'SynthSpace\n深空极简',
    desc: '深空 + 细白线 + 极简画廊。拖拽漫游。',
    feats: ['毛玻璃 HUD', '无边框悬浮', 'Instrument Serif'],
    bg: '#0a0a0f', accent: '#ffffff', accentText: '#0a0a0f', font: '"Instrument Serif", serif', stack: 'Void · Gallery'
  },
  {
    path: '/desk', icon: '✎', tag: '04 — PAPER', title: 'SynthDesk\n暖纸拟物',
    desc: '牛皮桌面 + 活页纸 + 胶带毛玻璃。拖拽拍立得。',
    feats: ['纸纤维 + 木纹', '1px #d8c6a8', 'Caveat 手写'],
    bg: '#f6f1e1', accent: '#c9b088', accentText: '#0a0a0f', font: '"Instrument Serif", serif', stack: 'Paper · Craft'
  },
  {
    path: '/chat', icon: '◉', tag: '05 — POP', title: 'SynthChat\n孟菲斯波普',
    desc: '高饱和交替 + 不规则旋转。群聊×等轴城市。',
    feats: ['3n 彩交替', 'rotate -.6deg', 'Bricolage 800'],
    bg: '#6b5ce7', accent: '#ffd700', accentText: '#0a0a0f', font: '"Bricolage Grotesque", sans-serif', stack: 'Pop · Memphis'
  },
  {
    path: '/magazine', icon: 'M', tag: '06 — EDITORIAL', title: 'Magazine\n杂志排版',
    desc: '首字下沉 + 分栏 + 红线 + 黑白转彩。',
    feats: ['column-count', 'hairline', 'Cormorant'],
    bg: '#faf9f6', accent: '#c1121f', accentText: '#fff', font: '"Cormorant Garamond", serif', stack: 'Editorial'
  },
  {
    path: '/newspaper', icon: 'N', tag: '07 — NEWSPAPER', title: 'Newspaper\n报纸档案',
    desc: '双线报头 + 粗规则线 + 油墨噪点。',
    feats: ['grayscale 高对比', 'Courier 正文', '3px 规则'],
    bg: '#e8e4d8', accent: '#0a0a0f', accentText: '#fff', font: '"Playfair Display", serif', stack: 'Newspaper'
  },
  {
    path: '/arcade', icon: '⬣', tag: '08 — ARCADE', title: 'Arcade\n霓虹卡带',
    desc: '紫青霓虹 + 像素标题 + 卡带插入雪花。',
    feats: ['Press Start 2P', '0 0 16px neon', '拖拽卡带'],
    bg: '#0a0014', accent: '#00ffd1', accentText: '#0a0014', font: '"Press Start 2P", monospace', stack: 'Vapor · Neon'
  },
]

function cardStyle(d: typeof demos[number]) {
  const isDark = d.bg === '#050508' || d.bg === '#0a0a0f' || d.bg === '#0a0014' || d.bg === '#6b5ce7'
  return {
    background: d.bg,
    color: isDark ? '#f4f4f0' : '#0a0a0f',
    border: isDark ? '1px solid rgba(255,255,255,.14)' : '1px solid #0a0a0f',
    fontFamily: d.font,
  }
}
</script>

<style scoped>
.hub { min-height: 100vh; background: #fcfcfa; color: #0a0a0f; padding-bottom: 32px; }
.top-rule { height: 3px; background: #0a0a0f; }
.marquee { overflow: hidden; white-space: nowrap; border-bottom: 1px solid #e8e0cc; padding: 8px 0; background: #fff; }
.marquee-inner { display: inline-flex; gap: 40px; animation: marquee 20s linear infinite; font-size: 10px; letter-spacing: .12em; }
@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
.hub-header { display: grid; grid-template-columns: 1.6fr .9fr; gap: 24px; padding: 26px 3%; border-bottom: 1px solid #e8e0cc; }
.eyebrow { font-size: 10px; letter-spacing: .14em; color: #888; margin-bottom: 10px; }
.title { font-size: clamp(32px, 5.6vw, 64px); line-height: .92; font-weight: 300; font-family: "Cormorant Garamond", serif; }
.title .thin { font-weight: 300; font-style: italic; }
.desc { margin-top: 12px; font-size: 12px; line-height: 1.7; color: #444; }
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.leg { display: inline-flex; align-items: center; gap: 6px; font-size: 10px; border: 1px solid #e8e0cc; padding: 4px 8px; background: #fff; }
.leg i { width: 12px; height: 12px; border: 1px solid #0a0a0f; display: inline-block; }
.hub-meta { background: #fff; border: 1px solid #e8e0cc; padding: 14px; align-self: start; }
.meta-row { display: flex; justify-content: space-between; font-size: 11px; padding: 6px 0; border-bottom: 1px solid #f0ece2; }
.meta-row b { font-weight: 800; }
.note { margin-top: 10px; font-size: 10px; color: #777; line-height: 1.5; }
.cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; padding: 18px 2.2%; }
.card { padding: 16px; min-height: 320px; display: flex; flex-direction: column; transition: transform .16s, box-shadow .16s; }
.card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,.12); }
.card-top { display: flex; justify-content: space-between; font-size: 9px; letter-spacing: .12em; font-weight: 800; opacity: .8; }
.card-icon { font-size: 28px; margin: 12px 0 4px; }
.card h2 { white-space: pre-line; font-size: 18px; line-height: 1; font-weight: 800; margin-bottom: 6px; }
.card-desc { font-size: 11px; line-height: 1.5; opacity: .8; min-height: 32px; }
.feats { list-style: none; margin-top: 10px; font-size: 10px; line-height: 1.6; opacity: .7; }
.card-foot { margin-top: auto; display: flex; justify-content: space-between; align-items: center; padding-top: 12px; font-size: 10px; }
.pill { padding: 4px 8px; border-radius: 999px; font-weight: 800; }
.go { font-weight: 800; text-decoration: underline; font-size: 11px; }
.hub-footer { display: flex; justify-content: space-between; padding: 14px 2.2% 0; font-size: 10px; letter-spacing: .08em; color: #888; border-top: 1px solid #e8e0cc; margin: 18px 2.2% 0; }
@media (max-width: 1200px) { .cards { grid-template-columns: repeat(2, 1fr); } .hub-header { grid-template-columns: 1fr; } }
@media (max-width: 640px) { .cards { grid-template-columns: 1fr; } }
</style>
