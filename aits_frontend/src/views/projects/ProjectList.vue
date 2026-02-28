<template>
  <div class="project-list-container">
    <el-card shadow="never">
      <!-- 列表头部，包含搜索和新增按钮 -->
      <div class="header-actions">
        <el-form :inline="true" :model="searchParams" class="search-form">
          <el-form-item label="项目名称">
            <el-input v-model="searchParams.search" placeholder="请输入项目名称或描述" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="success" icon="Plus" @click="handleAdd">新建项目</el-button>
      </div>

      <!-- 项目数据表格 -->
      <el-table
        v-loading="loading"
        :data="projects"
        border
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="项目名称" min-width="150" />
        <el-table-column prop="description" label="项目描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="members_count" label="成员数量" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="scope">
            {{ new Date(scope.row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="info" link @click="goEnvironment(scope.row)">环境配置</el-button>
            <el-popconfirm
              title="确定要删除该项目吗？包含的所有测试文件都将归档隐藏。"
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
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>
    </el-card>

    <!-- 新增/编辑项目弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑项目' : '新建项目'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="projectForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目背景描述等"
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
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject } from '../../utils/api_projects'
import { useRouter } from 'vue-router'

const router = useRouter()

// 状态及数据
const loading = ref(false)
const projects = ref([])
const total = ref(0)
const searchParams = reactive({
  page: 1,
  page_size: 10,
  search: ''
})

// 弹窗表单控制
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const projectForm = reactive({
  id: undefined,
  name: '',
  description: ''
})

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
})

// 初始化与拉取列表
const fetchProjects = async () => {
  loading.value = true
  try {
    const res: any = await getProjects(searchParams)
    // 根据 DRF 的分页响应结构判断
    if (res.results) {
        projects.value = res.results
        total.value = res.count
    } else {
        projects.value = res
        total.value = res.length
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProjects()
})

const handleSearch = () => {
  searchParams.page = 1
  fetchProjects()
}

const resetSearch = () => {
  searchParams.search = ''
  handleSearch()
}

// 增删改操作
const handleAdd = () => {
  isEdit.value = false
  projectForm.id = undefined
  projectForm.name = ''
  projectForm.description = ''
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  projectForm.id = row.id
  projectForm.name = row.name
  projectForm.description = row.description
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await deleteProject(row.id)
    ElMessage.success('删除成功')
    fetchProjects()
  } catch (error) {
    console.error(error)
  }
}

const goEnvironment = (row: any) => {
    router.push(`/projects/${row.id}/environments`)
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value && projectForm.id) {
          await updateProject(projectForm.id, {
            name: projectForm.name,
            description: projectForm.description
          })
          ElMessage.success('更新成功')
        } else {
          await createProject({
            name: projectForm.name,
            description: projectForm.description
          })
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchProjects()
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
