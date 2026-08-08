/**
 * 主题发现模块（主题系统单一入口）
 *
 * 自动扫描系统主题目录（src/themes/system/）与自定义主题目录（src/themes/custom/），
 * 每个主题一个目录，含：
 * - theme.json  元数据（id/name/icon/category/behaviors）
 * - theme.css   主题变量（[data-theme="id"] 块，自动全局加载）
 * - theme.ts    可选主题脚本（activate/deactivate 钩子，主题切换时调用）
 *
 * 自定义主题目录已被 gitignore，部署者自行添加主题不入仓库；
 * 自定义主题与系统主题 id 冲突时，自定义主题覆盖系统主题（并输出中文警告）。
 *
 * 主题 CSS 选择器约定：必须写成 `:root[data-theme="主题id"]`（特异性高于 :root），
 * 这样无论样式注入顺序如何，主题变量都能覆盖 base.css 的 :root 默认变量。
 */

// 主题基础样式（:root 默认变量 + 粒子画布/背景层/矩阵雨/过渡动画等共享样式）
// 必须在本模块（主题 glob CSS 注入之前）导入：styles/index.css 的 @import 在 dev 下
// 异步加载、晚于 glob 注入的 style，会反序覆盖主题变量（:root 与 [data-theme] 特异性相同）
import '@/styles/themes/base.css'

// ── 主题元数据与脚本契约 ──

/**
 * theme.json 元数据（容错解析：字段缺失时用默认值兜底）
 */
export interface ThemeMetaFile {
  id?: string
  name?: string
  icon?: string
  category?: string
  behaviors?: string[]
}

/**
 * 主题脚本契约（theme.ts，可选导出）：
 * - activate：主题被激活时调用（切换选中 / 首次加载为默认主题）
 *   可返回 cleanup 函数，离开主题时自动执行（清理 DOM/定时器/事件等）
 * - deactivate：可选，主题离开时调用（activate 未返回 cleanup 时兜底）
 * - 模块顶层禁止副作用，一切逻辑放在 activate 中
 */
export interface ThemeScriptContext {
  themeId: string
}

export interface ThemeScriptModule {
  activate?: (context: ThemeScriptContext) => void | (() => void)
  deactivate?: (context: ThemeScriptContext) => void
}

/**
 * 主题元数据（发现模块归一化后的结构）
 */
export interface ThemeMeta {
  id: string
  name: string
  icon: string
  category: string
  behaviors: string[]
  source: 'system' | 'custom'
  script?: ThemeScriptModule
}

// 主题 id 类型（动态发现，无法静态枚举，统一用 string）
export type Theme = string

// ── 已知分类的中文标签（未知分类回退原值） ──

const KNOWN_CATEGORY_LABELS: Record<string, string> = {
  scifi: '科幻',
  nature: '自然',
  healing: '治愈',
}

/**
 * 获取分类的中文标签；未知分类返回原值（自定义分类也能正常显示）
 */
export function getCategoryLabel(category: string): string {
  return KNOWN_CATEGORY_LABELS[category] || category
}

// ── 自动发现（Vite glob，编译期扫描） ──

// 元数据：system 与 custom 分开收集，便于冲突覆盖处理
const systemMetaFiles = import.meta.glob<ThemeMetaFile>('./system/*/theme.json', {
  eager: true,
  import: 'default',
})
const customMetaFiles = import.meta.glob<ThemeMetaFile>('./custom/*/theme.json', {
  eager: true,
  import: 'default',
})

// 主题 CSS：全局自动加载（system 先注入，custom 后注入，后者覆盖前者）
// 注意：glob 结果必须被引用（导出），否则 CSS 模块会被 tree-shake 丢弃
export const systemCssModules = import.meta.glob('./system/*/theme.css', { eager: true })
export const customCssModules = import.meta.glob('./custom/*/theme.css', { eager: true })

// 主题脚本：按主题目录收集，供 store 在主题切换时调用生命周期钩子
// 注意：不使用 import: 'default'（脚本可能只有命名导出 activate/deactivate），
// 直接取模块命名空间作为 ThemeScriptModule
const systemScripts = import.meta.glob('./system/*/theme.{ts,js}', { eager: true })
const customScripts = import.meta.glob('./custom/*/theme.{ts,js}', { eager: true })

// ── 主题收集与归一化 ──

