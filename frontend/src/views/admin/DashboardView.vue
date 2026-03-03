<!--
  管理后台概览
  展示统计数据和快捷入口
  (´；ω；`) 等后端接口 ready 了再实现
-->
<template>
  <div class="dashboard-view">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">--</span>
          <span class="stat-label">文章总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><User /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">--</span>
          <span class="stat-label">用户总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><PriceTag /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">--</span>
          <span class="stat-label">标签总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="24"><FolderOpened /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">--</span>
          <span class="stat-label">分组总数</span>
        </div>
      </div>
    </div>

    <div class="placeholder-section">
      <el-empty description="仪表盘数据开发中..." />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document, User, PriceTag, FolderOpened } from '@element-plus/icons-vue'
</script>

<style scoped>
.dashboard-view {
  padding: var(--space-xl) 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  transition: var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--accent-primary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: var(--gradient-hero);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.placeholder-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-2xl);
}
</style>
