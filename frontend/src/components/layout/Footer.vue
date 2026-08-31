<template>
  <!-- 页脚 - 按 design-system/pages/home.html 还原 -->
  <!-- 星绘注：设计稿是极简版，不要加多余的东西 -->
  <footer class="footer">
    <div class="footer-logo">
      <div class="footer-logo-icon" :class="{ 'has-image': !!siteLogo && !logoFailed }">
        <!-- 自定义 Logo（site.logo），复用为 favicon；失败回退 SVG -->
        <img
          v-if="siteLogo && !logoFailed"
          :src="siteLogo"
          alt="Logo"
          class="footer-logo-img"
          @error="logoFailed = true"
        />
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 4c2 2 3 5 2 8-1 2-3 3-4 2-2-1-2-4-1-7 1-2 2-3 3-3z"/>
          <path d="M20 14c-2 2-5 3-8 2-2-1-3-3-2-4 1-2 4-2 7-1 2 1 3 2 3 3z"/>
          <path d="M6 18c-1-3 0-6 3-7 2-1 4 0 4 2 0 2-3 4-6 5-1 0-1 0-1 0z"/>
        </svg>
      </div>
      <span class="footer-logo-text">{{ siteName }}</span>
    </div>
    <p class="footer-text">{{ cw.slogan }}</p>

    <!-- 版权行（可配置，非空才展示） -->
    <p v-if="copyright" class="footer-copyright">{{ copyright }}</p>

    <!-- 页脚链接组（可配置，未配置则为空数组不渲染） -->
    <div v-if="cw.links.length" class="footer-links">
      <div v-for="group in cw.links" :key="group.group" class="footer-link-group">
        <span class="footer-link-group-name">{{ group.group }}</span>
        <div class="footer-link-items">
          <template v-for="item in group.items" :key="item.href">
            <!-- 站内链接走路由跳转，外链新窗口打开 -->
            <router-link v-if="item.href.startsWith('/')" :to="item.href" class="footer-link">
              {{ item.label }}
            </router-link>
            <a v-else :href="item.href" target="_blank" rel="noopener noreferrer" class="footer-link">
              {{ item.label }}
            </a>
          </template>
        </div>
      </div>
    </div>

    <!-- 备案号（可配置，非空才展示） -->
    <p v-if="icp" class="footer-icp">{{ icp }}</p>
  </footer>
</template>

<script setup lang="ts">
/**
 * 页脚组件 - 极简版
 * 按 design-system/pages/home.html 还原
 * 
 * 设计稿就是简单的logo+文字，别画蛇添足
 */
import { ref } from 'vue'
import { getSiteConfig } from '@/config/siteConfig'

// 站点配置（内置默认 + 本地覆盖）
const cfg = getSiteConfig()

// 页脚文案
const cw = cfg.footer

// 页脚 logo 文字：显示站点名（与导航栏联动，可配置 site.name）
const siteName = cfg.site.name

// 版权行（如 "2026 SynthSpark"，非空才展示）
const copyright = cw.copyright

// 备案号（非空才在页脚最下方展示）
const icp = cfg.site.icp

// 站点 Logo（复用为 favicon；为空或加载失败时回退 SVG）
const siteLogo = cfg.site.logo?.trim() || ''
const logoFailed = ref(false)
</script>

<style scoped>
.footer {
  padding: 60px 5%;
  background: var(--bg-mid, var(--bg-secondary));
  border-top: 1px solid var(--border-subtle);
  text-align: center;
  position: relative;
  z-index: 1;
}

.footer-logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.footer-logo-icon {
  width: 36px;
  height: 36px;
  border: 2px solid var(--accent-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.footer-logo-icon svg {
  width: 18px;
  height: 18px;
}

/* 自定义 Logo 图片（复用为 favicon） */
.footer-logo-icon.has-image {
  padding: 0;
  overflow: hidden;
  background: transparent;
  border-color: transparent;
}

.footer-logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 6px;
}

.footer-logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display);
}

.footer-text {
  color: var(--text-tertiary);
  font-size: 14px;
}

/* 版权行：小号、低对比度（可配置，非空才展示） */
.footer-copyright {
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 12px;
  opacity: 0.7;
}

/* 页脚链接组区域 */
.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 32px 48px;
  margin-top: 32px;
}

/* 单个链接组：组名在上、链接横向排列 */
.footer-link-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.footer-link-group-name {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  letter-spacing: 1px;
}

.footer-link-items {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px 20px;
}

.footer-link {
  font-size: 13px;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: var(--transition-fast);
}

.footer-link:hover {
  color: var(--accent-primary);
}

/* 备案号：小号、低对比度 */
.footer-icp {
  margin-top: 28px;
  font-size: 12px;
  color: var(--text-tertiary);
  opacity: 0.6;
}
</style>
