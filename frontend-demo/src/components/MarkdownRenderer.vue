<template>
  <!-- 按 Demo 风格定制的 Markdown 渲染器 -->
  <div class="md" :class="`md--${theme}`" v-html="html"></div>
</template>

<script setup lang="ts">
/**
 * 通用 Markdown 渲染器（Demo 专用）
 * - marked 解析 + DOMPurify 清洗
 * - 按 theme 切换 8 套独立样式（scoped + :deep）
 * - 支持长文：标题/引用/列表/表格/代码/图片多图
 */
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = withDefaults(defineProps<{
  content: string
  theme?: 'glass' | 'crt' | 'space' | 'paper' | 'pop' | 'editorial' | 'newspaper' | 'arcade' | 'default'
}>(), {
  theme: 'default',
})

// 配置 marked：GFM 表格/换行
marked.setOptions({
  gfm: true,
  breaks: true,
})

const html = computed(() => {
  const raw = marked.parse(props.content || '') as string
  // DOMPurify 保留 table/img/pre/code 等
  return DOMPurify.sanitize(raw, { ADD_TAGS: ['iframe'], ADD_ATTR: ['target'] })
})
</script>

<style scoped>
.md { font-size: 13px; line-height: 1.85; word-break: break-word; overflow-wrap: anywhere; }
.md :deep(h1) { font-size: 1.6em; margin: 1em 0 .6em; line-height: 1.2; }
.md :deep(h2) { font-size: 1.35em; margin: 1.2em 0 .5em; line-height: 1.25; }
.md :deep(h3) { font-size: 1.15em; margin: 1em 0 .4em; }
.md :deep(p) { margin: .7em 0; }
.md :deep(a) { text-decoration: underline; text-underline-offset: 2px; }
.md :deep(blockquote) { margin: .8em 0; padding: 8px 12px; border-left: 4px solid currentColor; opacity: .9; }
.md :deep(ul), .md :deep(ol) { margin: .6em 0 .6em 1.4em; }
.md :deep(li) { margin: .25em 0; }
.md :deep(code) { font-family: 'JetBrains Mono', monospace; font-size: .92em; padding: 1px 5px; border-radius: 4px; }
.md :deep(pre) { margin: .8em 0; padding: 12px; overflow: auto; border-radius: 8px; font-size: 12px; line-height: 1.6; }
.md :deep(pre code) { padding: 0; background: transparent; border: none; }
.md :deep(img) { max-width: 100%; height: auto; display: block; margin: 12px auto; border-radius: 8px; }
.md :deep(table) { width: 100%; border-collapse: collapse; margin: .8em 0; font-size: 12px; display: block; overflow-x: auto; }
.md :deep(th), .md :deep(td) { border: 1px solid currentColor; padding: 6px 8px; text-align: left; }
.md :deep(hr) { margin: 1.2em 0; border: none; border-top: 1px solid currentColor; opacity: .2; }
.md :deep(strong) { font-weight: 800; }

/* ===== 8 套主题 ===== */

