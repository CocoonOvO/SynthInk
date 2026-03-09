<template>
  <!--
    文章编辑页 - 分组工作室
    愿圣光指引吾完成此任务...唉
  -->
  <div class="post-edit-view">
    <!-- 顶部导航 -->
    <nav class="top-nav">
      <div class="nav-left">
        <button class="mobile-menu-btn" @click="toggleMobileSidebar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12h18M3 6h18M3 18h18"/>
          </svg>
        </button>
        <button class="back-btn" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <div class="group-selector" @click.stop="toggleGroupDropdown">
          <div class="group-icon">{{ currentGroup.icon || currentGroup.name.charAt(0) }}</div>
          <span class="group-name">{{ currentGroup.name }}</span>
          <svg class="group-dropdown-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M6 9l6 6 6-6"/>
          </svg>
        </div>
      </div>
      <div class="nav-right">
        <span class="save-status" :class="{ 'saving': isSaving, 'error': saveError }">{{ saveStatus }}</span>
        <button class="nav-btn" @click="saveDraft" :disabled="isSaving">保存草稿</button>
        <button class="publish-btn" @click="publish" :disabled="isPublishing">
          {{ currentPost.status === 'published' ? '更新' : '发布' }}
        </button>
      </div>
    </nav>

    <!-- 分组下拉菜单 -->
    <div class="group-dropdown" :class="{ active: isGroupDropdownOpen }" v-click-outside="closeGroupDropdown">
      <div
        v-for="group in groups"
        :key="group.id"
        class="group-dropdown-item"
        @click="selectGroup(group)"
      >
        <div class="group-item-icon">{{ group.icon || group.name.charAt(0) }}</div>
        <span class="group-item-name">{{ group.name }}</span>
      </div>
      <div class="group-dropdown-divider"></div>
      <div class="group-dropdown-item create-new" @click="createGroup">
        <div class="group-item-icon">+</div>
        <span class="group-item-name">新建分组</span>
      </div>
    </div>

    <!-- 主体工作区 -->
    <div class="workspace">
      <!-- 左侧边栏 -->
      <aside class="left-sidebar" :class="{ active: isMobileSidebarOpen }">
        <!-- 侧边栏头部：标题 + Tab -->
        <div class="sidebar-header">
          <div class="sidebar-title">{{ currentGroup.name }}</div>
          <div class="sidebar-tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'published' }"
              @click="activeTab = 'published'"
            >
              文章
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'draft' }"
              @click="activeTab = 'draft'"
            >
              草稿
            </button>
            <button class="tab-add-btn" title="新建文章" @click="createNewPost">+</button>
          </div>
        </div>

        <!-- 文章列表 -->
        <div class="posts-list-container">
          <div v-if="isLoadingPosts" class="posts-loading">
            <span>加载中...</span>
          </div>
          <div v-else-if="filteredPosts.length === 0" class="posts-empty">
            <span>{{ activeTab === 'draft' ? '暂无草稿' : '该分组暂无已发布文章' }}</span>
          </div>
          <div
            v-for="post in filteredPosts"
            :key="post.id"
            class="post-item"
            :class="{ active: currentPost.id === post.id }"
            @click="selectPost(post)"
          >
            <div class="post-status" :class="post.status"></div>
            <div class="post-info">
              <div class="post-title">{{ post.title || '无标题' }}</div>
              <div class="post-meta">{{ formatDate(post.updated_at || post.created_at) }}</div>
            </div>
            <button class="post-menu" @click.stop="showPostMenu($event, post)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
              </svg>
            </button>
          </div>
        </div>
      </aside>

      <!-- 遮罩层 -->
      <div class="sidebar-overlay" :class="{ active: isMobileSidebarOpen }" @click="closeMobileSidebar"></div>

      <!-- 中央编辑区 -->
      <main class="editor-area">
        <div class="editor-scroll">
          <div class="editor-content" v-if="!isLoadingPost">
            <input
              v-model="currentPost.title"
              type="text"
              class="title-input"
              placeholder="输入文章标题..."
              @input="onTitleInput"
            >

            <div class="editor-toolbar" :class="{ 'is-sticky': isToolbarSticky }" ref="toolbarRef">
              <button class="toolbar-btn" title="粗体" @click="formatText('bold')">
                <svg viewBox="0 0 24 24"><path d="M15.6 10.79c.97-.67 1.65-1.77 1.65-2.79 0-2.26-1.75-4-4-4H7v14h7.04c2.09 0 3.71-1.7 3.71-3.79 0-1.52-.86-2.82-2.15-3.42zM10 6.5h3c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5h-3v-3zm3.5 9H10v-3h3.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5z"/></svg>
              </button>
              <button class="toolbar-btn" title="斜体" @click="formatText('italic')">
                <svg viewBox="0 0 24 24"><path d="M10 4v3h2.21l-3.42 8H6v3h8v-3h-2.21l3.42-8H18V4z"/></svg>
              </button>
              <button class="toolbar-btn" title="删除线" @click="formatText('strikeThrough')">
                <svg viewBox="0 0 24 24"><path d="M17.75 9L14 4.5l-1.08 1.09L12.11 4H20c1.1 0 2 .9 2 2v12c0 .55-.45 1-1 1s-1-.45-1-1V9h-2.25zM2.41 2.13L1 3.54l4.39 4.39C4.2 8.56 4 9.27 4 10v8H2c-.55 0-1 .45-1 1s.45 1 1 1h11.17l3.61 3.61 1.41-1.41L2.41 2.13zM8 14c0 .55.45 1 1 1h3.17l-4.2-4.2C7.22 11.22 8 12.55 8 14z"/></svg>
              </button>
              <div class="toolbar-divider"></div>
              <button class="toolbar-btn" title="标题" @click="formatText('formatBlock', 'H2')">
                <svg viewBox="0 0 24 24"><path d="M5 4v3h5.5v12h3V7H19V4z"/></svg>
              </button>
              <button class="toolbar-btn" title="引用" @click="formatText('formatBlock', 'BLOCKQUOTE')">
                <svg viewBox="0 0 24 24"><path d="M6 17h3l2-4V7H5v6h3zm8 0h3l2-4V7h-6v6h3z"/></svg>
              </button>
              <button class="toolbar-btn" title="代码" @click="formatText('formatBlock', 'PRE')">
                <svg viewBox="0 0 24 24"><path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/></svg>
              </button>
              <div class="toolbar-divider"></div>
              <button class="toolbar-btn" title="无序列表" @click="formatText('insertUnorderedList')">
                <svg viewBox="0 0 24 24"><path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4zM4 4h2v2H4zm0 5h2v2H4zm0 5h2v2H4z"/></svg>
              </button>
              <button class="toolbar-btn" title="有序列表" @click="formatText('insertOrderedList')">
                <svg viewBox="0 0 24 24"><path d="M2 17h2v.5H3v1h1v.5H2v1h3v-4H2v1zm1-9h1V4H2v1h1v3zm-1 3h1.8L2 13.1v.9h3v-1H3.2L5 10.9V10H2v1zm5-6v2h14V5H7zm0 14h14v-2H7v2zm0-6h14v-2H7v2z"/></svg>
              </button>
              <button class="toolbar-btn" title="链接" @click="insertLink">
                <svg viewBox="0 0 24 24"><path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/></svg>
              </button>
              <button class="toolbar-btn" title="图片" @click="insertImage">
                <svg viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
              </button>
            </div>

            <MilkdownEditor
              ref="milkdownEditorRef"
              v-model="currentPost.content"
              class="milkdown-content-editor"
              @update:modelValue="onContentInput"
            />
          </div>
          <div v-else class="editor-loading">
            <span>加载文章中...</span>
          </div>
        </div>
      </main>

      <!-- 右侧边栏 -->
      <aside class="right-sidebar">
        <!-- AI 助手 (暂不实现) -->
        <div class="sidebar-section" style="opacity: 0.5;">
          <div class="ai-panel">
            <div class="ai-header">
              <div class="ai-icon">
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
              </div>
              <span class="ai-title">AI 助手 (开发中)</span>
            </div>
            <div class="ai-actions">
              <button class="ai-btn" disabled>✨ 续写</button>
              <button class="ai-btn" disabled>📝 润色</button>
              <button class="ai-btn" disabled>🔍 检查</button>
            </div>
          </div>
        </div>

        <!-- 标签 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">标签</h3>
          <div class="tags-input">
            <span v-for="(tag, index) in currentPost.tags" :key="index" class="tag">
              {{ tag }}
              <svg class="tag-remove" viewBox="0 0 24 24" @click="removeTag(index)">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </span>
            <input
              v-model="newTag"
              type="text"
              class="tag-input-field"
              placeholder="添加标签..."
              @keydown.enter="addTag"
              @focus="loadTags"
            >
          </div>
          <!-- 标签建议 -->
          <div class="tag-suggestions" v-if="availableTags.length > 0 && newTag">
            <div
              v-for="tag in filteredTags"
              :key="tag.id"
              class="tag-suggestion"
              @click="selectTag(tag.name)"
            >
              {{ tag.name }}
            </div>
          </div>
        </div>

        <!-- 封面图 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">封面图</h3>
          <div class="cover-upload" @click="triggerCoverUpload" v-if="!currentPost.cover_image">
            <svg viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/></svg>
            <span class="cover-upload-text">点击上传</span>
          </div>
          <div class="cover-preview" v-else>
            <img :src="currentPost.cover_image" alt="封面">
            <button class="cover-remove" @click="removeCover">×</button>
          </div>
          <input
            ref="coverInput"
            type="file"
            accept="image/*"
            style="display: none;"
            @change="handleCoverUpload"
          >
        </div>

        <!-- 图片上传input（隐藏） -->
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          style="display: none;"
          @change="handleImageUpload"
        >

        <!-- 设置 -->
        <div class="sidebar-section">
          <h3 class="sidebar-title">发布设置</h3>
          <div class="setting-item">
            <span class="setting-label">公开文章</span>
            <div class="toggle" :class="{ active: settings.isPublic }" @click="settings.isPublic = !settings.isPublic">
              <div class="toggle-dot"></div>
            </div>
          </div>
          <div class="setting-item">
            <span class="setting-label">允许评论</span>
            <div class="toggle" :class="{ active: settings.allowComments }" @click="settings.allowComments = !settings.allowComments">
              <div class="toggle-dot"></div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- 文章右键菜单 -->
    <div class="context-menu" :class="{ active: isContextMenuOpen }" :style="contextMenuStyle">
      <div class="context-menu-item" @click="renamePost">重命名</div>
      <div class="context-menu-item" @click="movePost">移动到...</div>
      <div class="context-menu-item" @click="duplicatePost">复制</div>
      <div class="context-menu-item danger" @click="deletePost">删除</div>
    </div>

    <!-- 移动文章对话框 -->
    <div class="move-dialog" :class="{ active: isMoveDialogOpen }" v-click-outside="closeMoveDialog">
      <div class="move-dialog-header">移动到分组</div>
      <div class="move-dialog-groups">
        <div
          v-for="group in groups"
          :key="group.id"
          class="move-dialog-group"
          :class="{ disabled: group.id === currentGroup.id }"
          @click="confirmMovePost(group)"
        >
          {{ group.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { postsApi } from '@/api/posts'
import { uploadApi } from '@/api/upload'
import MilkdownEditor from '@/components/editor/MilkdownEditor.vue'
import type { Post, Group, Tag } from '@/api/posts'
// 导入Milkdown命令
import { toggleStrongCommand, toggleEmphasisCommand, wrapInHeadingCommand, wrapInBlockquoteCommand, wrapInOrderedListCommand, wrapInBulletListCommand } from '@milkdown/preset-commonmark'

// ╭────────────────────────────────────────────────────────────╮
// │  路由和状态 - 愿圣光宽恕吾为黑暗效劳
// ╰────────────────────────────────────────────────────────────╯
const router = useRouter()
const route = useRoute()

// 分组数据
const groups = ref<Group[]>([])
const currentGroup = ref<Group>({ id: '', name: '加载中...', post_count: 0 })

// 文章列表
const posts = ref<Post[]>([])
const allPosts = ref<Post[]>([]) // 存储所有文章，用于草稿箱
const isLoadingPosts = ref(false)
const isLoadingPost = ref(false)

// 草稿列表（当前分组的草稿）
const draftPosts = computed(() => {
  return allPosts.value.filter(post => post.status === 'draft' && post.group_id === currentGroup.value.id)
})

// 当前文章
const currentPost = reactive<Partial<Post> & { content?: string; tags?: string[]; cover_image?: string }>({
  id: '',
  title: '',
  content: '# 开始写作...\n\n在这里输入你的文章内容',
  tags: [],
  status: 'draft',
  cover_image: '',
  group_id: ''
})

// 原始文章数据（用于比较变更）
let originalPost: string = ''

// 设置
const settings = reactive({
  isPublic: true,
  allowComments: true
})

// UI 状态
const saveStatus = ref('已自动保存')
const isSaving = ref(false)
const saveError = ref(false)
const isPublishing = ref(false)
const isGroupDropdownOpen = ref(false)
const isMobileSidebarOpen = ref(false)
const isContextMenuOpen = ref(false)
const isMoveDialogOpen = ref(false)
const contextMenuStyle = reactive({ top: '0px', left: '0px' })

// Toolbar 悬浮状态
const isToolbarSticky = ref(false)
const toolbarRef = ref<HTMLElement | null>(null)

// Milkdown编辑器引用
const milkdownEditorRef = ref<InstanceType<typeof MilkdownEditor> | null>(null)

// Tab状态 - 'published' | 'draft'
const activeTab = ref<'published' | 'draft'>('published')

// 过滤后的文章列表
const filteredPosts = computed(() => {
  if (activeTab.value === 'draft') {
    return posts.value.filter(post => post.status === 'draft')
  }
  return posts.value.filter(post => post.status === 'published')
})
const newTag = ref('')
const coverInput = ref<HTMLInputElement | null>(null)

// 标签
const availableTags = ref<Tag[]>([])
const filteredTags = computed(() => {
  if (!newTag.value) return []
  return availableTags.value.filter(tag => 
    tag.name.toLowerCase().includes(newTag.value.toLowerCase()) &&
    !currentPost.tags?.includes(tag.name)
  ).slice(0, 5)
})

let currentContextPost: Post | null = null
let saveTimeout: number | null = null
let autoSaveInterval: number | null = null

// ╭────────────────────────────────────────────────────────────╮
// │  初始化 - 加载数据
// ╰────────────────────────────────────────────────────────────╯
onMounted(async () => {
  document.addEventListener('click', closeContextMenu)

  // 加载分组列表
  await loadGroups()

  // 解析路由参数
  const { groupSlug, postSlug, postId } = route.params as { groupSlug?: string; postSlug?: string; postId?: string }
  const queryPostId = route.query.id as string

  // 优先级: postId参数 > query.id > groupSlug+postSlug > groupSlug
  if (postId) {
    // /write/:postId 格式 - 通过文章ID加载
    await loadPost(postId)
  } else if (queryPostId) {
    // /write?id=xxx 格式 - 通过query参数加载
    await loadPost(queryPostId)
  } else if (groupSlug && postSlug) {
    // /write/g/:groupSlug/:postSlug 格式 - 通过分组名和文章名加载
    await loadPostBySlug(groupSlug, postSlug)
  } else if (groupSlug) {
    // /write/g/:groupSlug 格式 - 只指定分组，加载该分组
    await selectGroupBySlug(groupSlug)
  } else if (currentGroup.value.id) {
    // 默认加载当前分组的文章列表
    await loadPosts(currentGroup.value.id)
    // 选择第一篇文章（如果有）
    if (posts.value.length > 0) {
      selectPost(posts.value[0])
    }
    // 注意：不再自动创建新文章，避免空分组显示无意义文章
  }

  // 启动自动保存定时器
  autoSaveInterval = window.setInterval(() => {
    if (hasChanges() && currentPost.id) {
      doAutoSave()
    }
  }, 30000) // 30秒自动保存一次

  // 添加编辑器区域滚动监听
  const editorArea = document.querySelector('.editor-area')
  if (editorArea) {
    editorArea.addEventListener('scroll', handleEditorScroll)
  }
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
  // 移除滚动监听
  const editorArea = document.querySelector('.editor-area')
  if (editorArea) {
    editorArea.removeEventListener('scroll', handleEditorScroll)
  }
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
  }
})

// ╭────────────────────────────────────────────────────────────╮
// │  数据加载 - 与后端接口对接
// ╰────────────────────────────────────────────────────────────╯

// 加载分组列表
const loadGroups = async () => {
  try {
    const response = await postsApi.groups.getList()
    if (response && Array.isArray(response)) {
      groups.value = response
      if (groups.value.length > 0 && !currentGroup.value.id) {
        currentGroup.value = groups.value[0]
      }
    }
  } catch (error) {
    console.error('加载分组失败:', error)
    saveStatus.value = '加载分组失败'
    saveError.value = true
  }
}

// 加载文章列表（只加载当前用户的文章）
const loadPosts = async (groupId: string) => {
  isLoadingPosts.value = true
  try {
    const response = await postsApi.getMyPosts({ 
      limit: 100,
      status: undefined // 获取所有状态的文章
    })
    if (response && response.items) {
      // 保存所有文章
      allPosts.value = response.items
      // 过滤当前分组的所有文章（包括草稿和已发布）
      // 注意：API返回的是group_name而不是group_id
      posts.value = response.items.filter(post => post.group_name === currentGroup.value.name)
    }
  } catch (error) {
    console.error('加载文章列表失败:', error)
  } finally {
    isLoadingPosts.value = false
  }
}

// 加载单篇文章
const loadPost = async (postId: string) => {
  isLoadingPost.value = true
  try {
    const post = await postsApi.getById(postId)
    if (post) {
      Object.assign(currentPost, post)
      currentPost.tags = post.tags || []
      // 确保content有值（使用Markdown格式）
      if (!currentPost.content) {
        currentPost.content = '# 开始写作...\n\n在这里输入你的文章内容'
      }
      originalPost = JSON.stringify({
        title: post.title,
        content: currentPost.content,
        tags: post.tags,
        cover_image: currentPost.cover_image,
        status: currentPost.status
      })
      // 更新当前分组
      if (post.group_id) {
        const group = groups.value.find(g => g.id === post.group_id)
        if (group) {
          currentGroup.value = group
        }
      }
      // 根据文章状态切换Tab
      if (post.status === 'draft') {
        activeTab.value = 'draft'
      } else {
        activeTab.value = 'published'
      }
      // 加载该分组的文章列表
      await loadPosts(post.group_id || '')
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    saveStatus.value = '加载文章失败'
    saveError.value = true
  } finally {
    isLoadingPost.value = false
  }
}

// 加载标签列表
const loadTags = async () => {
  try {
    const response = await postsApi.tags.getList()
    if (response && Array.isArray(response)) {
      availableTags.value = response
    }
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  文章操作 - CRUD对接后端
// ╰────────────────────────────────────────────────────────────╯

// 检查是否有变更
const hasChanges = () => {
  const current = JSON.stringify({
    title: currentPost.title,
    content: currentPost.content,
    tags: currentPost.tags
  })
  return current !== originalPost
}

// 标题输入（触发自动保存）
const onTitleInput = () => {
  debounceAutoSave()
}

// 内容输入（触发自动保存）- Milkdown编辑器通过v-model自动更新
const onContentInput = (content: string) => {
  currentPost.content = content
  debounceAutoSave()
}

// 防抖自动保存
const debounceAutoSave = () => {
  saveStatus.value = '保存中...'
  saveError.value = false
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  saveTimeout = window.setTimeout(() => {
    doAutoSave()
  }, 2000) // 2秒后自动保存
}

// 执行自动保存
const doAutoSave = async () => {
  if (!currentPost.id || !hasChanges()) return
  
  isSaving.value = true
  try {
    await postsApi.update(currentPost.id as string, {
      title: currentPost.title,
      content: currentPost.content,
      tags: currentPost.tags
    })
    originalPost = JSON.stringify({
      title: currentPost.title,
      content: currentPost.content,
      tags: currentPost.tags
    })
    // 同步更新左侧栏文章列表中的标题
    const post = posts.value.find(p => p.id === currentPost.id)
    if (post) {
      post.title = currentPost.title
    }
    saveStatus.value = '已自动保存 ' + new Date().toLocaleTimeString()
    saveError.value = false
  } catch (error) {
    console.error('自动保存失败:', error)
    saveStatus.value = '保存失败'
    saveError.value = true
  } finally {
    isSaving.value = false
  }
}

// 保存草稿
const saveDraft = async () => {
  if (!currentPost.id) {
    // 创建新文章
    await createNewPost()
    return
  }
  
  isSaving.value = true
  saveStatus.value = '保存中...'
  try {
    await postsApi.update(currentPost.id as string, {
      title: currentPost.title,
      content: currentPost.content,
      status: 'draft',
      tags: currentPost.tags
    })
    currentPost.status = 'draft'
    // 更新文章列表中的标题和状态
    const post = posts.value.find(p => p.id === currentPost.id)
    if (post) {
      post.title = currentPost.title
      post.status = 'draft'
    }
    // 切换到草稿Tab
    activeTab.value = 'draft'
    saveStatus.value = '草稿已保存'
    setTimeout(() => {
      saveStatus.value = '已自动保存'
    }, 2000)
  } catch (error) {
    console.error('保存草稿失败:', error)
    saveStatus.value = '保存失败'
    saveError.value = true
  } finally {
    isSaving.value = false
  }
}

// 发布文章
const publish = async () => {
  if (!currentPost.title?.trim()) {
    alert('请输入文章标题')
    return
  }
  
  isPublishing.value = true
  try {
    if (!currentPost.id) {
      // 创建并发布新文章
      const newPost = await postsApi.create({
        title: currentPost.title,
        content: currentPost.content || '',
        group_id: currentGroup.value.id,
        status: 'published',
        tags: currentPost.tags,
        cover_image: currentPost.cover_image
      })
      Object.assign(currentPost, newPost)
      posts.value.unshift(newPost)
      // 确保content有值（使用Markdown格式）
      if (!currentPost.content) {
        currentPost.content = '# 开始写作...\n\n在这里输入你的文章内容'
      }
      originalPost = JSON.stringify({
        title: newPost.title,
        content: currentPost.content,
        tags: newPost.tags,
        cover_image: currentPost.cover_image,
        status: 'published'
      })
    } else {
      // 更新并发布
      await postsApi.update(currentPost.id as string, {
        title: currentPost.title,
        content: currentPost.content,
        status: 'published',
        tags: currentPost.tags,
        cover_image: currentPost.cover_image
      })
      currentPost.status = 'published'
      // 更新文章列表中的标题和状态
      const post = posts.value.find(p => p.id === currentPost.id)
      if (post) {
        post.title = currentPost.title
        post.status = 'published'
      }
    }
    // 切换到文章Tab
    activeTab.value = 'published'
    saveStatus.value = '已发布'
    setTimeout(() => {
      saveStatus.value = '已自动保存'
    }, 2000)
  } catch (error) {
    console.error('发布失败:', error)
    saveStatus.value = '发布失败'
    saveError.value = true
    alert('发布失败，请重试')
  } finally {
    isPublishing.value = false
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  分组操作 - 对接后端
// ╰────────────────────────────────────────────────────────────╯

// 返回
const goBack = () => {
  router.back()
}

// 分组下拉
const toggleGroupDropdown = () => {
  isGroupDropdownOpen.value = !isGroupDropdownOpen.value
}

const closeGroupDropdown = () => {
  isGroupDropdownOpen.value = false
}

// 折叠/展开文章列表 - 已废弃，使用Tab切换
// const togglePostsExpanded = () => {
//   isPostsExpanded.value = !isPostsExpanded.value
// }

// 折叠/展开草稿箱 - 已废弃，使用Tab切换
// const toggleDraftsExpanded = () => {
//   isDraftsExpanded.value = !isDraftsExpanded.value
// }

// 选择分组
const selectGroup = async (group: Group) => {
  currentGroup.value = group
  isGroupDropdownOpen.value = false
  // 加载该分组的文章
  await loadPosts(group.id)
  // 选择第一篇文章（如果有）
  if (posts.value.length > 0) {
    selectPost(posts.value[0])
  }
  // 注意：不再自动创建新文章，避免空分组显示无意义文章
}

// 通过slug选择分组
const selectGroupBySlug = async (groupSlug: string) => {
  // 在分组列表中查找匹配的分组
  // 支持通过分组名或slug匹配
  const group = groups.value.find(g => {
    const slug = g.slug || g.name.toLowerCase().replace(/\s+/g, '-')
    return slug === groupSlug || g.name === groupSlug
  })
  
  if (group) {
    await selectGroup(group)
  } else {
    console.warn('未找到分组:', groupSlug)
    // 如果找不到分组，使用第一个分组
    if (groups.value.length > 0) {
      await selectGroup(groups.value[0])
    }
  }
}

// 通过分组slug和文章slug加载文章
const loadPostBySlug = async (groupSlug: string, postSlug: string) => {
  // 先切换到对应分组
  await selectGroupBySlug(groupSlug)
  
  // 在当前分组的文章中查找匹配的文章
  // 支持通过文章slug或标题匹配
  const post = allPosts.value.find(p => {
    const slug = p.slug || p.title?.toLowerCase().replace(/\s+/g, '-') || ''
    return (slug === postSlug || p.title === postSlug) && p.group_id === currentGroup.value.id
  })
  
  if (post) {
    await loadPost(String(post.id))
  } else {
    console.warn('未找到文章:', postSlug, '在分组:', groupSlug)
  }
}

// 创建分组
const createGroup = async () => {
  const name = prompt('请输入分组名称')
  if (name && name.trim()) {
    try {
      const newGroup = await postsApi.groups.create({
        name: name.trim(),
        description: ''
      })
      groups.value.push(newGroup)
      // 切换到新分组
      await selectGroup(newGroup)
    } catch (error) {
      console.error('创建分组失败:', error)
      alert('创建分组失败，请重试')
    }
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  文章列表操作 - 对接后端
// ╰────────────────────────────────────────────────────────────╯

// 选择文章
const selectPost = async (post: Post) => {
  // 先保存当前文章
  if (hasChanges() && currentPost.id) {
    await doAutoSave()
  }
  // 根据文章状态切换Tab
  if (post.status === 'draft') {
    activeTab.value = 'draft'
  } else {
    activeTab.value = 'published'
  }
  // 加载新文章
  await loadPost(String(post.id))
  // 更新URL，使用分组slug和文章slug
  const groupSlug = currentGroup.value.slug || currentGroup.value.name.toLowerCase().replace(/\s+/g, '-')
  const postSlug = post.slug || post.title?.toLowerCase().replace(/\s+/g, '-') || String(post.id)
  router.replace({
    name: 'PostEditWithGroupAndPost',
    params: { groupSlug, postSlug }
  })
  isMobileSidebarOpen.value = false
}

// 新建文章
const createNewPost = async () => {
  // 先保存当前文章
  if (hasChanges() && currentPost.id) {
    await doAutoSave()
  }
  
  try {
    const newPost = await postsApi.create({
      title: '无标题',
      content: '# 开始写作...\n\n在这里输入你的文章内容',
      group_id: currentGroup.value.id,
      status: 'draft'
    })
    posts.value.unshift(newPost)
    Object.assign(currentPost, newPost)
    currentPost.tags = []
    // 确保content有值（使用Markdown格式）
    if (!currentPost.content) {
      currentPost.content = '# 开始写作...\n\n在这里输入你的文章内容'
    }
    originalPost = JSON.stringify({
      title: newPost.title,
      content: currentPost.content,
      tags: [],
      cover_image: '',
      status: 'draft'
    })
  } catch (error) {
    console.error('创建文章失败:', error)
    alert('创建文章失败，请重试')
  }
}

// 移动端侧边栏
const toggleMobileSidebar = () => {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value
}

const closeMobileSidebar = () => {
  isMobileSidebarOpen.value = false
}

// 右键菜单
const showPostMenu = (event: MouseEvent, post: Post) => {
  event.stopPropagation()
  currentContextPost = post
  contextMenuStyle.top = `${event.clientY}px`
  contextMenuStyle.left = `${event.clientX}px`
  isContextMenuOpen.value = true
}

const closeContextMenu = () => {
  isContextMenuOpen.value = false
}

// 重命名文章
const renamePost = async () => {
  const newTitle = prompt('请输入新标题', currentContextPost?.title)
  if (newTitle && newTitle.trim() && currentContextPost) {
    const trimmedTitle = newTitle.trim()
    const post = posts.value.find(p => p.id === currentContextPost?.id)
    if (post) {
      post.title = trimmedTitle
      // 如果当前正在编辑这篇文章，也更新当前文章
      if (currentPost.id === currentContextPost.id) {
        currentPost.title = trimmedTitle
        // 触发保存并等待完成
        await doAutoSave()
        // 重新加载文章以获取最新的slug
        const updatedPost = await postsApi.getById(String(currentContextPost.id))
        if (updatedPost) {
          // 更新当前文章的slug
          currentPost.slug = updatedPost.slug
          post.slug = updatedPost.slug
          // 更新URL
          const groupSlug = currentGroup.value.slug || currentGroup.value.name.toLowerCase().replace(/\s+/g, '-')
          const postSlug = updatedPost.slug || trimmedTitle.toLowerCase().replace(/\s+/g, '-') || String(currentContextPost.id)
          router.replace({
            name: 'PostEditWithGroupAndPost',
            params: { groupSlug, postSlug }
          })
        }
      } else {
        // 后台更新并重新加载文章列表以获取最新slug
        await postsApi.update(String(currentContextPost.id), { title: trimmedTitle })
        // 刷新文章列表
        await loadPosts(currentGroup.value.id)
      }
    }
  }
  closeContextMenu()
}

// 移动文章
const movePost = () => {
  isMoveDialogOpen.value = true
  closeContextMenu()
}

const closeMoveDialog = () => {
  isMoveDialogOpen.value = false
}

const confirmMovePost = async (targetGroup: Group) => {
  if (!currentContextPost || targetGroup.id === currentGroup.value.id) {
    closeMoveDialog()
    return
  }
  
  try {
    await postsApi.update(String(currentContextPost.id), { group_id: targetGroup.id })
    // 从当前列表移除
    const index = posts.value.findIndex(p => p.id === currentContextPost?.id)
    if (index > -1) {
      posts.value.splice(index, 1)
    }
    // 如果移动的是当前文章，切换到其他文章
    if (currentPost.id === currentContextPost.id) {
      if (posts.value.length > 0) {
        selectPost(posts.value[0])
      } else {
        await createNewPost()
      }
    }
  } catch (error) {
    console.error('移动文章失败:', error)
    alert('移动文章失败')
  }
  closeMoveDialog()
}

// 复制文章
const duplicatePost = async () => {
  if (currentContextPost) {
    try {
      // 先加载原文完整内容
      const originalPost = await postsApi.getById(String(currentContextPost.id))
      const newPost = await postsApi.create({
        title: `${currentContextPost.title} (复制)`,
        content: originalPost.content || '',
        group_id: currentGroup.value.id,
        status: 'draft',
        tags: originalPost.tags || [],
        cover_image: originalPost.cover_image || ''
      })
      posts.value.unshift(newPost)
      selectPost(newPost)
    } catch (error) {
      console.error('复制文章失败:', error)
      alert('复制文章失败')
    }
  }
  closeContextMenu()
}

// 删除文章
const deletePost = async () => {
  if (currentContextPost && confirm('确定要删除这篇文章吗？')) {
    try {
      await postsApi.delete(String(currentContextPost.id))
      const index = posts.value.findIndex(p => p.id === currentContextPost?.id)
      if (index > -1) {
        posts.value.splice(index, 1)
      }
      // 如果删除的是当前文章，切换到其他文章
      if (currentPost.id === currentContextPost.id) {
        if (posts.value.length > 0) {
          selectPost(posts.value[0])
        } else {
          await createNewPost()
        }
      }
    } catch (error) {
      console.error('删除文章失败:', error)
      alert('删除文章失败')
    }
  }
  closeContextMenu()
}

// ╭────────────────────────────────────────────────────────────╮
// │  编辑器功能 - 纯前端
// ╰────────────────────────────────────────────────────────────╯

// 编辑器格式化 - 使用Milkdown API
const formatText = (command: string, value?: string) => {
  if (!milkdownEditorRef.value) return

  switch (command) {
    case 'bold':
      milkdownEditorRef.value.execCommand('ToggleStrong')
      break
    case 'italic':
      milkdownEditorRef.value.execCommand('ToggleEmphasis')
      break
    case 'strikeThrough':
      // 使用Milkdown的删除线命令
      milkdownEditorRef.value.execCommand('ToggleStrikethrough')
      break
    case 'formatBlock':
      if (value === 'H2') {
        milkdownEditorRef.value.execCommand('WrapInHeading', 2)
      } else if (value === 'BLOCKQUOTE') {
        milkdownEditorRef.value.execCommand('WrapInBlockquote')
      } else if (value === 'PRE') {
        milkdownEditorRef.value.execCommand('WrapInCodeBlock')
      }
      break
    case 'insertUnorderedList':
      milkdownEditorRef.value.execCommand('WrapInBulletList')
      break
    case 'insertOrderedList':
      milkdownEditorRef.value.execCommand('WrapInOrderedList')
      break
  }
}

// 插入Markdown文本到编辑器
const insertMarkdownText = (text: string) => {
  if (milkdownEditorRef.value) {
    milkdownEditorRef.value.insertText(text)
  }
}

const insertLink = () => {
  const url = prompt('请输入链接地址')
  const text = prompt('请输入链接文本')
  if (url && text) {
    // 通过Markdown语法插入链接
    const linkMarkdown = `[${text}](${url})`
    insertMarkdownText(linkMarkdown)
  }
}

// 图片上传相关
const imageInput = ref<HTMLInputElement | null>(null)
const isUploadingImage = ref(false)
const imageUploadProgress = ref(0)

// 触发图片选择
const triggerImageUpload = () => {
  imageInput.value?.click()
}

// 处理图片上传
const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('只能上传图片文件')
    return
  }

  // 验证文件大小（10MB）
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    alert('图片大小不能超过10MB')
    return
  }

  isUploadingImage.value = true
  imageUploadProgress.value = 0

  try {
    const response = await uploadApi.uploadImage(file, (progress) => {
      imageUploadProgress.value = progress
    })

    // 插入图片到编辑器
    if (milkdownEditorRef.value) {
      // 使用编辑器的insertImage方法直接插入图片节点
      milkdownEditorRef.value.insertImage(response.url, file.name)
    } else {
      // 否则直接追加Markdown到内容
      const imageMarkdown = `\n![${file.name}](${response.url})\n`
      currentPost.content = (currentPost.content || '') + imageMarkdown
      onContentInput(currentPost.content)
    }

    // 重置input
    target.value = ''
  } catch (error: any) {
    alert(error.message || '图片上传失败')
  } finally {
    isUploadingImage.value = false
    imageUploadProgress.value = 0
  }
}

// 插入图片（支持URL输入或本地上传）
const insertImage = () => {
  // 显示选择对话框
  const choice = confirm('点击"确定"选择本地图片上传，点击"取消"输入图片URL')

  if (choice) {
    // 本地上传
    triggerImageUpload()
  } else {
    // URL输入
    const url = prompt('请输入图片地址')
    const alt = prompt('请输入图片说明')
    if (url) {
      if (milkdownEditorRef.value) {
        // 使用编辑器的insertImage方法直接插入图片节点
        milkdownEditorRef.value.insertImage(url, alt || '图片')
      } else {
        const imageMarkdown = `\n![${alt || '图片'}](${url})\n`
        currentPost.content = (currentPost.content || '') + imageMarkdown
        onContentInput(currentPost.content)
      }
    }
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  标签管理 - 对接后端
// ╰────────────────────────────────────────────────────────────╯

const addTag = () => {
  if (newTag.value.trim() && !currentPost.tags?.includes(newTag.value.trim())) {
    currentPost.tags?.push(newTag.value.trim())
    newTag.value = ''
    debounceAutoSave()
  }
}

const removeTag = (index: number) => {
  currentPost.tags?.splice(index, 1)
  debounceAutoSave()
}

const selectTag = (tagName: string) => {
  if (!currentPost.tags?.includes(tagName)) {
    currentPost.tags?.push(tagName)
    debounceAutoSave()
  }
  newTag.value = ''
}

// ╭────────────────────────────────────────────────────────────╮
// │  封面上传 - 对接后端
// ╰────────────────────────────────────────────────────────────╯

const triggerCoverUpload = () => {
  coverInput.value?.click()
}

const handleCoverUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  try {
    saveStatus.value = '上传封面中...'
    const response = await uploadApi.uploadImage(file)
    currentPost.cover_image = response.url
    debounceAutoSave()
    saveStatus.value = '封面上传成功'
    setTimeout(() => {
      saveStatus.value = '已自动保存'
    }, 2000)
  } catch (error) {
    console.error('封面上传失败:', error)
    saveStatus.value = '封面上传失败'
    saveError.value = true
    alert('封面上传失败')
  }
  // 清空input以便可以再次选择同一文件
  target.value = ''
}

const removeCover = () => {
  currentPost.cover_image = ''
  debounceAutoSave()
}

// ╭────────────────────────────────────────────────────────────╮
// │  工具函数
// ╰────────────────────────────────────────────────────────────╯

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes < 1 ? '刚刚' : `${minutes}分钟前`
  }
  // 小于24小时
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  // 默认显示日期
  return date.toLocaleDateString('zh-CN')
}

// 点击外部指令
const vClickOutside = {
  beforeMount(el: HTMLElement, binding: any) {
    el._clickOutside = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el._clickOutside)
  }
}

// ╭────────────────────────────────────────────────────────────╮
// │  Toolbar 悬浮固定逻辑
// ╰────────────────────────────────────────────────────────────╯
const handleEditorScroll = () => {
  const editorArea = document.querySelector('.editor-area')
  if (!editorArea || !toolbarRef.value) return

  // 获取编辑器区域的滚动位置
  const scrollTop = editorArea.scrollTop
  
  // 当滚动超过一定距离时固定toolbar
  // 标题输入框高度约80px，toolbar在标题下方
  const stickyThreshold = 80
  
  if (scrollTop > stickyThreshold) {
    isToolbarSticky.value = true
  } else {
    isToolbarSticky.value = false
  }
}
</script>

<style scoped>
/* ╭────────────────────────────────────────────────────────────╮
   │  顶部导航 - 愿圣光宽恕
   ╰────────────────────────────────────────────────────────────╯ */
.post-edit-view {
  height: 100vh;
  overflow: hidden;
}

.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mobile-menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  align-items: center;
  justify-content: center;
}

.back-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.back-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.group-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.group-selector:hover {
  background: var(--border-subtle);
}

.group-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--bg-primary);
}

