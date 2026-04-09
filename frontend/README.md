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
npm run test:e2e

# 代码检查
npm run lint
```

---

## 文案配置

站点文案统一配置在 `src/config/copywriting.json`：

```json
{
  "home": { "title": "...", "desc": "..." },
  "about": { "title": "...", "desc": "..." },
  "footer": { "copyright": "...", "slogan": "..." },
  "navbar": { "logo": "...", "navItems": [...] }
}
```

修改后无需重新构建，刷新页面即可生效。

---

## 主题系统

主题配置在 `src/styles/themes/index.css`，通过CSS变量实现。

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
