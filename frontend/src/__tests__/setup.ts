/**
 * Vitest 全局测试配置
 * 每个测试前后清理 localStorage 并重置 fetch mock
 */
import { afterEach, vi } from 'vitest'

// localStorage 测试前清空（jsdom 已提供实现，这里确保每次干净）
afterEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})
