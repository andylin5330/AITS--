<template>
  <div class="api-test-suite-container">
    <el-card shadow="never">
      <!-- 搜索栏及操作按钮 -->
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
          <el-form-item label="套件名称">
            <el-input v-model="searchParams.search" placeholder="请输入名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="success" icon="Plus" @click="handleAdd" :disabled="!searchParams.project">新建套件</el-button>
      </div>

      <!-- 套件表格 -->
      <el-table
        v-loading="loading"
        :data="testSuites"
        border
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="测试套件名称" min-width="180" />
        <el-table-column label="包含用例数" width="120" align="center">
          <template #default="scope">
            {{ scope.row.cases ? scope.row.cases.length : 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="viewHistory(scope.row)">历史与报告</el-button>
            <el-button size="small" type="success" link @click="handleRun(scope.row)" :loading="runLoadingId === scope.row.id">执行</el-button>
            <el-popconfirm
              title="确定要删除该测试套件吗？"
              @confirm="handleDelete(scope.row)"
            >
              <template #reference>
                <el-button size="small" type="danger" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchTestSuites"
          @current-change="fetchTestSuites"
        />
      </div>
    </el-card>

    <!-- 新建测试套件弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建测试套件"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="suiteForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入套件名称，例如: 核心功能回归测试" />
        </el-form-item>
        <el-form-item label="选择测试用例" prop="cases">
          <el-select
            v-model="suiteForm.cases"
            multiple
            placeholder="请选择要包含的测试用例"
            style="width: 100%;"
          >
            <el-option
              v-for="item in testCaseOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
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

    <!-- 执行记录与报告抽屉 -->
    <el-drawer
      v-model="historyDrawerVisible"
      title="执行历史与 Allure 测试报告"
      size="50%"
    >
      <div v-loading="historyLoading">
        <el-button type="primary" icon="Refresh" circle style="margin-bottom: 10px;" @click="fetchExecutionHistory" />
        <el-table :data="executionHistory" border style="width: 100%">
          <el-table-column prop="id" label="ID" width="60" align="center" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.status === 'passed'" type="success">成功</el-tag>
              <el-tag v-else-if="scope.row.status === 'failed'" type="danger">失败</el-tag>
              <el-tag v-else-if="scope.row.status === 'error'" type="danger">错误</el-tag>
              <el-tag v-else-if="scope.row.status === 'running'" type="warning">运行中</el-tag>
              <el-tag v-else type="info">等待</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" min-width="150">
            <template #default="scope">
              {{ scope.row.start_time ? new Date(scope.row.start_time).toLocaleString() : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="Allure 报告" min-width="120" fixed="right">
            <template #default="scope">
              <el-button 
                v-if="scope.row.report_data && scope.row.report_data.report_url"
                size="small" type="primary" plain
                @click="openReport(scope.row.report_data.report_url)"
              >
                查看报告
              </el-button>
              <span v-else style="color:#999;font-size:12px;">暂无报告</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getAPITestSuites, createAPITestSuite, deleteAPITestSuite, getAPITestCases, executeAPITestSuite, getAPITestExecutions } from '../../utils/api_testing'
import { getProjects } from '../../utils/api_projects'

const loading = ref(false)
const testSuites = ref([])
const total = ref(0)
const projectOptions = ref<any[]>([])
const testCaseOptions = ref<any[]>([])

const searchParams = reactive({
  page: 1,
  page_size: 10,
  search: '',
  project: ''
})

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const suiteForm = reactive({
  name: '',
  cases: [] as number[]
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入测试套件名称', trigger: 'blur' }]
})

const fetchProjectOptions = async () => {
    try {
        const res: any = await getProjects({ page_size: 100 })
        projectOptions.value = res.results || res
        if (projectOptions.value.length > 0 && !searchParams.project) {
            searchParams.project = projectOptions.value[0].id
        }
        fetchTestSuites()
        fetchTestCaseOptions()
    } catch (e) {
        console.error('Failed to load projects', e)
    }
}

const fetchTestCaseOptions = async () => {
  if (!searchParams.project) return
  try {
    const res: any = await getAPITestCases({ project: searchParams.project, page_size: 1000 })
    testCaseOptions.value = res.results || res
  } catch (error) {
    console.error(error)
  }
}

const fetchTestSuites = async () => {
  if (!searchParams.project) return
  loading.value = true
  try {
    const res: any = await getAPITestSuites(searchParams)
    if (res.results) {
        testSuites.value = res.results
        total.value = res.count
    } else {
        testSuites.value = res
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
  fetchTestSuites()
  fetchTestCaseOptions() // Reload cases when project changes
}

const resetSearch = () => {
  searchParams.search = ''
  handleSearch()
}

const handleAdd = () => {
  if (!searchParams.project) {
      ElMessage.warning('请先选择一个所属项目')
      return
  }
  suiteForm.name = ''
  suiteForm.cases = []
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteAPITestSuite(row.id)
    ElMessage.success('删除成功')
    fetchTestSuites()
  } catch (error) {
    console.error(error)
  }
}

const runLoadingId = ref<number | null>(null)

const handleRun = (row: any) => {
  ElMessageBox.confirm(
    `确定要立即执行测试套件 [${row.name}] 吗？引擎将在后台为您调度 Pytest 并生成 Allure。`,
    '执行确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    runLoadingId.value = row.id
    try {
      await executeAPITestSuite(row.id)
      ElMessage.success(`测试套件 [${row.name}] 已下发执行指令，请从历史记录中查看报告！`)
      // Optional: automatically open drawer
      viewHistory(row)
    } catch (e) {
      console.error(e)
    } finally {
      runLoadingId.value = null
    }
  }).catch(() => {})
}

// 抽屉及报告查看逻辑
const historyDrawerVisible = ref(false)
const historyLoading = ref(false)
const executionHistory = ref<any[]>([])
const currentSuiteId = ref<number | null>(null)

const viewHistory = (row: any) => {
  currentSuiteId.value = row.id
  historyDrawerVisible.value = true
  fetchExecutionHistory()
}

const fetchExecutionHistory = async () => {
  if (!currentSuiteId.value) return
  historyLoading.value = true
  try {
    const res: any = await getAPITestExecutions({ suite: currentSuiteId.value, page_size: 50, ordering: '-id' })
    executionHistory.value = res.results || res
  } catch (e) {
    console.error(e)
  } finally {
    historyLoading.value = false
  }
}

const openReport = (url: string) => {
  // We expect URL to be absolute or relative path that maps to Media Root. 
  // BaseURL will be handled by browser natively if relative starting with /, but typically backend gives back exact relative path.
  // Django's backend is on 8000. If we are proxying /media we are good.
  const proxyUrl = url.startsWith('/') ? `http://127.0.0.1:8000${url}` : url
  window.open(proxyUrl, '_blank')
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      const payload = {
        project: searchParams.project,
        name: suiteForm.name,
        cases: suiteForm.cases
      }

      try {
        await createAPITestSuite(payload)
        ElMessage.success('配置测试套件成功')
        dialogVisible.value = false
        fetchTestSuites()
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
