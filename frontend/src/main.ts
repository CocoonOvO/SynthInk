/**
 * 应用入口文件
 * 初始化 Vue 应用，加载插件和样式
 * (´；ω；`) 打工人的一天从这里开始
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 导入 Element Plus 样式
import 'element-plus/dist/index.css'

// 导入自定义主题样式
import './styles/themes.css'

// 导入应用组件
import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')
