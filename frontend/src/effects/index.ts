/**
 * 动效系统入口
 * 从 design-system/js/effects/ 搬运并适配Vue3
 * 
 * 包含所有视觉效果：打字机、数字滚动、文字扰乱、浮动元素、鼠标光晕、3D卡片、粒子系统
 * 老大让我搬的，搬完了，累死了 (´；ω；`)
 */

// 打字机效果
export {
  useTypewriter,
  Typewriter,
  autoInitTypewriter,
  type TypewriterOptions
} from './typewriter'

// 数字滚动效果
export {
  useCountUp,
  CountUp,
  autoInitCountUp,
  type CountUpOptions
} from './countUp'

// 文字扰乱效果
export {
  useTextScramble,
  TextScramble,
  autoInitTextScramble,
  type TextScrambleOptions
} from './textScramble'

// 浮动装饰元素
export {
  useFloating,
  FloatingElements,
  autoInitFloating,
  type FloatingOptions
} from './floating'

// 鼠标跟随光晕
export {
  useMouseGlow,
  MouseGlow,
  autoInitMouseGlow,
  type MouseGlowOptions
} from './mouseGlow'

// 3D卡片倾斜
export {
  useTiltCard,
  TiltCard,
  autoInitTiltCard,
  type TiltCardOptions
} from './tiltCard'

// 粒子系统
export {
  useParticles,
  ParticleSystem,
  autoInitParticles,
  type ParticleOptions,
  type ParticleType
} from './particles'

// 导入函数用于本地使用
import { autoInitTypewriter } from './typewriter'
import { autoInitCountUp } from './countUp'
import { autoInitTextScramble } from './textScramble'
import { autoInitFloating } from './floating'
import { autoInitMouseGlow } from './mouseGlow'
import { autoInitTiltCard } from './tiltCard'
import { autoInitParticles } from './particles'

/**
 * 自动初始化所有动效
 * 在 main.ts 中调用，会自动检测并初始化带 data-* 属性的元素
 */
export function autoInitAllEffects(): void {
  // 等待DOM加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEffects)
  } else {
    initEffects()
  }
}

/**
 * 初始化所有动效
 */
function initEffects(): void {
  // 打字机效果
  autoInitTypewriter()
  
  // 数字滚动效果
  autoInitCountUp()
  
  // 文字扰乱效果
  autoInitTextScramble()
  
  // 浮动装饰元素
  autoInitFloating()
  
  // 鼠标跟随光晕
  autoInitMouseGlow()
  
  // 3D卡片倾斜
  autoInitTiltCard()
  
  // 粒子系统（根据当前主题自动初始化）
  autoInitParticles()
}

export default {
  autoInit: autoInitAllEffects
}
