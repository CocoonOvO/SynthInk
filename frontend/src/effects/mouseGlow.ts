/**
 * 鼠标跟随光晕效果
 * 从 design-system/js/effects/mouse-glow.js 搬运并适配Vue3
 * 
 * 鼠标移动时产生跟随的光晕效果，触摸设备自动禁用
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 鼠标光晕配置接口
export interface MouseGlowOptions {
  size?: number       // 光晕大小(px)
  blur?: number       // 模糊程度(px)
  opacity?: number    // 不透明度
  color?: string      // 颜色（CSS变量或颜色值）
  smooth?: number     // 平滑系数(0-1)
}

// 默认配置
const defaultOptions: Required<MouseGlowOptions> = {
  size: 200,
  blur: 50,
  opacity: 0.15,
  color: 'var(--accent-primary)',
  smooth: 0.1
}

/**
 * Vue3 组合式函数 - 鼠标跟随光晕
 * 使用方法：const { isActive, glowStyle } = useMouseGlow({ size: 200 })
 */
export function useMouseGlow(options: MouseGlowOptions = {}) {
  const config = { ...defaultOptions, ...options }
  const isActive = ref(false)
  const glowStyle = ref<Record<string, string>>({
    position: 'fixed',
    width: `${config.size}px`,
    height: `${config.size}px`,
    borderRadius: '50%',
    filter: `blur(${config.blur}px)`,
    opacity: '0',
    pointerEvents: 'none',
    zIndex: '9999',
    transform: 'translate(-50%, -50%)',
    transition: 'opacity 0.3s ease'
  })
  
  const mouseX = ref(0)
  const mouseY = ref(0)
  const currentX = ref(0)
  const currentY = ref(0)
  let rafId: number | null = null

  /**
   * 获取当前主题色
   */
  const getColor = (): string => {
    const style = getComputedStyle(document.body)
    const accent = style.getPropertyValue('--accent-primary').trim()
    return accent || config.color
  }

  /**
   * 更新光晕背景
   */
  const updateGlowBackground = () => {
    const color = getColor()
    glowStyle.value.background = `radial-gradient(circle, ${color} 0%, transparent 70%)`
  }

  /**
   * 动画循环 - 平滑跟随
   */
  const animate = () => {
    const update = () => {
      // 平滑跟随
      currentX.value += (mouseX.value - currentX.value) * config.smooth
      currentY.value += (mouseY.value - currentY.value) * config.smooth

      glowStyle.value.left = `${currentX.value}px`
      glowStyle.value.top = `${currentY.value}px`

      rafId = requestAnimationFrame(update)
    }

    update()
  }

  /**
   * 处理鼠标移动
   */
  const handleMouseMove = (e: MouseEvent) => {
    mouseX.value = e.clientX
    mouseY.value = e.clientY
    isActive.value = true
    glowStyle.value.opacity = String(config.opacity)
  }

  /**
   * 处理鼠标离开
   */
  const handleMouseLeave = () => {
    isActive.value = false
    glowStyle.value.opacity = '0'
  }

  /**
   * 处理主题变化
   */
  const handleThemeChange = () => {
    updateGlowBackground()
  }

  onMounted(() => {
    // 检测是否为触摸设备
    if (window.matchMedia('(pointer: coarse)').matches) {
      return // 触摸设备不启用
    }

    updateGlowBackground()
    
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseleave', handleMouseLeave)
    window.addEventListener('themechange', handleThemeChange)
    
    animate()
  })

  onUnmounted(() => {
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseleave', handleMouseLeave)
    window.removeEventListener('themechange', handleThemeChange)
    
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
  })

  return {
    isActive,
    glowStyle
  }
}

/**
 * 类方式 - 鼠标跟随光晕
 * 用于非Vue组件场景
 */
export class MouseGlow {
  private config: Required<MouseGlowOptions>
  private mouseX = 0
  private mouseY = 0
  private currentX = 0
  private currentY = 0
  private glow: HTMLElement | null = null
  private rafId: number | null = null

  constructor(options: MouseGlowOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化鼠标光晕
   * @param options - 可选的自定义配置
   */
  init(options: MouseGlowOptions = {}): void {
    const config = { ...this.config, ...options }

    // 检测是否为触摸设备
    if (window.matchMedia('(pointer: coarse)').matches) {
      return // 触摸设备不启用
    }

    this.createGlow(config)
    this.bindEvents()
    this.animate()
  }

  /**
   * 创建光晕元素
   */
  private createGlow(config: Required<MouseGlowOptions>): void {
    this.glow = document.createElement('div')
    this.glow.className = 'mouse-glow'
    this.glow.style.cssText = `
      position: fixed;
      width: ${config.size}px;
      height: ${config.size}px;
      border-radius: 50%;
      background: radial-gradient(circle, ${this.getColor()} 0%, transparent 70%);
      filter: blur(${config.blur}px);
      opacity: 0;
      pointer-events: none;
      z-index: 9999;
      transform: translate(-50%, -50%);
      transition: opacity 0.3s ease;
    `
    document.body.appendChild(this.glow)
  }

  /**
   * 获取当前主题色
   */
  private getColor(): string {
    const style = getComputedStyle(document.body)
    const accent = style.getPropertyValue('--accent-primary').trim()
    return accent || this.config.color
  }

  /**
   * 绑定事件
   */
  private bindEvents(): void {
    document.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX
      this.mouseY = e.clientY

      if (this.glow) {
        this.glow.style.opacity = String(this.config.opacity)
      }
    })

    document.addEventListener('mouseleave', () => {
      if (this.glow) {
        this.glow.style.opacity = '0'
      }
    })

    // 监听主题变化
    window.addEventListener('themechange', () => {
      if (this.glow) {
        this.glow.style.background = `radial-gradient(circle, ${this.getColor()} 0%, transparent 70%)`
      }
    })
  }

  /**
   * 动画循环
   */
  private animate(): void {
    const update = () => {
      // 平滑跟随
      this.currentX += (this.mouseX - this.currentX) * this.config.smooth
      this.currentY += (this.mouseY - this.currentY) * this.config.smooth

      if (this.glow) {
        this.glow.style.left = `${this.currentX}px`
        this.glow.style.top = `${this.currentY}px`
      }

      this.rafId = requestAnimationFrame(update)
    }

    update()
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    if (this.rafId) {
      cancelAnimationFrame(this.rafId)
    }
    if (this.glow) {
      this.glow.remove()
    }
  }
}

/**
 * 自动初始化
 * 在main.ts中调用
 */
export function autoInitMouseGlow(): void {
  if (
    document.querySelector('[data-mouse-glow]') ||
    document.body.dataset.mouseGlow !== 'false'
  ) {
    const mouseGlow = new MouseGlow()
    mouseGlow.init()
  }
}

export default MouseGlow
