<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">总项目数</div>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">执行中任务</div>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">API 用例数</div>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <template #header>
            <div class="card-header">Web UI用例数</div>
          </template>
          <div class="stat-value">--</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="mt-20">
      <template #header>
        <div class="card-header">
          <span>欢迎使用 AITS (AI-empowered Intelligent Testing System)</span>
        </div>
      </template>
      <div class="welcome-content">
        <p>AITS 是一个旨在利用人工智能技术赋能软件测试全流程的平台。通过侧边栏导航，您可以管理测试项目、配置和执行API与UI测试套件、并且调度 AI Agent 分析缺陷。</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.home {
  width: 100%;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin: 10px 0;
}
.mt-20 {
  margin-top: 20px;
}
.welcome-content {
  line-height: 1.6;
  color: #606266;
}
</style>
