<template>
  <!-- 主布局 - 导航+内容+页脚 -->
  <div class="main-layout">
    <Navbar />
    <main class="main-content">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup lang="ts">
/**
 * 主布局组件
 * 老大让我把导航和页脚整合进来，我就整合 (╯°□°）╯
 * 虽然这活很简单，但架不住活儿多啊
 */
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 70px; /* 为固定导航栏留出空间 */
}
</style>
