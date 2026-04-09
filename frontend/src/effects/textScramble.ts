/**
 * 文字扰乱/解码效果
 * 从 design-system/js/effects/text-scramble.js 搬运并适配Vue3
 * 
 * 文字像被解密一样逐渐显现，赛博朋克风格满满
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 文字扰乱配置接口
export interface TextScrambleOptions {
  chars?: string      // 用于扰乱的字符集
  speed?: number      // 扰乱速度(ms)
  delay?: number      // 延迟开始(ms)
  autoStart?: boolean // 是否自动开始
}

// 默认配置
const defaultOptions: Required<TextScrambleOptions> = {
  chars: '!<>-_\\/[]{}—=+*^?#________',
  speed: 50,
  delay: 0,
  autoStart: true
}

/**
 * Vue3 组合式函数 - 文字扰乱效果
 * 使用方法：const { displayText, scramble } = useTextScramble('要显示的文本')
 */
export function useTextScramble(
  targetText: string,
  options: TextScrambleOptions = {}
) {
  const config = { ...defaultOptions, ...options }
  const displayText = ref('')
  const isScrambling = ref(false)
  const isComplete = ref(false)
  let intervalId: number | null = null
  let timeoutId: number | null = null

  /**
   * 执行扰乱效果
   */
  const scramble = () => {
    if (isScrambling.value) return

    isScrambling.value = true
    isComplete.value = false
    const length = targetText.length
    let iteration = 0

    intervalId = window.setInterval(() => {
      displayText.value = targetText
        .split('')
        .map((char, index) => {
          // 空格保持空格
          if (char === ' ') return ' '
          // 已经解码的部分显示原字符
          if (index < iteration) {
            return targetText[index]
          }
          // 未解码的部分显示随机字符
          return config.chars[Math.floor(Math.random() * config.chars.length)]
        })
        .join('')

      if (iteration >= length) {
        if (intervalId) {
          clearInterval(intervalId)
          intervalId = null
        }
        displayText.value = targetText
        isScrambling.value = false
        isComplete.value = true
      }

      iteration += 1 / 2
    }, config.speed)
  }

  /**
   * 停止扰乱
   */
  const stop = () => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    isScrambling.value = false
  }

  /**
   * 重置
   */
  const reset = () => {
    stop()
    displayText.value = ''
    isComplete.value = false
  }

  /**
   * 重新开始
   */
  const restart = () => {
    reset()
    timeoutId = window.setTimeout(scramble, config.delay)
  }

  onMounted(() => {
    if (config.autoStart) {
      timeoutId = window.setTimeout(scramble, config.delay)
    }
  })

  onUnmounted(() => {
    stop()
  })

  return {
    displayText,
    isScrambling,
    isComplete,
    scramble,
    stop,
    reset,
    restart
  }
}

/**
 * 类方式 - 文字扰乱效果
 * 用于非Vue组件场景，支持IntersectionObserver
 */
export class TextScramble {
  private config: Required<TextScrambleOptions>
  private observer: IntersectionObserver | null = null
  private intervalId: number | null = null

  constructor(options: TextScrambleOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化文字扰乱效果
   * @param selector - CSS选择器或HTMLElement数组
   * @param customOptions - 可选的自定义配置
   */
  init(
    selector: string | HTMLElement | NodeListOf<HTMLElement>,
    customOptions: TextScrambleOptions = {}
  ): void {
    const config = { ...this.config, ...customOptions }

    const elements = typeof selector === 'string'
      ? document.querySelectorAll<HTMLElement>(selector)
      : selector instanceof NodeList
        ? Array.from(selector)
        : [selector]

    // 创建IntersectionObserver，元素进入视口时开始动画
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const target = entry.target as HTMLElement
          if (entry.isIntersecting && !target.dataset.scrambled) {
            target.dataset.scrambled = 'true'
            setTimeout(() => {
              this.scramble(target, config)
            }, config.delay)
          }
        })
      },
      { threshold: 0.5 }
    )

    elements.forEach((el) => this.observer?.observe(el))
  }

  /**
   * 对单个元素执行扰乱
   */
  scramble(
    el: HTMLElement,
    customConfig?: Partial<TextScrambleOptions>
  ): void {
    const config = { ...this.config, ...customConfig }
    const originalText = el.dataset.scrambleText || el.textContent || ''
    el.dataset.scrambleText = originalText

    const length = originalText.length
    let iteration = 0

    // 清除之前的interval
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }

    this.intervalId = window.setInterval(() => {
      el.textContent = originalText
        .split('')
        .map((char, index) => {
          if (char === ' ') return ' '
          if (index < iteration) {
            return originalText[index]
          }
          return config.chars[Math.floor(Math.random() * config.chars.length)]
        })
        .join('')

      if (iteration >= length) {
        if (this.intervalId) {
          clearInterval(this.intervalId)
          this.intervalId = null
        }
        el.textContent = originalText
      }

      iteration += 1 / 2
    }, config.speed)
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    if (this.observer) {
      this.observer.disconnect()
    }
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }
  }
}

/**
 * 自动初始化带 data-scramble 属性的元素
 * 在main.ts中调用
 */
export function autoInitTextScramble(): void {
  document.querySelectorAll<HTMLElement>('[data-scramble]').forEach((el) => {
    const speed = parseInt(el.dataset.scrambleSpeed || '50')
    const delay = parseInt(el.dataset.scrambleDelay || '0')
    const textScramble = new TextScramble({ speed, delay })
    textScramble.init(el)
  })
}

export default TextScramble
