<template>
  <!-- Markdown渲染 - 使用Milkdown -->
  <div ref="containerRef" class="markdown-renderer">
    <div ref="previewRef" class="markdown-preview"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from '@milkdown/core'
import { commonmark } from '@milkdown/preset-commonmark'
import { useMilkdownTheme } from '@/composables/useMilkdownTheme'

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

onMounted(async () => {
  if (!previewRef.value) return

  // 应用主题
  watchTheme(containerRef.value)

  editor = await Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, previewRef.value!)
      ctx.set(defaultValueCtx, props.content || '')
      // 设置为只读模式
      ctx.set(editorViewOptionsCtx, {
        editable: () => false
      })
    })
    // 不使用nord主题，使用自定义CSS
    .use(commonmark)
    .create()

  // 等待渲染完成后添加 ID
  await nextTick()
  addHeadingIds()
  emit('rendered')
})

onUnmounted(() => {
  editor?.destroy()
})

// 监听内容变化
watch(() => props.content, async (newValue) => {
  if (editor) {
    // 销毁旧实例并创建新实例
    editor.destroy()
    editor = await Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, previewRef.value!)
        ctx.set(defaultValueCtx, newValue || '')
        ctx.set(editorViewOptionsCtx, {
          editable: () => false
        })
      })
      // 不使用nord主题，使用自定义CSS
      .use(commonmark)
      .create()

    // 等待渲染完成后添加 ID
    await nextTick()
    addHeadingIds()
    emit('rendered')
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
</style>
