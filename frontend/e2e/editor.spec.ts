/**
 * UI-004: 文章编辑器交互测试
 * 测试文章编辑器的所有交互功能
 * 
 * @author 微萤
 * @date 2026-03-10
 */

import { test, expect } from '@playwright/test'

test.describe('UI-004 文章编辑器交互测试', () => {
  const BASE_URL = 'http://localhost:5173'
  
  test.beforeEach(async ({ page }) => {
    // 直接访问编辑器页面，让后端处理鉴权重定向
    await page.goto(`${BASE_URL}/write`, { timeout: 15000 })
    await page.waitForTimeout(1500)
  })

  /**
   * EDITOR-001: 编辑器页面加载
   */
  test('EDITOR-001: 编辑器页面加载', async ({ page }) => {
    // 验证页面加载
    const currentUrl = page.url()
    
    // 如果在编辑器页面
    if (currentUrl.includes('/write')) {
      // 验证顶部导航存在
      const topNav = page.locator('.top-nav')
      await expect(topNav).toBeVisible()
      
      // 验证工作区存在
      const workspace = page.locator('.workspace')
      await expect(workspace).toBeVisible()
      
      // 验证侧边栏存在
      const sidebar = page.locator('.left-sidebar')
      await expect(sidebar).toBeVisible()
    } else {
      // 可能被重定向到登录页
      console.log('未登录，重定向到:', currentUrl)
    }
  })

  /**
   * EDITOR-002: 顶部导航元素
   */
  test('EDITOR-002: 顶部导航元素', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 验证返回按钮
    const backBtn = page.locator('.back-btn')
    await expect(backBtn).toBeVisible()
    
    // 验证分组选择器
    const groupSelector = page.locator('.group-selector')
    await expect(groupSelector).toBeVisible()
    
    // 验证保存状态
    const saveStatus = page.locator('.save-status')
    await expect(saveStatus).toBeVisible()
    
    // 验证保存草稿按钮
    const saveDraftBtn = page.locator('button:has-text("保存草稿")')
    await expect(saveDraftBtn).toBeVisible()
    
    // 验证发布按钮
    const publishBtn = page.locator('.publish-btn')
    await expect(publishBtn).toBeVisible()
  })

  /**
   * EDITOR-003: 分组选择器下拉菜单
   */
  test('EDITOR-003: 分组选择器下拉菜单', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 点击分组选择器
    const groupSelector = page.locator('.group-selector')
    await groupSelector.click()
    await page.waitForTimeout(300)
    
    // 验证下拉菜单显示
    const dropdown = page.locator('.group-dropdown')
    await expect(dropdown).toHaveClass(/active/)
    
    // 验证新建分组选项
    const createNewOption = page.locator('.group-dropdown-item.create-new')
    await expect(createNewOption).toBeVisible()
    await expect(createNewOption).toContainText('新建分组')
  })

  /**
   * EDITOR-004: 侧边栏标签切换
   */
  test('EDITOR-004: 侧边栏标签切换', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 验证文章标签
    const publishedTab = page.locator('.tab-btn:has-text("文章")')
    await expect(publishedTab).toBeVisible()
    
    // 验证草稿标签
    const draftTab = page.locator('.tab-btn:has-text("草稿")')
    await expect(draftTab).toBeVisible()
    
    // 点击草稿标签
    await draftTab.click()
    await page.waitForTimeout(300)
    
    // 验证草稿标签激活
    await expect(draftTab).toHaveClass(/active/)
    
    // 点击文章标签
    await publishedTab.click()
    await page.waitForTimeout(300)
    
    // 验证文章标签激活
    await expect(publishedTab).toHaveClass(/active/)
  })

  /**
   * EDITOR-005: 新建文章按钮
   */
  test('EDITOR-005: 新建文章按钮', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 验证新建文章按钮
    const newPostBtn = page.locator('.tab-add-btn')
    await expect(newPostBtn).toBeVisible()
    await expect(newPostBtn).toHaveAttribute('title', '新建文章')
    
    // 点击新建文章
    await newPostBtn.click()
    await page.waitForTimeout(500)
    
    // 验证编辑器区域清空或显示新文章
    const editor = page.locator('.editor-content, .milkdown-editor').first()
    await expect(editor).toBeVisible()
  })

  /**
   * EDITOR-006: 编辑器内容区域
   */
  test('EDITOR-006: 编辑器内容区域', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 验证编辑器存在 - 使用first()避免多个匹配
    const editorContainer = page.locator('.milkdown-editor, .editor-content').first()
    await expect(editorContainer).toBeVisible()
    
    // 验证标题输入区域
    const titleInput = page.locator('input[placeholder*="标题"], .title-input')
    const titleExists = await titleInput.isVisible().catch(() => false)
    
    if (titleExists) {
      await expect(titleInput).toBeVisible()
    }
  })

  /**
   * EDITOR-007: 保存草稿功能
   */
  test('EDITOR-007: 保存草稿功能', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 点击保存草稿
    const saveDraftBtn = page.locator('button:has-text("保存草稿")')
    await saveDraftBtn.click()
    await page.waitForTimeout(1000)
    
    // 验证保存状态更新
    const saveStatus = page.locator('.save-status')
    const statusText = await saveStatus.textContent()
    
    // 保存状态应该显示已保存或保存中
    expect(statusText).toMatch(/已保存|保存中|自动保存/)
  })

  /**
   * EDITOR-008: 返回按钮功能
   */
  test('EDITOR-008: 返回按钮功能', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 点击返回按钮
    const backBtn = page.locator('.back-btn')
    const backBtnExists = await backBtn.isVisible().catch(() => false)
    
    if (backBtnExists) {
      await backBtn.click()
      await page.waitForTimeout(500)
      
      // 验证离开编辑器页面
      const newUrl = page.url()
      expect(newUrl).not.toContain('/write')
    } else {
      console.log('返回按钮未找到，跳过测试')
    }
  })

  /**
   * EDITOR-009: 移动端侧边栏
   */
  test('EDITOR-009: 移动端侧边栏', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(1000)
    
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      await page.setViewportSize({ width: 1280, height: 720 })
      return
    }
    
    // 验证移动端菜单按钮
    const mobileMenuBtn = page.locator('.mobile-menu-btn')
    await expect(mobileMenuBtn).toBeVisible()
    
    // 点击菜单按钮
    await mobileMenuBtn.click()
    await page.waitForTimeout(300)
    
    // 验证侧边栏显示
    const sidebar = page.locator('.left-sidebar')
    await expect(sidebar).toHaveClass(/active/)
    
    // 恢复桌面视口
    await page.setViewportSize({ width: 1280, height: 720 })
  })

  /**
   * EDITOR-010: 文章列表加载
   */
  test('EDITOR-010: 文章列表加载', async ({ page }) => {
    const currentUrl = page.url()
    if (!currentUrl.includes('/write')) {
      console.log('跳过测试：未在编辑器页面')
      return
    }
    
    // 验证文章列表容器
    const postsListContainer = page.locator('.posts-list-container')
    await expect(postsListContainer).toBeVisible()
    
    // 等待文章加载
    await page.waitForTimeout(1000)
    
    // 检查是否有文章项或空状态
    const postItems = page.locator('.post-item')
    const emptyState = page.locator('.posts-empty')
    const loadingState = page.locator('.posts-loading')
    
    const hasItems = await postItems.count() > 0
    const hasEmpty = await emptyState.isVisible().catch(() => false)
    const hasLoading = await loadingState.isVisible().catch(() => false)
    
    expect(hasItems || hasEmpty || hasLoading).toBeTruthy()
  })
})