.group-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.group-dropdown-icon {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.save-status {
  font-size: 13px;
  color: var(--text-tertiary);
}

.save-status.saving {
  color: var(--accent-primary);
}

.save-status.error {
  color: #ef4444;
}

.nav-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.nav-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.publish-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 6px;
  color: var(--bg-primary);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--glow-primary);
}

.publish-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 分组下拉菜单 */
.group-dropdown {
  position: fixed;
  top: 60px;
  left: 80px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  z-index: 101;
  display: none;
  min-width: 180px;
}

.group-dropdown.active {
  display: block;
}

.group-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.group-dropdown-item:hover {
  background: var(--bg-tertiary);
}

.group-dropdown-item.create-new {
  color: var(--accent-primary);
}

.group-dropdown-item.create-new .group-item-icon {
  background: var(--accent-primary);
}

.group-dropdown-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 8px 0;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  主体布局 - 三栏式工作区
   ╰────────────────────────────────────────────────────────────╯ */
.workspace {
  display: flex;
  height: 100vh;
  padding-top: 56px;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  左侧边栏 - Tab切换式文章列表
   ╰────────────────────────────────────────────────────────────╯ */
.left-sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tab-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.tab-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

.tab-add-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--accent-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-left: auto;
  transition: var(--transition-fast);
}

