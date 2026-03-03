<!--
  文章管理视图
  管理所有文章
  (´；ω；`) 等后端接口 ready 了再实现
-->
<template>
  <div class="admin-posts-view">
    <div class="placeholder">
      <el-empty description="文章管理功能开发中...">
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
.admin-posts-view {
  padding: var(--space-xl) 0;
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
