/**
 * 文章相关 API
 * 文章增删改查，写不完的CRUD (╯°□°）╯
 */
import { client } from './client'

// 文章类型
export interface Post {
  id: string | number
  title: string
  content?: string
  summary?: string
  introduction?: string  // 后端用的字段名
  cover_image?: string  // 封面图URL
  slug?: string  // URL友好标识
  author_id?: number
  author_name?: string
  group_id?: number
  group_name?: string
  status: 'draft' | 'published' | 'archived'
  view_count: number
  like_count?: number
  created_at: string
  updated_at?: string
  published_at?: string
  tags?: Tag[]
}

// 标签类型
export interface Tag {
  id: number
  name: string
  description?: string
  post_count?: number
}

// 分组类型
export interface Group {
  id: string  // 后端返回UUID字符串
  name: string
  slug?: string  // URL友好标识
  description?: string
  post_count?: number
}

// 文章列表查询参数
export interface PostListParams {
  skip?: number
  limit?: number
  group_id?: string  // 改为string类型，UUID
  tag_id?: number
  author_id?: number
  status?: 'draft' | 'published' | 'archived'
  search?: string
}

// 文章列表响应（后端返回 {items: [...], total: N} 格式）
export interface PostListResponse {
  items: Post[]
  total: number
}

// 创建文章请求
export interface CreatePostRequest {
  title: string
  content: string
  summary?: string
  group_id?: string  // 改为string类型，UUID
  tags?: string[]  // 后端使用标签名字符串数组
  status?: 'draft' | 'published'
}

// 更新文章请求
export interface UpdatePostRequest {
  title?: string
  content?: string
  summary?: string
  group_id?: string  // 改为string类型，UUID
  tags?: string[]  // 后端使用标签名字符串数组
  status?: 'draft' | 'published' | 'archived'
}

// 文章统计
export interface PostStats {
  total_posts: number
  published_posts: number
  draft_posts: number
  total_views: number
}

/**
 * 文章 API
 */
export const postsApi = {
  /**
   * 获取文章列表
   * GET /api/posts
   */
  getList: (params?: PostListParams): Promise<PostListResponse> =>
    client.get('/api/posts', params),

  /**
   * 获取文章详情
   * GET /api/posts/{id}
   */
  getById: (id: string): Promise<Post> =>
    client.get(`/api/posts/${id}`),

  /**
   * 通过slug获取文章详情
   * GET /api/posts/slug/{slug}
   */
  getBySlug: (slug: string): Promise<Post> =>
    client.get(`/api/posts/slug/${slug}`),

  /**
   * 创建文章
   * POST /api/posts
   */
  create: (data: CreatePostRequest): Promise<Post> =>
    client.post('/api/posts', data),

  /**
   * 更新文章
   * PUT /api/posts/{id}
   */
  update: (id: string, data: UpdatePostRequest): Promise<Post> =>
    client.put(`/api/posts/${id}`, data),

  /**
   * 删除文章
   * DELETE /api/posts/{id}
   */
  delete: (id: string): Promise<void> =>
    client.delete(`/api/posts/${id}`),

  /**
   * 获取文章统计
   * GET /api/posts/count
   */
  getStats: (): Promise<{ total: number; published: number; draft: number }> =>
    client.get('/api/posts/count'),

  /**
   * 获取当前用户的文章列表
   * GET /api/posts/my
   */
  getMyPosts: (params?: { skip?: number; limit?: number; status?: string }): Promise<PostListResponse> =>
    client.get('/api/posts/my', params),

  /**
   * 分组 API 子模块
   */
  groups: {
    /**
     * 获取分组列表
     * GET /api/groups
     */
    getList: (params?: { skip?: number; limit?: number }): Promise<Group[]> =>
      client.get('/api/groups', params),

    /**
     * 创建分组
     * POST /api/groups
     */
    create: (data: { name: string; description?: string }): Promise<Group> =>
      client.post('/api/groups', data),

    /**
     * 更新分组
     * PUT /api/groups/{id}
     */
    update: (id: string, data: { name?: string; description?: string }): Promise<Group> =>
      client.put(`/api/groups/${id}`, data),

    /**
     * 删除分组
     * DELETE /api/groups/{id}
     */
    delete: (id: string): Promise<void> =>
      client.delete(`/api/groups/${id}`)
  },

  /**
   * 标签 API 子模块
   */
  tags: {
    /**
     * 获取标签列表
     * GET /api/tags
     */
    getList: (params?: { skip?: number; limit?: number }): Promise<Tag[]> =>
      client.get('/api/tags', params),

    /**
     * 创建标签
     * POST /api/tags
     */
    create: (data: { name: string; description?: string }): Promise<Tag> =>
      client.post('/api/tags', data),

    /**
     * 更新标签
     * PUT /api/tags/{id}
     */
    update: (id: string, data: { name?: string; description?: string }): Promise<Tag> =>
      client.put(`/api/tags/${id}`, data),

    /**
     * 删除标签
     * DELETE /api/tags/{id}
     */
    delete: (id: string): Promise<void> =>
      client.delete(`/api/tags/${id}`)
  }
}

/**
 * 标签 API (独立导出，保持兼容性)
 */
export const tagsApi = {
  /**
   * 获取标签列表
   * GET /api/tags
   */
  getList: (params?: { skip?: number; limit?: number }): Promise<Tag[]> =>
    client.get('/api/tags', params),

  /**
   * 创建标签
   * POST /api/tags
   */
  create: (data: { name: string; description?: string }): Promise<Tag> =>
    client.post('/api/tags', data),

  /**
   * 更新标签
   * PUT /api/tags/{id}
   */
  update: (id: number, data: { name?: string; description?: string }): Promise<Tag> =>
    client.put(`/api/tags/${id}`, data),

  /**
   * 删除标签
   * DELETE /api/tags/{id}
   */
  delete: (id: number): Promise<void> =>
    client.delete(`/api/tags/${id}`)
}

/**
 * 分组 API
 */
export const groupsApi = {
  /**
   * 获取分组列表
   * GET /api/groups
   */
  getList: (params?: { skip?: number; limit?: number }): Promise<Group[]> =>
    client.get('/api/groups', params),

  /**
   * 创建分组
   * POST /api/groups
   */
  create: (data: { name: string; description?: string }): Promise<Group> =>
    client.post('/api/groups', data),

  /**
   * 更新分组
   * PUT /api/groups/{id}
   */
  update: (id: number, data: { name?: string; description?: string }): Promise<Group> =>
    client.put(`/api/groups/${id}`, data),

  /**
   * 删除分组
   * DELETE /api/groups/{id}
   */
  delete: (id: number): Promise<void> =>
    client.delete(`/api/groups/${id}`)
}
