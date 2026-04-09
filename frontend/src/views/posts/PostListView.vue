<template>
  <!-- 
    文章列表页 - 知识的星图，每一篇文章都是一颗发光的星
    老大又让写页面，我的人生就像这个列表一样 endless...
  -->
  <div class="post-list-view">
    <!-- 页面标题区 -->
    <header class="page-header">
      <h1 class="page-title">文章列表</h1>
      <p class="page-subtitle">探索创作者们的精彩文章</p>
    </header>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <!-- 搜索行 - 左侧展开+AI开关，右侧搜索 -->
      <div class="filter-search-line">
        <div class="filter-left-group">
          <div class="filter-expand-hint" @click.stop="showFilters = !showFilters">
            <span class="hint-text">点击展开筛选</span>
            <span class="hint-arrow" :class="{ up: showFilters }">▼</span>
          </div>
          
          <!-- AI文章显示开关 -->
          <div class="ai-filter-switch compact" :title="showAIPosts ? '点击隐藏AI创作的文章' : '点击显示AI创作的文章'">
            <span class="switch-label">{{ showAIPosts ? '显示AI' : '隐藏AI' }}</span>
            <label class="switch small">
              <input v-model="showAIPosts" type="checkbox" @change="handleAIFilterChange">
              <span class="slider small"></span>
            </label>
          </div>
        </div>
        
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="搜索文章..."
            @input="handleSearch"
          >
        </div>
      </div>
      
      <!-- 展开的面板 -->
      <div v-show="showFilters" class="filter-panel">
        <!-- 分组行 -->
        <div class="filter-row">
          <!-- 分组 -->
          <div class="filter-section-compact flex-1">
            <span class="section-label">分组</span>
            <div class="filter-chips-scroll">
              <button
                v-for="group in groups"
                :key="group.id"
                class="filter-chip"
                :class="{ active: selectedGroup === group.id }"
                @click="selectGroup(group.id)"
              >
                {{ group.name }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- 标签 -->
        <div class="filter-section-compact">
          <span class="section-label">标签</span>
          <div class="filter-chips-scroll">
            <button
              v-for="tag in tags"
              :key="tag.id"
              class="filter-chip tag"
              :class="{ active: selectedTags.includes(tag.id) }"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 文章网格 -->
    <main class="content-area">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载文章中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="loadError" class="error-state">
        <p>{{ loadError }}</p>
        <button class="btn-primary" @click="loadData">重试</button>
      </div>

      <!-- 文章网格 -->
      <div v-else class="articles-grid">
        <article
          v-for="(article, index) in displayedArticles"
          :key="article.id"
          class="article-card"
          :class="{ visible: visibleCards.has(index) }"
          :data-index="index"
          @click="goToArticle(article)"
        >
          <div
            class="card-cover"
            :style="article.cover_image ? { backgroundImage: `url(${article.cover_image})` } : { background: getCoverGradient(index) }"
          >
            <span class="card-category">{{ article.group_name || '未分类' }}</span>
          </div>
          <div class="card-content">
            <div class="card-meta">
              <span class="card-date">{{ formatDate(article.created_at) }}</span>
              <span v-if="article.author_type === 'agent'" class="ai-badge">AI创作</span>
            </div>
            <h2 class="card-title">{{ article.title }}</h2>
            <p class="card-excerpt">{{ article.introduction || article.summary || (article.content ? article.content.slice(0, 100) + '...' : '') }}</p>
            <div class="card-footer">
              <div class="card-author" @click.stop="goToUserProfile(article.author_username)">
                <div class="author-avatar">
                  <img v-if="article.author_avatar" :src="article.author_avatar" class="author-avatar-img" alt="头像">
                  <span v-else>{{ article.author_name?.[0] || '?' }}</span>
                </div>
                <span class="author-name">{{ article.author_name || '未知作者' }}</span>
              </div>
              <div class="card-stats">
                <span class="stat-item">👁 {{ formatNumber(article.view_count || 0) }}</span>
                <span class="stat-item">❤ {{ article.like_count || 0 }}</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- 空状态 -->
      <div v-if="!isLoading && !loadError && displayedArticles.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p class="empty-text">没有找到匹配的文章</p>
        <button class="btn-primary" @click="clearFilters">清除筛选</button>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          ←
        </button>
        <button
          v-for="page in displayedPages"
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
        >
          →
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { postsApi, tagsApi, groupsApi } from '@/api'
import type { Post, Tag } from '@/types'
import type { Group } from '@/api/posts'

// 路由
const router = useRouter()
const route = useRoute()

// ╭────────────────────────────────────────────────────────────╮
// │  筛选状态管理 - 为什么总是我来做这些状态管理 (´；ω；`)
// ╰────────────────────────────────────────────────────────────╯
const selectedGroup = ref<string>('')  // 改为string类型，存储group_id
const selectedTags = ref<number[]>([])
const searchQuery = ref('')
const showFilters = ref(false)
const currentPage = ref(1)
const pageSize = 9

// AI文章显示开关 - 默认开启显示所有文章
const showAIPosts = ref(true)

// API数据
const groups = ref<Group[]>([])
const tags = ref<Tag[]>([])
const articles = ref<Post[]>([])
const totalArticles = ref(0)
const isLoading = ref(false)
const loadError = ref('')

// 存储原始搜索结果，用于前端筛选
const searchResults = ref<any[]>([])

// 存储原始文章列表（用于AI筛选时恢复数据）
const rawArticles = ref<any[]>([])
const rawTotal = ref(0)

// 从API加载数据
const loadData = async () => {
  isLoading.value = true
  loadError.value = ''

  try {
    // 先加载分组和标签数据（如果还没有加载）
    if (groups.value.length === 0) {
      const [groupsRes, tagsRes] = await Promise.all([
        groupsApi.getList(),
        tagsApi.getList()
      ])
      groups.value = [{ id: '', name: '全部', description: '所有文章' }, ...groupsRes]
      tags.value = tagsRes
      
      // 如果从URL读取的是分组名称，现在转换为ID
      if (selectedGroup.value) {
        const groupByName = groups.value.find((g: Group) => g.name === selectedGroup.value)
        if (groupByName) {
          selectedGroup.value = String(groupByName.id)
        }
      }
    }

    // 如果有搜索关键词，使用搜索接口
    if (searchQuery.value.trim()) {
      await searchArticles()
      return
    }

    // 构建查询参数
    const params: any = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      status: 'published'
    }

    // 添加分组筛选
    if (selectedGroup.value) {
      params.group_id = selectedGroup.value
    }

    // 添加标签筛选 - 后端用tag参数（标签名），不是tag_id
    if (selectedTags.value.length > 0) {
      const tagName = getTagName(selectedTags.value[0])
      if (tagName) {
        params.tag = tagName // 后端用tag参数（标签名）
      }
    }

    // 加载文章列表（分组和标签已在上面的代码中加载）
    const postsRes = await postsApi.getList(params)

    // 后端返回 {items: [...], total: N} 格式
    const loadedArticles = postsRes.items || []
    const loadedTotal = postsRes.total || 0
    
    // 保存原始数据
    rawArticles.value = loadedArticles
    rawTotal.value = loadedTotal
    
    // 应用AI筛选
    applyAIFilter()
    
    // 清空搜索结果缓存
    searchResults.value = []
  } catch (error) {
    console.error('加载数据失败:', error)
    loadError.value = '加载数据失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

// 搜索文章 - 使用搜索接口
const searchArticles = async () => {
  try {
    const { searchApi } = await import('@/api/search')
    // 搜索时获取更多结果，用于前端筛选
    const result = await searchApi.search({
      q: searchQuery.value.trim(),
      type: 'posts',
      offset: 0, // 获取所有结果用于前端筛选
      limit: 100 // 获取更多结果
    })
    
    // 搜索返回的是SearchResult格式，直接使用posts数组
    const postResults = result.posts || []
    const mappedResults = postResults.map(r => ({
      id: r.id,
      title: r.title,
      slug: r.slug,
      introduction: r.excerpt || r.introduction,
      cover_image: r.cover_image,
      group_name: r.group_name,
      author_name: r.author_name,
      author_username: r.author_username,  // 用户名用于跳转用户主页
      author_avatar: r.author_avatar,
      author_type: r.author_type || 'user',
      view_count: r.view_count,
      like_count: r.like_count || 0,
      created_at: r.date || r.created_at
    })) as Post[]
    
    // 保存原始搜索结果
    searchResults.value = mappedResults
    
    // 应用前端筛选
    applyFilters()
  } catch (error) {
    console.error('搜索失败:', error)
    loadError.value = '搜索失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

// 应用前端筛选（用于搜索结果的分组和标签筛选）
const applyFilters = () => {
  let filtered = [...searchResults.value]
  
  // AI文章筛选 - 关闭时只显示非AI创作的文章
  if (!showAIPosts.value) {
    filtered = filtered.filter(post => post.author_type !== 'agent')
  }
  
  // 分组筛选 - 使用group_id而不是group_name
  if (selectedGroup.value) {
    // 注意：搜索结果中只有group_name，没有group_id
    // 需要通过group_name找到对应的group_id
    const selectedGroupData = groups.value.find((g: Group) => g.id === selectedGroup.value)
    if (selectedGroupData) {
      filtered = filtered.filter(post => post.group_name === selectedGroupData.name)
    }
  }
  
  // 标签筛选 - 搜索接口返回的文章需要检查标签
  // 注意：搜索结果可能没有tags字段，这里简化处理
  // 如果需要完整支持，需要后端搜索接口返回tags字段
  
  // 分页
  totalArticles.value = filtered.length
  const start = (currentPage.value - 1) * pageSize
  articles.value = filtered.slice(start, start + pageSize)
  console.log('筛选后文章数:', filtered.length)
}

// ╭────────────────────────────────────────────────────────────╮
// │  计算属性 - 筛选和分页逻辑，每天都在写这种重复代码
// ╰────────────────────────────────────────────────────────────╯

// 搜索框占位符
const filterPlaceholder = computed(() => {
  if (selectedGroup.value && selectedTags.value.length > 0) {
    return `分组: ${getGroupName(selectedGroup.value)} + ${selectedTags.value.length}个标签`
  } else if (selectedGroup.value) {
    return `分组: ${getGroupName(selectedGroup.value)}`
  } else if (selectedTags.value.length > 0) {
    return `已选 ${selectedTags.value.length} 个标签`
  }
  return '搜索文章...'
})

// 当前页显示的文章（直接使用API返回的数据）
const displayedArticles = computed(() => articles.value)

// 总页数
const totalPages = computed(() =>
  Math.ceil(totalArticles.value / pageSize)
)

// 分页按钮显示
const displayedPages = computed(() => {
  const pages: number[] = []
  const maxButtons = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxButtons / 2))
  let end = Math.min(totalPages.value, start + maxButtons - 1)

  if (end - start < maxButtons - 1) {
    start = Math.max(1, end - maxButtons + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// ╭────────────────────────────────────────────────────────────╮
// │  方法 - 各种事件处理，点来点去的人生
// ╰────────────────────────────────────────────────────────────╯

// AI筛选开关变化处理
const handleAIFilterChange = () => {
  currentPage.value = 1 // 重置到第一页
  // 如果有搜索结果，使用前端筛选
  if (searchQuery.value.trim() && searchResults.value.length > 0) {
    applyFilters()
  } else {
    // 对于普通列表，应用AI筛选
    applyAIFilter()
  }
}

// 应用AI筛选（从原始数据中筛选）
const applyAIFilter = () => {
  if (!showAIPosts.value) {
    // 关闭时过滤掉AI创作的文章
    articles.value = rawArticles.value.filter(post => post.author_type !== 'agent')
    totalArticles.value = articles.value.length
  } else {
    // 开启时显示所有文章（使用展开运算符创建新数组，保持响应式）
    articles.value = [...rawArticles.value]
    totalArticles.value = rawTotal.value
  }
  
  // 强制显示所有卡片（避免IntersectionObserver延迟导致卡片不可见）
  nextTick(() => {
    const cards = document.querySelectorAll('.article-card')
    cards.forEach((card, index) => {
      visibleCards.value.add(index)
      observer?.observe(card)
    })
  })
}

// 选择分组
const selectGroup = (groupId: string) => {
  selectedGroup.value = groupId
  currentPage.value = 1 // 重置到第一页
  updateUrlQuery() // 更新URL
  // 如果有搜索结果，使用前端筛选；否则重新加载数据
  if (searchQuery.value.trim() && searchResults.value.length > 0) {
    applyFilters()
  } else {
    loadData() // 重新加载数据
  }
}

// 切换标签
const toggleTag = (tagId: number) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagId)
  }
  currentPage.value = 1 // 重置到第一页
  updateUrlQuery() // 更新URL
  // 如果有搜索结果，使用前端筛选；否则重新加载数据
  if (searchQuery.value.trim() && searchResults.value.length > 0) {
    applyFilters()
  } else {
    loadData() // 重新加载数据
  }
}

// 获取分组名称
const getGroupName = (groupId: string) => {
  const group = groups.value.find((g: Group) => g.id === groupId)
  return group?.name || groupId
}

// 获取标签名称
const getTagName = (tagId: number | undefined) => {
  if (tagId === undefined) return ''
  const tag = tags.value.find(t => t.id === tagId)
  return tag?.name || String(tagId)
}

// 清除筛选
const clearFilters = () => {
  selectedGroup.value = ''
  selectedTags.value = []
  searchQuery.value = ''
  currentPage.value = 1
  // 清除URL参数
  router.replace({ query: {} })
  loadData()
}

// 更新URL参数
const updateUrlQuery = () => {
  const query: Record<string, string> = {}
  
  if (searchQuery.value.trim()) {
    query.q = searchQuery.value.trim()
  }
  
  // URL中显示分组名称而不是ID
  if (selectedGroup.value) {
    const groupName = getGroupName(selectedGroup.value)
    if (groupName) {
      query.group = encodeURIComponent(groupName)
    }
  }
  
  if (selectedTags.value.length > 0) {
    query.tags = selectedTags.value.join(',')
  }
  
  if (currentPage.value > 1) {
    query.page = String(currentPage.value)
  }
  
  router.replace({ query })
}

// 从URL读取参数
const initFromUrl = () => {
  const { q, group, tags, page } = route.query
  
  if (q && typeof q === 'string') {
    searchQuery.value = q
  }
  
  // 从URL读取分组名称，然后通过名称找到对应的ID
  if (group && typeof group === 'string') {
    const groupName = decodeURIComponent(group)
    // 先保存分组名称，等分组数据加载后再查找对应的ID
    // 这里使用一个特殊的标记，在分组数据加载后处理
    selectedGroup.value = groupName
  }
  
  if (tags && typeof tags === 'string') {
    selectedTags.value = tags.split(',').map(id => parseInt(id, 10)).filter(id => !isNaN(id))
  }
  
  if (page && typeof page === 'string') {
    currentPage.value = parseInt(page, 10) || 1
  }
}

// 搜索处理
let searchTimeout: number | null = null
const handleSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = window.setTimeout(() => {
    currentPage.value = 1
    updateUrlQuery() // 更新URL
    loadData() // 重新加载数据
  }, 300)
}

// 跳转到文章详情（优先使用slug）
const goToArticle = (article: any) => {
  const slug = article.slug || article.id
  router.push(`/post/${slug}`)
}

// 跳转到用户主页
const goToUserProfile = (username: string | undefined) => {
  if (username) {
    router.push(`/user/${username}`)
  }
}

// 分页跳转
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    updateUrlQuery() // 更新URL
    // 如果有搜索结果，使用前端筛选分页；否则重新加载数据
    if (searchQuery.value.trim() && searchResults.value.length > 0) {
      applyFilters()
    } else {
      loadData()
    }
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 格式化日期
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

// 获取封面渐变（根据索引循环使用）
const gradients = [
  'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
  'linear-gradient(135deg, #ff6b6b, #feca57)',
  'linear-gradient(135deg, #a29bfe, #6c5ce7)',
  'linear-gradient(135deg, #00b894, #00cec9)',
  'linear-gradient(135deg, #fd79a8, #e84393)',
  'linear-gradient(135deg, #74b9ff, #0984e3)',
  'linear-gradient(135deg, #a8e6cf, #88d8b0)',
  'linear-gradient(135deg, #ffeaa7, #fdcb6e)',
  'linear-gradient(135deg, #dfe6e9, #b2bec3)'
]
const getCoverGradient = (index: number): string => {
  const gradientIndex = index % gradients.length
  return gradients[gradientIndex] ?? gradients[0]!
}

// ╭────────────────────────────────────────────────────────────╮
// │  滚动动画 - Intersection Observer，又是你
// ╰────────────────────────────────────────────────────────────╯
const visibleCards = ref(new Set<number>())
let observer: IntersectionObserver | null = null

onMounted(async () => {
  // 从URL读取参数
  initFromUrl()
  
  // 加载数据
  await loadData()

  // 初始化 Intersection Observer
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const index = parseInt(entry.target.getAttribute('data-index') || '0')
          visibleCards.value.add(index)
        }
      })
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    }
  )

  // 观察所有文章卡片
  setTimeout(() => {
    const cards = document.querySelectorAll('.article-card')
    cards.forEach((card) => {
      observer?.observe(card)
    })
  }, 100)
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

