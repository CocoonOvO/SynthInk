<template>
  <div class="hljs-code-block" :class="{ 'is-editable': editable }">
    <div v-if="editable" class="code-header">
      <select v-model="currentLang" @change="onLangChange">
        <option value="javascript">JavaScript</option>
        <option value="typescript">TypeScript</option>
        <option value="python">Python</option>
        <option value="java">Java</option>
        <option value="css">CSS</option>
        <option value="html">HTML</option>
        <option value="json">JSON</option>
        <option value="sql">SQL</option>
        <option value="bash">Bash</option>
      </select>
    </div>
    <div class="code-wrapper">
      <pre
        v-show="isEditing"
        ref="editRef"
        class="code-editor"
        contenteditable="true"
        @input="onInput"
        @blur="onBlur"
      ><code :class="`language-${currentLang}`">{{ modelValue }}</code></pre>
      <pre
        v-show="!isEditing"
        class="code-display"
        :class="{ 'clickable': editable }"
        @click="startEdit"
      ><code :class="`language-${currentLang}`" v-html="highlighted"></code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import hljs from 'highlight.js'

const props = withDefaults(defineProps<{
  modelValue: string
  language?: string
  editable?: boolean
}>(), {
  language: 'javascript',
  editable: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const DARK_THEME = 'atom-one-dark'
const LIGHT_THEME = 'atom-one-light'

const isDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)
const isEditing = ref(false)
const editRef = ref<HTMLElement>()
const currentLang = ref(props.language)
let themeLink: HTMLLinkElement | null = null

const loadTheme = (dark: boolean) => {
  const themeName = dark ? DARK_THEME : LIGHT_THEME
  const themePath = `${themeName}.css`
  
  if (themeLink) {
    themeLink.remove()
    themeLink = null
  }
  
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = `/node_modules/highlight.js/styles/${themePath}`
  link.onload = () => nextTick(() => highlightAll())
  link.onerror = () => console.error('加载主题失败:', themePath)
  
  document.head.appendChild(link)
  themeLink = link
}

const highlighted = computed(() => {
  try {
    const result = hljs.highlight(props.modelValue, { language: currentLang.value })
    return result.value
  } catch {
    return props.modelValue
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
  }
})

const highlightAll = () => {
  document.querySelectorAll('.hljs-code-block .code-display code:not(.hljs-processed)').forEach((block) => {
    hljs.highlightElement(block as HTMLElement)
  })
}

const startEdit = () => {
  if (!props.editable) return
  isEditing.value = true
  nextTick(() => editRef.value?.focus())
}

const onInput = () => {
  if (editRef.value) {
    const code = editRef.value.querySelector('code')
    if (code) {
      emit('update:modelValue', code.textContent || '')
    }
  }
}

const onBlur = () => {
  isEditing.value = false
}

const onLangChange = () => {
  isEditing.value = false
}

watch(() => props.language, (lang) => {
  currentLang.value = lang
})

watch(isDark, (dark) => {
  loadTheme(dark)
})

onMounted(() => {
  loadTheme(isDark.value)
  
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    isDark.value = e.matches
  })
})
</script>

<style scoped>
.hljs-code-block {
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
  font-size: 14px;
}

.hljs-code-block.is-editable .code-header {
  background: #f5f5f5;
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
}

.hljs-code-block.is-editable .code-header select {
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
}

.code-wrapper {
  position: relative;
}

.code-wrapper pre {
  margin: 0;
  padding: 16px;
  min-height: 100px;
  background: #282c34;
}

.code-wrapper code {
  display: block;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.code-editor {
  color: #abb2bf;
  background: #282c34;
}

.code-editor code {
  background: transparent;
}

.code-display {
  background: #282c34;
}

.code-display.clickable {
  cursor: pointer;
}

.code-display.clickable:hover {
  filter: brightness(1.1);
}

.code-display code {
  background: transparent;
  pointer-events: none;
}
</style>
