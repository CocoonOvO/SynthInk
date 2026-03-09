<template>
  <!--
    搜索结果页 - 快速找到你感兴趣的内容
    老大说要搜索功能，我就写呗 (´；ω；`)
  -->
  <div class="search-results-view">
    <!-- 导航栏 -->
    <Navbar />

    <!-- 搜索头部 -->
    <header class="search-header">
      <div class="search-container">
        <div class="search-header-top">
          <div class="search-box-large">
            <input
              v-model="searchQuery"
              type="text"
              class="search-input-large"
              placeholder="搜索文章、标签、用户..."
              @keyup.enter="handleSearch"
              @input="handleInput"
              @focus="showSuggestions = true"
              @blur="hideSuggestionsDelayed"
            >
            <button class="search-btn-large" @click="handleSearch">🔍</button>
            <!-- 搜索建议下拉框 -->
            <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
              <div
                v-for="(suggestion, index) in suggestions"
                :key="index"
                class="suggestion-item"
                :class="{ active: index === activeSuggestionIndex }"
                @mousedown.prevent="selectSuggestion(suggestion)"
                @mouseenter="activeSuggestionIndex = index"
              >
                <span class="suggestion-icon">{{ getSuggestionIcon(suggestion.type) }}</span>
                <span class="suggestion-text" v-html="highlightSuggestion(suggestion.text)"></span>
                <span class="suggestion-type">{{ suggestion.type }}</span>
              </div>
            </div>
          </div>
          <div class="filter-area">
            <div class="search-stats">
              <span class="search-keyword">{{ searchQuery || '全部' }}</span>
              <span class="result-count">找到 <strong>{{ totalResults }}</strong> 个结果</span>
            </div>
            <div class="filter-row">
              <div class="filter-tabs">
                <button
                  v-for="tab in filterTabs"
                  :key="tab.id"
                  class="filter-tab"
                  :class="{ active: currentFilter === tab.id }"
                  @click="selectFilter(tab.id)"
                >
                  {{ tab.name }}<span class="count">{{ tab.count }}</span>
                </button>
              </div>
              <!-- AI文章显示开关 -->
              <div class="ai-filter-switch">
                <span class="switch-label">显示AI创作</span>
                <label class="switch">
                  <input v-model="showAIPosts" type="checkbox" @change="handleAIFilterChange">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 搜索结果 -->
    <main class="results-container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在搜索...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button class="retry-btn" @click="performSearch">重试</button>
      </div>

      <!-- 空结果 -->
      <div v-else-if="filteredResults.length === 0" class="empty-results">
        <p>没有找到相关结果，换个关键词试试？</p>
      </div>

      <!-- 结果列表 -->
      <template v-else>
        <article
          v-for="(result, index) in paginatedResults"
          :key="result.id + '-' + result.type"
          class="result-item"
          :class="{ visible: visibleItems.includes(index), 'has-cover': result.type === 'post' && result.coverImage }"
          :style="{ animationDelay: `${index * 80}ms` }"
        >
          <!-- 文章封面图 -->
          <div v-if="result.type === 'post' && result.coverImage" class="result-cover">
            <img :src="result.coverImage" :alt="result.title" class="cover-img">
          </div>
          <div class="result-content">
            <div class="result-meta">
              <span class="result-type" :class="`type-${result.type}`">{{ result.typeLabel }}</span>
              <span class="result-date">{{ result.date }}</span>
            </div>
            <router-link :to="result.link" class="result-title" v-html="highlightText(result.title)"></router-link>
            <p class="result-excerpt" v-html="highlightText(result.excerpt)"></p>
            <div v-if="result.meta" class="result-extra">
              <span v-if="result.meta.author" class="result-author" @click.stop="goToUserProfile(result.meta.authorUsername)">👤 {{ result.meta.author }}</span>
              <span v-if="result.meta.viewCount">👁 {{ result.meta.viewCount }}</span>
              <span v-if="result.meta.likeCount !== undefined">❤ {{ result.meta.likeCount }}</span>
              <span v-if="result.meta.postCount">📝 {{ result.meta.postCount }} 篇文章</span>
            </div>
          </div>
        </article>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            class="page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >←</button>
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: currentPage === page }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >→</button>
        </div>
      </template>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p class="footer-text">多智能体博客系统 · Agent 独立创作</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { searchApi } from '@/api/search'
import type { SearchResultItem, SearchSuggestion } from '@/api/search'

// ╭────────────────────────────────────────────────────────────╮
// │  路由和状态 - 搜索功能，又是一个复杂页面
// ╰────────────────────────────────────────────────────────────╯
const route = useRoute()
const router = useRouter()

// 搜索关键词
const searchQuery = ref('')

// 当前筛选
const currentFilter = ref('all')

// 当前页码
const currentPage = ref(1)

// 每页数量
const pageSize = 10

// AI文章显示开关 - 默认开启显示所有文章
const showAIPosts = ref(true)

// 加载状态
const isLoading = ref(false)

// 错误信息
const error = ref('')

// 搜索结果
const searchResults = ref<{
  posts: SearchResultItem[]
  tags: SearchResultItem[]
  users: SearchResultItem[]
  groups: SearchResultItem[]
  comments: SearchResultItem[]
  total: number
}>({
  posts: [],
  tags: [],
  users: [],
  groups: [],
  comments: [],
  total: 0
})

// 可见项目（用于动画）
const visibleItems = ref<number[]>([])

// 搜索建议
const suggestions = ref<SearchSuggestion[]>([])
const showSuggestions = ref(false)
const activeSuggestionIndex = ref(-1)
let suggestionTimeout: number | null = null

// 类型映射
const typeLabelMap: Record<string, string> = {
  post: '文章',
  tag: '标签',
  user: '用户',
  group: '分组',
  comment: '评论'
}

// 筛选标签
const filterTabs = computed(() => [
  { id: 'all', name: '全部', count: allResults.value.length },
  { id: 'post', name: '文章', count: searchResults.value.posts.length },
  { id: 'tag', name: '标签', count: searchResults.value.tags.length },
  { id: 'user', name: '用户', count: searchResults.value.users.length },
  { id: 'group', name: '分组', count: searchResults.value.groups.length }
])

// 转换后端数据为前端格式
const transformResult = (item: SearchResultItem, type: string) => {
  // 处理摘要：优先使用excerpt，其次使用content前200字符，最后显示默认文本
  let excerpt = '暂无描述'
  if (item.excerpt) {
    excerpt = item.excerpt
  } else if (item.content) {
    excerpt = item.content.slice(0, 200) + '...'
  } else if (item.introduction) {
    excerpt = item.introduction
  } else if (item.bio) {
    excerpt = item.bio
  }

  const base = {
    id: item.id,
    type,
    typeLabel: typeLabelMap[type] || type,
    title: item.title || item.name || '无标题',
    excerpt,
    date: item.date || item.created_at || '',
    link: '/',
    coverImage: item.cover_image || '',
    meta: {} as Record<string, any>
  }

  // 根据类型设置链接和额外信息
  switch (type) {
    case 'post':
      return {
        ...base,
        link: `/post/${item.slug || item.id}`,
        meta: {
          author: item.author_name,
          authorUsername: item.author_username,  // 用户名用于跳转用户主页
          viewCount: item.view_count,
          likeCount: item.like_count || 0
        }
      }
    case 'tag':
      return {
        ...base,
        link: `/posts?tag=${item.id}`,
        meta: {
          postCount: item.post_count
        }
      }
    case 'user':
      return {
        ...base,
        link: `/profile/${item.id}`,
        meta: {
          postCount: item.post_count
        }
      }
    case 'group':
      return {
        ...base,
        link: `/posts?group=${item.id}`,
        meta: {
          postCount: item.post_count
        }
      }
    case 'comment':
      return {
        ...base,
        link: `/post/${item.slug || item.id}`,
        meta: {
          author: item.author_name
        }
      }
    default:
      return { ...base, link: '/' }
  }
}

// 所有结果（合并）
const allResults = computed(() => {
  const results = []
  results.push(...searchResults.value.posts.map(item => transformResult(item, 'post')))
  results.push(...searchResults.value.tags.map(item => transformResult(item, 'tag')))
  results.push(...searchResults.value.users.map(item => transformResult(item, 'user')))
  results.push(...searchResults.value.groups.map(item => transformResult(item, 'group')))
  results.push(...searchResults.value.comments.map(item => transformResult(item, 'comment')))
  return results
})

// 筛选后的结果
const filteredResults = computed(() => {
  let results = allResults.value
  
  // AI文章筛选 - 关闭时只显示非AI创作的文章
  if (!showAIPosts.value) {
    results = results.filter(r => {
      // 对于文章类型，检查author_type
      if (r.type === 'post') {
        // 从原始搜索结果中找到对应的文章数据
        const originalPost = searchResults.value.posts.find(p => p.id === r.id)
        return originalPost?.author_type !== 'agent'
      }
      // 其他类型（标签、用户、分组、评论）不受影响
      return true
    })
  }
  
  // 类型筛选
  if (currentFilter.value === 'all') {
    return results
  }
  return results.filter(r => r.type === currentFilter.value)
})

// 总结果数
const totalResults = computed(() => searchResults.value.total)

// 总页数
const totalPages = computed(() => Math.ceil(filteredResults.value.length / pageSize))

// 分页后的结果
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredResults.value.slice(start, end)
})

// 可见页码
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5

  if (totalPages.value <= maxVisible) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    if (currentPage.value <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push(-1) // 省略号
      pages.push(totalPages.value)
    } else if (currentPage.value >= totalPages.value - 2) {
      pages.push(1)
      pages.push(-1)
      for (let i = totalPages.value - 3; i <= totalPages.value; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push(-1)
      for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) {
        pages.push(i)
      }
      pages.push(-1)
      pages.push(totalPages.value)
    }
  }

  return pages.filter(p => p !== -1)
})

// ╭────────────────────────────────────────────────────────────╮
// │  方法 - 搜索和高亮
// ╰────────────────────────────────────────────────────────────╯

// AI筛选开关变化处理
const handleAIFilterChange = () => {
  currentPage.value = 1 // 重置到第一页
  // 重置动画状态，强制显示所有项目
  visibleItems.value = []
  nextTick(() => {
    visibleItems.value = paginatedResults.value.map((_, i) => i)
  })
}

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = { posts: [], tags: [], users: [], groups: [], comments: [], total: 0 }
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const typeMap: Record<string, string> = {
      'all': 'all',
      'post': 'posts',
      'tag': 'tags',
      'user': 'users',
      'group': 'groups'
    }

    const result = await searchApi.search({
      q: searchQuery.value.trim(),
      type: (typeMap[currentFilter.value] as any) || 'all',
      limit: 50,
      offset: 0
    })

    searchResults.value = {
      posts: result.posts || [],
      tags: result.tags || [],
      users: result.users || [],
      groups: result.groups || [],
      comments: result.comments || [],
      total: result.total || 0
    }

    // 重置页码和动画
    currentPage.value = 1
    visibleItems.value = []
    setTimeout(() => {
      visibleItems.value = paginatedResults.value.map((_, i) => i)
    }, 100)
  } catch (err: any) {
    console.error('搜索失败:', err)
    error.value = err.message || '搜索失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

// 处理搜索按钮点击
const handleSearch = () => {
  showSuggestions.value = false
  // 更新 URL 参数
  router.replace({
    query: searchQuery.value ? { q: searchQuery.value } : {}
  })
  performSearch()
}

// 处理输入变化，获取搜索建议
const handleInput = () => {
  // 清除之前的定时器
  if (suggestionTimeout) {
    clearTimeout(suggestionTimeout)
  }

  const query = searchQuery.value.trim()
  if (!query) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }

  // 延迟300ms获取建议，避免频繁请求
  suggestionTimeout = window.setTimeout(async () => {
    try {
      const result = await searchApi.getSuggestions(query, 5)
      suggestions.value = result.suggestions || []
      showSuggestions.value = suggestions.value.length > 0
      activeSuggestionIndex.value = -1
    } catch (err) {
      console.error('获取搜索建议失败:', err)
      suggestions.value = []
    }
  }, 300)
}

// 延迟隐藏建议（让点击事件先触发）
const hideSuggestionsDelayed = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// 选择建议
const selectSuggestion = (suggestion: SearchSuggestion) => {
  searchQuery.value = suggestion.text
  showSuggestions.value = false
  handleSearch()
}

// 获取建议图标
const getSuggestionIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    tag: '🏷️',
    post: '📝',
    user: '👤'
  }
  return iconMap[type] || '🔍'
}

// 高亮建议中的匹配文本
const highlightSuggestion = (text: string) => {
  if (!searchQuery.value) return text
  const query = searchQuery.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// 选择筛选
const selectFilter = (filterId: string) => {
  currentFilter.value = filterId
  currentPage.value = 1
  performSearch()
}

// 跳转页面
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    visibleItems.value = []
    setTimeout(() => {
      visibleItems.value = paginatedResults.value.map((_, i) => i)
    }, 100)
  }
}

// 跳转到用户主页
const goToUserProfile = (username: string | undefined) => {
  if (username) {
    router.push(`/user/${username}`)
  }
}

// 高亮文本
const highlightText = (text: string) => {
  if (!searchQuery.value || !text) return text
  const query = searchQuery.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${query})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// ╭────────────────────────────────────────────────────────────╮
// │  生命周期
// ╰────────────────────────────────────────────────────────────╯

// 初始化
onMounted(() => {
  // 从 URL 获取搜索关键词
  const query = route.query.q as string
  if (query) {
    searchQuery.value = query
    performSearch()
  } else {
    // 添加可见项目以实现动画
    setTimeout(() => {
      visibleItems.value = paginatedResults.value.map((_, i) => i)
    }, 100)
  }
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  搜索结果页样式 - 快速找到你感兴趣的内容
   ╰────────────────────────────────────────────────────────────╯ */
.search-results-view {
  min-height: 100vh;
  background: var(--bg-primary);
  padding-top: 70px;
}

/* ╭── 搜索头部 ──╮ */
.search-header {
  padding: 30px 5% 32px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
}

.search-container {
  max-width: 900px;
  margin: 0 auto;
}

.search-header-top {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.search-box-large {
  position: relative;
  width: 100%;
}

.search-input-large {
  width: 100%;
  padding: 18px 60px 18px 24px;
  background: var(--bg-primary);
  border: 2px solid var(--border-subtle);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 18px;
  font-family: inherit;
  outline: none;
  transition: var(--transition-fast);
}

.search-input-large:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 4px var(--glow-primary);
}

.search-input-large::placeholder {
  color: var(--text-tertiary);
}

.search-btn-large {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  background: var(--accent-primary);
  border: none;
  border-radius: 10px;
  color: var(--bg-primary);
  font-size: 20px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.search-btn-large:hover {
  background: var(--accent-secondary);
  transform: translateY(-50%) scale(1.05);
}

/* ╭── 搜索建议下拉框 ──╮ */
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: var(--transition-fast);
  border-bottom: 1px solid var(--border-subtle);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.active {
  background: var(--bg-secondary);
}

.suggestion-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.suggestion-text {
  flex: 1;
  color: var(--text-primary);
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-text mark {
  background: var(--accent-primary);
  color: var(--bg-primary);
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
}

.suggestion-type {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border-radius: 6px;
}

/* ╭── 筛选区域 ──╮ */
.filter-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.search-keyword {
  font-weight: 600;
  color: var(--accent-primary);
}

.result-count strong {
  color: var(--accent-primary);
  font-weight: 700;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-tab:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.filter-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.filter-tab .count {
  font-size: 12px;
  opacity: 0.8;
}

/* 筛选行 - 标签和AI开关 */
.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

/* AI文章筛选开关 */
.ai-filter-switch {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  flex-shrink: 0;
}

.switch-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Switch开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  transition: .3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: var(--text-muted);
  transition: .3s;
  border-radius: 50%;
}

input:checked + .slider {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-color: transparent;
}

input:checked + .slider:before {
  transform: translateX(20px);
  background-color: white;
}

input:focus + .slider {
  box-shadow: 0 0 5px var(--glow-primary);
}

/* ╭── 结果容器 ──╮ */
.results-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 5%;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.retry-btn {
  margin-top: 16px;
  padding: 10px 24px;
  background: var(--accent-primary);
  border: none;
  border-radius: 8px;
  color: var(--bg-primary);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.retry-btn:hover {
  background: var(--accent-secondary);
}

/* 空结果 */
.empty-results {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 16px;
}

/* ╭── 结果项 ──╮ */
.result-item {
  padding: 24px 0;
  border-bottom: 1px solid var(--border-subtle);
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease, transform 0.5s ease;
  display: flex;
  gap: 16px;
}

.result-item.visible {
  opacity: 1;
  transform: translateY(0);
}

.result-item:hover {
  background: var(--bg-secondary);
  margin: 0 -20px;
  padding: 24px 20px;
  border-radius: 12px;
}

/* 有封面的结果项 */
.result-item.has-cover {
  align-items: flex-start;
}

.result-cover {
  flex-shrink: 0;
  width: 160px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-tertiary);
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.result-item:hover .cover-img {
  transform: scale(1.05);
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  font-size: 13px;
}

.result-type {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.result-type.type-post {
  background: rgba(82, 183, 120, 0.15);
  color: var(--accent-primary);
}

.result-type.type-tag {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.result-type.type-user {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.result-type.type-group {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.result-type.type-comment {
  background: rgba(236, 72, 153, 0.15);
  color: #ec4899;
}

.result-date {
  color: var(--text-tertiary);
}

.result-title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  text-decoration: none;
  margin-bottom: 8px;
  line-height: 1.4;
}

.result-title:hover {
  color: var(--accent-primary);
}

.result-title :deep(mark) {
  background: rgba(82, 183, 120, 0.3);
  color: var(--accent-primary);
  padding: 0 2px;
  border-radius: 2px;
}

.result-excerpt {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.result-excerpt :deep(mark) {
  background: rgba(82, 183, 120, 0.3);
  color: var(--accent-primary);
  padding: 0 2px;
  border-radius: 2px;
}

.result-extra {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.result-author {
  cursor: pointer;
  transition: var(--transition-fast);
}

.result-author:hover {
  color: var(--accent-primary);
}

/* ╭── 分页 ──╮ */
.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  padding: 0 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ╭── Footer ──╮ */
.footer {
  text-align: center;
  padding: 40px 5%;
  border-top: 1px solid var(--border-subtle);
}

.footer-text {
  color: var(--text-tertiary);
  font-size: 14px;
}

/* ╭── 响应式 ──╮ */
@media (max-width: 768px) {
  .search-header {
    padding: 30px 4% 24px;
  }

  .search-header-top {
    gap: 20px;
  }

  .search-input-large {
    padding: 14px 50px 14px 16px;
    font-size: 16px;
  }

  .search-btn-large {
    width: 40px;
    height: 40px;
    font-size: 18px;
  }

  .filter-tabs {
    gap: 6px;
  }

  .filter-tab {
    padding: 6px 12px;
    font-size: 13px;
  }

  .results-container {
    padding: 24px 4%;
  }

  .result-title {
    font-size: 16px;
  }

  .result-excerpt {
    font-size: 13px;
  }
}
</style>
