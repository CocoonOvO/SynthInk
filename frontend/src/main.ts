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

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(hljsVuePlugin)

// 初始化主题 - 需要在pinia挂载后才能使用store
const themeStore = useThemeStore(pinia)
themeStore.initTheme()

app.mount('#app')
