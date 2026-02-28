<template>
  <div class="web-ui-test-case-container">
    <el-card shadow="never">
      <!-- 搜索栏及操作按钮 -->
      <div class="header-actions">
        <el-form :inline="true" :model="searchParams" class="search-form">
          <el-form-item label="所属项目" prop="project">
            <el-select v-model="searchParams.project" placeholder="切换项目" @change="handleSearch" clearable style="width: 160px;">
              <el-option
                v-for="item in projectOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="">
            <el-select v-model="searchParams.priority" placeholder="优先级" @change="handleSearch" clearable style="width: 120px;">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </el-form-item>
          <el-form-item label="">
            <el-select v-model="searchParams.test_type" placeholder="类别" @change="handleSearch" clearable style="width: 140px;">
              <el-option label="功能测试" value="功能测试" />
              <el-option label="异常测试" value="异常测试" />
              <el-option label="边界测试" value="边界测试" />
              <el-option label="安全测试" value="安全测试" />
              <el-option label="性能测试" value="性能测试" />
            </el-select>
          </el-form-item>
          <el-form-item label="">
            <el-input v-model="searchParams.search" placeholder="搜索测试用例..." clearable prefix-icon="Search" @keyup.enter="handleSearch" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="success" icon="Plus" @click="handleAdd" :disabled="!searchParams.project">新建用例</el-button>
      </div>

      <!-- 用例表格 -->
      <el-table
        v-loading="loading"
        :data="testCases"
        border
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="用例名称" min-width="250">
          <template #default="scope">
            <div style="font-weight: bold; margin-bottom: 4px;">{{ scope.row.name }}</div>
            <div style="font-size: 12px; color: #909399;" class="truncate">{{ scope.row.description || '暂无描述' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="test_type" label="测试类型" width="120" align="center">
          <template #default="scope">
             <el-tag
                :type="getTypeTagTheme(scope.row.test_type)"
                effect="plain"
             >
                {{ scope.row.test_type }}
             </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" align="center">
          <template #default="scope">
             <span :style="{ color: getPriorityColor(scope.row.priority), fontWeight: 'bold' }">
                {{ scope.row.priority }}
             </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建者" width="100" align="center">
            <template #default="scope">
                {{ scope.row.created_by_name || 'admin' }}
            </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="150" align="center">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="scope">
            <el-button size="small" link icon="Edit" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" link icon="Document" @click="openScriptEditor(scope.row)">脚本</el-button>
            
            <el-button size="small" type="primary" icon="VideoPlay" @click="handleExecuteUI(scope.row)">执行用例</el-button>

            <el-popconfirm
              title="确定要删除该测试用例吗？"
              @confirm="handleDelete(scope.row)"
            >
              <template #reference>
                <el-button size="small" type="danger" link icon="Delete" style="margin-left: 10px;"></el-button>
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
          @size-change="fetchTestCases"
          @current-change="fetchTestCases"
        />
      </div>
    </el-card>

    <!-- 新建/编辑属性弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑基础属性' : '新建 UI 用例'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="caseForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="caseForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="caseForm.priority">
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试类型">
              <el-select v-model="caseForm.test_type">
                <el-option label="功能测试" value="功能测试" />
                <el-option label="异常测试" value="异常测试" />
                <el-option label="边界测试" value="边界测试" />
                <el-option label="安全测试" value="安全测试" />
                <el-option label="性能测试" value="性能测试" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="用例描述" prop="description">
          <el-input
            v-model="caseForm.description"
            type="textarea"
            :rows="3"
            placeholder="简述测试流程"
          />
        </el-form-item>
        <el-form-item label="步骤定义" prop="steps">
          <el-input
            v-model="caseForm.steps"
            type="textarea"
            :rows="4"
            placeholder='Playwright 等普通执行逻辑 (JSON数组)'
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

    <!-- MidScene 编辑抽屉 -->
    <el-drawer v-model="drawerVisible" title="编辑 MidScene 视觉脚本" size="50%">
      <div v-loading="drawerLoading" style="padding: 0 20px;">
        <el-alert title="利用 MidScene 自然语言指令进行前端交互验证" type="info" show-icon style="margin-bottom: 20px;" />
        <el-form label-position="top">
            <el-form-item label="脚本内容 (支持自然语言描述的操作):">
                <el-input
                    v-model="currentScript.script_content"
                    type="textarea"
                    :rows="20"
                    placeholder="例如：&#10;1. 输入用户名 admin&#10;2. 输入密码 admin123&#10;3. 点击登录按钮&#10;4. 校验页面上方是否包含智能测试字样"
                />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitMidSceneScript">保存运行脚本</el-button>
            </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getWebUITestCases, createWebUITestCase, updateWebUITestCase, deleteWebUITestCase, getMidSceneScript, saveMidSceneScript } from '../../utils/api_web_testing'
import { getProjects } from '../../utils/api_projects'

const loading = ref(false)
const testCases = ref([])
const total = ref(0)
const projectOptions = ref<any[]>([])

const searchParams = reactive({
  page: 1,
  page_size: 10,
  search: '',
  project: '',
  priority: '',
  test_type: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const caseForm = reactive({
  id: undefined,
  name: '',
  description: '',
  priority: '中',
  test_type: '功能测试',
  steps: '[]'
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }]
})

const drawerVisible = ref(false)
const drawerLoading = ref(false)
const currentScript = reactive({
    id: undefined,
    case: undefined,
    script_content: ''
})

const fetchProjectOptions = async () => {
    try {
        const res: any = await getProjects({ page_size: 100 })
        projectOptions.value = res.results || res
        if (projectOptions.value.length > 0 && !searchParams.project) {
            searchParams.project = projectOptions.value[0].id
        }
        fetchTestCases()
    } catch (e) {
        console.error('Failed to load projects', e)
    }
}

const fetchTestCases = async () => {
  if (!searchParams.project) return
  loading.value = true
  try {
    const res: any = await getWebUITestCases(searchParams)
    if (res.results) {
        testCases.value = res.results
        total.value = res.count
    } else {
        testCases.value = res
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
  fetchTestCases()
}

const resetSearch = () => {
  searchParams.search = ''
  searchParams.priority = ''
  searchParams.test_type = ''
  handleSearch()
}

const handleAdd = () => {
  if (!searchParams.project) {
      ElMessage.warning('请先选择一个所属项目')
      return
  }
  isEdit.value = false
  caseForm.id = undefined
  caseForm.name = ''
  caseForm.description = ''
  caseForm.priority = '中'
  caseForm.test_type = '功能测试'
  caseForm.steps = '[]'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  caseForm.id = row.id
  caseForm.name = row.name
  caseForm.description = row.description
  caseForm.priority = row.priority || '中'
  caseForm.test_type = row.test_type || '功能测试'
  caseForm.steps = JSON.stringify(row.steps || [], null, 2)
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteWebUITestCase(row.id)
    ElMessage.success('删除成功')
    fetchTestCases()
  } catch (error) {
    console.error(error)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      let parsedSteps = []
      try {
        parsedSteps = JSON.parse(caseForm.steps)
      } catch (e) {
        ElMessage.error('JSON格式不合法')
        return
      }

      submitLoading.value = true
      const payload = {
        project: searchParams.project,
        name: caseForm.name,
        description: caseForm.description,
        priority: caseForm.priority,
        test_type: caseForm.test_type,
        steps: parsedSteps
      }

      try {
        if (isEdit.value && caseForm.id) {
          await updateWebUITestCase(caseForm.id, payload)
          ElMessage.success('更新成功')
        } else {
          await createWebUITestCase(payload)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchTestCases()
      } catch (error) {
        console.error(error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const openScriptEditor = async (row: any) => {
    currentScript.id = undefined
    currentScript.case = row.id
    currentScript.script_content = ''
    drawerVisible.value = true
    drawerLoading.value = true
    
    try {
        const res: any = await getMidSceneScript(row.id)
        if (res.results && res.results.length > 0) {
            currentScript.id = res.results[0].id
            currentScript.script_content = res.results[0].script_content
        } else if (res.length > 0) {
            currentScript.id = res[0].id
            currentScript.script_content = res[0].script_content
        }

    } catch (e) {
        console.error(e)
    } finally {
        drawerLoading.value = false
    }
}

const submitMidSceneScript = async () => {
    try {
        await saveMidSceneScript({
            id: currentScript.id,
            case: currentScript.case,
            script_content: currentScript.script_content
        })
        ElMessage.success('脚本保存成功')
        drawerVisible.value = false
    } catch (e) {
        ElMessage.error('脚本保存失败')
    }
}

// UI Formatters
const getTypeTagTheme = (type: string) => {
    const map: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
        '异常测试': 'warning',
        '安全测试': 'danger',
        '边界测试': 'info',
        '功能测试': 'success',
        '性能测试': 'primary'
    }
    return map[type] || 'info'
}

const getPriorityColor = (priority: string) => {
    const map: Record<string, string> = {
        '高': '#F56C6C', // element danger color
        '中': '#E6A23C', // element warning color
        '低': '#67C23A'  // element success color
    }
    return map[priority] || '#909399'
}

const formatDateTime = (dateStr: string) => {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const handleExecuteUI = (row: any) => {
    ElMessage.info('前端单用例执行钩子触发: 待接入测试机 Worker')
    // Open some drawer or push to queue API
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
.search-form .el-form-item {
  margin-right: 12px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
