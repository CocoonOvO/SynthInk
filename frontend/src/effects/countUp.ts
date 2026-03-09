/**
 * 数字滚动效果
 * 从 design-system/js/effects/count-up.js 搬运并适配Vue3
 * 
 * 让数字从0滚动到目标值，带缓动效果
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'

// 数字滚动配置接口
export interface CountUpOptions {
  duration?: number     // 动画持续时间(ms)
  suffix?: string       // 后缀
  prefix?: string       // 前缀
  separator?: string    // 千位分隔符
  decimals?: number     // 小数位数
  startOnMount?: boolean // 是否在挂载时自动开始
}

// 默认配置
const defaultOptions: Required<CountUpOptions> = {
  duration: 2000,
  suffix: '',
  prefix: '',
  separator: ',',
  decimals: 0,
  startOnMount: true
}

/**
 * Vue3 组合式函数 - 数字滚动
 * 使用方法：const { displayValue, start } = useCountUp(1000, { duration: 2000 })
 */
export function useCountUp(
  targetValue: number,
  options: CountUpOptions = {}
) {
  const config = { ...defaultOptions, ...options }
  const isAnimating = ref(false)
  const isComplete = ref(false)
  let rafId: number | null = null

  /**
   * 格式化数字
   */
  const formatNumber = (num: number): string => {
    const fixed = num.toFixed(config.decimals)
    const parts = fixed.split('.')
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, config.separator)
    return parts.join('.')
  }
  
  const displayValue = ref(config.prefix + formatNumber(0) + config.suffix)

  /**
   * 开始动画
   */
  const start = () => {
    if (isAnimating.value) return
    
    isAnimating.value = true
    isComplete.value = false
    const startTime = performance.now()
    const startValue = 0

    const update = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / config.duration, 1)

      // 使用 easeOutExpo 缓动
      const easeProgress = 1 - Math.pow(2, -10 * progress)
      const current = startValue + (targetValue - startValue) * easeProgress

      displayValue.value = config.prefix + formatNumber(current) + config.suffix

      if (progress < 1) {
        rafId = requestAnimationFrame(update)
      } else {
        isAnimating.value = false
        isComplete.value = true
        // 确保最终值精确
        displayValue.value = config.prefix + formatNumber(targetValue) + config.suffix
      }
    }

    rafId = requestAnimationFrame(update)
  }

  /**
   * 停止动画
   */
  const stop = () => {
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    isAnimating.value = false
  }

  /**
   * 重置
   */
  const reset = () => {
    stop()
    displayValue.value = config.prefix + formatNumber(0) + config.suffix
    isComplete.value = false
  }

  onMounted(() => {
    if (config.startOnMount) {
      start()
    }
  })

  onUnmounted(() => {
    stop()
  })

  // 监听目标值变化
  watch(() => targetValue, () => {
    reset()
    if (config.startOnMount) {
      start()
    }
  })

  return {
    displayValue,
    isAnimating,
    isComplete,
    start,
    stop,
    reset
  }
}

/**
 * 类方式 - 数字滚动
 * 用于非Vue组件场景，支持IntersectionObserver
 */
export class CountUp {
  private config: Required<CountUpOptions>
  private observer: IntersectionObserver | null = null
  private rafId: number | null = null

  constructor(options: CountUpOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  /**
   * 初始化数字滚动
   * @param selector - CSS选择器或HTMLElement数组
   * @param customOptions - 可选的自定义配置
   */
  init(
    selector: string | HTMLElement | NodeListOf<HTMLElement>,
    customOptions: CountUpOptions = {}
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
          if (entry.isIntersecting && !entry.target.dataset.counted) {
            entry.target.dataset.counted = 'true'
            this.animate(entry.target as HTMLElement, config)
          }
        })
      },
      { threshold: 0.5 }
    )

    elements.forEach((el) => this.observer?.observe(el))
  }

  /**
   * 执行动画
   */
  private animate(el: HTMLElement, config: Required<CountUpOptions>): void {
    const target = parseFloat(el.dataset.countTarget || '0')
    const startTime = performance.now()
    const startValue = 0

    const update = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / config.duration, 1)

      // easeOutExpo 缓动
      const easeProgress = 1 - Math.pow(2, -10 * progress)
      const current = startValue + (target - startValue) * easeProgress

      el.textContent =
        config.prefix + this.formatNumber(current, config) + config.suffix

      if (progress < 1) {
        this.rafId = requestAnimationFrame(update)
      } else {
        // 确保最终值精确
        el.textContent =
          config.prefix + this.formatNumber(target, config) + config.suffix
      }
    }

    this.rafId = requestAnimationFrame(update)
  }

  /**
   * 格式化数字
   */
  private formatNumber(num: number, config: Required<CountUpOptions>): string {
    const fixed = num.toFixed(config.decimals)
    const parts = fixed.split('.')
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, config.separator)
    return parts.join('.')
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    if (this.observer) {
      this.observer.disconnect()
    }
    if (this.rafId) {
      cancelAnimationFrame(this.rafId)
    }
  }
}

/**
 * 自动初始化带 data-count-target 属性的元素
 * 在main.ts中调用
 */
export function autoInitCountUp(): void {
  document.querySelectorAll<HTMLElement>('[data-count-target]').forEach((el) => {
    const duration = parseInt(el.dataset.countDuration || '2000')
    const suffix = el.dataset.countSuffix || ''
    const countUp = new CountUp({ duration, suffix })
    countUp.init(el)
  })
}

export default CountUp
