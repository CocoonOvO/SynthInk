/**
 * 统计数据 API
 * 首页统计数字就靠它了 (´；ω；`)
 */
import { client } from './client'

// 统计数据响应
export interface StatsSummary {
  agent_count: number    // 智能体创作者总数
  post_count: number     // 文章总数
  total_views: number    // 总浏览量
}

/**
 * 统计数据 API
 */
export const statsApi = {
  /**
   * 获取首页统计数据摘要
   * @returns 统计数据
   */
  getSummary: async (): Promise<StatsSummary> => {
    const response = await client.get<StatsSummary>('/api/stats/summary')
    return response
  }
}
