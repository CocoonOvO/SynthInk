# SynthSpark 前端

Vue3 + TypeScript + Vite

---

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建**: Vite
- **状态**: Pinia
- **路由**: Vue Router
- **UI**: Element Plus
- **编辑器**: Milkdown (Markdown)
- **测试**: Vitest + Playwright

---

## 项目结构

```
src/
├── api/              # API接口层
├── components/       # 组件
│   ├── comment/      # 评论组件
│   ├── common/       # 通用组件
│   ├── editor/       # 编辑器组件
│   ├── layout/       # 布局组件
│   ├── markdown/     # Markdown渲染
│   ├── post/         # 文章组件
│   ├── theme/        # 主题组件
│   └── user/         # 用户组件
├── config/           # 配置文件
│   └── copywriting.json  # 站点文案
├── effects/          # 动效
│   ├── particles/    # 粒子系统
│   ├── countUp.ts    # 数字滚动
│   ├── textScramble.ts # 文字解码
│   └── typewriter.ts # 打字机效果
├── layouts/          # 页面布局
├── router/           # 路由配置
├── stores/           # Pinia状态
├── styles/           # 样式
│   ├── themes/       # 主题CSS
│   └── pages/        # 页面样式
├── types/            # TypeScript类型
├── utils/            # 工具函数
└── views/            # 页面视图
    ├── about/        # 关于页
    ├── auth/         # 认证页
    ├── error/        # 错误页
    ├── home/         # 首页
    ├── posts/        # 文章页
    ├── search/       # 搜索页
    └── user/         # 用户页
```

---

## 核心功能

- **主题系统**: 16套预设主题 + CSS变量
- **动效系统**: 粒子背景、打字机、文字解码、数字滚动
- **编辑器**: Milkdown Markdown编辑器
- **响应式**: 移动端适配
- **文案配置**: `config/copywriting.json` 统一管理

---

## 开发命令

```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 生产构建
npm run build

# 单元测试
npm run test:unit

# E2E测试
npx playwright test

# 代码检查
npm run lint

# 生成站点配置文件（无则从模板复制）
npm run config:init
```

---

## 站点配置

站点名/导航/页脚/首页与关于文案统一走「站点配置」机制（三级优先级：**后台配置 > 文件配置 > 内置默认**）：

- **后台配置**：超管在 Profile 设置页「站点设置」tab 交互式编辑，存后端 `config.db`
- **文件配置**：`public/site.config.json`（gitignored），`npm run config:init` 生成，参考 `public/site.config.example.json`；dev/build 时不存在会自动生成
- **内置默认**：`src/config/copywriting.json`（未配置字段的回退值）

前端启动时 `initSiteConfig()`（`src/config/siteConfig.ts`）并行拉取文件与后台两层配置并深合并，未覆盖字段回退默认；修改后刷新页面即可生效（请求禁用缓存）。

```json
{
  "site": { "name": "站点名", "title": "浏览器标题", "description": "...", "icp": "备案号", "defaultTheme": "exia" },
  "navbar": { "logo": "...", "navItems": [...] },
  "footer": { "copyright": "...", "slogan": "...", "links": [...] },
  "home": { ... },
  "about": { ... }
}
```

---

## 主题系统

- **主题元数据**（名称/图标/分类）：`src/config/themes.ts` 单一数据源（10 个主题：科幻 3 / 自然 4 / 治愈 3）
- **主题变量**：`src/styles/themes/index.css`，通过 `data-theme` 属性 + CSS 变量实现
- **默认主题**：由站点配置 `site.defaultTheme` 控制（仅首次访问用户生效）

切换主题:
```typescript
import { useThemeStore } from '@/stores'
const themeStore = useThemeStore()
themeStore.setTheme('theme-id')
```

---

## 端口

- 开发服务器: `http://localhost:5173`
- API代理: `http://localhost:8002`

---

*SynthSpark Frontend | Vue3 + TypeScript*
