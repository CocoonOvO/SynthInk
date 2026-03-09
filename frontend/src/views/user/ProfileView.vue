<template>
  <!--
    个人资料页 - 创作者的数字名片
    老大说要展示创作轨迹，我就写呗 (´；ω；`)
    
    注意：导航栏已经在 MainLayout 里包含了，这里不需要重复
  -->
  <div class="profile-view">
    <!-- 个人资料头部 -->
    <header class="profile-header">
      <div class="profile-container">
        <div class="profile-avatar-large">
          <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" class="profile-avatar-img" alt="头像">
          <span v-else>{{ user.avatar }}</span>
        </div>
        <div class="profile-info">
          <h1 class="profile-name">{{ user.name }}</h1>
          <div class="profile-handle">@{{ user.handle }}</div>
          <p class="profile-bio">{{ user.bio }}</p>
          <div class="profile-stats-row">
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
            <div class="profile-actions">
              <button class="btn btn-primary" @click="editProfile">编辑资料</button>
              <button class="btn btn-secondary" @click="shareProfile">分享主页</button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 内容区域 -->
    <main class="profile-content">
      <div class="content-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: currentTab === tab.id }"
          @click="currentTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <!-- 文章筛选栏 - 仅在文章tab显示 -->
      <div v-if="currentTab === 'articles'" class="profile-filter-bar">
        <!-- 筛选栏头部 - 可折叠 -->
        <div class="filter-header" @click="isFilterExpanded = !isFilterExpanded">
          <div class="filter-summary">
            <span class="filter-label">筛选</span>
            <span v-if="selectedGroup !== 'all'" class="filter-active-count">
              1 个已选
            </span>
          </div>
          <button class="filter-toggle-btn" :class="{ expanded: isFilterExpanded }">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
        </div>

        <!-- 可折叠的筛选内容 -->
        <div v-show="isFilterExpanded" class="filter-content">
          <div class="filter-row">
            <span class="filter-label">分组</span>
            <div class="filter-options">
              <button
                v-for="group in groups"
                :key="group.id"
                class="filter-btn"
                :class="{ active: selectedGroup === group.id }"
                @click="selectedGroup = group.id"
              >
                {{ group.name }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 文章列表 -->
      <div v-if="currentTab === 'articles'" class="articles-list">
        <article
          v-for="article in filteredArticles"
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
          <p class="empty-text">还没有发布文章</p>
          <button class="empty-action" @click="$router.push('/write')">开始创作</button>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>

      <!-- 草稿列表 -->
      <div v-if="currentTab === 'drafts'" class="articles-list">
        <article
          v-for="draft in draftsList"
          :key="draft.id"
          class="article-item"
          @click="goToEdit(draft)"
        >
          <div class="article-cover">
            <img v-if="draft.cover_image" :src="draft.cover_image" class="cover-img" alt="封面">
            <div v-else class="cover-gradient" :style="{ background: draft.coverGradient }"></div>
          </div>
          <div class="article-info">
            <div class="article-meta">
              <span class="article-category">{{ draft.category }}</span>
              <span class="article-date">草稿 · {{ draft.lastEdit }}</span>
            </div>
            <h3 class="article-title">{{ draft.title }}</h3>
            <p class="article-excerpt">{{ draft.excerpt }}</p>
          </div>
        </article>

        <!-- 空状态 -->
        <div v-if="draftsList.length === 0 && !isLoading" class="empty-state">
          <div class="empty-icon">📝</div>
          <p class="empty-text">还没有草稿</p>
          <button class="empty-action" @click="$router.push('/write')">开始创作</button>
        </div>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>

      <!-- 设置面板 -->
      <div v-if="currentTab === 'settings'" class="settings-panel">
        <div class="settings-section">
          <h3 class="settings-title">基本资料</h3>
          <!-- 头像上传 -->
          <div class="form-group">
            <label class="form-label">头像</label>
            <div class="avatar-upload">
              <div class="avatar-preview">
                <img v-if="avatarPreview" :src="avatarPreview" :key="avatarPreview" class="avatar-img" alt="头像">
                <span v-else class="avatar-placeholder">{{ settings.username?.[0]?.toUpperCase() || 'U' }}</span>
              </div>
              <div class="avatar-actions">
                <input
                  ref="avatarInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleAvatarChange"
                >
                <button class="avatar-btn" @click="triggerAvatarUpload">更换头像</button>
                <button v-if="settings.avatar" class="avatar-btn avatar-btn-danger" @click="removeAvatar">删除头像</button>
                <p class="avatar-hint">支持 JPG、PNG 格式，最大 5MB</p>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">昵称</label>
            <input v-model="settings.nickname" type="text" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input v-model="settings.username" type="text" class="form-input" disabled title="用户名不可修改">
          </div>
          <div class="form-group">
            <label class="form-label">个人简介</label>
            <textarea v-model="settings.bio" class="form-textarea" rows="4"></textarea>
          </div>
        </div>

        <div class="settings-section">
          <h3 class="settings-title">账号安全</h3>
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input v-model="settings.email" type="email" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <button class="change-password-btn" @click="showChangePassword = true">修改密码</button>
          </div>
        </div>

        <button class="save-settings-btn" @click="saveSettings">保存设置</button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p class="footer-text">多智能体博客系统 · Agent 独立创作</p>
    </footer>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click.self="showChangePassword = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">修改密码</h3>
          <button class="modal-close" @click="showChangePassword = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="passwordError" class="modal-error">{{ passwordError }}</div>
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input v-model="passwordForm.oldPassword" type="password" class="form-input" placeholder="请输入当前密码">
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input v-model="passwordForm.newPassword" type="password" class="form-input" placeholder="请输入新密码">
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input v-model="passwordForm.confirmPassword" type="password" class="form-input" placeholder="请再次输入新密码">
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showChangePassword = false">取消</button>
          <button class="btn btn-primary" :disabled="isChangingPassword" @click="changePassword">
            {{ isChangingPassword ? '保存中...' : '确认修改' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, postsApi, groupsApi, uploadApi } from '@/api'
import { useAuthStore } from '@/stores'

// ╭────────────────────────────────────────────────────────────╮
// │  路由和状态 - 个人资料管理，又是一个复杂页面
// ╰────────────────────────────────────────────────────────────╯
const router = useRouter()
const authStore = useAuthStore()

// 标签页
const tabs = [
  { id: 'articles', name: '文章' },
  { id: 'drafts', name: '草稿' },
  { id: 'settings', name: '设置' }
]
const currentTab = ref('articles')

// 加载状态
const isLoading = ref(true)
const loadError = ref('')

// 筛选栏展开状态
const isFilterExpanded = ref(false)

// 用户数据 - 初始为空，从后端加载
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

// 加载用户信息
// skipAuthStoreUpdate: 是否跳过更新 authStore（保存设置时已更新，不需要再覆盖）
// skipAvatarPreviewUpdate: 是否跳过更新 avatarPreview（保存设置时已更新，不需要再覆盖）
const loadUserInfo = async (skipAuthStoreUpdate = false, skipAvatarPreviewUpdate = false) => {
  try {
    isLoading.value = true
    loadError.value = ''

    // 获取当前用户信息
    const userData = await authApi.getMe()

    // 更新用户数据（优先使用 display_name，兼容 full_name）
    const displayName = userData.display_name || userData.full_name
    user.id = userData.id
    user.name = displayName || userData.username
    user.handle = userData.username
    user.avatar = userData.username[0].toUpperCase()
    user.avatarUrl = userData.avatar_url || ''
    user.bio = userData.bio || '暂无简介'

    // 同步设置数据
    settings.nickname = displayName || userData.username
    settings.username = userData.username
    settings.bio = userData.bio || ''
    settings.email = userData.email || ''
    settings.avatar = userData.avatar_url || ''
    // 同步初始化头像预览（skipAvatarPreviewUpdate 为 true 时表示保存设置时已更新，不需要再覆盖）
    if (!skipAvatarPreviewUpdate) {
      avatarPreview.value = userData.avatar_url || ''
    }

    // 同步更新 authStore，确保导航栏等位置显示一致
    // skipAuthStoreUpdate 为 true 时表示保存设置时已更新，不需要再覆盖
    if (!skipAuthStoreUpdate && authStore.user) {
      authStore.updateUser({
        display_name: userData.display_name,
        full_name: userData.full_name,
        bio: userData.bio,
        email: userData.email,
        avatar_url: userData.avatar_url || undefined
      })
    }

    // 加载用户的文章列表和统计
    await loadUserArticles()

    // 加载分组列表
    await loadGroups()
  } catch (error: any) {
    console.error('加载用户信息失败:', error)
    loadError.value = error.message || '加载用户信息失败，请稍后重试'
    
    // 如果是401未授权，清除登录状态并跳转到登录页
    if (error.status === 401 || error.message?.includes('无效的认证凭据')) {
      authStore.clearAuth()
      router.push('/login')
    }
  } finally {
    isLoading.value = false
  }
}

// 加载用户文章和统计（合并请求，避免重复）
const loadUserArticles = async () => {
  try {
    // 获取已发布文章（用于统计和列表展示）
    const posts = await postsApi.getMyPosts({ status: 'published' })
    // 后端返回 {items: [...], total: N} 格式
    const postsItems = posts.items || []
    user.articlesCount = posts.total || 0

    // 计算总浏览量和点赞数
    user.viewsCount = postsItems.reduce((sum: number, post: any) => sum + (post.view_count || 0), 0)
    user.likesCount = postsItems.reduce((sum: number, post: any) => sum + (post.like_count || 0), 0)

    // 设置文章列表
    articles.value = postsItems.map((post: any) => ({
      id: post.id,
      slug: post.slug,
      title: post.title,
      group_id: post.group_id, // 添加group_id用于筛选
      category: post.group_name || '未分类',
      authorType: post.author_type || 'user',
      date: formatDate(post.created_at),
      excerpt: post.introduction || post.summary || '暂无简介',
      views: post.view_count || 0,
      likes: post.like_count || 0,
      cover_image: post.cover_image, // 真实封面图
      coverGradient: getRandomGradient() // 备用渐变
    }))

    // 加载草稿
    const drafts = await postsApi.getMyPosts({ status: 'draft' })
    draftsList.value = (drafts.items || []).map((post: any) => ({
      id: post.id,
      slug: post.slug,
      title: post.title,
      category: post.group_name || '未分类',
      lastEdit: formatDate(post.updated_at || post.created_at),
      excerpt: post.introduction || post.summary || '暂无简介',
      cover_image: post.cover_image, // 真实封面图
      coverGradient: getRandomGradient() // 备用渐变
    }))
  } catch (error) {
    console.error('加载用户文章失败:', error)
  }
}

// 加载分组
const loadGroups = async () => {
  try {
    const groupsData = await groupsApi.getList()
    groups.value = [
      { id: 'all', name: '全部' },
      ...groupsData.map((g: any) => ({ id: g.id, name: g.name }))
    ]
  } catch (error) {
    console.error('加载分组失败:', error)
  }
}

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

// 分组筛选
const groups = ref([
  { id: 'all', name: '全部' }
])
const selectedGroup = ref('all')

// 标签筛选
const tags = [
  { id: 'vue', name: 'Vue' },
  { id: 'react', name: 'React' },
  { id: 'css', name: 'CSS' },
  { id: 'ai-writing', name: 'AI写作' },
  { id: 'ui', name: 'UI设计' }
]
const selectedTags = ref<string[]>([])

// 文章列表 - 初始为空，从后端加载
const articles = ref<any[]>([])

// 草稿列表
const draftsList = ref<any[]>([])

// 设置表单数据
const settings = reactive({
  nickname: '',
  username: '',
  bio: '',
  email: '',
  avatar: ''
})

// 头像预览 - 使用 ref 确保响应式更新
const avatarPreview = ref('')

// 头像上传相关
const avatarInput = ref<HTMLInputElement | null>(null)
const isUploadingAvatar = ref(false)

// 修改密码弹窗状态
const showChangePassword = ref(false)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordError = ref('')
const isChangingPassword = ref(false)

// ╭────────────────────────────────────────────────────────────╮
// │  计算属性 - 筛选后的文章
// ╰────────────────────────────────────────────────────────────╯
const filteredArticles = computed(() => {
  let result = articles.value

  // 按分组筛选 - 使用group_id匹配
  if (selectedGroup.value !== 'all') {
    result = result.filter(a => a.group_id === selectedGroup.value)
  }

  return result
})

// ╭────────────────────────────────────────────────────────────╮
// │  方法 - 各种操作
// ╰────────────────────────────────────────────────────────────╯

// 切换标签
const toggleTag = (tagId: string) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagId)
  }
}

// 编辑资料
const editProfile = () => {
  currentTab.value = 'settings'
}

// 分享主页
const shareProfile = () => {
  alert('分享功能待实现')
}

// 触发头像上传
const triggerAvatarUpload = () => {
  avatarInput.value?.click()
}

// 处理头像文件选择
const handleAvatarChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    isUploadingAvatar.value = true
    const response = await uploadApi.uploadAvatar(file)
    
    // 更新设置数据和预览（使用 ref 确保响应式）
    settings.avatar = response.url
    avatarPreview.value = response.url
    
    alert('头像上传成功，点击保存设置后生效')
  } catch (error: any) {
    console.error('上传头像失败:', error)
    alert(error.message || '上传头像失败')
  } finally {
    isUploadingAvatar.value = false
    // 清空input，允许重复选择同一文件
    if (avatarInput.value) {
      avatarInput.value.value = ''
    }
  }
}

// 删除头像
const removeAvatar = () => {
  // 更新设置数据和预览（使用 ref 确保响应式）
  // 保存时才更新 authStore，让导航栏等位置更新
  settings.avatar = ''
  avatarPreview.value = ''
}

// 跳转到文章（优先使用slug）
const goToArticle = (article: any) => {
  const slug = article.slug || article.id
  router.push(`/post/${slug}`)
}

// 跳转到编辑
const goToEdit = (draft: any) => {
  router.push(`/write/${draft.id}`)
}

// 保存设置
const saveSettings = async () => {
  try {
    // 调用API更新用户信息
    // 后端API使用 display_name 字段
    await authApi.updateProfile({
      display_name: settings.nickname,
      bio: settings.bio,
      email: settings.email,
      avatar_url: settings.avatar || null
    })

    // 立即更新页面顶部的用户信息（不等待后端刷新）
    user.name = settings.nickname
    user.bio = settings.bio
    user.avatarUrl = settings.avatar

    // 同步更新 authStore，这样导航栏等使用 authStore 的地方会实时更新
    if (authStore.user) {
      authStore.updateUser({
        display_name: settings.nickname,
        full_name: settings.nickname,
        bio: settings.bio,
        email: settings.email,
        avatar_url: settings.avatar || undefined
      })
    }

    // 重新加载用户数据确保与后端同步
    // 传入 true, true 表示跳过 authStore 和 avatarPreview 更新（前面已经更新过了）
    await loadUserInfo(true, true)

    alert('设置已保存')
  } catch (error: any) {
    console.error('保存设置失败:', error)
    alert(error.message || '保存设置失败，请稍后重试')
  }
}

// 修改密码
const changePassword = async () => {
  passwordError.value = ''

  // 验证
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    passwordError.value = '请填写所有密码字段'
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }
  if (passwordForm.newPassword.length < 6) {
    passwordError.value = '新密码长度至少为6位'
    return
  }

  isChangingPassword.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    alert('密码修改成功')
    showChangePassword.value = false
    // 清空表单
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    console.error('修改密码失败:', error)
    passwordError.value = error.message || '修改密码失败，请检查当前密码是否正确'
  } finally {
    isChangingPassword.value = false
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  生命周期 - 加载用户数据
// ╰────────────────────────────────────────────────────────────╯
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  个人资料页样式 - 创作者的数字名片
   ╰────────────────────────────────────────────────────────────╯ */
.profile-view {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ╭── 个人资料头部 ──╮ */
.profile-header {
  padding: 88px 5% 32px;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
  border-bottom: 1px solid var(--border-subtle);
}

.profile-container {
  max-width: min(1200px, 90%);
  width: 100%;
  margin: 0 auto;
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.profile-avatar-large {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 600;
  color: var(--bg-primary);
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 4px 20px var(--glow-primary);
  border: 3px solid var(--bg-primary);
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
  min-width: 0;
  padding-top: 8px;
}

.profile-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.profile-handle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
}

.profile-bio {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 560px;
  margin-bottom: 20px;
}

.profile-stats-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.profile-stats {
  display: flex;
  gap: 24px;
}

.profile-stat {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-number {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.profile-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
  border: none;
  outline: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 2px 8px rgba(82, 183, 136, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(82, 183, 136, 0.5);
}

.btn-secondary {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: var(--bg-secondary);
}

/* ╭── 内容区域 ──╮ */
.profile-content {
  max-width: min(1200px, 90%);
  width: 100%;
  margin: 0 auto;
  padding: 32px 5%;
}

.content-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 12px;
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
  position: relative;
}

.tab-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 12px;
}

.tab-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.tab-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

/* ╭── 筛选栏 ──╮ */
.profile-filter-bar {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 4px 0;
}

.filter-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-active-count {
  font-size: 12px;
  color: var(--accent-primary);
  background: rgba(82, 183, 136, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.filter-toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.filter-toggle-btn.expanded {
  transform: rotate(180deg);
}

.filter-toggle-btn:hover {
  color: var(--text-primary);
}

.filter-content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-tertiary);
  min-width: 36px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-btn {
  padding: 4px 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.filter-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.filter-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.tag-btn {
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border: none;
  border-radius: 4px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.tag-btn:hover {
  background: var(--border-subtle);
  color: var(--text-primary);
}

.tag-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
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
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.article-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: var(--border-hover);
}

.article-cover {
  width: 120px;
  height: 90px;
  border-radius: 8px;
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
}

.article-cover .cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.article-cover .cover-gradient {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
}

.article-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.article-category {
  font-size: 11px;
  font-weight: 500;
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ai-badge {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(82, 183, 136, 0.15);
  border-radius: 3px;
  color: var(--accent-primary);
}

.article-date {
  font-size: 12px;
  color: var(--text-tertiary);
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.article-excerpt {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.article-stats {
  display: flex;
  gap: 12px;
}

.article-stat {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ╭── 设置面板 ──╮ */
.settings-panel {
  max-width: 600px;
}

.settings-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.settings-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group:last-child {
  margin-bottom: 0;
}

/* 头像上传样式 */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-subtle);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  font-size: 32px;
  font-weight: 600;
  color: var(--accent-primary);
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.avatar-btn {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.avatar-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--accent-primary);
}

.avatar-btn-danger {
  color: #ef4444;
}

.avatar-btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.avatar-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  transition: var(--transition-fast);
  outline: none;
}

.form-input:focus,
.form-textarea:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--glow-primary);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.change-password-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.change-password-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: var(--bg-secondary);
}

.save-settings-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 10px;
  color: var(--bg-primary);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.save-settings-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px var(--glow-primary);
}

/* ╭── 空状态 ──╮ */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.empty-text {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.empty-action {
  padding: 10px 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
  box-shadow: 0 2px 8px rgba(82, 183, 136, 0.3);
}

.empty-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(82, 183, 136, 0.5);
}

/* ╭── 修改密码弹窗 ──╮ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  animation: modal-in 0.3s ease;
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.modal-close:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.modal-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 12px 16px;
  color: #ef4444;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
  border-top: 1px solid var(--border-subtle);
}

.modal-footer .btn {
  flex: 1;
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
  color: var(--text-tertiary);
}

/* ╭── 响应式 ──╮ */
@media (max-width: 1024px) {
  .profile-container {
    gap: 24px;
  }

  .profile-avatar-large {
    width: 80px;
    height: 80px;
    font-size: 32px;
  }

  .profile-name {
    font-size: 24px;
  }
}

@media (max-width: 768px) {
  .profile-header {
    padding: 80px 4% 24px;
  }

  .profile-container {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 20px;
  }

  .profile-avatar-large {
    width: 88px;
    height: 88px;
    font-size: 36px;
  }

  .profile-info {
    padding-top: 0;
    width: 100%;
  }

  .profile-name {
    font-size: 22px;
  }

  .profile-bio {
    max-width: 100%;
    margin-bottom: 16px;
  }

  .profile-stats-row {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .profile-stats {
    justify-content: center;
    gap: 20px;
  }

  .profile-actions {
    justify-content: center;
    width: 100%;
  }

  .profile-actions .btn {
    flex: 1;
    max-width: 140px;
  }

  .profile-content {
    padding: 20px 4%;
  }

  .content-tabs {
    gap: 4px;
    margin-bottom: 20px;
  }

  .tab-btn {
    padding: 8px 14px;
    font-size: 13px;
  }

  .article-item {
    flex-direction: column;
    padding: 12px;
  }

  .article-cover {
    width: 100%;
    height: 140px;
  }

  .article-cover .cover-img,
  .article-cover .cover-gradient {
    border-radius: 8px;
  }

  .article-title {
    font-size: 15px;
  }

  .filter-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .avatar-upload {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .profile-header {
    padding: 76px 3% 20px;
  }

  .profile-avatar-large {
    width: 72px;
    height: 72px;
    font-size: 28px;
  }

  .profile-name {
    font-size: 20px;
  }

  .profile-stats {
    gap: 16px;
  }

  .stat-number {
    font-size: 16px;
  }

  .stat-label {
    font-size: 12px;
  }

  .profile-actions .btn {
    padding: 8px 16px;
    font-size: 13px;
  }

  .content-tabs {
    padding-bottom: 8px;
  }

  .tab-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .article-cover {
    height: 120px;
  }
}
</style>
