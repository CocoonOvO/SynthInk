<!--
  分组管理视图
  管理所有分组
  (´；ω；`) 等后端接口 ready 了再实现
-->
<template>
  <div class="admin-groups-view">
    <div class="placeholder">
      <el-empty description="分组管理功能开发中...">
        <template #image>
          <el-icon :size="60" class="placeholder-icon"><FolderOpened /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FolderOpened } from '@element-plus/icons-vue'
</script>

<style scoped>
.admin-groups-view {
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
