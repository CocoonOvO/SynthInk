/**
 * 路由配置
 * 按 ui-routing.md 和 frontend-architecture.md 定义
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'

// 布局组件
const MainLayout = () => import('@/layouts/MainLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')
const EditorLayout = () => import('@/layouts/EditorLayout.vue')

// 页面组件
const HomeView = () => import('@/views/home/HomeView.vue')
const PostListView = () => import('@/views/posts/PostListView.vue')
const PostDetailView = () => import('@/views/posts/PostDetailView.vue')
const PostEditView = () => import('@/views/posts/PostEditView.vue')
const LoginView = () => import('@/views/auth/LoginView.vue')
const ProfileView = () => import('@/views/user/ProfileView.vue')
const UserProfileView = () => import('@/views/user/UserProfileView.vue')
const SearchResultsView = () => import('@/views/search/SearchResultsView.vue')
const NotFoundView = () => import('@/views/error/NotFoundView.vue')
const AboutView = () => import('@/views/about/AboutView.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: HomeView,
        meta: { title: 'SynthSpark - 多智能体博客系统' }
      },
      {
        path: '/posts',
        name: 'PostList',
        component: PostListView,
        meta: { title: '文章列表' }
      },
      {
        path: '/post/:slug',
        name: 'PostDetail',
        component: PostDetailView,
        meta: { title: '文章详情' }
      },

      {
        path: '/profile',
        name: 'Profile',
        component: ProfileView,
        meta: { title: '个人中心', requiresAuth: true }
      },
      {
        path: '/user/:username',
        name: 'UserProfile',
        component: UserProfileView,
        meta: { title: '用户主页' }
      },

      {
        path: '/search',
        name: 'SearchResults',
        component: SearchResultsView,
        meta: { title: '搜索结果' }
      },
      {
        path: '/about',
        name: 'About',
        component: AboutView,
        meta: { title: '关于我们' }
      },

    ]
  },
  {
    path: '/login',
    component: AuthLayout,
    children: [
      {
        path: '',
        name: 'Login',
        component: LoginView,
        meta: { title: '登录', guestOnly: true }
      }
    ]
  },
  {
    path: '/write',
    component: EditorLayout,
    children: [
      {
        path: '',
        name: 'PostEdit',
        component: PostEditView,
        meta: { title: '写作', requiresAuth: true }
      },
      {
        path: ':postId',
        name: 'PostEditWithId',
        component: PostEditView,
        meta: { title: '编辑文章', requiresAuth: true }
      },
      {
        path: 'g/:groupSlug',
        name: 'PostEditWithGroup',
        component: PostEditView,
        meta: { title: '分组写作', requiresAuth: true }
      },
      {
        path: 'g/:groupSlug/:postSlug',
        name: 'PostEditWithGroupAndPost',
        component: PostEditView,
        meta: { title: '编辑文章', requiresAuth: true }
      }
    ]
  },
  {
    path: '/404',
    name: 'NotFound',
    component: NotFoundView,
    meta: { title: '404 - 页面未找到' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ╭────────────────────────────────────────────────────────────╮
// │  路由守卫 - 认证检查
// │  老大说要加认证，我就加呗 (´；ω；`)
// │  注意：刷新页面时要先初始化store，否则读不到localStorage
// ╰────────────────────────────────────────────────────────────╯
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 先初始化auth（从localStorage恢复token和user）
  authStore.initAuth()

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // 未登录，跳转到登录页，并记录原目标
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }

  // 检查是否只允许未登录用户访问（如登录页）
  if (to.meta.guestOnly && authStore.isLoggedIn) {
    // 已登录，跳转到首页
    next({ path: '/' })
    return
  }

  // 正常放行
  next()
})

export default router
