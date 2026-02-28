<template>
  <div class="rag-config-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>RAG 知识库配置</span>
        </div>
      </template>
      <div class="header-actions">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增向量数据库</el-button>
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
        <el-table-column prop="db_type" label="数据库类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.db_type === 'chromadb' ? 'warning' : 'primary'">
              {{ scope.row.db_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="connection_kwargs" label="连接参数" min-width="250" show-overflow-tooltip>
            <template #default="scope">
                {{ JSON.stringify(scope.row.connection_kwargs) }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm title="确定要删除该 RAG 配置吗？" @confirm="handleDelete(scope.row)">
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
      :title="isEdit ? '编辑RAG配置' : '新增知识库连接'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入如: 系统本地检索库" />
        </el-form-item>
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="form.db_type" placeholder="选择类型" style="width: 100%;">
            <el-option label="ChromaDB" value="chromadb" />
            <el-option label="Milvus" value="milvus" />
          </el-select>
        </el-form-item>
        <el-form-item label="连接参数" prop="connection_kwargs">
            <el-input
                v-model="form.connection_kwargs"
                type="textarea"
                :rows="4"
                placeholder='JSON格式, 例如: {"host": "127.0.0.1", "port": 19530}'
            />
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
import { getRAGConfigs, createRAGConfig, updateRAGConfig, deleteRAGConfig } from '../../utils/api_ai_core'

const loading = ref(false)
const configs = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: undefined,
  name: '',
  db_type: 'chromadb',
  connection_kwargs: '{}'
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }]
})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res: any = await getRAGConfigs()
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
  form.db_type = 'chromadb'
  form.connection_kwargs = '{}'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.db_type = row.db_type
  form.connection_kwargs = JSON.stringify(row.connection_kwargs || {}, null, 2)
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteRAGConfig(row.id)
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
      let parsedKwargs = {}
      try {
        parsedKwargs = JSON.parse(form.connection_kwargs)
      } catch (e) {
        ElMessage.error('连接参数必须为合法的 JSON 对象')
        return
      }

      submitLoading.value = true
      const payload = {
        name: form.name,
        db_type: form.db_type,
        connection_kwargs: parsedKwargs
      }

      try {
        if (isEdit.value && form.id) {
          await updateRAGConfig(form.id, payload)
          ElMessage.success('更新成功')
        } else {
          await createRAGConfig(payload)
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
