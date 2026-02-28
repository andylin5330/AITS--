<template>
  <div class="web-ui-test-suite-container">
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
        <el-button type="success" icon="Plus" @click="handleAdd" :disabled="!searchParams.project">新建 UI 套件</el-button>
      </div>

      <!-- 套件表格 -->
      <el-table
        v-loading="loading"
        :data="testSuites"
        border
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="UI 测试套件名称" min-width="180" />
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
            <el-button size="small" type="success" link @click="handleRun(scope.row)">执行</el-button>
            <el-popconfirm
              title="确定要删除该 UI 测试套件吗？"
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

    <!-- 新建 UI 测试套件弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建 Web UI 测试套件"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="suiteForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入 UI 套件名称，例如: 登录相关页面视觉回归" />
        </el-form-item>
        <el-form-item label="选择 UI 用例" prop="cases">
          <el-select
            v-model="suiteForm.cases"
            multiple
            placeholder="请选择要包含的 UI 用例"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getWebUITestSuites, createWebUITestSuite, deleteWebUITestSuite, getWebUITestCases } from '../../utils/api_web_testing'
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
    const res: any = await getWebUITestCases({ project: searchParams.project, page_size: 1000 })
    testCaseOptions.value = res.results || res
  } catch (error) {
    console.error(error)
  }
}

const fetchTestSuites = async () => {
  if (!searchParams.project) return
  loading.value = true
  try {
    const res: any = await getWebUITestSuites(searchParams)
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
  fetchTestCaseOptions()
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
    await deleteWebUITestSuite(row.id)
    ElMessage.success('删除成功')
    fetchTestSuites()
  } catch (error) {
    console.error(error)
  }
}

const handleRun = (row: any) => {
  ElMessageBox.confirm(
    `确定要立即执行 UI 测试套件 [${row.name}] 吗？`,
    '执行确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success(`UI 测试套件 [${row.name}] 已派发给底层 Playwright 集群`)
  }).catch(() => {})
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
        await createWebUITestSuite(payload)
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
