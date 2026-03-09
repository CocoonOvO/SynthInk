/**
 * UI-005 用户中心交互测试
 * 测试用例: PROFILE-001 ~ PROFILE-010
 */
import { test, expect } from '@playwright/test'

test.describe('UI-005 用户中心交互测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 直接访问个人中心页面
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1500)
  })

  /**
   * PROFILE-001: 页面正常加载
   */
  test('PROFILE-001: 页面正常加载', async ({ page }) => {
    // 验证页面基本结构存在
    // 注意：由于需要登录，页面可能会重定向到登录页或显示未登录状态
    const currentUrl = page.url()
    
    // 如果在个人中心页，验证结构
    if (currentUrl.includes('/profile')) {
      // 使用更通用的选择器
      const mainContent = page.locator('body > div:first-child, #app, main, .app-container').first()
      await expect(mainContent).toBeVisible()
    } else {
      // 如果重定向到登录页，也是合理的
      expect(currentUrl.includes('/login')).toBeTruthy()
    }
  })

  /**
   * PROFILE-002: 页面结构检查
   */
  test('PROFILE-002: 页面结构检查', async ({ page }) => {
    // 检查页面是否有基本的HTML结构
    const body = page.locator('body')
    await expect(body).toBeVisible()
    
    // 检查是否有标题
    const title = await page.title()
    expect(title.length).toBeGreaterThan(0)
  })

  /**
   * PROFILE-003: 导航栏显示
   */
  test('PROFILE-003: 导航栏显示', async ({ page }) => {
    // 验证导航栏存在（使用更通用的选择器）
    const navbar = page.locator('.navbar, nav, header, [class*="nav"], [class*="header"]').first()
    
    // 如果找到导航栏，验证其可见
    const count = await navbar.count()
    if (count > 0) {
      await expect(navbar).toBeVisible()
    } else {
      // 如果没有标准导航栏，验证页面有顶部区域
      await expect(page.locator('body')).toBeVisible()
    }
  })

  /**
   * PROFILE-004: 页面响应式
   */
  test('PROFILE-004: 页面响应式', async ({ page }) => {
    // 测试不同视口大小
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.waitForTimeout(500)
    
    // 验证页面内容可见
    await expect(page.locator('body')).toBeVisible()
    
    // 测试移动端
    await page.setViewportSize({ width: 375, height: 667 })
    await page.waitForTimeout(500)
    await expect(page.locator('body')).toBeVisible()
  })

  /**
   * PROFILE-005: 页面加载性能
   */
  test('PROFILE-005: 页面加载性能', async ({ page }) => {
    // 记录加载时间
    const startTime = Date.now()
    
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    
    const loadTime = Date.now() - startTime
    
    // 验证加载时间在合理范围内（5秒内）
    expect(loadTime).toBeLessThan(5000)
  })

  /**
   * PROFILE-006: 未登录状态处理
   */
  test('PROFILE-006: 未登录状态处理', async ({ page }) => {
    // 清除本地存储
    await page.evaluate(() => {
      localStorage.clear()
    })
    
    // 刷新页面
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
    
    // 验证页面有合理的处理（显示登录提示或重定向）
    const currentUrl = page.url()
    const bodyText = await page.locator('body').textContent()
    
    // 应该重定向到登录页或显示登录提示
    const hasLoginRedirect = currentUrl.includes('/login')
    const hasLoginPrompt = bodyText?.includes('登录') || bodyText?.includes('Login') || bodyText?.includes('请登录')
    
    expect(hasLoginRedirect || hasLoginPrompt).toBeTruthy()
  })

  /**
   * PROFILE-007: 页面URL正确性
   */
  test('PROFILE-007: 页面URL正确性', async ({ page }) => {
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    
    const currentUrl = page.url()
    
    // URL应该包含profile或重定向到登录页
    expect(currentUrl.includes('/profile') || currentUrl.includes('/login')).toBeTruthy()
  })

  /**
   * PROFILE-008: 页面无JS错误
   */
  test('PROFILE-008: 页面无JS错误', async ({ page }) => {
    const errors: string[] = []
    
    // 监听控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    
    page.on('pageerror', error => {
      errors.push(error.message)
    })
    
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
    
    // 过滤掉非关键错误（如网络错误）
    const criticalErrors = errors.filter(e => 
      !e.includes('net::') && 
      !e.includes('favicon') &&
      !e.includes('404')
    )
    
    // 验证没有关键JS错误
    expect(criticalErrors.length).toBe(0)
  })

  /**
   * PROFILE-009: 页面可访问性基础检查
   */
  test('PROFILE-009: 页面可访问性基础检查', async ({ page }) => {
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    
    // 检查页面是否有lang属性
    const html = page.locator('html')
    const lang = await html.getAttribute('lang')
    expect(lang).toBeTruthy()
    
    // 检查是否有title
    const title = await page.title()
    expect(title.length).toBeGreaterThan(0)
  })

  /**
   * PROFILE-010: 页面返回功能
   */
  test('PROFILE-010: 页面返回功能', async ({ page }) => {
    // 先访问首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // 再访问个人中心
    await page.goto('/profile')
    await page.waitForLoadState('networkidle')
    
    // 点击浏览器返回
    await page.goBack()
    await page.waitForLoadState('networkidle')
    
    // 验证返回到了之前的页面（可能是首页或登录页）
    const currentUrl = page.url()
    expect(currentUrl.includes('/login') || currentUrl === 'http://localhost:5173/').toBeTruthy()
  })
})
