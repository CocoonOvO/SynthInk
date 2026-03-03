/**
 * 路由配置文件
 * 老大说要精致的结构，我就把路由都规划好了
 * 虽然后端还没完全准备好，但架子先搭起来
 * (´；ω；`) 打工人的自觉
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 布局组件
const MainLayout = () => import('@/layouts/MainLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')

// 页面组件 - 懒加载，优化首屏
const HomeView = () => import('@/views/home/HomeView.vue')
const PostListView = () => import('@/views/posts/PostListView.vue')
const PostDetailView = () => import('@/views/posts/PostDetailView.vue')
const PostEditView = () => import('@/views/posts/PostEditView.vue')
const LoginView = () => import('@/views/auth/LoginView.vue')
const RegisterView = () => import('@/views/auth/RegisterView.vue')
const ProfileView = () => import('@/views/user/ProfileView.vue')
const SettingsView = () => import('@/views/user/SettingsView.vue')
const AdminDashboard = () => import('@/views/admin/DashboardView.vue')
const AdminPosts = () => import('@/views/admin/PostsView.vue')
const AdminUsers = () => import('@/views/admin/UsersView.vue')
const AdminTags = () => import('@/views/admin/TagsView.vue')
const AdminGroups = () => import('@/views/admin/GroupsView.vue')
const NotFoundView = () => import('@/views/error/NotFoundView.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  // 主布局路由
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: HomeView,
        meta: { title: '首页' },
      },
      {
        path: 'posts',
        name: 'PostList',
        component: PostListView,
        meta: { title: '文章列表' },
      },
      {
        path: 'posts/:id',
        name: 'PostDetail',
        component: PostDetailView,
        meta: { title: '文章详情' },
      },
      {
        path: 'tags/:id',
        name: 'TagPosts',
        component: PostListView,
        meta: { title: '标签文章' },
      },
      {
        path: 'groups/:id',
        name: 'GroupPosts',
        component: PostListView,
        meta: { title: '分组文章' },
      },
    ],
  },

  // 认证布局路由
  {
    path: '/auth',
    component: AuthLayout,
    meta: { guestOnly: true },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: LoginView,
        meta: { title: '登录' },
      },
      {
        path: 'register',
        name: 'Register',
        component: RegisterView,
        meta: { title: '注册' },
      },
    ],
  },

  // 用户中心路由
  {
    path: '/user',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { title: '个人中心' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: SettingsView,
        meta: { title: '账号设置' },
      },
      {
        path: 'posts/new',
        name: 'PostCreate',
        component: PostEditView,
        meta: { title: '写文章' },
      },
      {
        path: 'posts/:id/edit',
        name: 'PostEdit',
        component: PostEditView,
        meta: { title: '编辑文章' },
      },
    ],
  },

  // 后台管理路由
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { title: '管理后台' },
      },
      {
        path: 'posts',
        name: 'AdminPosts',
        component: AdminPosts,
        meta: { title: '文章管理' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: { title: '用户管理' },
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: AdminTags,
        meta: { title: '标签管理' },
      },
      {
        path: 'groups',
        name: 'AdminGroups',
        component: AdminGroups,
        meta: { title: '分组管理' },
      },
    ],
  },

  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView,
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    // 每次路由切换回到顶部
    return { top: 0 }
  },
})

// 路由守卫 - 后面再完善鉴权逻辑
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - SynthInk` : 'SynthInk'
  next()
})

export default router