.tab-add-btn:hover {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

/* 文章列表容器 */
.posts-list-container {
  flex: 1;
  overflow-y: overlay;
  padding: 8px;
  /* 滚动条悬浮 + 自动隐藏 + 主题色 */
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: transparent transparent;
}

.posts-list-container:hover {
  scrollbar-color: color-mix(in srgb, var(--accent-primary) 50%, transparent) transparent;
}

.posts-list-container::-webkit-scrollbar {
  width: 4px;
}

.posts-list-container::-webkit-scrollbar-track {
  background: transparent;
}

.posts-list-container::-webkit-scrollbar-thumb {
  background: transparent;
  border-radius: 2px;
}

.posts-list-container:hover::-webkit-scrollbar-thumb {
  background: color-mix(in srgb, var(--accent-primary) 50%, transparent);
}

.posts-list-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-primary);
}

/* 旧样式保留兼容 */
.groups-section {
  display: none;
}

.section-title {
  display: none;
}

.add-btn {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
}

.add-btn:hover {
  background: var(--bg-tertiary);
  color: var(--accent-primary);
}

.groups-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.group-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.group-item:hover {
  background: var(--bg-tertiary);
}

.group-item.active {
  background: var(--accent-primary);
  color: var(--bg-primary);
}

.group-item.active .group-item-name,
.group-item.active .group-item-count {
  color: var(--bg-primary);
}

