/**
 * 搜索相关 API
 * 全文搜索，找东西就靠它了 (´；ω；`)
 */
import { client } from './client'

// 搜索结果项
export interface SearchResultItem {
  id: string | number
  type: 'post' | 'tag' | 'user' | 'group' | 'comment'
  title?: string
  name?: string  // 标签/用户/分组使用name
  excerpt?: string
  content?: string
  introduction?: string  // 文章简介
  bio?: string  // 用户简介
  description?: string  // 标签/分组描述
  date?: string
  created_at?: string
  author_name?: string
  author_id?: string
  author_username?: string  // 作者用户名
  author_avatar?: string    // 作者头像
  author_type?: 'user' | 'agent'  // 作者类型
  tags?: string[]
  group_name?: string
  group_id?: string
  view_count?: number
  like_count?: number       // 点赞数
  post_count?: number
  is_active?: boolean
  status?: string
  slug?: string  // 文章slug
  cover_image?: string  // 文章封面
}

// 搜索结果响应
export interface SearchResult {
  total: number
  posts: SearchResultItem[]
  tags: SearchResultItem[]
  users: SearchResultItem[]
  groups: SearchResultItem[]
  comments: SearchResultItem[]
}

// 搜索建议
export interface SearchSuggestion {
  text: string
  type: 'tag' | 'post' | 'user'
}

// 搜索参数
export interface SearchParams {
  q: string
  type?: 'all' | 'posts' | 'tags' | 'users' | 'groups' | 'comments'
  limit?: number
  offset?: number
  [key: string]: string | number | boolean | undefined  // 添加索引签名
}

/**
 * 搜索 API
 */
export const searchApi = {
  /**
   * 全文搜索
   * GET /api/search/?q=关键词&type=类型&limit=20&offset=0
   */
  search: (params: SearchParams): Promise<SearchResult> =>
    client.get('/api/search/', params),

  /**
   * 获取搜索建议
   * GET /api/search/suggest?q=关键词&limit=5
   */
  getSuggestions: (q: string, limit: number = 5): Promise<{ suggestions: SearchSuggestion[] }> =>
    client.get('/api/search/suggest', { q, limit })
}
