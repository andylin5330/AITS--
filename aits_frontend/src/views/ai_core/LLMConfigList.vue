<template>
  <div class="llm-config-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>大语言模型 (LLM) 接入配置</span>
        </div>
      </template>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增模型接入</el-button>
        <el-button @click="fetchConfigs" icon="Refresh">刷新</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="configs"
        border
        style="width: 100%; margin-top: 15px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column prop="provider" label="模型厂商" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getProviderTagType(scope.row.provider)">
              {{ scope.row.provider }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="api_base" label="API Base" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_vision_model" label="视觉模型" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_vision_model ? 'success' : 'info'" effect="plain">
              {{ scope.row.is_vision_model ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm title="确定要删除该配置吗？" @confirm="handleDelete(scope.row)">
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑大模型配置' : '新增大模型接入'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入如: 官方GPT-4" />
        </el-form-item>
        <el-form-item label="模型提供商" prop="provider">
          <el-select v-model="form.provider" placeholder="选择厂商" style="width: 100%;">
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="Ollama (本地)" value="ollama" />
            <el-option label="Qwen (通义)" value="qwen" />
            <el-option label="Custom (自定义)" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" placeholder="请输入密钥 (如果需要)" type="password" show-password />
        </el-form-item>
        <el-form-item label="API Base" prop="api_base">
          <el-input v-model="form.api_base" placeholder="如需代理或转发则必填" />
        </el-form-item>
        <el-form-item label="视觉模型" prop="is_vision_model">
          <el-switch v-model="form.is_vision_model" />
          <span style="font-size: 12px; color: #999; margin-left: 10px;">是否支持传入图像处理</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getLLMConfigs, createLLMConfig, updateLLMConfig, deleteLLMConfig } from '../../utils/api_ai_core'

const loading = ref(false)
const configs = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: undefined,
  name: '',
  provider: 'openai',
  api_key: '',
  api_base: '',
  is_vision_model: false
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择厂商', trigger: 'change' }]
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res: any = await getLLMConfigs()
    configs.value = res.results || res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getProviderTagType = (provider: string) => {
  const map: Record<string, string> = {
    openai: 'success',
    deepseek: 'primary',
    ollama: 'warning',
    qwen: 'info',
    custom: 'danger'
  }
  return map[provider] || ''
}

onMounted(() => {
  fetchConfigs()
})

const handleAdd = () => {
  isEdit.value = false
  form.id = undefined
  form.name = ''
  form.provider = 'openai'
  form.api_key = ''
  form.api_base = ''
  form.is_vision_model = false
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.provider = row.provider
  form.api_key = row.api_key
  form.api_base = row.api_base
  form.is_vision_model = row.is_vision_model
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteLLMConfig(row.id)
    ElMessage.success('删除成功')
    fetchConfigs()
  } catch (error) {
    console.error(error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && form.id) {
          await updateLLMConfig(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createLLMConfig(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchConfigs()
      } catch (error) {
        console.error(error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.card-header {
  font-weight: bold;
}
</style>
