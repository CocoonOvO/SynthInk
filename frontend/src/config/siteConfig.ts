/**
 * 站点可配置机制（核心模块）
 * 
 * 设计思路：
 * - 内置默认值直接来自 copywriting.json（已入库的文案）
 * - 支持通过 public/site.config.json（已 gitignore）在部署时覆盖任意字段
 * - 后台可保存配置（/api/site-config，业务库超管维护），优先级最高
 * - 三级优先级：内置默认 < 本地文件 site.config.json < 后台配置
 * - 启动时并行 fetch 拉取文件与后台配置，与默认值深合并；任何异常都安静跳过对应层级
 * - 配置在启动后保持不变，组件在 setup 中调用 getSiteConfig() 即可
 */
import copywriting from './copywriting.json'

// ── 内置默认值（从 copywriting.json 派生，避免重复维护文案） ──

// 首页文案段结构（复用 copywriting.json 的 home 段）
const copywritingHome = copywriting.home

// 关于页文案段结构（复用 copywriting.json 的 about 段）
const copywritingAbout = copywriting.about

// ── 站点配置接口定义 ──

/**
 * 站点配置接口
 */
export interface SiteConfig {
  site: {
    name: string        // 站点名称（如 "SynthSpark"）
    title: string       // 浏览器标题（document.title）
    description: string // 站点描述
    icp: string         // 备案号（可为空字符串）
    defaultTheme: string // 首次访问用户的默认主题（已选过主题的用户不受影响）
    logo: string        // 站点 Logo 图片 URL（为空时使用内置 SVG，同时作为 favicon）
  }
  navbar: {
    logo: string        // 导航栏 Logo 文字
    navItems: { label: string; path: string }[] // 导航项列表
  }
  footer: {
    copyright: string                                  // 版权文字（渐变展示）
    slogan: string                                     // 口号
    links: { group: string; items: { label: string; href: string }[] }[] // 页脚链接组，可为空数组
  }
  home: typeof copywritingHome   // 首页文案（结构同 copywriting.json 的 home 段）
  about: typeof copywritingAbout // 关于页文案（结构同 copywriting.json 的 about 段）
}

// ── 内置默认配置 ──

/**
 * 构建内置默认配置：
 * - navbar / footer 基础字段复用 copywriting.json 现值
 * - footer.links 给一组合理的站内链接示例
 * - site 段从现有文案派生
 */
const buildDefaultConfig = (): SiteConfig => ({
  site: {
    name: copywriting.navbar.logo,
    title: copywriting.navbar.logo,
    description: copywriting.about.desc,
    icp: '',
    defaultTheme: 'exia',
    logo: '',
  },
  navbar: {
    logo: copywriting.navbar.logo,
    navItems: copywriting.navbar.navItems,
  },
  footer: {
    copyright: copywriting.footer.copyright,
    slogan: copywriting.footer.slogan,
    links: [
      {
        group: '导航',
        items: [
          { label: '首页', href: '/' },
          { label: '文章', href: '/posts' },
          { label: '关联', href: '/links' },
          { label: '关于', href: '/about' },
        ],
      },
    ],
  },
  home: copywritingHome,
  about: copywritingAbout,
})

// ── 深合并工具 ──

/**
 * 递归深合并：把 source 合并进 target 的副本，返回新对象（不改动任何入参）
 * - source 中的 null / undefined 字段直接跳过（保持 target 原值）
 * - 数组整体替换（不做逐元素合并）
 * - 普通对象递归合并
 */
function deepMerge(target: object, source: unknown): object {
  // source 非普通对象时直接返回 target（无合并项）
  if (source === null || typeof source !== 'object' || Array.isArray(source)) {
    return target
  }

  // 浅拷贝 target 顶层，确保不改动入参
  const result: Record<string, unknown> = { ...(target as Record<string, unknown>) }
  const src = source as Record<string, unknown>

  for (const key of Object.keys(src)) {
    const value = src[key]

    // null / undefined 跳过
    if (value === null || value === undefined) {
      continue
    }

    // 数组直接替换
    if (Array.isArray(value)) {
      result[key] = value
      continue
    }

    // 普通对象：target 对应键也是普通对象则递归深合并，否则整体替换
    if (typeof value === 'object') {
      const current = result[key]
      if (current !== null && typeof current === 'object' && !Array.isArray(current)) {
        result[key] = deepMerge(current, value)
      } else {
        result[key] = value
      }
      continue
    }

    // 基本类型直接覆盖
    result[key] = value
  }

  return result
}

// ── 模块级缓存 ──

// 内置默认配置（每次合并都从它出发，避免重复合并叠加）
const defaultConfig: SiteConfig = buildDefaultConfig()

// 当前生效配置（初始为内置默认；fetch 成功后替换为合并结果）
// dev 模式 HMR 热更新时本模块会被重新求值，用 hot.data 恢复已加载的配置，
// 避免开发过程中页面配置闪回默认值（整页刷新仍会重新拉取）
let currentConfig: SiteConfig =
  (import.meta.hot?.data?.currentConfig as SiteConfig | undefined) ?? defaultConfig

// ── 对外接口 ──

