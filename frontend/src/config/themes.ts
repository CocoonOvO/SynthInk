/**
 * 主题元数据单一数据源
 * 收敛了原本散落在 Navbar.vue / stores/theme.ts 中的主题名称、图标与分类信息
 *
 * 科幻：深空 / 赛博朋克 / 能天使
 * 自然：樱花 / 竹林绿 / 双子 / 星歌
 * 治愈：草莓奶油 / 薄荷巧克力 / 香橙气泡
 */

// 主题类型 - 10个核心主题
export type Theme =
  | 'deep-space'    // 深空（原dark）
  | 'cyberpunk'     // 赛博朋克
  | 'exia'          // 能天使
  | 'sakura'        // 樱花
  | 'bamboo'        // 竹林绿
  | 'twins'         // 双子
  | 'mygo-light'    // 星歌
  | 'strawberry-cream'  // 草莓奶油
  | 'mint-choco'    // 薄荷巧克力
  | 'orange-soda'   // 香橙气泡

// 主题分类类型
export type ThemeCategory = 'scifi' | 'nature' | 'healing'

// 分类中文标签
export const THEME_CATEGORY_LABELS: Record<ThemeCategory, string> = {
  scifi: '科幻',
  nature: '自然',
  healing: '治愈'
}

// 主题元数据接口
export interface ThemeMeta {
  id: Theme
  name: string
  icon: string
  category: ThemeCategory
}

// 全部主题元数据（名称/图标/分类的唯一定义处）
export const THEMES: ThemeMeta[] = [
  { id: 'deep-space', name: '深空', icon: '🌙', category: 'scifi' },
  { id: 'cyberpunk', name: '赛博朋克', icon: '🌃', category: 'scifi' },
  { id: 'exia', name: '能天使', icon: '⚡', category: 'scifi' },
  { id: 'sakura', name: '樱花', icon: '🌸', category: 'nature' },
  { id: 'bamboo', name: '竹林绿', icon: '🎋', category: 'nature' },
  { id: 'twins', name: '双子', icon: '♊', category: 'nature' },
  { id: 'mygo-light', name: '星歌', icon: '⭐', category: 'nature' },
  { id: 'strawberry-cream', name: '草莓奶油', icon: '🍓', category: 'healing' },
  { id: 'mint-choco', name: '薄荷巧克力', icon: '🍃', category: 'healing' },
  { id: 'orange-soda', name: '香橙气泡', icon: '🍊', category: 'healing' }
]

// 分类主题分组
export const themeCategories: Record<ThemeCategory, Theme[]> = {
  scifi: ['deep-space', 'cyberpunk', 'exia'],
  nature: ['sakura', 'bamboo', 'twins', 'mygo-light'],
  healing: ['strawberry-cream', 'mint-choco', 'orange-soda']
}
