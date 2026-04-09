/**
 * 粒子系统管理器
 * 完全还原 design-system/js/theme-system.js 的粒子效果
 * 
 * 每个主题都有独特的视觉语言：
 * - firefly: 林间闪烁的萤火，带光晕呼吸
 * - sakura: 飘落的樱花瓣，椭圆旋转摆动
 * - bubble: 上升的气泡，带描边和高光
 * - rising: 轻盈上升的光点，渐隐效果
 * - wireframe: 水平穿过的线框，科技感
 * - datastream: 数据字符流，黑客帝国风格
 * - twinparticle: 金蓝双色粒子，双子交织
 * - creamy: 奶油色柔和光斑，带脉冲
 * - musical: 飘动的音符，livehouse氛围
 * - spotlight: 舞台聚光灯，径向渐变
 */

import { ref, onMounted, onUnmounted } from 'vue'

// 粒子类型
export type ParticleType = 
  | 'floating' 
  | 'bubble' 
  | 'firefly' 
  | 'matrix' 
  | 'sakura' 
  | 'rising'
  | 'datastream'
  | 'twinparticle'
  | 'musical'
  | 'spotlight'
  | 'wireframe'
  | 'creamy'

// 粒子配置接口
export interface ParticleOptions {
  type?: ParticleType
  count?: number
  color?: string
  opacity?: number
  speed?: number
  size?: number
}

// 粒子对象接口
interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  rotation?: number
  rotationSpeed?: number
  char?: string
  // firefly
  flashPhase?: number
  flashSpeed?: number
  baseOpacity?: number
  // sakura
  swayPhase?: number
  swayAmplitude?: number
  // bubble
  wobble?: number
  wobbleSpeed?: number
  // wireframe
  length?: number
  // datastream
  // twinparticle
  isGold?: boolean
  // creamy
  pulsePhase?: number
  pulseSpeed?: number
  baseSize?: number
  // musical
  noteType?: number
  // spotlight
  targetX?: number
  targetY?: number
  moveSpeed?: number
  beamWidth?: number
  beamOpacity?: number
  fadePhase?: number
  fadeSpeed?: number
  // lifecycle
  life: number
  maxLife: number
}

// 默认配置
const defaultOptions: Required<ParticleOptions> = {
  type: 'floating',
  count: 50,
  color: '#52b788',
  opacity: 0.5,
  speed: 1,
  size: 2
}

// 矩阵雨字符集
const matrixChars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789'

/**
 * Vue3 组合式函数 - 粒子系统
 */
