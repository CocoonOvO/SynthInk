import { createRouter, createWebHistory } from 'vue-router'

const HubView = () => import('@/views/HubView.vue')
const OsDemo = () => import('@/views/demos/OsDemo.vue')
const TerminalDemo = () => import('@/views/demos/TerminalDemo.vue')
const SpaceDemo = () => import('@/views/demos/SpaceDemo.vue')
const DeskDemo = () => import('@/views/demos/DeskDemo.vue')
const ChatDemo = () => import('@/views/demos/ChatDemo.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Hub', component: HubView },
    { path: '/os', name: 'Os', component: OsDemo },
    { path: '/terminal', name: 'Terminal', component: TerminalDemo },
    { path: '/space', name: 'Space', component: SpaceDemo },
    { path: '/desk', name: 'Desk', component: DeskDemo },
    { path: '/chat', name: 'Chat', component: ChatDemo },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() { return { top: 0 } }
})

export default router
