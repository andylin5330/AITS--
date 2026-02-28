<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="aside">
      <div class="logo">AITS 智能测试</div>
      <el-menu
        default-active="1"
        class="el-menu-vertical-demo"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
        router
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>首页仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-sub-menu index="/api-testing">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>接口自动化</span>
          </template>
          <el-menu-item index="/api-testing/navigation">API功能导航</el-menu-item>
          <el-menu-item index="/api-testing/standard">API规范管理</el-menu-item>
          <el-menu-item index="/api-testing/agent">AI场景智能体</el-menu-item>
          <el-menu-item index="/api-testing/cases">测试用例管理</el-menu-item>
          <el-menu-item index="/api-testing/suites">测试套件管理</el-menu-item>
          <el-menu-item index="/api-testing/records">测试执行记录</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/web-testing">
          <template #title>
            <el-icon><PictureRounded /></el-icon>
            <span>Web测试</span>
          </template>
          <el-menu-item index="/web-testing/agent-generator">测试用例生成智能体</el-menu-item>
          <el-menu-item index="/web-testing/agent-runner">自动化测试智能体</el-menu-item>
          <el-menu-item index="/web-testing/cases">测试用例管理</el-menu-item>
          <el-menu-item index="/web-testing/suites">测试套件管理</el-menu-item>
          <el-menu-item index="/web-testing/records">测试执行记录</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="/ai-core">
          <template #title>
            <el-icon><Cpu /></el-icon>
            <span>AI 核心配置</span>
          </template>
          <el-menu-item index="/ai-core/llm">大模型接入</el-menu-item>
          <el-menu-item index="/ai-core/rag">RAG 知识库</el-menu-item>
          <el-menu-item index="/ai-core/mcp">MCP 插件集</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/scheduled-tasks">
          <el-icon><Clock /></el-icon>
          <span>定时任务调度</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container class="main-container">
      <el-header class="header">
        <div class="breadcrumb">
           AITS 智能测试平台
        </div>
        <div class="user-info">
          <span>欢迎, {{ userStore.userInfo.username }}</span>
          <el-button type="danger" link @click="handleLogout">退出登录</el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useUserStore } from '../store/user'
import { useRouter } from 'vue-router'
import {
  Monitor,
  Folder,
  Connection,
  PictureRounded,
  Cpu,
  Clock
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  display: flex;
}
.aside {
  background-color: #545c64;
  display: flex;
  flex-direction: column;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid #434a50;
  background-color: #434a50;
}
.el-menu-vertical-demo {
  flex: 1;
  border-right: none;
}
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}
.header {
  height: 60px;
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.breadcrumb {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.main-content {
  padding: 20px;
  overflow: auto;
}
</style>