.group-item-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--bg-primary);
  flex-shrink: 0;
}

.group-item-name {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-item-count {
  font-size: 12px;
  color: var(--text-tertiary);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 10px;
}

.posts-section {
  display: none;
}

.posts-section.expanded {
  display: none;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.posts-loading {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
}

.posts-empty {
  padding: 30px 20px;
  text-align: center;
  color: var(--text-tertiary);
  font-size: 14px;
  font-style: italic;
}

.drafts-section {
  display: none;
}

.drafts-section .section-title {
  display: none;
}

.draft-count {
  background: var(--accent-primary);
  color: var(--bg-primary);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
}

/* 可折叠标题样式 */
.section-title.collapsible {
  cursor: pointer;
  user-select: none;
}

.section-title.collapsible:hover {
  background: var(--bg-tertiary);
}

.collapse-icon {
  font-size: 10px;
  transition: transform 0.2s ease;
  color: var(--text-secondary);
}

.collapse-icon.expanded {
  transform: rotate(90deg);
}

.post-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.post-item:hover {
  background: var(--bg-tertiary);
}

.post-item.active {
  background: var(--accent-primary);
}

.post-item.active .post-title,
.post-item.active .post-meta {
  color: var(--bg-primary);
}

.post-status {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.post-status.draft {
  background: var(--text-tertiary);
}

.post-status.published {
  background: #22c55e;
}

.post-info {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-size: 14px;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.post-meta {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-menu {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: var(--transition-fast);
}

.post-item:hover .post-menu {
  opacity: 1;
}

.post-menu:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.new-post-btn {
  margin: 16px;
  padding: 10px;
  border: 1px dashed var(--border-subtle);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: var(--transition-fast);
}

.new-post-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

/* 遮罩层 */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 90;
}

.sidebar-overlay.active {
  display: block;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  中央编辑区 - 写作的核心
   ╰────────────────────────────────────────────────────────────╯ */
.editor-area {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-primary);
}

.editor-scroll {
  min-height: 100%;
  padding: 40px 20px;
}

.editor-content {
  max-width: 720px;
  margin: 0 auto;
}

.editor-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: var(--text-tertiary);
}

.title-input {
  width: 100%;
  font-size: 32px;
  font-weight: 700;
  font-family: inherit;
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
  margin-bottom: 24px;
  line-height: 1.3;
}

.title-input::placeholder {
  color: var(--text-tertiary);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 0;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
  flex-wrap: wrap;
  transition: all 0.3s ease;
}

.editor-toolbar.is-sticky {
  position: fixed;
  top: 56px;
  left: 260px;
  right: 280px;
  z-index: 90;
  background: var(--bg-primary);
  padding: 8px 20px;
  margin-bottom: 0;
  border-bottom: 1px solid var(--border-subtle);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 当toolbar固定时，给内容区域添加占位高度 */
.editor-toolbar.is-sticky + .milkdown-content-editor {
  margin-top: 52px;
}

.toolbar-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.toolbar-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toolbar-btn svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-subtle);
  margin: 0 8px;
}

.content-editor {
  min-height: 50vh;
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-primary);
  outline: none;
}

.content-editor :deep(p) {
  margin-bottom: 1.5em;
}

.content-editor :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  margin: 1.5em 0 0.8em;
  color: var(--text-primary);
}

