<template>
  <div class="agent-generator-container">
    <el-card class="box-card" shadow="never" body-style="padding: 0; display: flex; flex-direction: column; height: 100%;">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="status-indicator">
          <el-tag :type="wsConnected ? 'success' : 'info'" effect="light" size="small" round>
            {{ wsConnected ? '已连接: ' + taskId : '未连接' }}
          </el-tag>
          <span class="title">WebUI测试用例生成智能体</span>
        </div>
        <div class="actions">
          <el-button size="small" :icon="Delete" @click="clearChat">清空对话</el-button>
          <el-button size="small" :icon="Download">导出对话</el-button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="main-content">
        <!-- Left Chat Area -->
        <div class="chat-area">
          <div class="chat-history" ref="chatHistoryRef">
            <!-- Welcome Message / System Instruction -->
            <div class="system-message">
              <div class="robot-icon">
                <el-icon :size="48" color="#409EFC"><Service /></el-icon>
              </div>
              <h2 class="welcome-title">欢迎使用WebUI测试用例生成智能体</h2>
              <p class="welcome-desc">请描述您想要测试的Web界面功能，我将帮您生成符合业务场景的完整自动化测试用例。</p>
            </div>
            
            <!-- Dynamic Chat Messages -->
            <div v-for="(msg, idx) in messages" :key="idx" :class="['chat-bubble-wrapper', msg.role === 'user' ? 'user-wrapper' : 'agent-wrapper']">
              <div v-if="msg.role === 'agent'" class="avatar agent-avatar"><el-icon><Service /></el-icon></div>
              <div :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'agent-bubble']">
                <div class="message-content" v-html="formatMessage(msg.content)"></div>
                <div v-if="msg.pending" class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
              <div v-if="msg.role === 'user'" class="avatar user-avatar"><el-icon><User /></el-icon></div>
            </div>
          </div>

          <!-- Bottom Input Area -->
          <div class="input-area">
            <el-input
              v-model="promptText"
              placeholder="用户登录、搜索商品、加入购物车的完整流程..."
              class="chat-input"
              @keyup.enter="handleSend"
              :disabled="agentThinking"
            >
              <template #append>
                <el-button type="primary" class="send-btn" @click="handleSend" :disabled="agentThinking || !promptText.trim()" circle>
                  <el-icon><Top /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
        </div>

        <!-- Right Timeline Area -->
        <div class="timeline-area">
          <div class="timeline-header">
            <el-icon><Clock /></el-icon>
            <span>智能体执行时间线</span>
          </div>
          <div class="timeline-content">
             <div v-if="timelineSteps.length === 0" class="empty-state">
                <el-icon :size="60" color="#dcdfe6" style="margin-bottom: 20px;"><Timer /></el-icon>
                <p>等待智能体开始执行...</p>
             </div>
             <el-timeline v-else style="padding: 20px; width: 100%;">
                <el-timeline-item
                  v-for="(step, index) in timelineSteps"
                  :key="index"
                  :type="index === timelineSteps.length - 1 && agentThinking ? 'primary' : 'success'"
                  :hollow="index === timelineSteps.length - 1 && agentThinking"
                  :timestamp="step.time"
                >
                  {{ step.content }}
                </el-timeline-item>
             </el-timeline>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Service, Top, Clock, Timer, Delete, Download, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ breaks: true })

const promptText = ref('')
const chatHistoryRef = ref<HTMLElement | null>(null)

interface ChatMessage {
    role: 'user' | 'agent'
    content: string
    pending?: boolean
}

interface TimelineStep {
    time: string
    content: string
}

const messages = ref<ChatMessage[]>([])
const timelineSteps = ref<TimelineStep[]>([])
const agentThinking = ref(false)
const wsConnected = ref(false)

const taskId = ref('agent_sess_' + Math.random().toString(36).substr(2, 6))
let ws: WebSocket | null = null

const formatMessage = (text: string) => {
    return md.render(text || '')
}

