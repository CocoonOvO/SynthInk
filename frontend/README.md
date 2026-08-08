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

主题由 `src/themes/index.ts` 自动发现，每个主题一个独立目录：

```
src/themes/
├── index.ts              # 发现模块：自动扫描 system/ 与 custom/，聚合元数据/CSS/脚本
├── system/               # 系统主题（入库）：deep-space/ cyberpunk/ exia/ sakura/ bamboo/
│   │                     #   twins/ mygo-light/ strawberry-cream/ mint-choco/ orange-soda/
│   └── <id>/theme.json + theme.css
└── custom/               # 自定义主题（gitignore，不入仓库）
    └── <id>/theme.json + theme.css + theme.ts(可选)
```

- **theme.json** 元数据：`id` / `name` / `icon` / `category`（任意字符串，未知分类自动归组）/ `behaviors`（可选能力标记，如 `["matrix-rain"]`）
- **theme.css** 主题变量：选择器**必须写 `:root[data-theme="主题id"]`**（特异性高于 `:root`，避免注入顺序导致变量被默认值覆盖）；可含 `--particle-type` 等粒子变量
- **theme.ts** 可选主题脚本：`export function activate(ctx)`（返回可选 cleanup）+ 可选 `export function deactivate(ctx)`；主题切换/初始化时由 store 自动调用
- **自定义主题**：放入 `custom/<id>/` 即自动出现在主题面板；与系统主题同 id 时**覆盖**系统主题（CSS 与脚本）；新增主题后 dev 需重启（或触发模块重载），build 自动扫描
- **矩阵雨等能力判断**：用 `themeHasBehavior(id, 'matrix-rain')`，不要硬编码主题 id

切换主题:
```typescript
import { useThemeStore } from '@/stores'
const themeStore = useThemeStore()
themeStore.setTheme('theme-id')
```

默认主题：由站点配置 `site.defaultTheme` 控制（仅首次访问用户生效）。

---

## 端口

- 开发服务器: `http://localhost:5173`
- API代理: `http://localhost:8002`

---

*SynthSpark Frontend | Vue3 + TypeScript*