export function useParticles(options: ParticleOptions = {}) {
  const config = { ...defaultOptions, ...options }
  const canvas = ref<HTMLCanvasElement | null>(null)
  const ctx = ref<CanvasRenderingContext2D | null>(null)
  const particles = ref<Particle[]>([])
  const isRunning = ref(false)
  let rafId: number | null = null

  const initCanvas = (canvasEl: HTMLCanvasElement) => {
    canvas.value = canvasEl
    ctx.value = canvasEl.getContext('2d')
    resizeCanvas()
    createParticles()
    window.addEventListener('resize', resizeCanvas)
  }

  const resizeCanvas = () => {
    if (!canvas.value) return
    canvas.value.width = window.innerWidth
    canvas.value.height = window.innerHeight
  }

  const createParticles = () => {
    particles.value = []
    const count = window.innerWidth < 768 ? Math.floor(config.count / 2) : config.count
    for (let i = 0; i < count; i++) {
      particles.value.push(createParticle())
    }
  }

  const createParticle = (): Particle => {
    const canvasWidth = canvas.value?.width || window.innerWidth
    const canvasHeight = canvas.value?.height || window.innerHeight
    const baseOp = Math.random() * 0.3 + 0.2
    const maxLife = Math.random() * 200 + 100

    switch (config.type) {
      case 'firefly':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.8,
          vy: (Math.random() - 0.5) * 0.8,
          size: Math.random() * 3 + 1,
          opacity: baseOp,
          baseOpacity: config.opacity,
          flashSpeed: Math.random() * 0.05 + 0.02,
          flashPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'sakura':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 1.2,
          vy: Math.random() * 0.6 + 0.3,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.5 + 0.2,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.04,
          swayAmplitude: Math.random() * 30 + 20,
          swayPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'bubble':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.3,
          vy: -(Math.random() * 0.4 + 0.15),
          size: Math.random() * 4 + 2,
          opacity: baseOp,
          baseOpacity: config.opacity,
          wobble: Math.random() * Math.PI * 2,
          wobbleSpeed: Math.random() * 0.03 + 0.01,
          life: 0,
          maxLife
        }
      
      case 'rising':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.2,
          vy: -(Math.random() * 1.2 + 0.6),
          size: Math.random() * 2 + 1,
          opacity: Math.random() * baseOp,
          baseOpacity: config.opacity,
          life: 0,
          maxLife
        }
      
      case 'wireframe':
        return {
          x: Math.random() * (canvasWidth + 400) - 200,
          y: Math.random() * canvasHeight,
          vx: Math.random() * 4 + 3,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.3 + 0.1,
          length: Math.random() * 25 + 10,
          life: 0,
          maxLife
        }
      
      case 'datastream':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: Math.random() * 2 + 1,
          size: Math.random() * 3 + 2,
          opacity: Math.random() * 0.4 + 0.2,
          char: matrixChars[Math.floor(Math.random() * matrixChars.length)],
          life: 0,
          maxLife
        }
      
      case 'twinparticle':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 1.5,
          vy: (Math.random() - 0.5) * 1.5,
          size: Math.random() * 3 + 2,
          opacity: Math.random() * 0.4 + 0.2,
          isGold: Math.random() > 0.5,
          life: 0,
          maxLife
        }
      
      case 'creamy':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          size: Math.random() * 4 + 2,
          baseSize: Math.random() * 4 + 2,
          opacity: baseOp,
          baseOpacity: config.opacity,
          pulsePhase: Math.random() * Math.PI * 2,
          pulseSpeed: Math.random() * 0.02 + 0.01,
          life: 0,
          maxLife
        }
      
      case 'musical':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.8,
          vy: -Math.random() * 0.5 - 0.2,
          size: Math.random() * 3 + 1,
          opacity: baseOp,
          baseOpacity: config.opacity,
          noteType: Math.floor(Math.random() * 3),
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.03,
          swayPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'spotlight':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: 0,
          size: Math.random() * 3 + 2,
          opacity: 0,
          targetX: Math.random() * canvasWidth,
          targetY: Math.random() * canvasHeight,
          moveSpeed: Math.random() * 0.5 + 0.2,
          beamWidth: Math.random() * 40 + 20,
          beamOpacity: 0,
          fadePhase: Math.random() * Math.PI * 2,
          fadeSpeed: Math.random() * 0.02 + 0.01,
          life: 0,
          maxLife
        }
      
      case 'matrix':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: Math.random() * 3 + 2,
          size: 14,
          opacity: Math.random() * 0.5 + 0.3,
          char: matrixChars[Math.floor(Math.random() * matrixChars.length)],
          life: 0,
          maxLife
        }
      
      default: // floating
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.3 + 0.1,
          life: 0,
          maxLife
        }
    }
  }

  const updateParticles = () => {
    const canvasWidth = canvas.value?.width || window.innerWidth
    const canvasHeight = canvas.value?.height || window.innerHeight

    particles.value.forEach(p => {
      p.life++

      switch (config.type) {
        case 'firefly':
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          p.flashPhase! += p.flashSpeed!
          p.opacity = p.baseOpacity! * (0.5 + 0.5 * Math.sin(p.flashPhase!))
          if (p.x < 0 || p.x > canvasWidth || p.y < 0 || p.y > canvasHeight) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'sakura':
          p.swayPhase! += 0.02
          p.x += p.vx * config.speed + Math.sin(p.swayPhase!) * 0.3
          p.y += p.vy * config.speed
          p.rotation! += p.rotationSpeed!
          if (p.y > canvasHeight + 20 || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'bubble':
          p.wobble! += p.wobbleSpeed!
          p.x += p.vx * config.speed + Math.sin(p.wobble!) * 0.3
          p.y += p.vy * config.speed
          p.opacity = p.baseOpacity! * (0.7 + 0.3 * Math.sin(p.wobble!))
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'rising':
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          p.opacity = p.baseOpacity! * Math.min(1, p.life / 30)
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'wireframe':
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          if (p.x > canvasWidth + 50) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'datastream':
        case 'matrix':
          p.y += p.vy * config.speed
          if (p.y > canvasHeight || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'twinparticle':
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          if (p.x < 0 || p.x > canvasWidth || p.y < 0 || p.y > canvasHeight || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'creamy':
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          p.pulsePhase! += p.pulseSpeed!
          p.size = p.baseSize! * (1 + Math.sin(p.pulsePhase!) * 0.3)
          p.opacity = p.baseOpacity! * (0.6 + 0.4 * Math.sin(p.pulsePhase!))
          if (p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'musical':
          p.swayPhase! += 0.03
          p.x += p.vx * config.speed + Math.sin(p.swayPhase!) * 0.5
          p.y += p.vy * config.speed
          p.rotation! += p.rotationSpeed!
          p.opacity = p.baseOpacity! * Math.max(0, 1 - p.life / p.maxLife)
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        case 'spotlight':
          p.x += (p.targetX! - p.x) * p.moveSpeed! * 0.02
          p.y += (p.targetY! - p.y) * p.moveSpeed! * 0.02
          p.fadePhase! += p.fadeSpeed!
          p.beamOpacity = 0.15 + 0.1 * Math.sin(p.fadePhase!)
          if (Math.abs(p.x - p.targetX!) < 5 && Math.abs(p.y - p.targetY!) < 5) {
            p.targetX = Math.random() * canvasWidth
            p.targetY = Math.random() * canvasHeight
          }
          if (p.life > p.maxLife) {
            Object.assign(p, createParticle())
          }
          break
        
        default: // floating
          p.x += p.vx * config.speed
          p.y += p.vy * config.speed
          if (p.x < 0) p.x = canvasWidth
          if (p.x > canvasWidth) p.x = 0
          if (p.y < 0) p.y = canvasHeight
          if (p.y > canvasHeight) p.y = 0
      }
    })
  }

  const drawParticles = () => {
    if (!ctx.value || !canvas.value) return
    ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)

    particles.value.forEach(p => {
      ctx.value!.save()

      switch (config.type) {
        case 'firefly':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.shadowBlur = 15
          ctx.value!.shadowColor = config.color
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'sakura':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.translate(p.x, p.y)
          ctx.value!.rotate(p.rotation || 0)
          ctx.value!.beginPath()
          ctx.value!.ellipse(0, 0, p.size * 2, p.size, 0, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'bubble':
          ctx.value!.globalAlpha = p.opacity * 0.6
          ctx.value!.strokeStyle = config.color
          ctx.value!.lineWidth = 1
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2)
          ctx.value!.stroke()
          ctx.value!.globalAlpha = p.opacity * 0.3
          ctx.value!.fillStyle = config.color
          ctx.value!.beginPath()
          ctx.value!.arc(p.x - p.size, p.y - p.size, p.size * 0.5, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'wireframe':
          ctx.value!.globalAlpha = p.opacity * 0.8
          ctx.value!.strokeStyle = config.color
          ctx.value!.lineWidth = 1.5
          ctx.value!.shadowBlur = 8
          ctx.value!.shadowColor = config.color
          ctx.value!.beginPath()
          ctx.value!.moveTo(p.x, p.y)
          ctx.value!.lineTo(p.x - p.length!, p.y)
          ctx.value!.stroke()
          break
        
        case 'datastream':
        case 'matrix':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.font = `${p.size * (config.type === 'matrix' ? 1 : 4)}px monospace`
          ctx.value!.textAlign = 'center'
          ctx.value!.textBaseline = 'middle'
          ctx.value!.shadowBlur = 5
          ctx.value!.shadowColor = config.color
          ctx.value!.fillText(p.char || '', p.x, p.y)
          break
        
        case 'twinparticle':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = p.isGold ? '#ffd700' : '#00bfff'
          ctx.value!.shadowBlur = 10
          ctx.value!.shadowColor = ctx.value!.fillStyle
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'creamy':
          ctx.value!.globalAlpha = p.opacity * 0.7
          ctx.value!.fillStyle = config.color
          ctx.value!.shadowBlur = 20
          ctx.value!.shadowColor = config.color
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2)
          ctx.value!.fill()
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = '#ffffff'
          ctx.value!.beginPath()
          ctx.value!.arc(p.x - p.size * 0.3, p.y - p.size * 0.3, p.size * 0.4, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'musical':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.shadowBlur = 8
          ctx.value!.shadowColor = config.color
          ctx.value!.translate(p.x, p.y)
          ctx.value!.rotate(p.rotation || 0)
          const notes = ['♪', '♫', '♬']
          ctx.value!.font = `${p.size * 3}px Arial`
          ctx.value!.textAlign = 'center'
          ctx.value!.textBaseline = 'middle'
          ctx.value!.fillText(notes[p.noteType || 0] ?? '♪', 0, 0)
          break
        
        case 'spotlight':
          const gradient = ctx.value!.createRadialGradient(
            p.x, p.y, 0,
            p.x, p.y, p.beamWidth!
          )
          gradient.addColorStop(0, `rgba(255, 255, 255, ${p.beamOpacity})`)
          gradient.addColorStop(0.5, `rgba(255, 255, 255, ${p.beamOpacity! * 0.3})`)
          gradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
          ctx.value!.globalAlpha = 1
          ctx.value!.fillStyle = gradient
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.beamWidth!, 0, Math.PI * 2)
          ctx.value!.fill()
          ctx.value!.globalAlpha = p.beamOpacity! * 2
          ctx.value!.fillStyle = '#ffffff'
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        case 'rising':
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.value!.fill()
          break
        
        default: // floating
          ctx.value!.globalAlpha = p.opacity
          ctx.value!.fillStyle = config.color
          ctx.value!.beginPath()
          ctx.value!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          ctx.value!.fill()
      }

      ctx.value!.restore()
    })
  }

  const animate = () => {
    if (!isRunning.value) return
    updateParticles()
    drawParticles()
    rafId = requestAnimationFrame(animate)
  }

  const start = () => {
    if (isRunning.value) return
    isRunning.value = true
    animate()
  }

  const stop = () => {
    isRunning.value = false
    if (rafId) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  }

  const destroy = () => {
    stop()
    window.removeEventListener('resize', resizeCanvas)
  }

  onUnmounted(() => {
    destroy()
  })

  return {
    canvas,
    ctx,
    particles,
    isRunning,
    initCanvas,
    start,
    stop,
    destroy
  }
}

/**
 * 类方式 - 粒子系统
 * 用于非Vue组件场景
 */
export class ParticleSystem {
  private config: Required<ParticleOptions>
  private canvas: HTMLCanvasElement | null = null
  private ctx: CanvasRenderingContext2D | null = null
  private particles: Particle[] = []
  private rafId: number | null = null
  private isRunning = false

  constructor(options: ParticleOptions = {}) {
    this.config = { ...defaultOptions, ...options }
  }

  init(container: HTMLElement | HTMLCanvasElement): void {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return
    }

    if (container instanceof HTMLCanvasElement) {
      this.canvas = container
    } else {
      this.canvas = document.createElement('canvas')
      this.canvas.id = 'particle-canvas'
      this.canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
      `
      container.appendChild(this.canvas)
    }

    this.ctx = this.canvas.getContext('2d')
    if (!this.ctx) {
      console.error('Failed to get 2D context from canvas')
      return
    }
    this.resize()
    this.createParticles()
    window.addEventListener('resize', () => this.resize())
    this.start()
  }

  private resize(): void {
    if (!this.canvas) return
    this.canvas.width = window.innerWidth
    this.canvas.height = window.innerHeight
  }

  private createParticles(): void {
    this.particles = []
    const count = window.innerWidth < 768 ? Math.floor(this.config.count / 2) : this.config.count
    for (let i = 0; i < count; i++) {
      this.particles.push(this.createParticle())
    }
  }

  private createParticle(): Particle {
    const canvasWidth = this.canvas?.width || window.innerWidth
    const canvasHeight = this.canvas?.height || window.innerHeight
    const baseOp = Math.random() * 0.3 + 0.2
    const maxLife = Math.random() * 200 + 100

    switch (this.config.type) {
      case 'firefly':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.8,
          vy: (Math.random() - 0.5) * 0.8,
          size: Math.random() * 3 + 1,
          opacity: baseOp,
          baseOpacity: this.config.opacity,
          flashSpeed: Math.random() * 0.05 + 0.02,
          flashPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'sakura':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 1.2,
          vy: Math.random() * 0.6 + 0.3,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.5 + 0.2,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.04,
          swayAmplitude: Math.random() * 30 + 20,
          swayPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'bubble':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.3,
          vy: -(Math.random() * 0.4 + 0.15),
          size: Math.random() * 4 + 2,
          opacity: baseOp,
          baseOpacity: this.config.opacity,
          wobble: Math.random() * Math.PI * 2,
          wobbleSpeed: Math.random() * 0.03 + 0.01,
          life: 0,
          maxLife
        }
      
      case 'rising':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.2,
          vy: -(Math.random() * 1.2 + 0.6),
          size: Math.random() * 2 + 1,
          opacity: Math.random() * baseOp,
          baseOpacity: this.config.opacity,
          life: 0,
          maxLife
        }
      
      case 'wireframe':
        return {
          x: Math.random() * (canvasWidth + 400) - 200,
          y: Math.random() * canvasHeight,
          vx: Math.random() * 4 + 3,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.3 + 0.1,
          length: Math.random() * 25 + 10,
          life: 0,
          maxLife
        }
      
      case 'datastream':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: Math.random() * 2 + 1,
          size: Math.random() * 3 + 2,
          opacity: Math.random() * 0.4 + 0.2,
          char: matrixChars[Math.floor(Math.random() * matrixChars.length)],
          life: 0,
          maxLife
        }
      
      case 'twinparticle':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 1.5,
          vy: (Math.random() - 0.5) * 1.5,
          size: Math.random() * 3 + 2,
          opacity: Math.random() * 0.4 + 0.2,
          isGold: Math.random() > 0.5,
          life: 0,
          maxLife
        }
      
      case 'creamy':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.2,
          vy: (Math.random() - 0.5) * 0.2,
          size: Math.random() * 2 + 1.5,
          baseSize: Math.random() * 2 + 1.5,
          opacity: baseOp * 0.7,
          baseOpacity: this.config.opacity * 0.7,
          pulsePhase: Math.random() * Math.PI * 2,
          pulseSpeed: Math.random() * 0.015 + 0.005,
          life: 0,
          maxLife: maxLife * 1.5
        }
      
      case 'musical':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.8,
          vy: -Math.random() * 0.5 - 0.2,
          size: Math.random() * 3 + 1,
          opacity: baseOp,
          baseOpacity: this.config.opacity,
          noteType: Math.floor(Math.random() * 3),
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.03,
          swayPhase: Math.random() * Math.PI * 2,
          life: 0,
          maxLife
        }
      
      case 'spotlight':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: 0,
          size: Math.random() * 3 + 2,
          opacity: 0,
          targetX: Math.random() * canvasWidth,
          targetY: Math.random() * canvasHeight,
          moveSpeed: Math.random() * 0.5 + 0.2,
          beamWidth: Math.random() * 40 + 20,
          beamOpacity: 0,
          fadePhase: Math.random() * Math.PI * 2,
          fadeSpeed: Math.random() * 0.02 + 0.01,
          life: 0,
          maxLife
        }
      
      case 'matrix':
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: 0,
          vy: Math.random() * 3 + 2,
          size: 14,
          opacity: Math.random() * 0.5 + 0.3,
          char: matrixChars[Math.floor(Math.random() * matrixChars.length)],
          life: 0,
          maxLife
        }
      
      default: // floating
        return {
          x: Math.random() * canvasWidth,
          y: Math.random() * canvasHeight,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1,
          opacity: Math.random() * 0.3 + 0.1,
          life: 0,
          maxLife
        }
    }
  }

  private updateParticles(): void {
    const canvasWidth = this.canvas?.width || window.innerWidth
    const canvasHeight = this.canvas?.height || window.innerHeight

    this.particles.forEach(p => {
      p.life++

      switch (this.config.type) {
        case 'firefly':
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          p.flashPhase! += p.flashSpeed!
          p.opacity = p.baseOpacity! * (0.5 + 0.5 * Math.sin(p.flashPhase!))
          if (p.x < 0 || p.x > canvasWidth || p.y < 0 || p.y > canvasHeight) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'sakura':
          p.swayPhase! += 0.02
          p.x += p.vx * this.config.speed + Math.sin(p.swayPhase!) * 0.3
          p.y += p.vy * this.config.speed
          p.rotation! += p.rotationSpeed!
          if (p.y > canvasHeight + 20 || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'bubble':
          p.wobble! += p.wobbleSpeed!
          p.x += p.vx * this.config.speed + Math.sin(p.wobble!) * 0.3
          p.y += p.vy * this.config.speed
          p.opacity = p.baseOpacity! * (0.7 + 0.3 * Math.sin(p.wobble!))
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'rising':
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          p.opacity = p.baseOpacity! * Math.min(1, p.life / 30)
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'wireframe':
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          if (p.x > canvasWidth + 50) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'datastream':
        case 'matrix':
          p.y += p.vy * this.config.speed
          if (p.y > canvasHeight || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'twinparticle':
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          if (p.x < 0 || p.x > canvasWidth || p.y < 0 || p.y > canvasHeight || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'creamy':
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          p.pulsePhase! += p.pulseSpeed!
          p.size = p.baseSize! * (1 + Math.sin(p.pulsePhase!) * 0.3)
          p.opacity = p.baseOpacity! * (0.6 + 0.4 * Math.sin(p.pulsePhase!))
          if (p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'musical':
          p.swayPhase! += 0.03
          p.x += p.vx * this.config.speed + Math.sin(p.swayPhase!) * 0.5
          p.y += p.vy * this.config.speed
          p.rotation! += p.rotationSpeed!
          p.opacity = p.baseOpacity! * Math.max(0, 1 - p.life / p.maxLife)
          if (p.y < -20 || p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        case 'spotlight':
          p.x += (p.targetX! - p.x) * p.moveSpeed! * 0.02
          p.y += (p.targetY! - p.y) * p.moveSpeed! * 0.02
          p.fadePhase! += p.fadeSpeed!
          p.beamOpacity = 0.15 + 0.1 * Math.sin(p.fadePhase!)
          if (Math.abs(p.x - p.targetX!) < 5 && Math.abs(p.y - p.targetY!) < 5) {
            p.targetX = Math.random() * canvasWidth
            p.targetY = Math.random() * canvasHeight
          }
          if (p.life > p.maxLife) {
            Object.assign(p, this.createParticle())
          }
          break
        
        default: // floating
          p.x += p.vx * this.config.speed
          p.y += p.vy * this.config.speed
          if (p.x < 0) p.x = canvasWidth
          if (p.x > canvasWidth) p.x = 0
          if (p.y < 0) p.y = canvasHeight
          if (p.y > canvasHeight) p.y = 0
      }
    })
  }

  private drawParticles(): void {
    if (!this.ctx || !this.canvas) return
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

    this.particles.forEach(p => {
      this.ctx!.save()

      switch (this.config.type) {
        case 'firefly':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.shadowBlur = 15
          this.ctx!.shadowColor = this.config.color
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'sakura':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.translate(p.x, p.y)
          this.ctx!.rotate(p.rotation || 0)
          this.ctx!.beginPath()
          this.ctx!.ellipse(0, 0, p.size * 2, p.size, 0, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'bubble':
          this.ctx!.globalAlpha = p.opacity * 0.6
          this.ctx!.strokeStyle = this.config.color
          this.ctx!.lineWidth = 1
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2)
          this.ctx!.stroke()
          this.ctx!.globalAlpha = p.opacity * 0.3
          this.ctx!.fillStyle = this.config.color
          this.ctx!.beginPath()
          this.ctx!.arc(p.x - p.size, p.y - p.size, p.size * 0.5, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'wireframe':
          this.ctx!.globalAlpha = p.opacity * 0.8
          this.ctx!.strokeStyle = this.config.color
          this.ctx!.lineWidth = 1.5
          this.ctx!.shadowBlur = 8
          this.ctx!.shadowColor = this.config.color
          this.ctx!.beginPath()
          this.ctx!.moveTo(p.x, p.y)
          this.ctx!.lineTo(p.x - p.length!, p.y)
          this.ctx!.stroke()
          break
        
        case 'datastream':
        case 'matrix':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.font = `${p.size * (this.config.type === 'matrix' ? 1 : 4)}px monospace`
          this.ctx!.textAlign = 'center'
          this.ctx!.textBaseline = 'middle'
          this.ctx!.shadowBlur = 5
          this.ctx!.shadowColor = this.config.color
          this.ctx!.fillText(p.char || '', p.x, p.y)
          break
        
        case 'twinparticle':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = p.isGold ? '#ffd700' : '#00bfff'
          this.ctx!.shadowBlur = 10
          this.ctx!.shadowColor = this.ctx!.fillStyle
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'creamy':
          this.ctx!.globalAlpha = p.opacity * 0.7
          this.ctx!.fillStyle = this.config.color
          this.ctx!.shadowBlur = 20
          this.ctx!.shadowColor = this.config.color
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2)
          this.ctx!.fill()
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = '#ffffff'
          this.ctx!.beginPath()
          this.ctx!.arc(p.x - p.size * 0.3, p.y - p.size * 0.3, p.size * 0.4, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'musical':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.shadowBlur = 8
          this.ctx!.shadowColor = this.config.color
          this.ctx!.translate(p.x, p.y)
          this.ctx!.rotate(p.rotation || 0)
          const notes = ['♪', '♫', '♬']
          this.ctx!.font = `${p.size * 3}px Arial`
          this.ctx!.textAlign = 'center'
          this.ctx!.textBaseline = 'middle'
          this.ctx!.fillText(notes[p.noteType || 0] ?? '♪', 0, 0)
          break
        
        case 'spotlight':
          const gradient = this.ctx!.createRadialGradient(
            p.x, p.y, 0,
            p.x, p.y, p.beamWidth!
          )
          gradient.addColorStop(0, `rgba(255, 255, 255, ${p.beamOpacity})`)
          gradient.addColorStop(0.5, `rgba(255, 255, 255, ${p.beamOpacity! * 0.3})`)
          gradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
          this.ctx!.globalAlpha = 1
          this.ctx!.fillStyle = gradient
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.beamWidth!, 0, Math.PI * 2)
          this.ctx!.fill()
          this.ctx!.globalAlpha = p.beamOpacity! * 2
          this.ctx!.fillStyle = '#ffffff'
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        case 'rising':
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          this.ctx!.fill()
          break
        
        default: // floating
          this.ctx!.globalAlpha = p.opacity
          this.ctx!.fillStyle = this.config.color
          this.ctx!.beginPath()
          this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2)
          this.ctx!.fill()
      }

      this.ctx!.restore()
    })
  }

  private animate(): void {
    if (!this.isRunning) return
    this.updateParticles()
    this.drawParticles()
    this.rafId = requestAnimationFrame(() => this.animate())
  }

  start(): void {
    if (this.isRunning) return
    this.isRunning = true
    this.animate()
  }

  stop(): void {
    this.isRunning = false
    if (this.rafId) {
      cancelAnimationFrame(this.rafId)
      this.rafId = null
    }
  }

  destroy(removeCanvas: boolean = false): void {
    this.stop()
    if (removeCanvas && this.canvas && this.canvas.parentElement) {
      this.canvas.remove()
    }
    this.canvas = null
    this.ctx = null
    this.particles = []
  }
}

/**
 * 从CSS变量自动初始化粒子系统
 */
export function autoInitParticles(container: HTMLElement = document.body): void {
  const style = getComputedStyle(document.body)
  const particleType = style.getPropertyValue('--particle-type').trim() as ParticleType
  const particleColor = style.getPropertyValue('--particle-color').trim() || '#52b788'
  const particleOpacity = parseFloat(style.getPropertyValue('--particle-opacity')) || 0.5

  if (particleType) {
    const particleSystem = new ParticleSystem({
      type: particleType,
      color: particleColor,
      opacity: particleOpacity,
      count: 50
    })
    particleSystem.init(container)
  }
}

export default ParticleSystem