const scrollToBottom = async () => {
    await nextTick()
    if (chatHistoryRef.value) {
        chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
}

const connectWs = () => {
  const host = 'ws://127.0.0.1:8000'
  const wsUrl = `${host}/ws/logs/${taskId.value}/`
  
  ws = new WebSocket(wsUrl)

  ws.onopen = () => { wsConnected.value = true }
  
  ws.onmessage = (event) => {
    try {
        const payload = JSON.parse(event.data)
        const data = JSON.parse(payload.message) // Because our backend sent json string inside message field

        if (data.event === 'status') {
            const now = new Date()
            timelineSteps.value.push({
                time: now.toLocaleTimeString(),
                content: data.message
            })
            scrollToBottom()
        } else if (data.event === 'chunk') {
            // Find last agent message and append
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg && lastMsg.role === 'agent') {
                lastMsg.content += data.message
                scrollToBottom()
            }
        } else if (data.event === 'complete') {
            agentThinking.value = false
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg && lastMsg.role === 'agent') {
                lastMsg.pending = false
            }
            ElMessage.success('测试用例生成完成！')
            scrollToBottom()
        }
    } catch(e) { /* Ignore non-json or pure connection msgs */ }
  }

  ws.onclose = () => { wsConnected.value = false }
}

onMounted(() => {
    connectWs()
})

onUnmounted(() => {
    if (ws) {
        ws.close()
    }
})

const handleSend = async () => {
  const text = promptText.value.trim()
  if (!text || agentThinking.value) return

  // 1. Append user message
  messages.value.push({ role: 'user', content: text })
  promptText.value = ''
  
  // 2. Clear timeline for new execution and append empty agent bubble
  timelineSteps.value = []
  agentThinking.value = true
  messages.value.push({ role: 'agent', content: '', pending: true })
  scrollToBottom()

  // 3. Trigger API
  try {
      const host = 'http://127.0.0.1:8000'
      const response = await axios.post(`${host}/api/ai-core/agent/generate/?_t=${Date.now()}`, {
          prompt: text,
          task_id: taskId.value
      })
      if(response.data.status !== 'success') {
          throw new Error('API failed')
      }
  } catch(e) {
      ElMessage.error('智能体服调用失败，请检查网络或后端服务！')
      agentThinking.value = false
      const lastMsg = messages.value[messages.value.length - 1]
      if (lastMsg && lastMsg.role === 'agent') lastMsg.pending = false
  }
}

const clearChat = () => {
    messages.value = []
    timelineSteps.value = []
}
</script>

<style scoped>
.agent-generator-container {
  height: calc(100vh - 100px);
  display: flex;
}
.box-card {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fafafa;
}
.status-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}
.title {
  font-weight: bold;
  font-size: 15px;
  color: #333;
}
.actions {
  display: flex;
  gap: 10px;
}
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Chat Area */
.chat-area {
  flex: 2;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #f0f0f0;
  background-color: #f7f9fc;
}
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
}
.system-message {
  max-width: 600px;
  text-align: center;
  margin: 0 auto 40px auto;
}
.robot-icon {
  margin-bottom: 15px;
}
.welcome-title {
  font-size: 22px;
  color: #303133;
  margin-bottom: 15px;
}
.welcome-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 30px;
  line-height: 1.6;
}

/* Dynamic Chat Bubbles */
.chat-bubble-wrapper {
  display: flex;
  width: 100%;
  margin-bottom: 25px;
}
.user-wrapper {
  justify-content: flex-end;
}
.agent-wrapper {
  justify-content: flex-start;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}
.user-avatar {
  background-color: #18A058;
  margin-left: 15px;
}
.agent-avatar {
  background-color: #409EFF;
  margin-right: 15px;
}
.chat-bubble {
  max-width: 75%;
  padding: 15px 20px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.user-bubble {
  background-color: #E2F3E8;
  color: #0d5c31;
  border-top-right-radius: 2px;
}
.agent-bubble {
  background-color: #ffffff;
  color: #333333;
  border-top-left-radius: 2px;
  border: 1px solid #ebeef5;
}

.message-content :deep(p) { margin-top: 0; margin-bottom: 10px; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(ul), .message-content :deep(ol) { margin: 10px 0; padding-left: 20px; }

/* Typing animation */
.typing-indicator span {
  display: inline-block;
  width: 6px;
  height: 6px;
  background-color: #909399;
  border-radius: 50%;
  margin-right: 4px;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input Area */
.input-area {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid transparent;
}
.chat-input :deep(.el-input-group__append) {
  background-color: transparent;
  border-left: 0;
  padding: 0 10px;
}
.chat-input :deep(.el-input__wrapper) {
  border-radius: 20px 0 0 20px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  padding-left: 20px;
}
.chat-input :deep(.el-input-group__append) {
  border-radius: 0 20px 20px 0;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}
.send-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  padding: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.send-btn:hover {
  background-color: #66b1ff;
}

/* Timeline Area */
.timeline-area {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}
.timeline-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}
.timeline-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.empty-state {
  margin: auto;
  text-align: center;
  color: #909399;
  font-size: 14px;
}
</style>
