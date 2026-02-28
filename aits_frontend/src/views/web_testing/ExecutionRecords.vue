<template>
  <div class="execution-records-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>测试执行记录</span>
        </div>
      </template>
      <div class="empty-state">
        <el-empty description="执行记录列表开发中..." />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// Placeholder for Execution Records component
</script>

<style scoped>
.card-header {
  font-weight: bold;
}
</style>
