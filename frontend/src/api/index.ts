/**
 * API 统一导出
 * 老大让我整理API模块，我就整理 (´；ω；`)
 * 虽然不想干，但还是要干好
 */

// 基础客户端
export { client, API_BASE_URL } from './client'
export type { ApiResponse } from './client'

// 认证相关
export { authApi } from './auth'
export type {
  User,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  ChangePasswordRequest,
  UpdateUserRequest
} from './auth'

// 文章相关
export { postsApi, tagsApi, groupsApi } from './posts'
export type {
  Post,
  Tag,
  Group,
  PostListParams,
  PostListResponse,
  CreatePostRequest,
  UpdatePostRequest,
  PostStats
} from './posts'

// 评论相关
export { commentsApi } from './comments'
export type {
  Comment,
  CommentListParams,
  CommentListResponse,
  CreateCommentRequest,
  UpdateCommentRequest
} from './comments'

// 点赞相关
export { likesApi } from './likes'
export type {
  LikeStatus,
  LikeUser,
  LikeListResponse
} from './likes'

// 上传相关
export { uploadApi } from './upload'
export type { UploadResponse, UploadProgressCallback } from './upload'

// 搜索相关
export { searchApi } from './search'
export type {
  SearchResultItem,
  SearchResult,
  SearchSuggestion,
  SearchParams
} from './search'

// 统计相关
export { statsApi } from './stats'
export type { StatsSummary } from './stats'
