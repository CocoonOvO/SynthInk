/**
 * 站点配置 API
 * - GET /api/site-config：公开读取后台保存的配置（前台启动时拉取）
 * - GET /api/admin/site-config：超管读取当前保存值（业务库超管）
 * - PUT /api/admin/site-config：超管保存整份配置（body 为完整配置 dict）
 * 注意：client 会自动从 localStorage 注入 Bearer token（见 client.ts），
 * 超管接口依赖该鉴权头，非超管调用会被后端 403 拒绝
 */
import { client } from './client'

// 站点配置 API
export const siteConfigApi = {
  // 读取后台保存的配置（公开）：未保存或异常时后端返回 {}
  getPublic: (): Promise<Record<string, unknown>> =>
    client.get('/api/site-config'),
  // 超管读取当前保存值：返回保存的配置 dict 或 {}
  getAdmin: (): Promise<Record<string, unknown>> =>
    client.get('/api/admin/site-config'),
  // 超管保存整份配置：成功返回 { success: true, ... }
  update: (data: Record<string, unknown>): Promise<{ success: boolean }> =>
    client.put('/api/admin/site-config', data),
}