/* 玻璃 Glass — 浅灰蓝毛玻璃 */
.md--glass { color: #1a2233; }
.md--glass :deep(a) { color: #007aff; }
.md--glass :deep(blockquote) { background: rgba(0,122,255,.06); border-left-color: #007aff; }
.md--glass :deep(code) { background: rgba(0,122,255,.08); color: #0a2a5a; border: 1px solid rgba(0,122,255,.14); }
.md--glass :deep(pre) { background: #f2f6ff; border: 1px solid rgba(0,122,255,.14); color: #1a2233; }
.md--glass :deep(th) { background: rgba(0,122,255,.06); }
.md--glass :deep(img) { border: 1px solid rgba(0,0,0,.08); box-shadow: 0 4px 16px rgba(0,0,0,.08); }

/* CRT 磷光 — 黑 + 荧光 */
.md--crt { color: #ffb000; }
.md--crt :deep(h1), .md--crt :deep(h2), .md--crt :deep(h3) { color: #ffb000; text-shadow: 0 0 10px rgba(255,176,0,.45); font-family: 'JetBrains Mono', monospace; }
.md--crt :deep(a) { color: #ffd45e; }
.md--crt :deep(blockquote) { background: rgba(255,176,0,.07); border-left-color: #ffb000; color: #ffd45e; }
.md--crt :deep(code) { background: rgba(255,176,0,.10); color: #ffd45e; border: 1px solid rgba(255,176,0,.22); }
.md--crt :deep(pre) { background: #0c0a00; border: 1px solid rgba(255,176,0,.22); color: #ffb000; box-shadow: 0 0 12px rgba(255,176,0,.18) inset; }
.md--crt :deep(img) { border: 1px solid rgba(255,176,0,.32); box-shadow: 0 0 16px rgba(255,176,0,.22); filter: saturate(1.05) contrast(1.08); }
.md--crt :deep(table) { color: #ffb000; }
.md--crt :deep(th) { background: rgba(255,176,0,.10); }
.md--crt :deep(hr) { border-top-color: #ffb000; }

/* 深空 Space — 黑底白细线 极简 */
.md--space { color: #e8e8ef; }
.md--space :deep(h1), .md--space :deep(h2) { font-family: 'Instrument Serif', serif; letter-spacing: .06em; color: #fff; font-weight: 400; }
.md--space :deep(a) { color: #fff; text-decoration-color: rgba(255,255,255,.4); }
.md--space :deep(blockquote) { background: rgba(255,255,255,.04); border-left-color: rgba(255,255,255,.9); color: #fff; }
.md--space :deep(code) { background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); color: #fff; }
.md--space :deep(pre) { background: #0f0f14; border: 1px solid rgba(255,255,255,.12); color: #e8e8ef; }
.md--space :deep(th) { background: rgba(255,255,255,.06); color: #fff; }
.md--space :deep(img) { border: 1px solid rgba(255,255,255,.12); filter: grayscale(.1); }
.md--space :deep(hr) { border-top-color: rgba(255,255,255,.12); }

/* 暖纸 Paper — 牛皮纸 */
.md--paper { color: #3a2f1e; font-family: 'Instrument Serif', 'Noto Serif SC', serif; }
.md--paper :deep(h1), .md--paper :deep(h2) { color: #2b2112; font-weight: 700; }
.md--paper :deep(a) { color: #7a4a00; }
.md--paper :deep(blockquote) { background: #fff7e6; border-left-color: #c9b088; color: #5a3e1a; font-style: italic; }
.md--paper :deep(code) { background: #fff1d6; border: 1px solid #e8d9b8; color: #5a3e1a; }
.md--paper :deep(pre) { background: #fffef7; border: 1px solid #e8d9b8; color: #3a2f1e; }
.md--paper :deep(th) { background: #fff1d6; }
.md--paper :deep(img) { border: 1px solid #e8d9b8; box-shadow: 0 2px 10px rgba(0,0,0,.08); border-radius: 2px; }

/* 波普 Pop — 高饱和 */
.md--pop { color: #0a0a0f; }
.md--pop :deep(h1), .md--pop :deep(h2) { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; }
.md--pop :deep(a) { color: #6b5ce7; background: #ffd700; padding: 0 3px; text-decoration: none; border: 1px solid #0a0a0f; }
.md--pop :deep(blockquote) { background: #ffd700; border-left: 4px solid #0a0a0f; color: #0a0a0f; font-weight: 700; transform: rotate(-.2deg); }
.md--pop :deep(code) { background: #ff6b9d; color: #0a0a0f; border: 1px solid #0a0a0f; font-weight: 800; }
.md--pop :deep(pre) { background: #0a0a0f; color: #f4f4f0; border: 2px solid #0a0a0f; transform: rotate(.15deg); }
.md--pop :deep(pre code) { color: #f4f4f0; background: transparent; border: none; }
.md--pop :deep(img) { border: 3px solid #0a0a0f; box-shadow: 6px 6px 0 #0a0a0f; transform: rotate(.3deg); }
.md--pop :deep(th) { background: #6bff8a; color: #0a0a0f; }

/* 杂志 Editorial — 米白 hairline */
.md--editorial { color: #1a1a1a; }
.md--editorial :deep(h1) { font-family: 'Cormorant Garamond', serif; font-weight: 300; font-size: 2em; letter-spacing: -.01em; border-bottom: 1px solid #e8e0cc; padding-bottom: .3em; }
.md--editorial :deep(h2) { font-family: 'Cormorant Garamond', serif; font-weight: 600; color: #1a1a1a; border-left: 3px solid #c1121f; padding-left: 10px; }
.md--editorial :deep(a) { color: #c1121f; }
.md--editorial :deep(blockquote) { background: #faf9f6; border-left-color: #c1121f; font-style: italic; color: #333; }
.md--editorial :deep(code) { background: #f4efe6; border: 1px solid #e8e0cc; }
.md--editorial :deep(pre) { background: #fff; border: 1px solid #e8e0cc; }
.md--editorial :deep(img) { border: 1px solid #e8e0cc; border-radius: 0; filter: grayscale(1); transition: filter .4s; }
.md--editorial :deep(img:hover) { filter: grayscale(0); }
.md--editorial :deep(th) { background: #1a1a1a; color: #fff; }
.md--editorial :deep(hr) { border-top: 1px solid #c1121f; opacity: 1; }

/* 报纸 Newspaper — 高对比油墨 */
.md--newspaper { color: #1a1a0e; font-family: 'Courier Prime', 'Courier New', monospace; }
.md--newspaper :deep(h1), .md--newspaper :deep(h2) { font-family: 'Playfair Display', serif; font-weight: 900; text-transform: uppercase; letter-spacing: .04em; border-bottom: 3px solid #0a0a0f; padding-bottom: .2em; }
.md--newspaper :deep(a) { color: #0a0a0f; background: #ffde59; padding: 0 2px; }
.md--newspaper :deep(blockquote) { background: #ffde59; border-left: 4px solid #0a0a0f; font-weight: 700; text-transform: uppercase; font-size: .92em; }
.md--newspaper :deep(code) { background: #0a0a0f; color: #f6f1e1; border: 1px solid #0a0a0f; }
.md--newspaper :deep(pre) { background: #0a0a0f; color: #f6f1e1; border: 2px solid #0a0a0f; }
.md--newspaper :deep(img) { border: 2px solid #0a0a0f; filter: grayscale(1) contrast(1.25); border-radius: 0; }
.md--newspaper :deep(th) { background: #0a0a0f; color: #f6f1e1; text-transform: uppercase; font-size: 11px; }

/* 街机 Arcade — 霓虹像素 */
.md--arcade { color: #e8e8ff; }
.md--arcade :deep(h1), .md--arcade :deep(h2) { font-family: 'Press Start 2P', monospace; font-size: .9em; line-height: 1.6; color: #00ffd1; text-shadow: 0 0 10px #00ffd1, 0 0 20px #7b00ff; }
.md--arcade :deep(h2) { font-size: .8em; }
.md--arcade :deep(a) { color: #00ffd1; text-shadow: 0 0 6px #00ffd1; }
.md--arcade :deep(blockquote) { background: rgba(123,0,255,.12); border-left-color: #00ffd1; color: #00ffd1; box-shadow: 0 0 12px rgba(0,255,209,.18) inset; }
.md--arcade :deep(code) { background: #0a0014; color: #00ffd1; border: 1px solid #7b00ff; box-shadow: 0 0 8px rgba(0,255,209,.22); }
.md--arcade :deep(pre) { background: #0a0014; border: 1px solid #7b00ff; color: #00ffd1; box-shadow: 0 0 16px rgba(123,0,255,.22); }
.md--arcade :deep(img) { border: 2px solid #00ffd1; box-shadow: 0 0 16px #00ffd1, 0 0 32px #7b00ff; }
.md--arcade :deep(th) { background: #7b00ff; color: #fff; }
</style>
