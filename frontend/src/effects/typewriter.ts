/**
 * 打字机效果
 * 从 design-system/js/effects/typewriter.js 搬运并适配Vue3
 * 
 * 老大让我搬的，我不敢不搬 (╯°□°）╯
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 打字机配置接口
export interface TypewriterOptions {
  speed?: number        // 打字速度(ms)
  delay?: number        // 延迟开始(ms)
  cursor?: boolean      // 是否显示光标
  cursorChar?: string   // 光标字符
}

// 默认配置
const defaultOptions: Required<TypewriterOptions> = {
  speed: 50,
  delay: 0,
  cursor: true,
  cursorChar: '|'
}

/**
 * Vue3 组合式函数 - 打字机效果
 * 使用方法：const { text, isTyping } = useTypewriter('要显示的文本', { speed: 50 })
 */
export function useTypewriter(
  targetText: string,
  options: TypewriterOptions = {}
) {
  const config = { ...defaultOptions, ...options }
  const displayText = ref('')
  const isTyping = ref(false)
  const isComplete = ref(false)
  let timeoutId: number | null = null
  let rafId: number | null = null

  const startTyping = () => {
    isTyping.value = true
    isComplete.value = false
    displayText.value = ''
    
    let index = 0
    
    const type = () => {
      if (index < targetText.length) {
        displayText.value += targetText[index]
        index++
        timeoutId = window.setTimeout(type, config.speed)
      } else {
        isTyping.value = false
        isComplete.value = true
      }
    }

    // 延迟后开始
    timeoutId = window.setTimeout(type, config.delay)
  }

  const stopTyping = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    isTyping.value = false
  }

  const reset = () => {
    stopTyping()
    displayText.value = ''
    isComplete.value = false
  }

  const restart = () => {
    reset()
    startTyping()
  }

  onMounted(() => {
    startTyping()
  })

  onUnmounted(() => {
    stopTyping()
  })

  return {
    text: displayText,
    isTyping,
    isComplete,
    start: startTyping,
    stop: stopTyping,
    reset,
    restart
  }
}

/**
 * 类方式 - 打字机效果
 * 用于非Vue组件场景
 */
export class Typewriter {
  private config: Required<TypewriterOptions>
  private element: HTMLElement | null = null
  private cursor: HTMLElement | null = null
  private timeoutId: number | null = null
  private originalText: string = ''

  constructor(options: TypewriterOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化打字机效果
   * @param selector - CSS选择器或HTMLElement
   * @param customOptions - 可选的自定义配置
   */
  init(
    selector: string | HTMLElement,
    customOptions: TypewriterOptions = {}
  ): void {
    const config = { ...this.config, ...customOptions }
    
    const elements = typeof selector === 'string'
      ? document.querySelectorAll<HTMLElement>(selector)
      : [selector]

    elements.forEach((el) => {
      this.originalText = el.textContent || ''
      el.textContent = ''
      el.style.opacity = '1'

      // 创建光标
      if (config.cursor) {
        this.cursor = document.createElement('span')
        this.cursor.className = 'typewriter-cursor'
        this.cursor.textContent = config.cursorChar
        this.cursor.style.cssText = `
          display: inline-block;
          animation: typewriter-blink 1s infinite;
          color: var(--accent-primary);
          margin-left: 2px;
        `
        el.appendChild(this.cursor)
      }

      // 延迟后开始打字
      this.timeoutId = window.setTimeout(() => {
        this.type(el, this.originalText, config.speed, 0)
      }, config.delay)
    })

    // 添加光标闪烁动画样式
    this.addCursorStyle()
  }

  /**
   * 递归打字
   */
  private type(
    el: HTMLElement,
    text: string,
    speed: number,
    index: number
  ): void {
    const cursor = el.querySelector('.typewriter-cursor')

    if (index < text.length) {
      const charText = text[index] ?? ''
      const char = document.createTextNode(charText)
      if (cursor) {
        el.insertBefore(char, cursor)
      } else {
        el.appendChild(char)
      }
      this.timeoutId = window.setTimeout(() => {
        this.type(el, text, speed, index + 1)
      }, speed)
    }
  }

  /**
   * 添加光标闪烁动画样式
   */
  private addCursorStyle(): void {
    if (document.getElementById('typewriter-style')) return

    const style = document.createElement('style')
    style.id = 'typewriter-style'
    style.textContent = `
      @keyframes typewriter-blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
      }
    `
    document.head.appendChild(style)
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
    }
  }
}

/**
 * 自动初始化带 data-typewriter 属性的元素
 * 在main.ts中调用
 */
export function autoInitTypewriter(): void {
  document.querySelectorAll<HTMLElement>('[data-typewriter]').forEach((el) => {
    const speed = parseInt(el.dataset.typewriterSpeed || '50')
    const delay = parseInt(el.dataset.typewriterDelay || '0')
    const typewriter = new Typewriter({ speed, delay })
    typewriter.init(el)
  })
}

export default Typewriter
