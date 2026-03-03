<!--
  文章列表视图
  展示文章列表，支持筛选和分页
  (´；ω；`) 虽然还没数据，但架子要先搭好
-->
<template>
  <div class="post-list-view">
    <h1 class="page-title">文章列表</h1>
    <div class="placeholder">
      <el-empty description="文章列表功能开发中...">
        <template #image>
          <el-icon :size="60" class="placeholder-icon"><Document /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'
</script>

<style scoped>
.post-list-view {
  padding: var(--space-xl) 0;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xl);
}

.placeholder {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl);
  text-align: center;
}

.placeholder-icon {
  color: var(--accent-primary);
  margin-bottom: var(--space-md);
}
</style>
