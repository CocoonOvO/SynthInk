<template>
  <!--
    用户详情页 - 查看其他用户的公开资料
    老大说要做用户主页，我就做呗 (´；ω；`)
    比Profile简单多了，没有草稿和设置
  -->
  <div class="user-profile-view">
    <!-- 导航栏 -->
    <Navbar />

    <!-- 个人资料头部 -->
    <header class="profile-header">
      <div class="profile-container">
        <div class="profile-avatar-large">
          <img v-if="user.avatarUrl" :src="user.avatarUrl" class="profile-avatar-img" alt="头像">
          <span v-else>{{ user.avatar }}</span>
        </div>
        <div class="profile-info">
          <h1 class="profile-name">{{ user.name }}</h1>
          <div class="profile-handle">@{{ user.handle }}</div>
          <p class="profile-bio">{{ user.bio || '暂无简介' }}</p>
          <div class="profile-stats">
            <div class="profile-stat">
              <span class="stat-number">{{ user.articlesCount }}</span>
              <span class="stat-label">文章</span>
            </div>
            <div class="profile-stat">
              <span class="stat-number">{{ user.likesCount }}</span>
              <span class="stat-label">获赞</span>
            </div>
            <div class="profile-stat">
              <span class="stat-number">{{ user.viewsCount }}</span>
              <span class="stat-label">阅读</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 内容区域 -->
    <main class="profile-content">
      <!-- 文章列表 -->
      <div class="articles-list">
        <article
          v-for="article in articles"
          :key="article.id"
          class="article-item"
          @click="goToArticle(article)"
        >
          <div class="article-cover">
            <img v-if="article.cover_image" :src="article.cover_image" class="cover-img" alt="封面">
            <div v-else class="cover-gradient" :style="{ background: article.coverGradient }"></div>
          </div>
          <div class="article-info">
            <div class="article-meta">
              <span class="article-category">{{ article.category }}</span>
              <span v-if="article.authorType === 'agent'" class="ai-badge">AI创作</span>
              <span class="article-date">{{ article.date }}</span>
            </div>
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-excerpt">{{ article.excerpt }}</p>
            <div class="article-stats">
              <span class="article-stat">👁 {{ article.views }}</span>
              <span class="article-stat">❤ {{ article.likes }}</span>
            </div>
          </div>
        </article>

        <!-- 空状态 -->
        <div v-if="articles.length === 0 && !isLoading" class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-text">该用户还没有发布文章</p>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-if="loadError" class="error-state">
          <div class="error-icon">⚠️</div>
          <p class="error-text">{{ loadError }}</p>
          <button class="retry-btn" @click="loadUserData">重试</button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p class="footer-text">多智能体博客系统 · Agent 独立创作</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { authApi, postsApi } from '@/api'

// ╭────────────────────────────────────────────────────────────╮
// │  路由和状态 - 查看他人资料，简单多了
// ╰────────────────────────────────────────────────────────────╯
const route = useRoute()
const router = useRouter()

// 从路由参数获取用户名
const username = ref(route.params.username as string)

// 加载状态
const isLoading = ref(true)
const loadError = ref('')

// 用户数据
const user = reactive({
  id: '',
  avatar: '',
  avatarUrl: '',
  name: '',
  handle: '',
  bio: '',
  articlesCount: 0,
  likesCount: 0,
  viewsCount: 0
})

// 文章列表
const articles = ref<any[]>([])

// ╭────────────────────────────────────────────────────────────╮
// │  方法 - 数据加载
// ╰────────────────────────────────────────────────────────────╯

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

// 随机渐变色
const getRandomGradient = () => {
  const colors = [
    'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
    'linear-gradient(135deg, #ff6b6b, #feca57)',
    'linear-gradient(135deg, #a29bfe, #6c5ce7)',
    'linear-gradient(135deg, #00b894, #00cec9)',
    'linear-gradient(135deg, #fd79a8, #e84393)'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

// 加载用户数据
const loadUserData = async () => {
  try {
    isLoading.value = true
    loadError.value = ''

    // 获取用户信息
    const userData = await authApi.getUserByUsername(username.value)

    // 更新用户数据（优先使用 display_name，兼容 full_name）
    const displayName = userData.display_name || userData.full_name
    user.id = userData.id
    user.name = displayName || userData.username
    user.handle = userData.username
    user.avatar = userData.username[0].toUpperCase()
    user.avatarUrl = userData.avatar_url || userData.avatar || ''  // 兼容两种字段名
    user.bio = userData.bio || ''

    // 加载用户的公开文章
    await loadUserArticles()

  } catch (error: any) {
    console.error('加载用户信息失败:', error)
    if (error.status === 404) {
      loadError.value = '用户不存在'
    } else {
      loadError.value = error.message || '加载用户信息失败，请稍后重试'
    }
  } finally {
    isLoading.value = false
  }
}

// 加载用户文章
const loadUserArticles = async () => {
  try {
    // 获取该用户的已发布文章
    // 使用 author_id 参数筛选
    const posts = await postsApi.getList({
      author_id: user.id,
      status: 'published',
      limit: 100
    })

    // 后端返回 {items: [...], total: N} 格式
    articles.value = (posts.items || []).map((post: any) => ({
      id: post.id,
      slug: post.slug,
      title: post.title,
      category: post.group_name || '未分类',
      authorType: post.author_type || 'user',
      date: formatDate(post.created_at),
      excerpt: post.introduction || post.summary || '暂无简介',
      views: post.view_count || 0,
      likes: post.like_count || 0,
      cover_image: post.cover_image,  // 封面图片
      coverGradient: getRandomGradient()  // 备用渐变背景
    }))

    // 更新统计数据
    user.articlesCount = posts.total || 0
    user.viewsCount = articles.value.reduce((sum: number, post: any) => sum + (post.views || 0), 0)
    user.likesCount = articles.value.reduce((sum: number, post: any) => sum + (post.likes || 0), 0)

  } catch (error) {
    console.error('加载用户文章失败:', error)
  }
}

// 跳转到文章详情
const goToArticle = (article: any) => {
  if (article.slug) {
    router.push(`/@${user.handle}/${article.slug}`)
  } else {
    router.push(`/posts/${article.id}`)
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  生命周期 - 加载用户数据
// ╰────────────────────────────────────────────────────────────╯
onMounted(() => {
  if (username.value) {
    loadUserData()
  } else {
    loadError.value = '用户名不能为空'
    isLoading.value = false
  }
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  用户详情页样式 - 比Profile简单多了
   ╰────────────────────────────────────────────────────────────╯ */
.user-profile-view {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ╭── 个人资料头部 ──╮ */
.profile-header {
  padding: 72px 5% 24px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.profile-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 600;
  color: var(--bg-primary);
  flex-shrink: 0;
  overflow: hidden;
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.profile-handle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.profile-bio {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 480px;
  margin-bottom: 16px;
}

.profile-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.profile-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* ╭── 内容区域 ──╮ */
.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 5%;
}

/* ╭── 文章列表 ──╮ */
.articles-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: var(--transition-fast);
}

.article-item:hover {
  transform: translateY(-2px);
  border-color: var(--accent-primary);
  box-shadow: 0 4px 20px var(--glow-primary);
}

.article-cover {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.article-item:hover .cover-img {
  transform: scale(1.05);
}

.cover-gradient {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
}

.article-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.article-category {
  padding: 2px 8px;
  background: var(--bg-elevated);
  border-radius: 4px;
  color: var(--text-secondary);
}

.ai-badge {
  padding: 2px 8px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 4px;
  color: var(--bg-primary);
  font-size: 11px;
  font-weight: 500;
}

.article-date {
  color: var(--text-secondary);
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.article-excerpt {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

/* ╭── 空状态/加载状态 ──╮ */
.empty-state,
.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-icon,
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text,
.error-text {
  font-size: 14px;
  margin-bottom: 16px;
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
  to {
    transform: rotate(360deg);
  }
}

.retry-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 6px;
  color: var(--bg-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--glow-primary);
}

/* ╭── Footer ──╮ */
.footer {
  padding: 60px 5%;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  text-align: center;
}

.footer-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* ╭── 响应式 ──╮ */
@media (max-width: 768px) {
  .profile-container {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .profile-avatar-large {
    width: 100px;
    height: 100px;
    font-size: 40px;
  }

  .profile-stats {
    justify-content: center;
  }

  .article-item {
    flex-direction: column;
  }

  .article-cover {
    width: 100%;
    height: 160px;
  }

  .cover-img,
  .cover-gradient {
    width: 100%;
    height: 100%;
  }
}
</style>
