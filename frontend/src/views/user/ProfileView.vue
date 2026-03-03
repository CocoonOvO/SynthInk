<!--
  个人中心视图
  展示用户信息和个人文章
  (´；ω；`) 等后端接口 ready 了再实现
-->
<template>
  <div class="profile-view">
    <h1 class="page-title">个人中心</h1>
    <div class="placeholder">
      <el-empty description="个人中心功能开发中...">
        <template #image>
          <el-icon :size="60" class="placeholder-icon"><User /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User } from '@element-plus/icons-vue'
</script>

<style scoped>
.profile-view {
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
