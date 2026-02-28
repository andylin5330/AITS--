<template>
  <div class="mcp-config-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>MCP (Model Context Protocol) 插件集配置</span>
        </div>
      </template>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增 MCP 节点</el-button>
        <el-button @click="fetchConfigs" icon="Refresh">刷新</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="configs"
        border
        style="width: 100%; margin-top: 15px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="插件名称" min-width="150" />
        <el-table-column prop="server_url" label="服务地址 (Server URL)" min-width="250" show-overflow-tooltip />
        <el-table-column prop="description" label="描述说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="激活态" width="100" align="center">
          <template #default="scope">
            <el-switch v-model="scope.row.is_active" @change="handleToggleStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm title="确定要删除该 MCP 插件节点吗？" @confirm="handleDelete(scope.row)">
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
      :title="isEdit ? '编辑 MCP 节点' : '新增 MCP 服务接入'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <el-form-item label="插件名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入如: GitLab-MCP-Server" />
        </el-form-item>
        <el-form-item label="服务地址" prop="server_url">
          <el-input v-model="form.server_url" placeholder="如: sse://127.0.0.1:3000/messages" />
        </el-form-item>
        <el-form-item label="描述说明" prop="description">
            <el-input
                v-model="form.description"
                type="textarea"
                :rows="3"
                placeholder="在此说明该节点的工具用途..."
            />
        </el-form-item>
        <el-form-item label="默认激活" prop="is_active">
            <el-switch v-model="form.is_active" />
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
import { getMCPConfigs, createMCPConfig, updateMCPConfig, deleteMCPConfig } from '../../utils/api_ai_core'

const loading = ref(false)
const configs = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: undefined,
  name: '',
  server_url: '',
  description: '',
  is_active: true
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入插件名称', trigger: 'blur' }],
  server_url: [{ required: true, message: '请输入服务地址', trigger: 'blur' }]
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res: any = await getMCPConfigs()
    configs.value = res.results || res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchConfigs()
})

const handleAdd = () => {
  isEdit.value = false
  form.id = undefined
  form.name = ''
  form.server_url = ''
  form.description = ''
  form.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.server_url = row.server_url
  form.description = row.description
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleToggleStatus = async (row: any) => {
    try {
        await updateMCPConfig(row.id, { is_active: row.is_active })
        ElMessage.success(`MCP 节点 ${row.name} 已${row.is_active ? '启用' : '停用'}`)
    } catch (e) {
        row.is_active = !row.is_active // 失败则回滚 UI 侧
    }
}

const handleDelete = async (row: any) => {
  try {
    await deleteMCPConfig(row.id)
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
          await updateMCPConfig(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createMCPConfig(form)
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