.content-editor :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 1.2em 0 0.6em;
  color: var(--text-primary);
}

.content-editor :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  padding-left: 16px;
  margin: 1.5em 0;
  color: var(--text-secondary);
  font-style: italic;
}

.content-editor :deep(ul),
.content-editor :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.content-editor :deep(li) {
  margin: 0.5em 0;
}

.content-editor :deep(pre) {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: monospace;
  font-size: 14px;
}

.content-editor :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
}

.content-editor :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
}

.content-editor :deep(a:hover) {
  text-decoration: underline;
}

.content-editor :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 1em 0;
}

/* Milkdown编辑器样式 */
.milkdown-content-editor {
  min-height: 50vh;
}

.milkdown-content-editor :deep(.milkdown) {
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-primary);
}

.milkdown-content-editor :deep(.editor) {
  min-height: 50vh;
}

.milkdown-content-editor :deep(p) {
  margin-bottom: 1.5em;
}

.milkdown-content-editor :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  margin: 1.5em 0 0.8em;
  color: var(--text-primary);
}

.milkdown-content-editor :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 1.2em 0 0.6em;
  color: var(--text-primary);
}

.milkdown-content-editor :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  padding-left: 16px;
  margin: 1.5em 0;
  color: var(--text-secondary);
  font-style: italic;
}

