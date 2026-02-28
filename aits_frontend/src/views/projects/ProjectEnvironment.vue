<template>
  <div class="project-environments-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button icon="Back" @click="goBack" circle />
            <span class="title">环境配置 - 项目 ID: {{ projectId }}</span>
          </div>
          <el-button type="success" icon="Plus" @click="handleAdd">新建环境</el-button>
        </div>
      </template>

      <!-- 环境数据列表 -->
      <el-table
        v-loading="loading"
        :data="environments"
        border
        style="width: 100%;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="环境名称" min-width="120">
          <template #default="scope">
            <el-tag :type="getEnvTypeTag(scope.row.name)">{{ scope.row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="base_url" label="Base URL" min-width="250" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除该环境配置吗？"
              @confirm="handleDelete(scope.row)"
            >
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑环境配置弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑环境' : '新建环境'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="envForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="环境名称" prop="name">
          <el-select v-model="envForm.name" placeholder="请选择或输入环境名称" filterable allow-create>
            <el-option label="DEV" value="DEV" />
            <el-option label="TEST" value="TEST" />
            <el-option label="UAT" value="UAT" />
            <el-option label="PROD" value="PROD" />
          </el-select>
        </el-form-item>
        <el-form-item label="Base URL" prop="base_url">
          <el-input v-model="envForm.base_url" placeholder="如: https://api.uat.example.com" />
        </el-form-item>
        <el-form-item label="全局变量" prop="global_variables">
          <el-input
            v-model="envForm.global_variables"
            type="textarea"
            :rows="4"
            placeholder="请输入 JSON 格式的全局变量，例如: { &quot;token&quot;: &quot;abc&quot; }"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="envForm.description"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import request from '../../utils/request'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string

// 状态及数据
const loading = ref(false)
const environments = ref([])

// 弹窗控制
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const envForm = reactive({
  id: undefined,
  name: 'TEST',
  base_url: '',
  global_variables: '{}',
  description: '',
  project: projectId // 绑定项目外键
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '环境名称不能为空', trigger: 'change' }],
  base_url: [{ required: true, message: 'Base URL 不能为空', trigger: 'blur' }]
})

const getEnvTypeTag = (name: string) => {
  const n = name.toUpperCase()
  if (n.includes('PROD')) return 'danger'
  if (n.includes('UAT')) return 'warning'
  if (n.includes('TEST')) return 'success'
  return 'info'
}

const goBack = () => {
  router.push('/projects')
}

// 获取环境列表
const fetchEnvironments = async () => {
  loading.value = true
  try {
    const res: any = await request.get(`/environments/`, {
      params: { project: projectId }
    })
    // 根据 DRF 分页情况处理
    environments.value = res.results || res
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEnvironments()
})

const handleAdd = () => {
  isEdit.value = false
  envForm.id = undefined
  envForm.name = 'TEST'
  envForm.base_url = ''
  envForm.global_variables = '{}'
  envForm.description = ''
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  envForm.id = row.id
  envForm.name = row.name
  envForm.base_url = row.base_url
  envForm.global_variables = JSON.stringify(row.global_variables || {}, null, 2)
  envForm.description = row.description
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await request.delete(`/environments/${row.id}/`)
    ElMessage.success('删除成功')
    fetchEnvironments()
  } catch (error) {
    console.error(error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // 简单验证 JSON 格式
      let parsedVars = {}
      try {
        if (envForm.global_variables.trim()) {
           parsedVars = JSON.parse(envForm.global_variables)
        }
      } catch (e) {
        ElMessage.error('全局变量格式错误，不是有效的 JSON')
        return
      }

      submitLoading.value = true
      const payload = {
        project: projectId,
        name: envForm.name,
        base_url: envForm.base_url,
        global_variables: parsedVars,
        description: envForm.description
      }

      try {
        if (isEdit.value && envForm.id) {
          await request.put(`/environments/${envForm.id}/`, payload)
          ElMessage.success('更新成功')
        } else {
          await request.post(`/environments/`, payload)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchEnvironments()
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}
.title {
  font-size: 16px;
  font-weight: bold;
}
</style>
