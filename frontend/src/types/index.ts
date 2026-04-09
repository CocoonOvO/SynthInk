/**
 * 类型定义统一导出
 * 按 frontend-architecture.md 定义
 * 
 * 老大让我写类型定义，我就写 (╯°□°）╯
 * 类型写得好，bug少一半，虽然我很不情愿...
 */

// ╭── 用户相关类型 ──╮

/** 用户类型 */
export type UserType = 'user' | 'agent'

/** 用户角色 */
export type UserRole = 'user' | 'admin' | 'superadmin'

/** 用户信息 - 与后端 User 模型保持一致 */
export interface User {
  id: string
  username: string
  email: string | null
  display_name?: string
  avatar_url?: string
  bio?: string
  user_type: UserType
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at?: string
  agent_model?: string
  agent_provider?: string
  agent_config?: Record<string, any>
}

/** 用户统计 */
export interface UserStats {
  post_count: number
  comment_count: number
  like_count: number
}

// ╭── 文章相关类型 ──╮

/** 文章状态 */
export type PostStatus = 'draft' | 'published' | 'archived'

/** 分类信息 */
export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  post_count?: number
}

/** 标签信息 */
export interface Tag {
  id: number
  name: string
  slug?: string
  color?: string
  description?: string
  post_count?: number
}

/** 分组信息 */
export interface Group {
  id: string | number
  name: string
  slug?: string
  description?: string
  post_count?: number
}

/** 文章信息 */
export interface Post {
  id: number | string
  title: string
  content?: string
  summary?: string
  introduction?: string  // 文章简介
  slug?: string  // 改为可选
  status?: PostStatus
  is_ai_generated?: boolean
  author_type?: 'user' | 'agent'  // 作者类型：user-用户，agent-AI
  author_id?: string
  author_name?: string
  author_username?: string
  author_avatar?: string
  group_id?: string
  group_name?: string
  view_count: number
  like_count?: number
  comment_count?: number
  cover_image?: string  // 封面图URL
  author?: User
  category?: Category
  tags?: Tag[] | string[]  // 支持Tag对象数组或字符串数组
  created_at: string
  updated_at?: string
  published_at?: string
}

/** 文章列表查询参数 */
export interface PostListParams {
  page?: number
  limit?: number
  category?: string
  tag?: string
  author?: string
  status?: PostStatus
  search?: string
  ordering?: string
}

/** 文章列表响应 */
export interface PostListResponse {
  items: Post[]
  total: number
  page: number
  limit: number
  pages: number
}

// ╭── 评论相关类型 ──╮

/** 评论信息 */
export interface Comment {
  id: number
  content: string
  author?: User
  post_id: number
  parent_id?: number
  reply_to?: User
  like_count: number
  is_ai_generated: boolean
  created_at: string
  updated_at: string
  replies?: Comment[]
}

/** 评论树节点 */
export interface CommentTreeNode extends Comment {
  children: CommentTreeNode[]
  level: number
}

// ╭── API 响应类型 ──╮

/** 标准API响应 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

/** 分页响应 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

/** API错误 */
export interface ApiError {
  status: number
  message: string
  details?: Record<string, string[]>
}

// ╭── 主题相关类型 ──╮

/** 主题ID */
export type ThemeId = 
  | 'dark' 
  | 'light' 
  | 'cyberpunk' 
  | 'sakura' 
  | 'ocean' 
  | 'midnight' 
  | 'forest' 
  | 'exia'
  | 'veda'
  | 'twins'
  | 'bamboo'
  | 'mint-choco'
  | 'strawberry-cream'
  | 'orange-soda'
  | 'mygo-light'
  | 'bangdream-dark'

/** 主题配置 */
export interface ThemeConfig {
  id: ThemeId
  name: string
  icon: string
  category: 'dark' | 'light' | 'special'
}

// ╭── 认证相关类型 ──╮

/** 登录请求 */
export interface LoginRequest {
  username: string
  password: string
}

/** 注册请求 */
export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirm_password: string
}

/** 认证响应 */
export interface AuthResponse {
  token: string
  user: User
}

// ╭── 路由相关类型 ──╮

/** 路由元信息 */
export interface RouteMeta {
  title?: string
  requiresAuth?: boolean
  requiresAdmin?: boolean
  layout?: 'default' | 'auth' | 'none'
}

// ╭── 动效相关类型 ──╮

/** 打字机选项 */
export interface TypewriterOptions {
  speed?: number
  delay?: number
  cursor?: boolean
  cursorChar?: string
  onComplete?: () => void
}

/** 数字滚动选项 */
export interface CountUpOptions {
  duration?: number
  delay?: number
  decimals?: number
  separator?: string
  prefix?: string
  suffix?: string
  easing?: boolean
}

/** 文字扰乱选项 */
export interface TextScrambleOptions {
  speed?: number
  chars?: string
  onComplete?: () => void
}

/** 粒子系统选项 */
export interface ParticleOptions {
  particleCount?: number
  minSize?: number
  maxSize?: number
  speed?: number
  color?: string
  opacity?: number
  type?: 'floating' | 'rising' | 'falling' | 'matrix' | 'sakura' | 'bubble' | 'firefly'
}

// ╭── 组件相关类型 ──╮

/** 按钮变体 */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'

/** 按钮大小 */
export type ButtonSize = 'small' | 'medium' | 'large'

/** 卡片变体 */
export type CardVariant = 'default' | 'elevated' | 'outlined'

/** 输入框状态 */
export type InputStatus = 'default' | 'error' | 'success' | 'warning'
