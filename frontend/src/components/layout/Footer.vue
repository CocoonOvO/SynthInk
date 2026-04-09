<template>
  <!-- 页脚 - 按 design-system/pages/home.html 还原 -->
  <!-- 星绘注：设计稿是极简版，不要加多余的东西 -->
  <footer class="footer">
    <div class="footer-logo">
      <div class="footer-logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 4c2 2 3 5 2 8-1 2-3 3-4 2-2-1-2-4-1-7 1-2 2-3 3-3z"/>
          <path d="M20 14c-2 2-5 3-8 2-2-1-3-3-2-4 1-2 4-2 7-1 2 1 3 2 3 3z"/>
          <path d="M6 18c-1-3 0-6 3-7 2-1 4 0 4 2 0 2-3 4-6 5-1 0-1 0-1 0z"/>
        </svg>
      </div>
      <span class="footer-logo-text">{{ cw.copyright }}</span>
    </div>
    <p class="footer-text">{{ cw.slogan }}</p>
  </footer>
</template>

<script setup lang="ts">
/**
 * 页脚组件 - 极简版
 * 按 design-system/pages/home.html 还原
 * 
 * 设计稿就是简单的logo+文字，别画蛇添足
 */
import copywriting from '@/config/copywriting.json'

// 文案配置
const cw = copywriting.footer
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
</style>