/**
 * 归一化单个主题元数据；非法（缺 id / 缺 name）返回 null
 */
function normalizeTheme(
  file: ThemeMetaFile,
  source: 'system' | 'custom',
  script?: ThemeScriptModule
): ThemeMeta | null {
  const id = file.id?.trim()
  const name = file.name?.trim()
  // id 与 name 必填，缺失视为非法主题
  if (!id || !name) {
    console.warn(`[主题系统] 忽略非法主题（${source}，缺少 id 或 name）`)
    return null
  }
  return {
    id,
    name,
    icon: file.icon || '🎨',
    category: file.category || 'custom',
    behaviors: Array.isArray(file.behaviors) ? file.behaviors : [],
    source,
    script,
  }
}

// 按 id 收集：system 先入，custom 覆盖（自定义优先）
const themeMap = new Map<string, ThemeMeta>()

for (const [path, file] of Object.entries(systemMetaFiles)) {
  // 主题脚本（可选）：glob 值为模块命名空间，直接作为脚本模块使用
  const script = (systemScripts[path.replace(/\.json$/, '.ts')] || systemScripts[path.replace(/\.json$/, '.js')]) as ThemeScriptModule | undefined
  const meta = normalizeTheme(file ?? {}, 'system', script)
  if (meta && !themeMap.has(meta.id)) {
    themeMap.set(meta.id, meta)
  }
}

for (const [path, file] of Object.entries(customMetaFiles)) {
  const script = (customScripts[path.replace(/\.json$/, '.ts')] || customScripts[path.replace(/\.json$/, '.js')]) as ThemeScriptModule | undefined
  const meta = normalizeTheme(file ?? {}, 'custom', script)
  if (meta) {
    if (themeMap.has(meta.id)) {
      // 自定义主题覆盖同名系统主题（CSS 与脚本均已随 glob 顺序生效）
      console.warn(`[主题系统] 自定义主题「${meta.id}」覆盖同名系统主题`)
    }
    themeMap.set(meta.id, meta)
  }
}

// ── 对外导出 ──

/**
 * 全部已发现主题（系统 + 自定义，按名称排序保证展示顺序稳定）
 */
export const THEMES: ThemeMeta[] = [...themeMap.values()].sort((a, b) => a.name.localeCompare(b.name, 'zh'))

/**
 * 按分类分组的主题（面板展示用；未知分类按出现顺序归组，顺序：科幻/自然/治愈/其他）
 */
export const themeCategories: Record<string, ThemeMeta[]> = (() => {
  const groups = new Map<string, ThemeMeta[]>()
  for (const meta of THEMES) {
    const list = groups.get(meta.category) || []
    list.push(meta)
    groups.set(meta.category, list)
  }
  // 已知分类固定顺序，未知分类（custom）追加在后
  const ordered = new Map<string, ThemeMeta[]>()
  for (const key of ['scifi', 'nature', 'healing']) {
    if (groups.has(key)) ordered.set(key, groups.get(key)!)
  }
  for (const [key, list] of groups) {
    if (!ordered.has(key)) ordered.set(key, list)
  }
  return Object.fromEntries(ordered)
})()

/**
 * 按 id 获取主题元数据
 */
export function getThemeMeta(id: string): ThemeMeta | undefined {
  return themeMap.get(id)
}

/**
 * 查询主题是否具备某行为能力（替代硬编码主题 id 判断）
 * 例：themeHasBehavior(currentTheme, 'matrix-rain')
 */
export function themeHasBehavior(id: string, behavior: string): boolean {
  return themeMap.get(id)?.behaviors?.includes(behavior) ?? false
}

// ── 主题脚本生命周期（供 store 调用） ──

/**
 * 激活主题脚本：返回激活时注册的 cleanup（离开主题时由 store 调用）
 */
export function activateThemeScript(meta: ThemeMeta | undefined, themeId: string): (() => void) | undefined {
  if (!meta?.script?.activate) return undefined
  const cleanup = meta.script.activate({ themeId })
  return typeof cleanup === 'function' ? cleanup : undefined
}

/**
 * 停用主题脚本（activate 未返回 cleanup 时兜底调用 deactivate）
 */
export function deactivateThemeScript(meta: ThemeMeta | undefined, themeId: string): void {
  meta?.script?.deactivate?.({ themeId })
}