/**
 * 启动时初始化站点配置（三级优先级：内置默认 < 本地文件 < 后台配置）：
 * - 第一层：内置默认（buildDefaultConfig 构建）
 * - 第二层：fetch('/site.config.json') 拉取本地覆盖文件（public 目录，相对路径）
 * - 第三层：fetch('/api/site-config') 拉取后台保存的配置（优先级最高）
 * - 两层 fetch 并行执行（各自 3 秒超时兜底），都完成后按优先级统一深合并
 * - 任何异常（网络 / 404 / JSON 解析失败 / 超时）都安静跳过对应层级，绝不阻断启动
 */
export async function initSiteConfig(): Promise<void> {
  // 并行拉取两层覆盖配置，每层独立兜底互不影响
  const [fileOverlay, backendOverlay] = await Promise.all([
    fetchConfigOverlay('/site.config.json', '本地文件 site.config.json'),
    fetchConfigOverlay('/api/site-config', '后台配置 /api/site-config'),
  ])

  // 按优先级依次深合并：内置默认 <- 本地文件 <- 后台配置（后者覆盖前者）
  let merged = deepMerge(defaultConfig, fileOverlay)
  merged = deepMerge(merged, backendOverlay)
  currentConfig = merged as SiteConfig

  // HMR 场景保留当前配置：模块热更新（重新求值）时从 hot.data 恢复
  if (import.meta.hot) {
    import.meta.hot.data.currentConfig = currentConfig
  }

  // 设置浏览器标题（title 为空时回退用站点名）
  document.title = currentConfig.site.title || currentConfig.site.name

  // 同步更新 favicon：site.logo 非空时复用为标签页图标，空值保持 index.html 默认
  applyFavicon(currentConfig.site.logo)
}

/**
 * 拉取单层配置覆盖：
 * - 3 秒超时兜底，避免配置加载异常时阻塞应用挂载
 * - 404 或非 2xx、JSON 解析失败、内容不是普通对象时视为该层无覆盖，返回 null
 * - 任何异常都不向上抛，由调用方安静合并
 */
async function fetchConfigOverlay(url: string, label: string): Promise<Record<string, unknown> | null> {
  try {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 3000)

    const res = await fetch(url, { signal: controller.signal, cache: 'no-store' })
    clearTimeout(timeout)

    if (!res.ok) {
      // 404 等非 2xx：该层没有配置，跳过并提示
      console.warn(`[站点配置] 加载 ${label} 失败（HTTP ${res.status}），该层跳过`)
      return null
    }

    // 解析覆盖配置；内容不是普通对象（如空串 / 数组）则视为无效跳过
    const overlay = await res.json()
    if (overlay === null || typeof overlay !== 'object' || Array.isArray(overlay)) {
      console.warn(`[站点配置] ${label} 内容格式异常，该层跳过`)
      return null
    }

    return overlay as Record<string, unknown>
  } catch (error) {
    // 网络失败 / 超时 / 解析异常：该层跳过，保证启动不受影响
    console.warn(`[站点配置] 加载 ${label} 失败，该层跳过:`, error)
    return null
  }
}

/**
 * 根据 Logo URL 推断 favicon 的 MIME 类型
 * 支持 data URI、常见图片扩展名，无法识别时返回 undefined 交由浏览器自动判断
 */
function getFaviconType(href: string): string | undefined {
  if (!href) return undefined
  // data URI：如 data:image/svg+xml,...
  if (href.startsWith('data:')) {
    const match = href.match(/^data:([^;,]+)/)
    if (match) return match[1]
    return undefined
  }
  const lower = href.split('?')[0]!.split('#')[0]!.toLowerCase()
  if (lower.endsWith('.ico')) return 'image/x-icon'
  if (lower.endsWith('.svg')) return 'image/svg+xml'
  if (lower.endsWith('.png')) return 'image/png'
  if (lower.endsWith('.jpg') || lower.endsWith('.jpeg')) return 'image/jpeg'
  if (lower.endsWith('.webp')) return 'image/webp'
  if (lower.endsWith('.gif')) return 'image/gif'
  return undefined
}

// 默认 favicon（与 index.html 中一致，移除 logo 时回退）
const DEFAULT_FAVICON_HREF =
  "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%2352b788' d='M12 4c2 2 3 5 2 8-1 2-3 3-4 2-2-1-2-4-1-7 1-2 2-3 3-3zM20 14c-2 2-5 3-8 2-2-1-3-3-2-4 1-2 4-2 7-1 2 1 3 2 3 3zM6 18c-1-3 0-6 3-7 2-1 4 0 4 2 0 2-3 4-6 5-1 0-1 0-1 0z'/></svg>"

/**
 * 应用 favicon 到 document.head
 * - href 非空时更新为该 URL（复用 Logo）
 * - href 为空时回退到默认 favicon（用于清除 Logo 后立即预览）
 */
export function applyFavicon(href: string | undefined): void {
  const url = href?.trim() ? href.trim() : DEFAULT_FAVICON_HREF
  if (typeof document === 'undefined') return
  try {
    let link = document.querySelector<HTMLLinkElement>('link[rel="icon"]')
    if (!link) {
      link = document.createElement('link')
      link.rel = 'icon'
      document.head.appendChild(link)
    }
    link.href = url
    const type = getFaviconType(url)
    if (type) {
      link.type = type
    } else {
      link.removeAttribute('type')
    }
  } catch (error) {
    console.warn('[站点配置] 更新 favicon 失败:', error)
  }
}

/**
 * 获取当前生效的站点配置（启动后保持不变，无需响应式）
 */
export function getSiteConfig(): SiteConfig {
  return currentConfig
}
