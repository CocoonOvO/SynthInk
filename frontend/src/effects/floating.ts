/**
 * 浮动装饰元素
 * 从 design-system/js/effects/floating-elements.js 搬运并适配Vue3
 * 
 * 在页面背景生成缓慢浮动的装饰元素
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 浮动元素配置接口
export interface FloatingOptions {
  count?: number        // 元素数量
  shapes?: string[]     // 形状列表
  minSize?: number      // 最小尺寸
  maxSize?: number      // 最大尺寸
  colors?: string[]     // 颜色列表
  zIndex?: number       // z-index
  speed?: number        // 移动速度倍数
}

// 浮动元素接口
interface FloatingElement {
  el: HTMLElement
  x: number
  y: number
  speedX: number
  speedY: number
  rotation: number
  rotationSpeed: number
  opacity: number
}

// 默认配置
const defaultOptions: Required<FloatingOptions> = {
  count: 5,
  shapes: ['circle', 'square', 'triangle'],
  minSize: 20,
  maxSize: 80,
  colors: ['rgba(255,255,255,0.03)'],
  zIndex: -1,
  speed: 1
}

/**
 * Vue3 组合式函数 - 浮动装饰元素
 * 使用方法：const { elements, start, stop } = useFloating({ count: 5 })
 */
export function useFloating(options: FloatingOptions = {}) {
  const config = { ...defaultOptions, ...options }
  const elements = ref<FloatingElement[]>([])
  const isRunning = ref(false)
  let rafId: number | null = null
  let container: HTMLElement | null = null

  /**
   * 创建浮动元素
   */
  const createElements = (parentContainer: HTMLElement) => {
    container = parentContainer

    // 检测减少动画偏好
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return
    }

    for (let i = 0; i < config.count; i++) {
      const el = document.createElement('div')
      const size = random(config.minSize, config.maxSize)
      const shape = config.shapes[Math.floor(Math.random() * config.shapes.length)]
      const color = config.colors[Math.floor(Math.random() * config.colors.length)]

      el.style.cssText = `
        position: fixed;
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        z-index: ${config.zIndex};
        pointer-events: none;
      `

      // 根据形状设置样式
      if (shape === 'circle') {
        el.style.borderRadius = '50%'
      } else if (shape === 'triangle') {
        el.style.width = '0'
        el.style.height = '0'
        el.style.background = 'transparent'
        el.style.borderLeft = `${size / 2}px solid transparent`
        el.style.borderRight = `${size / 2}px solid transparent`
        el.style.borderBottom = `${size}px solid ${color}`
      }

      // 初始位置和动画参数
      const element: FloatingElement = {
        el,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        speedX: (Math.random() - 0.5) * 0.3 * config.speed,
        speedY: (Math.random() - 0.5) * 0.3 * config.speed,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 0.2,
        opacity: Math.random() * 0.5 + 0.1
      }

      el.style.left = `${element.x}px`
      el.style.top = `${element.y}px`
      el.style.opacity = String(element.opacity)

      document.body.appendChild(el)
      elements.value.push(element)
    }
  }

  /**
   * 动画循环
   */
  const animate = () => {
    const update = () => {
      elements.value.forEach((item) => {
        item.x += item.speedX
        item.y += item.speedY
        item.rotation += item.rotationSpeed

        // 边界检测 - 循环移动
        if (item.x < -100) item.x = window.innerWidth + 100
        if (item.x > window.innerWidth + 100) item.x = -100
        if (item.y < -100) item.y = window.innerHeight + 100
        if (item.y > window.innerHeight + 100) item.y = -100

        item.el.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotation}deg)`
      })

      if (isRunning.value) {
        rafId = requestAnimationFrame(update)
      }
    }

    update()
  }

  /**
   * 开始动画
   */
  const start = (parentContainer?: HTMLElement) => {
    if (isRunning.value) return

    // 如果还没有创建元素，先创建
    if (elements.value.length === 0 && parentContainer) {
      createElements(parentContainer)
    }

    isRunning.value = true
    animate()
  }

  /**
   * 停止动画
   */
  const stop = () => {
    isRunning.value = false
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  }

  /**
   * 销毁所有元素
   */
  const destroy = () => {
    stop()
    elements.value.forEach((item) => item.el.remove())
    elements.value = []
  }

  onUnmounted(() => {
    destroy()
  })

  return {
    elements,
    isRunning,
    createElements,
    start,
    stop,
    destroy
  }
}

/**
 * 类方式 - 浮动装饰元素
 * 用于非Vue组件场景
 */
export class FloatingElements {
  private config: Required<FloatingOptions>
  private elements: FloatingElement[] = []
  private rafId: number | null = null
  private isRunning = false

  constructor(options: FloatingOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化浮动元素
   * @param options - 可选的自定义配置
   */
  init(options: FloatingOptions = {}): void {
    const config = { ...this.config, ...options }

    // 检测减少动画偏好
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return
    }

    this.createElements(config)
    this.start()
  }

  /**
   * 创建元素
   */
  private createElements(config: Required<FloatingOptions>): void {
    for (let i = 0; i < config.count; i++) {
      const el = document.createElement('div')
      const size = random(config.minSize, config.maxSize)
      const shape = config.shapes[Math.floor(Math.random() * config.shapes.length)]
      const color = config.colors[Math.floor(Math.random() * config.colors.length)]

      el.style.cssText = `
        position: fixed;
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        z-index: ${config.zIndex};
        pointer-events: none;
      `

      if (shape === 'circle') {
        el.style.borderRadius = '50%'
      } else if (shape === 'triangle') {
        el.style.width = '0'
        el.style.height = '0'
        el.style.background = 'transparent'
        el.style.borderLeft = `${size / 2}px solid transparent`
        el.style.borderRight = `${size / 2}px solid transparent`
        el.style.borderBottom = `${size}px solid ${color}`
      }

      const element: FloatingElement = {
        el,
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        speedX: (Math.random() - 0.5) * 0.3 * config.speed,
        speedY: (Math.random() - 0.5) * 0.3 * config.speed,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 0.2,
        opacity: Math.random() * 0.5 + 0.1
      }

      el.style.left = `${element.x}px`
      el.style.top = `${element.y}px`
      el.style.opacity = String(element.opacity)

      document.body.appendChild(el)
      this.elements.push(element)
    }
  }

  /**
   * 动画循环
   */
  private animate(): void {
    const update = () => {
      this.elements.forEach((item) => {
        item.x += item.speedX
        item.y += item.speedY
        item.rotation += item.rotationSpeed

        if (item.x < -100) item.x = window.innerWidth + 100
        if (item.x > window.innerWidth + 100) item.x = -100
        if (item.y < -100) item.y = window.innerHeight + 100
        if (item.y > window.innerHeight + 100) item.y = -100

        item.el.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotation}deg)`
      })

      if (this.isRunning) {
        this.rafId = requestAnimationFrame(update)
      }
    }

    update()
  }

  /**
   * 开始动画
   */
  start(): void {
    if (this.isRunning) return
    this.isRunning = true
    this.animate()
  }

  /**
   * 停止动画
   */
  stop(): void {
    this.isRunning = false
    if (this.rafId) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
  }

  /**
   * 销毁
   */
  destroy(): void {
    this.stop()
    this.elements.forEach((item) => item.el.remove())
    this.elements = []
  }
}

/**
 * 生成随机数
 */
function random(min: number, max: number): number {
  return Math.random() * (max - min) + min
}

/**
 * 自动初始化
 * 在main.ts中调用
 */
export function autoInitFloating(): void {
  // 检查是否有data-floating属性或全局启用
  if (
    document.querySelector('[data-floating]') ||
    document.body.dataset.floating !== 'false'
  ) {
    const floating = new FloatingElements()
    floating.init()
  }
}

export default FloatingElements
