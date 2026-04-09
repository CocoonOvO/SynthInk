<template>
  <div class="code-block-demo">
    <h3>Highlight.js Vue3 Demo</h3>
    <p class="theme-hint">根据系统主题自动切换：Atom One Dark / Atom One Light</p>
    
    <!-- 方式1: 使用 highlightjs/vue-plugin -->
    <div class="demo-section">
      <h4>方式1: highlightjs/vue-plugin</h4>
      <pre><code ref="code1Ref" class="language-javascript">{{ code1 }}</code></pre>
    </div>
    
    <!-- 方式2: 直接使用 highlight.js -->
    <div class="demo-section">
      <h4>方式2: 直接使用 highlight.js</h4>
      <pre><code ref="code2Ref" class="language-typescript">{{ code2 }}</code></pre>
    </div>
    
    <!-- 方式3: 可编辑代码块（模拟 Milkdown 场景） -->
    <div class="demo-section">
      <h4>方式3: 可编辑代码块（无抖动）</h4>
      <div class="editable-code-block">
        <div class="code-header">
          <select v-model="selectedLanguage" @change="onLanguageChange">
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
          </select>
        </div>
        <div class="code-wrapper">
          <!-- 编辑层：纯文本 -->
          <pre 
            v-show="isEditing"
            ref="editRef"
            class="code-editor"
            contenteditable="true"
            @input="onCodeInput"
            @blur="onCodeBlur"
          ><code :class="`language-${selectedLanguage}`">{{ editableCode }}</code></pre>
          <!-- 展示层：高亮代码 -->
          <pre 
            v-show="!isEditing"
            class="code-display"
            @click="startEditing"
          ><code :class="`language-${selectedLanguage}`" v-html="highlightedCode"></code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch } from 'vue'
import hljs from 'highlight.js'

const DARK_THEME = 'atom-one-dark'
const LIGHT_THEME = 'atom-one-light'
let themeLink: HTMLLinkElement | null = null

const isDark = ref(window.matchMedia('(prefers-color-scheme: dark)').matches)

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

const currentTheme = computed(() => isDark.value ? DARK_THEME : LIGHT_THEME)

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

// 方式1的代码
const code1 = `const greeting = "Hello";
const name = "World";
console.log(greeting, name);

function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// 箭头函数
const multiply = (a, b) => a * b;

// 异步函数
async function fetchData() {
  const response = await fetch('/api/data');
  return response.json();
}`

// 方式2的代码
const code2 = `interface User {
  id: number;
  name: string;
  email: string;
}

class UserService {
  private users: User[] = [];
  
  async getUser(id: number): Promise<User | undefined> {
    return this.users.find(u => u.id === id);
  }
  
  addUser(user: User): void {
    this.users.push(user);
  }
}

// 泛型示例
function identity<T>(arg: T): T {
  return arg;
}`

// 方式3的可编辑代码
const selectedLanguage = ref('javascript')
const editableCode = ref(`// 在这里输入代码...
function example() {
  return "Hello World";
}

// 试试看编辑这段代码
// 点击代码开始编辑，失焦后自动高亮`)
const isEditing = ref(false)
const editRef = ref<HTMLElement>()
const code1Ref = ref<HTMLElement>()
const code2Ref = ref<HTMLElement>()

// 计算高亮后的代码
const highlightedCode = computed(() => {
  // 使用 highlight.js 高亮
  const result = hljs.highlight(editableCode.value, { language: selectedLanguage.value })
  return result.value
})

// 高亮所有代码
const highlightAll = () => {
  if (code1Ref.value) {
    hljs.highlightElement(code1Ref.value)
  }
  if (code2Ref.value) {
    hljs.highlightElement(code2Ref.value)
  }
}

// 开始编辑
const startEditing = () => {
  isEditing.value = true
  // 聚焦到编辑区域
  nextTick(() => {
    editRef.value?.focus()
  })
}

// 输入时更新代码
const onCodeInput = () => {
  if (editRef.value) {
    const codeElement = editRef.value.querySelector('code')
    if (codeElement) {
      editableCode.value = codeElement.textContent || ''
    }
  }
}

// 失焦时切换回高亮模式
const onCodeBlur = () => {
  isEditing.value = false
}

// 语言切换时重新高亮
const onLanguageChange = () => {
  // 语言切换后保持展示模式
  isEditing.value = false
}
</script>

<style scoped>
.code-block-demo {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.theme-hint {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.demo-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.demo-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.editable-code-block {
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.code-header {
  background: #f5f5f5;
  padding: 8px 12px;
  border-bottom: 1px solid #ddd;
}

.code-header select {
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
  min-height: 150px;
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
  background: #1e1e1e;
  color: #d4d4d4;
}

.code-editor code {
  background: transparent;
}

.code-display {
  cursor: pointer;
  background: #282c34;
}

.code-display code {
  background: transparent;
  pointer-events: none;
}

.code-display:hover {
  filter: brightness(1.05);
}
</style>