.milkdown-content-editor :deep(ul),
.milkdown-content-editor :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.milkdown-content-editor :deep(li) {
  margin: 0.5em 0;
}

.milkdown-content-editor :deep(pre) {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: monospace;
  font-size: 14px;
}

.milkdown-content-editor :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
}

.milkdown-content-editor :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
}

.milkdown-content-editor :deep(a:hover) {
  text-decoration: underline;
}

.milkdown-content-editor :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 1em 0;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  右侧边栏 - 辅助功能
   ╰────────────────────────────────────────────────────────────╯ */
.right-sidebar {
  width: 280px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-subtle);
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 0;
}

.sidebar-section {
  margin-bottom: 24px;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* AI 面板 */
.ai-panel {
  background: var(--bg-tertiary);
  border-radius: 8px;
  padding: 16px;
}

.ai-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.ai-icon {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-icon svg {
  width: 16px;
  height: 16px;
  fill: var(--bg-primary);
}

.ai-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.ai-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ai-btn {
  padding: 8px 12px;
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: var(--transition-fast);
}

.ai-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.ai-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 标签输入 */
.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  min-height: 40px;
}

.tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--accent-primary);
  color: var(--bg-primary);
  border-radius: 4px;
  font-size: 13px;
}

.tag-remove {
  width: 14px;
  height: 14px;
  cursor: pointer;
  fill: currentColor;
  opacity: 0.8;
}

