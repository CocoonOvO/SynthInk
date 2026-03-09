<template>
  <!--
    编辑器布局 - 没有普通导航栏
    老大说编辑页面要独立，不要和普通页面混在一起 (´；ω；`)
  -->
  <div class="editor-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
/**
 * 编辑器布局组件
 * 纯容器，啥也不包，让编辑页面自己玩
 */
</script>

<style scoped>
.editor-layout {
  min-height: 100vh;
  /* 编辑页面自己处理布局 */
}
</style>
