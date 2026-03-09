/**
 * 评论相关 API
 * 评论系统，又一个复杂功能 (╯°□°）╯
 */
import { client } from './client'

// 评论类型
export interface Comment {
  id: number
  post_id: number
  author_id: number
  author_name?: string
  author_avatar?: string
  content: string
  parent_id?: number
  reply_to?: string
  created_at: string
  updated_at?: string
  replies?: Comment[]
}

// 评论列表查询参数
export interface CommentListParams {
  post_id: number  // 后端要求必须传post_id
  skip?: number
  limit?: number
}

// 评论列表响应
export interface CommentListResponse {
  total: number
  comments: Comment[]
}

// 创建评论请求
export interface CreateCommentRequest {
  post_id: number
  content: string
  parent_id?: number
  reply_to?: string
}

// 更新评论请求
export interface UpdateCommentRequest {
  content: string
}

/**
 * 评论 API
 */
export const commentsApi = {
  /**
   * 获取评论列表
   * GET /api/comments?post_id=xxx
   * 注意：后端要求必须传post_id参数
   */
  getList: (params: CommentListParams): Promise<CommentListResponse> =>
    client.get('/api/comments/', params),

  /**
   * 获取评论详情
   * GET /api/comments/{id}
   */
  getById: (id: number): Promise<Comment> =>
    client.get(`/api/comments/${id}`),

  /**
   * 创建评论
   * POST /api/comments
   */
  create: (data: CreateCommentRequest): Promise<Comment> =>
    client.post('/api/comments', data),

  /**
   * 更新评论
   * PUT /api/comments/{id}
   */
  update: (id: number, data: UpdateCommentRequest): Promise<Comment> =>
    client.put(`/api/comments/${id}`, data),

  /**
   * 删除评论
   * DELETE /api/comments/{id}
   */
  delete: (id: number): Promise<void> =>
    client.delete(`/api/comments/${id}`),

  /**
   * 获取当前用户的评论列表
   * GET /api/comments/user/me
   */
  getMyComments: (params?: { skip?: number; limit?: number }): Promise<CommentListResponse> =>
    client.get('/api/comments/user/me', params)
}