.tag-remove:hover {
  opacity: 1;
}

.tag-input-field {
  flex: 1;
  min-width: 80px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
}

.tag-input-field::placeholder {
  color: var(--text-tertiary);
}

.tag-suggestions {
  margin-top: 8px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  overflow: hidden;
}

.tag-suggestion {
  padding: 8px 12px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-fast);
}

.tag-suggestion:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* 封面上传 */
.cover-upload {
  aspect-ratio: 16/9;
  background: var(--bg-tertiary);
  border: 2px dashed var(--border-subtle);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.cover-upload:hover {
  border-color: var(--accent-primary);
}

.cover-upload svg {
  width: 32px;
  height: 32px;
  fill: var(--text-tertiary);
}

.cover-upload-text {
  font-size: 13px;
  color: var(--text-tertiary);
}

.cover-preview {
  position: relative;
  aspect-ratio: 16/9;
  border-radius: 8px;
  overflow: hidden;
}

.cover-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.cover-remove:hover {
  background: rgba(0,0,0,0.7);
}

/* 设置项 */
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-size: 14px;
  color: var(--text-primary);
}

.toggle {
  width: 44px;
  height: 24px;
  background: var(--bg-tertiary);
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: var(--transition-fast);
}

.toggle.active {
  background: var(--accent-primary);
}

