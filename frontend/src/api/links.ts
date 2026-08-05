/**
 * 外链相关 API
 * 「工具」页面的外部链接管理，公开读、超管写
 */
import { client } from './client'

// 外链类型
export interface ExternalLink {
  id: string
  name: string
  url: string
  cover_image?: string
  sort_order: number
  created_at: string
  updated_at: string
}

// 创建/更新外链请求体
export interface ExternalLinkPayload {
  name: string
  url: string
  cover_image?: string
  sort_order?: number
}

// 外链API
export const linksApi = {
  // 获取外链列表（公开）
  getList: (params?: { skip?: number; limit?: number }): Promise<ExternalLink[]> =>
    client.get('/api/links', params),
  // 创建外链（仅超管）
  create: (data: ExternalLinkPayload): Promise<ExternalLink> =>
    client.post('/api/links', data),
  // 更新外链（仅超管）
  update: (id: string, data: ExternalLinkPayload): Promise<ExternalLink> =>
    client.put(`/api/links/${id}`, data),
  // 删除外链（仅超管）
  delete: (id: string): Promise<void> =>
    client.delete(`/api/links/${id}`)
}
