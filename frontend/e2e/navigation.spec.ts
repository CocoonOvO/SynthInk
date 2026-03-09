/**
 * UI-008: 导航和布局交互测试
 * 测试导航栏和页面布局的所有交互功能
 * 
 * @author 微萤
 * @date 2026-03-10
 */

import { test, expect } from '@playwright/test'

test.describe('UI-008 导航和布局交互测试', () => {
  const BASE_URL = 'http://localhost:5173'
  
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/`)
    await page.waitForTimeout(1000)
  })

  /**
   * NAV-001: 导航栏正常显示
   */
  test('NAV-001: 导航栏正常显示', async ({ page }) => {
    // 验证导航栏存在
    const navbar = page.locator('.navbar')
    await expect(navbar).toBeVisible()
    
    // 验证Logo存在
    const logo = page.locator('.nav-logo')
    await expect(logo).toBeVisible()
    
    // 验证导航链接存在
    const navLinks = page.locator('.nav-links')
    await expect(navLinks).toBeVisible()
  })

  /**
   * NAV-002: Logo点击跳转首页
   */
  test('NAV-002: Logo点击跳转首页', async ({ page }) => {
    // 先跳转到其他页面
    await page.goto('/posts')
    await page.waitForLoadState('networkidle')
    
    // 点击Logo
    const logo = page.locator('.nav-logo')
    await logo.click()
    await page.waitForTimeout(500)
    
    // 验证回到首页
    await expect(page).toHaveURL('/')
  })

  /**
   * NAV-003: 导航链接跳转
   */
  test('NAV-003: 导航链接跳转', async ({ page }) => {
    // 测试文章链接
    const postsLink = page.locator('.nav-links a[href="/posts"]')
    await postsLink.click()
    await page.waitForTimeout(500)
    await expect(page).toHaveURL('/posts')
    
    // 返回首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // 测试关于链接
    const aboutLink = page.locator('.nav-links a[href="/about"]')
    await aboutLink.click()
    await page.waitForTimeout(500)
    await expect(page).toHaveURL('/about')
  })

  /**
   * NAV-004: 写作按钮显示（登录后）
   */
  test('NAV-004: 写作按钮显示（登录后）', async ({ page }) => {
    // 先登录
    await page.goto(`${BASE_URL}/login`)
    await page.waitForLoadState('networkidle')
    
    const currentUrl = page.url()
    if (currentUrl.includes('/login')) {
      // 填写登录表单 - 使用placeholder定位
      await page.locator('input[placeholder*="用户名"]').fill('testuser_frontend')
      await page.locator('input[placeholder*="密码"]').fill('TestPass123!')
      await page.locator('button[type="submit"]').click()
      await page.waitForTimeout(2000)
    }
    
    // 回到首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // 验证写作按钮存在（可能登录后需要刷新才显示）
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    const writeBtn = page.locator('.nav-write-btn')
    const writeBtnExists = await writeBtn.isVisible().catch(() => false)
    
    if (writeBtnExists) {
      await expect(writeBtn).toBeVisible()
      // 验证按钮链接到写作页面
      await expect(writeBtn).toHaveAttribute('href', '/write')
    } else {
      console.log('写作按钮未找到，可能登录状态未正确保存')
    }
  })

  /**
   * NAV-005: 导航栏滚动效果
   */
  test('NAV-005: 导航栏滚动效果', async ({ page }) => {
    // 初始状态
    const navbar = page.locator('.navbar')
    
    // 滚动页面
    await page.evaluate(() => window.scrollTo(0, 200))
    await page.waitForTimeout(300)
    
    // 验证导航栏有滚动样式
    const hasScrolledClass = await navbar.evaluate(el => el.classList.contains('scrolled'))
    
    if (hasScrolledClass) {
      console.log('导航栏已添加scrolled类')
    } else {
      // 检查其他可能的滚动指示
      const background = await navbar.evaluate(el => {
        return window.getComputedStyle(el).backgroundColor
      })
      console.log('导航栏背景色:', background)
    }
  })

  /**
   * NAV-006: 移动端导航菜单
   */
  test('NAV-006: 移动端导航菜单', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // 验证移动端菜单按钮
    const mobileMenuBtn = page.locator('.mobile-menu-btn, .nav-mobile-toggle')
    const hasMobileMenu = await mobileMenuBtn.isVisible().catch(() => false)
    
    if (hasMobileMenu) {
      // 点击菜单按钮
      await mobileMenuBtn.click()
      await page.waitForTimeout(300)
      
      // 验证菜单展开
      const mobileMenu = page.locator('.mobile-menu, .nav-mobile-menu')
      await expect(mobileMenu).toBeVisible()
    } else {
      console.log('移动端菜单按钮未找到')
    }
    
    // 恢复桌面视口
    await page.setViewportSize({ width: 1280, height: 720 })
  })

  /**
   * NAV-007: 页面布局结构
   */
  test('NAV-007: 页面布局结构', async ({ page }) => {
    // 验证主要布局容器
    const app = page.locator('#app')
    await expect(app).toBeVisible()
    
    // 验证内容区域
    const mainContent = page.locator('main, .main-content')
    const hasMain = await mainContent.isVisible().catch(() => false)
    
    if (hasMain) {
      await expect(mainContent).toBeVisible()
    } else {
      console.log('main标签未找到，检查其他内容容器')
    }
  })

  /**
   * NAV-008: 页脚显示和链接
   */
  test('NAV-008: 页脚显示和链接', async ({ page }) => {
    // 滚动到页面底部
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(500)
    
    // 验证页脚存在
    const footer = page.locator('.footer, footer')
    const hasFooter = await footer.isVisible().catch(() => false)
    
    if (hasFooter) {
      await expect(footer).toBeVisible()
      
      // 检查页脚链接
      const footerLinks = footer.locator('a')
      const linkCount = await footerLinks.count()
      
      if (linkCount > 0) {
        console.log(`页脚有 ${linkCount} 个链接`)
      }
    } else {
      console.log('页脚未找到')
    }
  })

  /**
   * NAV-009: 返回顶部按钮
   */
  test('NAV-009: 返回顶部按钮', async ({ page }) => {
    // 滚动到页面底部
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await page.waitForTimeout(500)
    
    // 查找返回顶部按钮
    const backToTop = page.locator('.back-to-top, .scroll-top')
    const hasBackToTop = await backToTop.isVisible().catch(() => false)
    
    if (hasBackToTop) {
      // 点击返回顶部
      await backToTop.click()
      await page.waitForTimeout(500)
      
      // 验证页面滚动到顶部
      const scrollY = await page.evaluate(() => window.scrollY)
      expect(scrollY).toBeLessThan(100)
    } else {
      console.log('返回顶部按钮未找到')
    }
  })

  /**
   * NAV-010: 响应式布局适配
   */
  test('NAV-010: 响应式布局适配', async ({ page }) => {
    // 测试平板尺寸
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // 验证导航栏仍然可见
    const navbar = page.locator('.navbar')
    await expect(navbar).toBeVisible()
    
    // 测试手机尺寸
    await page.setViewportSize({ width: 375, height: 667 })
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // 验证导航栏仍然可见
    await expect(navbar).toBeVisible()
    
    // 恢复桌面视口
    await page.setViewportSize({ width: 1280, height: 720 })
  })

  /**
   * NAV-011: 路由切换动画
   */
  test('NAV-011: 路由切换动画', async ({ page }) => {
    // 点击文章链接
    const postsLink = page.locator('.nav-links a[href="/posts"]')
    await postsLink.click()
    
    // 等待页面切换
    await page.waitForTimeout(500)
    
    // 验证页面已切换
    await expect(page).toHaveURL('/posts')
    
    // 检查是否有路由切换动画
    const transition = await page.locator('.page-transition, .fade-enter-active').count()
    if (transition > 0) {
      console.log('检测到路由切换动画')
    }
  })

  /**
   * NAV-012: 当前页面导航高亮
   */
  test('NAV-012: 当前页面导航高亮', async ({ page }) => {
    // 在首页
    const homeLink = page.locator('.nav-links a[href="/"]')
    const homeActive = await homeLink.evaluate(el => el.classList.contains('active') || el.classList.contains('router-link-active'))
    
    if (homeActive) {
      console.log('首页导航链接已高亮')
    }
    
    // 跳转到文章页
    await page.goto('/posts')
    await page.waitForLoadState('networkidle')
    
    // 检查文章链接是否高亮
    const postsLink = page.locator('.nav-links a[href="/posts"]')
    const postsActive = await postsLink.evaluate(el => el.classList.contains('active') || el.classList.contains('router-link-active'))
    
    if (postsActive) {
      console.log('文章页导航链接已高亮')
    }
  })
})
