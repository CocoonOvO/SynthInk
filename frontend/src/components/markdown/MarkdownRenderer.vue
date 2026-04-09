<template>
  <!-- Markdown渲染 - 使用Milkdown -->
  <div ref="containerRef" class="markdown-renderer">
    <div ref="previewRef" class="markdown-preview"></div>
  </div>
</template>

<script setup lang="ts">
// Prism 主题 CSS - 必须在组件导入前加载
import 'prismjs/themes/prism-tomorrow.css'
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx, editorViewCtx } from '@milkdown/core'
import { commonmark } from '@milkdown/preset-commonmark'
import { gfm } from '@milkdown/preset-gfm'
import { prism, prismConfig } from '@milkdown/plugin-prism'
import { useMilkdownTheme } from '@/composables/useMilkdownTheme'
// Refractor 语言注册 - 使用 refractor/all 导入所有语言
import { refractor } from 'refractor/all'

const props = defineProps<{
  content: string
}>()

const emit = defineEmits<{
  rendered: []
}>()

const containerRef = ref<HTMLElement | null>(null)
const previewRef = ref<HTMLElement | null>(null)
let editor: Editor | null = null

// 主题适配
const { watchTheme } = useMilkdownTheme()

// 给标题添加 ID
const addHeadingIds = () => {
  if (!previewRef.value) return
  const headings = previewRef.value.querySelectorAll('h1, h2, h3')
  headings.forEach((heading, index) => {
    heading.id = `section-${index}`
  })
}

// 清理多余的空段落
const removeEmptyParagraphs = () => {
  // 使用 document.querySelector 直接获取，避免 ref 失效问题
  const previewEl = document.querySelector('.markdown-preview')
  if (!previewEl) return

  // 查找 ProseMirror 编辑器容器
  const prosemirror = previewEl.querySelector('.ProseMirror')
  const container = prosemirror || previewEl

  // 查找所有空的 <p> 元素（只包含空白字符或 <br>）
  const emptyParagraphs = container.querySelectorAll('p')
  emptyParagraphs.forEach((p) => {
    const text = p.textContent || ''
    const hasOnlyBr = p.querySelectorAll('br').length > 0 && text.trim() === ''
    const isEmpty = text.trim() === '' && !p.querySelector('img, code, a, strong, em')
    if (isEmpty || hasOnlyBr) {
      // 只移除文档开头和结尾的空段落
      const allParagraphs = Array.from(container.querySelectorAll('p'))
      const index = allParagraphs.indexOf(p)
      const isFirst = index === 0
      const isLast = index === allParagraphs.length - 1
      if (isFirst || isLast) {
        p.remove()
      }
    }
  })
}

// 创建编辑器实例
const createEditor = async (content: string) => {
  // 清理内容：去除首尾空白字符，避免渲染多余的空段落
  const cleanContent = (content || '').trim()
  return Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, previewRef.value!)
      ctx.set(defaultValueCtx, cleanContent)
      // 设置为只读模式
      ctx.set(editorViewOptionsCtx, {
        editable: () => false
      })
      // 配置 prism 语言
      ctx.set(prismConfig.key, {
        configureRefractor: () => refractor
      })
    })
    .use(commonmark)
    .use(gfm)
    .use(prism)
    .create()
}

// 强制触发 prism 高亮
const forcePrismHighlight = () => {
  setTimeout(() => {
    if (editor) {
      const view = editor.ctx.get(editorViewCtx)
      const tr = view.state.tr.insertText(' ', 0).delete(0, 1)
      view.dispatch(tr)
    }
  }, 100)
}

onMounted(async () => {
  if (!previewRef.value) return

  // 应用主题
  watchTheme(containerRef.value)

  editor = await createEditor(props.content || '')

  // 等待渲染完成后添加 ID、清理空段落并强制触发高亮
  // 使用 setTimeout 确保 Milkdown 完全渲染
  setTimeout(() => {
    addHeadingIds()
    forcePrismHighlight()
    // 在 forcePrismHighlight 之后清理空段落，避免它重新创建空段落
    setTimeout(() => {
      removeEmptyParagraphs()
      emit('rendered')
    }, 150)
  }, 100)
})

onUnmounted(() => {
  editor?.destroy()
})

// 监听内容变化
watch(() => props.content, async (newValue) => {
  if (editor) {
    // 销毁旧实例并创建新实例
    editor.destroy()
    editor = await createEditor(newValue || '')

    // 等待渲染完成后添加 ID、清理空段落并强制触发高亮
    // 使用 setTimeout 确保 Milkdown 完全渲染
    setTimeout(() => {
      addHeadingIds()
      forcePrismHighlight()
      // 在 forcePrismHighlight 之后清理空段落，避免它重新创建空段落
      setTimeout(() => {
        removeEmptyParagraphs()
        emit('rendered')
      }, 150)
    }, 100)
  }
})
</script>

<style scoped>
.markdown-renderer {
  width: 100%;
}

.markdown-preview {
  width: 100%;
}

/* Milkdown 预览样式 */
:deep(.milkdown) {
  padding: 0;
  background: transparent;
  color: var(--text-primary);
}

:deep(.milkdown .editor) {
  cursor: default;
}

/* 禁用编辑器交互 */
:deep(.milkdown .ProseMirror) {
  outline: none;
}

/* 代码块语言标识 */
:deep(pre[data-lang]) {
  position: relative;
  padding-top: 2.5em;
}

:deep(pre[data-lang]::before) {
  content: attr(data-lang);
  position: absolute;
  top: 0.5em;
  right: 0.8em;
  font-size: 0.75em;
  font-family: 'Fira Code', 'Consolas', monospace;
  color: var(--text-secondary, #6a737d);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.7;
}
</style>
