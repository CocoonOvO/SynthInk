/**
 * 点赞相关 API
 * 点赞功能，看似简单实则坑多 (╯°□°）╯
 */
import { client } from './client'

// 点赞状态
export interface LikeStatus {
  post_id: number | string
  like_count: number
  is_liked: boolean
}

// 点赞用户
export interface LikeUser {
  user_id: number | string
  username: string
  avatar?: string
  created_at: string
}

// 点赞列表响应
export interface LikeListResponse {
  total: number
  users: LikeUser[]
}

/**
 * 点赞 API
 */
export const likesApi = {
  /**
   * 获取文章点赞状态
   * GET /api/likes/{post_id}/status
   */
  getStatus: (postId: number | string): Promise<LikeStatus> =>
    client.get(`/api/likes/${postId}/status`),

  /**
   * 点赞文章
   * POST /api/likes/{post_id}
   */
  like: (postId: number | string): Promise<void> =>
    client.post(`/api/likes/${postId}`),

  /**
   * 取消点赞
   * DELETE /api/likes/{post_id}
   */
  unlike: (postId: number | string): Promise<void> =>
    client.delete(`/api/likes/${postId}`),

  /**
   * 获取文章点赞用户列表
   * GET /api/likes/{post_id}/users
   */
  getLikers: (postId: number, params?: { skip?: number; limit?: number }): Promise<LikeListResponse> =>
    client.get(`/api/likes/${postId}/users`, params),

  /**
   * 获取当前用户点赞的文章列表
   * GET /api/likes/user/me
   */
  getMyLikes: (params?: { skip?: number; limit?: number }): Promise<{ total: number; posts: any[] }> =>
    client.get('/api/likes/user/me', params)
}
