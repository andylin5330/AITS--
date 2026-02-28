<template>
  <div class="api-test-case-container">
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
          <el-form-item label="用例名称">
            <el-input v-model="searchParams.search" placeholder="请输入名称" clearable />
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
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="用例名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="case_type" label="类型" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.case_type === 'endpoint' ? 'primary' : 'warning'">
              {{ scope.row.case_type === 'endpoint' ? '单接口' : '场景链路' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_ai_generated" label="AI 生成" width="100" align="center">
          <template #default="scope">
            <el-switch v-model="scope.row.is_ai_generated" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button v-if="scope.row.is_ai_generated" size="small" type="success" link @click="viewAIContent(scope.row)">AI大纲</el-button>
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除该用例吗？"
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
          @size-change="fetchTestCases"
          @current-change="fetchTestCases"
        />
      </div>
    </el-card>

    <!-- 新建/编辑 用例弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用例' : '新建测试用例'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="caseForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="caseForm.name" placeholder="请输入用例名称规则或目的" />
        </el-form-item>
        <el-form-item label="用例类型" prop="case_type">
          <el-radio-group v-model="caseForm.case_type">
            <el-radio label="endpoint">单接口</el-radio>
            <el-radio label="scenario">场景链路</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="请求数据" prop="request_data">
          <el-input
            v-model="caseForm.request_data"
            type="textarea"
            :rows="5"
            placeholder='JSON格式, 例如: { "headers": {}, "params": {}, "body": {} }'
          />
        </el-form-item>
        <el-form-item label="断言规则" prop="assertions">
          <el-input
            v-model="caseForm.assertions"
            type="textarea"
            :rows="3"
            placeholder='JSON格式数组, 例如: [ {"eq": ["status_code", 200]} ]'
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

    <!-- AI 源码预览抽屉 -->
    <el-drawer
      v-model="aiDrawerVisible"
      title="来自智能体的测试用例大纲"
      size="45%"
    >
      <div v-if="aiMarkdownContent" class="markdown-preview" v-html="renderMarkdown(aiMarkdownContent)"></div>
      <el-empty v-else description="暂无生成的原文数据" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { getAPITestCases, createAPITestCase, updateAPITestCase, deleteAPITestCase } from '../../utils/api_testing'
import { getProjects } from '../../utils/api_projects'

const md = new MarkdownIt({ breaks: true })

const loading = ref(false)
const testCases = ref([])
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
const caseForm = reactive({
  id: undefined,
  name: '',
  case_type: 'endpoint',
  request_data: '{}',
  assertions: '[]'
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  case_type: [{ required: true, message: '请选择用例类型', trigger: 'change' }]
})

const aiDrawerVisible = ref(false)
const aiMarkdownContent = ref('')

const renderMarkdown = (text: string) => {
    return md.render(text || '')
}

const viewAIContent = (row: any) => {
    aiMarkdownContent.value = row.request_data?.ai_raw_content || ''
    aiDrawerVisible.value = true
}

// 获取项目列表以供选择
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
    const res: any = await getAPITestCases(searchParams)
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
  caseForm.case_type = 'endpoint'
  caseForm.request_data = '{}'
  caseForm.assertions = '[]'
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  caseForm.id = row.id
  caseForm.name = row.name
  caseForm.case_type = row.case_type
  caseForm.request_data = JSON.stringify(row.request_data || {}, null, 2)
  caseForm.assertions = JSON.stringify(row.assertions || [], null, 2)
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteAPITestCase(row.id)
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
      let parsedData = {}
      let parsedAssertions = []
      try {
        parsedData = JSON.parse(caseForm.request_data)
        parsedAssertions = JSON.parse(caseForm.assertions)
      } catch (e) {
        ElMessage.error('JSON格式不合法')
        return
      }

      submitLoading.value = true
      const payload = {
        project: searchParams.project,
        name: caseForm.name,
        case_type: caseForm.case_type,
        request_data: parsedData,
        assertions: parsedAssertions
      }

      try {
        if (isEdit.value && caseForm.id) {
          await updateAPITestCase(caseForm.id, payload)
          ElMessage.success('更新成功')
        } else {
          await createAPITestCase(payload)
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
.markdown-preview {
  line-height: 1.6;
  font-size: 14px;
  color: #333;
}
.markdown-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}
.markdown-preview :deep(th), .markdown-preview :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
}
.markdown-preview :deep(th) {
  background-color: #f5f7fa;
}
</style>
