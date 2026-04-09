<template>
  <!--
    API测试页面 - 测试后端接口是否正常
    老大说要测试API，我就写个测试页面 (´；ω；`)
  -->
  <div class="api-test-view">
    <div class="test-container">
      <h1 class="test-title">🔧 API 接口测试</h1>
      
      <div class="test-actions">
        <button class="test-btn" @click="runAllTests" :disabled="isTesting">
          {{ isTesting ? '测试中...' : '运行全部测试' }}
        </button>
        <button class="test-btn secondary" @click="clearResults">
          清空结果
        </button>
      </div>

      <div class="test-summary" v-if="results.length > 0">
        <div class="summary-item">
          <span class="summary-label">总计:</span>
          <span class="summary-value">{{ results.length }}</span>
        </div>
        <div class="summary-item success">
          <span class="summary-label">通过:</span>
          <span class="summary-value">{{ successCount }}</span>
        </div>
        <div class="summary-item error">
          <span class="summary-label">失败:</span>
          <span class="summary-value">{{ failCount }}</span>
        </div>
      </div>

      <div class="test-results">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="test-result"
          :class="{ success: result.success, error: !result.success }"
        >
          <div class="result-header">
            <span class="result-status">{{ result.success ? '✅' : '❌' }}</span>
            <span class="result-name">{{ result.name }}</span>
            <span class="result-duration">{{ result.duration }}ms</span>
          </div>
          <div class="result-body" v-if="!result.success">
            <div class="result-error">{{ result.error }}</div>
          </div>
          <div class="result-body" v-else-if="showData">
            <pre class="result-data">{{ JSON.stringify(result.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { postsApi, tagsApi, groupsApi, commentsApi, likesApi } from '@/api'

// 测试结果类型
interface TestResult {
  name: string
  success: boolean
  data?: any
  error?: string
  duration: number
}

// 状态
const isTesting = ref(false)
const results = ref<TestResult[]>([])
const showData = ref(false)

// 计算属性
const successCount = computed(() => results.value.filter(r => r.success).length)
const failCount = computed(() => results.value.filter(r => !r.success).length)

// 测试包装函数
async function test<T>(name: string, fn: () => Promise<T>): Promise<void> {
  const start = Date.now()
  try {
    const data = await fn()
    results.value.push({
      name,
      success: true,
      data,
      duration: Date.now() - start
    })
  } catch (error: any) {
    results.value.push({
      name,
      success: false,
      error: error.message,
      duration: Date.now() - start
    })
  }
}

// 运行所有测试
async function runAllTests() {
  isTesting.value = true
  results.value = []

  // 1. 测试文章统计
  await test('获取文章统计', () => postsApi.getStats())

  // 2. 测试文章列表
  await test('获取文章列表', () => postsApi.getList({ limit: 5 }))

  // 3. 测试标签列表
  await test('获取标签列表', () => tagsApi.getList({ limit: 5 }))

  // 4. 测试分组列表
  await test('获取分组列表', () => groupsApi.getList({ limit: 5 }))

  // 5. 测试评论列表（需要传post_id）
  await test('获取评论列表', () => commentsApi.getList({ post_id: '1', limit: 5 }))

  // 6. 测试点赞状态
  await test('获取点赞状态', () => likesApi.getStatus(1))

  isTesting.value = false
}

// 清空结果
function clearResults() {
  results.value = []
}
</script>

<style scoped>
.api-test-view {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 40px 20px;
}

.test-container {
  max-width: 800px;
  margin: 0 auto;
}

.test-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 30px;
  text-align: center;
}

.test-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
}

.test-btn {
  padding: 12px 24px;
  border: 2px solid var(--accent-primary);
  background: var(--accent-primary);
  color: var(--bg-primary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.test-btn:hover:not(:disabled) {
  background: transparent;
  color: var(--accent-primary);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.test-btn.secondary {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-color);
}

.test-btn.secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.test-summary {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 30px;
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.summary-item.success .summary-value {
  color: #10b981;
}

.summary-item.error .summary-value {
  color: #ef4444;
}

.summary-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.test-result {
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  overflow: hidden;
}

.test-result.success {
  border-left: 4px solid #10b981;
}

.test-result.error {
  border-left: 4px solid #ef4444;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  cursor: pointer;
}

.result-status {
  font-size: 1.25rem;
}

.result-name {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
}

.result-duration {
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-family: monospace;
}

.result-body {
  padding: 0 20px 15px 55px;
  border-top: 1px solid var(--border-color);
  margin-top: -5px;
}

.result-error {
  color: #ef4444;
  font-size: 0.875rem;
  padding: 10px 0;
}

.result-data {
  background: var(--bg-primary);
  padding: 15px;
  margin: 10px 0 0;
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