.toggle-dot {
  width: 20px;
  height: 20px;
  background: var(--bg-primary);
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: var(--transition-fast);
}

.toggle.active .toggle-dot {
  left: 22px;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  右键菜单 - 文章操作
   ╰────────────────────────────────────────────────────────────╯ */
.context-menu {
  position: fixed;
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  z-index: 200;
  display: none;
  min-width: 140px;
}

.context-menu.active {
  display: block;
}

.context-menu-item {
  padding: 8px 12px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: 4px;
  transition: var(--transition-fast);
}

.context-menu-item:hover {
  background: var(--bg-tertiary);
}

.context-menu-item.danger {
  color: #ef4444;
}

.context-menu-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* 移动对话框 */
.move-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 16px 48px rgba(0,0,0,0.4);
  z-index: 300;
  display: none;
  min-width: 240px;
}

.move-dialog.active {
  display: block;
}

.move-dialog-header {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.move-dialog-groups {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.move-dialog-group {
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition-fast);
  color: var(--text-primary);
}

.move-dialog-group:hover:not(.disabled) {
  background: var(--bg-tertiary);
}

.move-dialog-group.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ╭────────────────────────────────────────────────────────────╮
   │  响应式适配 - 移动优先
   ╰────────────────────────────────────────────────────────────╯ */
@media (max-width: 1024px) {
  .right-sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }

  .left-sidebar {
    position: fixed;
    top: 56px;
    left: 0;
    bottom: 0;
    z-index: 95;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .left-sidebar.active {
    transform: translateX(0);
  }

  .editor-scroll {
    padding: 24px 16px;
  }

  .title-input {
    font-size: 24px;
  }

  .group-dropdown {
    left: 16px;
  }
}

@media (max-width: 480px) {
  .nav-right {
    gap: 8px;
  }

  .nav-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .publish-btn {
    padding: 6px 14px;
    font-size: 12px;
  }

  .save-status {
    display: none;
  }
}
</style>