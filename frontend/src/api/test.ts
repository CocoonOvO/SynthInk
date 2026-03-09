/**
 * API 测试脚本
 * 老大说要测试，我就写测试 (´；ω；`)
 * 虽然测试很烦，但还是要测
 */

import { postsApi, authApi, tagsApi, groupsApi, commentsApi, likesApi } from './index'

// 测试结果
interface TestResult {
  name: string
  success: boolean
  data?: any
  error?: string
  duration: number
}

// 测试列表
const results: TestResult[] = []

// 测试包装函数
async function test<T>(name: string, fn: () => Promise<T>): Promise<void> {
  const start = Date.now()
  try {
    const data = await fn()
    results.push({
      name,
      success: true,
      data,
      duration: Date.now() - start
    })
    console.log(`✅ ${name} - ${Date.now() - start}ms`)
  } catch (error: any) {
    results.push({
      name,
      success: false,
      error: error.message,
      duration: Date.now() - start
    })
    console.log(`❌ ${name} - ${error.message}`)
  }
}

// 运行测试
export async function runTests() {
  console.log('🚀 开始API测试...\n')
  
  // 1. 测试文章统计（不需要登录）
  await test('获取文章统计', () => postsApi.getStats())
  
  // 2. 测试文章列表（不需要登录）
  await test('获取文章列表', () => postsApi.getList({ limit: 5 }))
  
  // 3. 测试标签列表
  await test('获取标签列表', () => tagsApi.getList({ limit: 5 }))
  
  // 4. 测试分组列表
  await test('获取分组列表', () => groupsApi.getList({ limit: 5 }))
  
  // 5. 测试评论列表
  await test('获取评论列表', () => commentsApi.getList({ limit: 5 }))
  
  // 6. 测试点赞状态（使用文章ID 1）
  await test('获取点赞状态', () => likesApi.getStatus(1))
  
  // 打印汇总
  console.log('\n📊 测试结果汇总:')
  console.log(`总计: ${results.length} 个测试`)
  console.log(`通过: ${results.filter(r => r.success).length} 个`)
  console.log(`失败: ${results.filter(r => !r.success).length} 个`)
  
  // 打印失败的测试
  const failed = results.filter(r => !r.success)
  if (failed.length > 0) {
    console.log('\n❌ 失败的测试:')
    failed.forEach(r => {
      console.log(`  - ${r.name}: ${r.error}`)
    })
  }
  
  return results
}

// 如果直接运行此文件
if (import.meta.url === `file://${process.cwd()}/src/api/test.ts`) {
  runTests()
}
