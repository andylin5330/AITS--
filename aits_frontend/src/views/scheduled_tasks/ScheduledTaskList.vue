<template>
  <div class="scheduled-task-container">
    <el-card shadow="never">
      <div class="header-actions">
        <el-form :inline="true" :model="searchParams" class="search-form">
          <el-form-item label="所属项目" prop="project">
            <el-select v-model="searchParams.project" placeholder="切换项目" @change="handleSearch" clearable>
              <el-option
                v-for="item in projectOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="计划名称">
            <el-input v-model="searchParams.search" placeholder="请输入名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="success" icon="Plus" @click="handleAdd" :disabled="!searchParams.project">新增定时任务</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="tasks"
        border
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="task_type" label="触发目标类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.task_type === 'api_suite' ? 'primary' : 'warning'">
              {{ scope.row.task_type === 'api_suite' ? 'API套件' : 'Web套件' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_id" label="目标套件ID" width="100" align="center" />
        <el-table-column prop="cron_expression" label="Cron 表达式" min-width="150" align="center">
          <template #default="scope">
            <el-tag effect="dark" type="info">{{ scope.row.cron_expression }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="启停状态" width="100" align="center">
          <template #default="scope">
            <el-switch v-model="scope.row.is_active" @change="handleToggleStatus(scope.row)" />
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="最后修改" min-width="170">
          <template #default="scope">
            {{ new Date(scope.row.updated_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm title="确定要删除该定时任务吗？" @confirm="handleDelete(scope.row)">
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchTasks"
          @current-change="fetchTasks"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑定时任务' : '新增调度计划'"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入如: 每日凌晨一点巡检" />
        </el-form-item>
        <el-form-item label="执行类型" prop="task_type">
          <el-select v-model="form.task_type" placeholder="选择目标环境" style="width: 100%;" @change="loadTargetOptions">
            <el-option label="API 测试套件" value="api_suite" />
            <el-option label="Web UI 测试套件" value="web_suite" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行目标 (套件)" prop="target_id">
          <el-select v-model="form.target_id" placeholder="请选择具体要跑的套件" style="width: 100%;">
            <el-option
              v-for="item in currentTargetOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cron_expression">
          <el-input v-model="form.cron_expression" placeholder="标准Cron如: 0 1 * * *" />
          <div style="font-size: 12px; color: #999; margin-top: 5px;">分 时 日 月 周，推荐在线工具生成后填入该栏</div>
        </el-form-item>
        <el-form-item label="立即激活" prop="is_active">
            <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="submitForm">保存调度</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getScheduledTasks, createScheduledTask, updateScheduledTask, deleteScheduledTask } from '../../utils/api_scheduled_tasks'
import { getProjects } from '../../utils/api_projects'
import { getAPITestSuites } from '../../utils/api_testing'
import { getWebUITestSuites } from '../../utils/api_web_testing'

const loading = ref(false)
const tasks = ref([])
const total = ref(0)
const projectOptions = ref<any[]>([])

const searchParams = reactive({
  page: 1,
  page_size: 10,
  search: '',
  project: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const currentTargetOptions = ref<any[]>([])

const form = reactive({
  id: undefined,
  name: '',
  task_type: 'api_suite',
  target_id: undefined,
  cron_expression: '',
  is_active: true
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  target_id: [{ required: true, message: '请选择业务套件', trigger: 'change' }],
  cron_expression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }]
})

const fetchProjectOptions = async () => {
    try {
        const res: any = await getProjects({ page_size: 100 })
        projectOptions.value = res.results || res
        if (projectOptions.value.length > 0 && !searchParams.project) {
            searchParams.project = projectOptions.value[0].id
        }
        fetchTasks()
    } catch (e) {
        console.error('Failed to load projects', e)
    }
}

const loadTargetOptions = async () => {
    form.target_id = undefined
    currentTargetOptions.value = []
    if (!searchParams.project) return
    
    try {
        if (form.task_type === 'api_suite') {
            const res: any = await getAPITestSuites({ project: searchParams.project, page_size: 1000 })
            currentTargetOptions.value = res.results || res
        } else if (form.task_type === 'web_suite') {
            const res: any = await getWebUITestSuites({ project: searchParams.project, page_size: 1000 })
            currentTargetOptions.value = res.results || res
        }
    } catch (e) {
        console.error("加载套件数据失败", e)
    }
}

const fetchTasks = async () => {
  if (!searchParams.project) return
  loading.value = true
  try {
    const res: any = await getScheduledTasks(searchParams)
    if (res.results) {
        tasks.value = res.results
        total.value = res.count
    } else {
        tasks.value = res
        total.value = res.length
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProjectOptions()
})

const handleSearch = () => {
  searchParams.page = 1
  fetchTasks()
}

const resetSearch = () => {
  searchParams.search = ''
  handleSearch()
}

const handleAdd = () => {
  if (!searchParams.project) {
      ElMessage.warning('请先选择项目')
      return
  }
  isEdit.value = false
  form.id = undefined
  form.name = ''
  form.task_type = 'api_suite'
  form.target_id = undefined
  form.cron_expression = ''
  form.is_active = true
  loadTargetOptions()
  dialogVisible.value = true
}

const handleEdit = async (row: any) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.task_type = row.task_type
  await loadTargetOptions()
  form.target_id = row.target_id
  form.cron_expression = row.cron_expression
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleToggleStatus = async (row: any) => {
    try {
        await updateScheduledTask(row.id, { is_active: row.is_active })
        ElMessage.success(`定时计划 [${row.name}] 已${row.is_active ? '开启' : '关闭'}`)
    } catch (e) {
        row.is_active = !row.is_active
    }
}

const handleDelete = async (row: any) => {
  try {
    await deleteScheduledTask(row.id)
    ElMessage.success('删除成功')
    fetchTasks()
  } catch (error) {
    console.error(error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      const payload = {
        project: searchParams.project,
        name: form.name,
        task_type: form.task_type,
        target_id: form.target_id,
        cron_expression: form.cron_expression,
        is_active: form.is_active
      }

      try {
        if (isEdit.value && form.id) {
          await updateScheduledTask(form.id, payload)
          ElMessage.success('计划修改成功')
        } else {
          await createScheduledTask(payload)
          ElMessage.success('计划创建成功')
        }
        dialogVisible.value = false
        fetchTasks()
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
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.search-form {
  display: flex;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
