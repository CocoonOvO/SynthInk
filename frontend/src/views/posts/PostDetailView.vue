<!--
  文章详情视图
  展示单篇文章内容
  (´；ω；`) 等后端接口 ready 了再实现
-->
<template>
  <div class="post-detail-view">
    <div class="placeholder">
      <el-empty description="文章详情功能开发中...">
        <template #image>
          <el-icon :size="60" class="placeholder-icon"><Reading /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Reading } from '@element-plus/icons-vue'
</script>

<style scoped>
.post-detail-view {
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
