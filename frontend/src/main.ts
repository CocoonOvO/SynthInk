/**
 * 前端入口文件
 * 老大让我初始化主题，我就初始化 (╯°□°）╯
 * 这活儿虽然简单，但架不住活儿多啊
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import hljsVuePlugin from '@highlightjs/vue-plugin'
import './utils/hljs-languages'

// Prism 主题 - 用于 Milkdown 代码块高亮
import 'prismjs/themes/prism-tomorrow.css'

// 样式入口
import './styles/index.css'

// 导入主题store进行初始化
import { useThemeStore } from './stores'

// 站点可配置（启动时拉取 public/site.config.json，失败自动回退内置默认）
import { initSiteConfig } from './config/siteConfig'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(hljsVuePlugin)

// 初始化主题 - 需要在pinia挂载后才能使用store
const themeStore = useThemeStore(pinia)

// 初始化站点配置后挂载：保证首屏可读到最终配置（含失败回退与超时兜底）
// 主题初始化也放到配置加载后：首次访问用户的默认主题取自站点配置（site.defaultTheme）
initSiteConfig().finally(() => {
  themeStore.initTheme()
  app.mount('#app')
})
