/**
 * 3D卡片倾斜效果
 * 从 design-system/js/effects/tilt-card.js 搬运并适配Vue3
 * 
 * 鼠标悬停时卡片产生3D倾斜效果，带反光
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 3D倾斜配置接口
export interface TiltCardOptions {
  maxTilt?: number      // 最大倾斜角度
  perspective?: number  // 透视距离
  scale?: number        // 悬停缩放
  speed?: number        // 过渡速度(ms)
  glare?: boolean       // 是否启用反光
  maxGlare?: number     // 最大反光强度
}

// 默认配置
const defaultOptions: Required<TiltCardOptions> = {
  maxTilt: 15,
  perspective: 1000,
  scale: 1.02,
  speed: 400,
  glare: true,
  maxGlare: 0.3
}

/**
 * Vue3 组合式函数 - 3D卡片倾斜
 * 使用方法：const { cardStyle, glareStyle } = useTiltCard({ maxTilt: 15 })
 */
export function useTiltCard(options: TiltCardOptions = {}) {
  const config = { ...defaultOptions, ...options }
  const cardStyle = ref<Record<string, string>>({
    transformStyle: 'preserve-3d',
    transition: `transform ${config.speed}ms ease`
  })
  const glareStyle = ref<Record<string, string>>({
    position: 'absolute',
    top: '0',
    left: '0',
    right: '0',
    bottom: '0',
    borderRadius: 'inherit',
    background: 'linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 100%)',
    pointerEvents: 'none',
    zIndex: '10',
    opacity: '0',
    transition: `opacity ${config.speed}ms ease`
  })
  const isHovered = ref(false)

  /**
   * 处理鼠标移动
   */
  const handleMouseMove = (e: MouseEvent, el: HTMLElement) => {
    const rect = el.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateX = ((y - centerY) / centerY) * -config.maxTilt
    const rotateY = ((x - centerX) / centerX) * config.maxTilt

    cardStyle.value.transform = `
      perspective(${config.perspective}px)
      rotateX(${rotateX}deg)
      rotateY(${rotateY}deg)
      scale3d(${config.scale}, ${config.scale}, ${config.scale})
    `

    // 更新反光
    if (config.glare) {
      const glareX = (x / rect.width) * 100
      const glareY = (y / rect.height) * 100
      glareStyle.value.background = `
        radial-gradient(circle at ${glareX}% ${glareY}%, 
        rgba(255,255,255,${config.maxGlare}) 0%, 
        rgba(255,255,255,0) 60%)
      `
      glareStyle.value.opacity = '1'
    }
  }

  /**
   * 处理鼠标离开
   */
  const handleMouseLeave = () => {
    isHovered.value = false
    cardStyle.value.transform = `
      perspective(${config.perspective}px)
      rotateX(0deg)
      rotateY(0deg)
      scale3d(1, 1, 1)
    `
    glareStyle.value.opacity = '0'
  }

  /**
   * 处理鼠标进入
   */
  const handleMouseEnter = () => {
    isHovered.value = true
    cardStyle.value.transition = 'none'
  }

  return {
    cardStyle,
    glareStyle,
    isHovered,
    handleMouseMove,
    handleMouseLeave,
    handleMouseEnter
  }
}

/**
 * 类方式 - 3D卡片倾斜
 * 用于非Vue组件场景
 */
export class TiltCard {
  private config: Required<TiltCardOptions>

  constructor(options: TiltCardOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化3D倾斜效果
   * @param selector - CSS选择器或HTMLElement
   * @param customOptions - 可选的自定义配置
   */
  init(
    selector: string | HTMLElement | NodeListOf<HTMLElement>,
    customOptions: TiltCardOptions = {}
  ): void {
    const config = { ...this.config, ...customOptions }

    const elements = typeof selector === 'string'
      ? document.querySelectorAll<HTMLElement>(selector)
      : selector instanceof NodeList
        ? Array.from(selector)
        : [selector]

    elements.forEach((el) => {
      this.bindEvents(el, config)
    })
  }

  /**
   * 绑定事件
   */
  private bindEvents(el: HTMLElement, config: Required<TiltCardOptions>): void {
    // 触摸设备跳过
    if (window.matchMedia('(pointer: coarse)').matches) return

    el.style.transformStyle = 'preserve-3d'
    el.style.transition = `transform ${config.speed}ms ease`

    if (config.glare) {
      this.createGlare(el, config)
    }

    el.addEventListener('mousemove', (e) => this.handleMouseMove(e, el, config))
    el.addEventListener('mouseleave', () => this.handleMouseLeave(el, config))
    el.addEventListener('mouseenter', () => this.handleMouseEnter(el, config))
  }

  /**
   * 创建反光层
   */
  private createGlare(el: HTMLElement, config: Required<TiltCardOptions>): void {
    const glare = document.createElement('div')
    glare.className = 'tilt-glare'
    glare.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      border-radius: inherit;
      background: linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 100%);
      pointer-events: none;
      z-index: 10;
      opacity: 0;
      transition: opacity ${config.speed}ms ease;
    `
    el.appendChild(glare)
    el.dataset.glare = 'true'
  }

  /**
   * 处理鼠标移动
   */
  private handleMouseMove(
    e: MouseEvent,
    el: HTMLElement,
    config: Required<TiltCardOptions>
  ): void {
    const rect = el.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const rotateX = ((y - centerY) / centerY) * -config.maxTilt
    const rotateY = ((x - centerX) / centerX) * config.maxTilt

    el.style.transform = `
      perspective(${config.perspective}px)
      rotateX(${rotateX}deg)
      rotateY(${rotateY}deg)
      scale3d(${config.scale}, ${config.scale}, ${config.scale})
    `

    // 更新反光
    if (el.dataset.glare === 'true') {
      const glare = el.querySelector('.tilt-glare') as HTMLElement
      if (glare) {
        const glareX = (x / rect.width) * 100
        const glareY = (y / rect.height) * 100
        glare.style.background = `
          radial-gradient(circle at ${glareX}% ${glareY}%, 
          rgba(255,255,255,${config.maxGlare}) 0%, 
          rgba(255,255,255,0) 60%)
        `
        glare.style.opacity = '1'
      }
    }
  }

  /**
   * 处理鼠标离开
   */
  private handleMouseLeave(
    el: HTMLElement,
    config: Required<TiltCardOptions>
  ): void {
    el.style.transform = `
      perspective(${config.perspective}px)
      rotateX(0deg)
      rotateY(0deg)
      scale3d(1, 1, 1)
    `

    const glare = el.querySelector('.tilt-glare') as HTMLElement
    if (glare) {
      glare.style.opacity = '0'
    }
  }

  /**
   * 处理鼠标进入
   */
  private handleMouseEnter(
    el: HTMLElement,
    config: Required<TiltCardOptions>
  ): void {
    el.style.transition = 'none'
  }
}

/**
 * 自动初始化带 data-tilt 属性的元素
 * 在main.ts中调用
 */
export function autoInitTiltCard(): void {
  const elements = document.querySelectorAll<HTMLElement>('[data-tilt]')
  if (elements.length > 0) {
    const tiltCard = new TiltCard()
    tiltCard.init(elements)
  }
}

export default TiltCard