// 监听文章列表变化，重新观察
watch(displayedArticles, () => {
  visibleCards.value.clear()
  setTimeout(() => {
    const cards = document.querySelectorAll('.article-card')
    cards.forEach((card) => {
      observer?.observe(card)
    })
  }, 100)
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  页面标题区 - 老大的需求总是这么具体
   ╰────────────────────────────────────────────────────────────╯ */
.page-header {
  padding: 30px 5% 20px;
  background: linear-gradient(180deg,
    var(--glow-primary) 0%,
    transparent 100%);
  border-bottom: 1px solid var(--border-subtle);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  筛选栏
   ╰────────────────────────────────────────────────────────────╯ */
.filter-bar {
  padding: 12px 5%;
  border-bottom: 1px solid var(--border-subtle);
}

/* 搜索行 */
.filter-search-line {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.filter-search-line .search-box {
  width: 200px;
  flex-shrink: 0;
  margin-left: auto;
}

/* 左侧组 - 筛选提示 + AI开关 */
.filter-left-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 搜索行中的AI筛选开关 - 紧凑版 */
.filter-search-line .ai-filter-switch.compact {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
}

.filter-search-line .ai-filter-switch.compact .switch-label {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* 小型switch开关 */
.switch.small {
  width: 28px;
  height: 16px;
}

.switch.small .slider.small {
  border-radius: 16px;
}

.switch.small .slider.small:before {
  height: 12px;
  width: 12px;
  left: 2px;
  bottom: 2px;
}

.switch.small input:checked + .slider.small:before {
  transform: translateX(12px);
}

/* 展开筛选提示 - 左侧 */
.filter-expand-hint {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 0;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 13px;
  transition: var(--transition-fast);
}

.filter-expand-hint:hover {
  color: var(--accent-primary);
}

.hint-arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

.hint-arrow.up {
  transform: rotate(180deg);
}

.clear-filters {
  font-size: 12px;
  color: var(--accent-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 12px;
  white-space: nowrap;
  transition: var(--transition-fast);
}

.clear-filters:hover {
  text-shadow: 0 0 10px var(--glow-primary);
}

/* 展开面板 */
.filter-panel {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-section-compact {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 40px;
}

.filter-chips-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex: 1;
}

.filter-chips-scroll::-webkit-scrollbar {
  display: none;
}

/* Chip样式 */
.filter-chip {
  padding: 6px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition-fast);
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-chip:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.filter-chip.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.filter-chip.tag {
  border-radius: 20px;
  background: transparent;
  font-size: 12px;
  padding: 4px 12px;
  border-style: dashed;
}

.filter-chip.tag:hover {
  border-style: solid;
}

.filter-chip.tag.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-style: solid;
  border-color: transparent;
}

/* 已选标签 */
.active-filter-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.active-filter-tag .remove {
  cursor: pointer;
  opacity: 0.6;
  font-size: 14px;
  line-height: 1;
  transition: var(--transition-fast);
}

.active-filter-tag .remove:hover {
  opacity: 1;
  color: var(--accent-primary);
}

.clear-filters {
  font-size: 12px;
  color: var(--accent-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  transition: var(--transition-fast);
}

.clear-filters:hover {
  text-shadow: 0 0 10px var(--glow-primary);
}

/* 筛选行 - 分组和AI开关 */
.filter-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filter-row .flex-1 {
  flex: 1;
  min-width: 0;
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

/* 搜索框 */
.search-box-compact {
  position: relative;
  flex: 1;
  max-width: 300px;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 20px var(--glow-primary);
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

/* ╭────────────────────────────────────────────────────────────╮
   │  文章网格 - 知识的星图，每一篇都是一颗星
   ╰────────────────────────────────────────────────────────────╯ */
.content-area {
  padding: 40px 5%;
  max-width: 1400px;
  margin: 0 auto;
}

.articles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.article-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  overflow: hidden;
  transition: var(--transition-normal);
  cursor: pointer;
  opacity: 0;
  transform: translateY(20px);
}

.article-card.visible {
  opacity: 1;
  transform: translateY(0);
}

.article-card:hover {
  transform: translateY(-5px);
  border-color: var(--accent-primary);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px var(--glow-primary);
}

.card-cover {
  height: 180px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
}

.card-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, var(--bg-secondary) 100%);
}

.card-category {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--bg-primary);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.card-content {
  padding: 20px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.card-date {
  font-size: 13px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}

.ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border: 1px solid var(--glow-primary);
  border-radius: 4px;
  font-size: 11px;
  color: var(--accent-primary);
  font-family: var(--font-mono);
}

.ai-badge::before {
  content: '✦';
  font-size: 10px;
}

.card-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 12px;
  line-height: 1.4;
  transition: var(--transition-fast);
}

.article-card:hover .card-title {
  color: var(--accent-primary);
}

.card-excerpt {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}

.card-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-secondary), var(--accent-tertiary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--bg-primary);
  overflow: hidden;
}

.author-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.card-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  加载/错误/空状态 - 人生的三种状态
   ╰────────────────────────────────────────────────────────────╯ */
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-subtle);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.empty-state .btn-primary {
  padding: 10px 24px;
  background: var(--accent-primary);
  color: var(--bg-primary);
  border: none;
  border-radius: var(--button-radius);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.empty-state .btn-primary:hover {
  background: var(--accent-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--glow-primary);
}

/* ╭────────────────────────────────────────────────────────────╮
   │  分页 - 翻页翻页，翻到什么时候是个头
   ╰────────────────────────────────────────────────────────────╯ */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 40px 0;
}

.page-btn {
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.page-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-color: transparent;
  color: var(--bg-primary);
  font-weight: 600;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  响应式 - 手机党的福音
   ╰────────────────────────────────────────────────────────────╯ */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
  }

  .filter-row {
    flex-direction: column;
    gap: 12px;
  }

  .filter-label {
    min-width: auto;
    padding-top: 0;
  }

  .filter-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .articles-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-wrap: wrap;
  }
}

@media (prefers-reduced-motion: reduce) {
  .article-card {
    opacity: 1;
    transform: none;
  }
}
</style>
