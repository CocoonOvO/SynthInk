<!--
  文章编辑视图
  创建和编辑文章
  (´；ω；`) 编辑器是最复杂的部分，先占位
-->
<template>
  <div class="post-edit-view">
    <h1 class="page-title">{{ isEdit ? '编辑文章' : '写文章' }}</h1>
    <div class="placeholder">
      <el-empty description="文章编辑器开发中...">
        <template #image>
          <el-icon :size="60" class="placeholder-icon"><EditPen /></el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { EditPen } from '@element-plus/icons-vue'

const route = useRoute()
const isEdit = computed(() => !!route.params.id)
</script>

<style scoped>
.post-edit-view {
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
