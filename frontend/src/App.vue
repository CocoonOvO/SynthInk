<template>
  <!-- 根组件 - 应用入口 -->
  <router-view />
</template>

<script setup lang="ts">
/**
 * 根组件
 * 老大让我保持简洁，我就保持简洁 (´；ω；`)
 * 虽然我想写点什么，但老大说不要...
 */
</script>

<style>
/* 字体引入 - 必须放在最前面 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Orbitron:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-body);
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  line-height: 1.6;
  position: relative;
}
</style>
