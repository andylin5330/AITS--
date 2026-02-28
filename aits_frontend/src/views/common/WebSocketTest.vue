<template>
  <div class="ws-test-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>WebSocket 日志实时接收测试</span>
        </div>
      </template>

      <div class="control-panel">
        <el-form :inline="true" :model="form" class="demo-form-inline">
          <el-form-item label="任务/房间 ID">
            <el-input v-model="form.taskId" placeholder="输入 task_id 如 general" />
          </el-form-item>
          <el-form-item>
            <el-button type="success" @click="connectWs" :disabled="isConnected">连接 WebSocket</el-button>
            <el-button type="danger" @click="disconnectWs" :disabled="!isConnected">断开连接</el-button>
            <el-button type="warning" @click="triggerTask" :disabled="!isConnected">触发Celery任务</el-button>
            <el-button @click="clearLogs">清空日志</el-button>
          </el-form-item>
        </el-form>
        <div style="margin-top: 10px;">
          <el-tag :type="isConnected ? 'success' : 'info'">
            状态: {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
        </div>
      </div>

      <div class="log-viewer" ref="logViewerRef">
        <div v-for="(log, index) in logs" :key="index" class="log-entry">
          <span class="timestamp">[{{ log.time }}]</span>
          <span class="message">{{ log.message }}</span>
        </div>
        <div v-if="logs.length === 0" class="empty-placeholder">暂无日志数据...</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onUnmounted } from 'vue'
import axios from 'axios'

const form = reactive({
  taskId: 'general'
})

const isConnected = ref(false)
const logs = ref<{ time: string, message: string }[]>([])
const logViewerRef = ref<HTMLElement | null>(null)
let ws: WebSocket | null = null

const scrollToBottom = async () => {
    await nextTick()
    if (logViewerRef.value) {
        logViewerRef.value.scrollTop = logViewerRef.value.scrollHeight
    }
}

const appendLog = (msg: string) => {
    const now = new Date()
    logs.value.push({
        time: now.toLocaleTimeString() + '.' + String(now.getMilliseconds()).padStart(3, '0'),
        message: msg
    })
    scrollToBottom()
}

const connectWs = () => {
  if (ws) {
      ws.close()
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  // For dev environment, point to local django server
  const host = import.meta.env.VITE_API_BASE_URL?.replace(/^http/, 'ws') || 'ws://127.0.0.1:8000'
  const wsUrl = `${host}/ws/logs/${form.taskId}/`
  
  appendLog(`正在尝试连接到: ${wsUrl}...`)
  
  ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    isConnected.value = true
    appendLog('【系统】WebSocket 连接已成功建立！')
  }

  ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data)
        appendLog(`[接收] ${data.message || event.data}`)
    } catch (e) {
        appendLog(`[接收Raw] ${event.data}`)
    }
  }

  ws.onclose = (event) => {
    isConnected.value = false
    appendLog(`【系统】WebSocket 连接已断开 (Code: ${event.code}, Reason: ${event.reason || '无'})`)
  }
  
  ws.onerror = (error) => {
    appendLog(`【错误】WebSocket 发生意外异常！`)
    console.error('WebSocket Error:', error)
  }
}

const disconnectWs = () => {
  if (ws) {
    appendLog('【系统】主动断开连接...')
    ws.close()
    ws = null
  }
}

const triggerTask = async () => {
    try {
        appendLog('【系统】正在请求后台启动任务: ' + form.taskId)
        const host = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
        await axios.post(`${host}/api/common/trigger-ws-task/`, {
            task_id: form.taskId,
            iterations: 5
        })
        appendLog('【系统】收到服务端任务部署成功的确认!')
    } catch(err) {
        appendLog('【系统】请求后台 Celery 任务失败: ' + err)
    }
}

const clearLogs = () => {
  logs.value = []
}

onUnmounted(() => {
    disconnectWs()
})
</script>

<style scoped>
.control-panel {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}
.log-viewer {
  background-color: #1e1e1e;
  color: #d4d4d4;
  height: 400px;
  overflow-y: auto;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}
.log-entry {
  margin-bottom: 5px;
  word-break: break-all;
}
.timestamp {
  color: #569cd6;
  margin-right: 10px;
}
.message {
  color: #ce9178;
}
.empty-placeholder {
  color: #808080;
  text-align: center;
  margin-top: 150px;
}
</style>
