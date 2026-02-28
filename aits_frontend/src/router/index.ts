import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../store/user'

const routes: Array<RouteRecordRaw> = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        component: () => import('../layout/AppLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                name: 'Home',
                component: () => import('../views/Home.vue')
            },
            {
                path: 'projects',
                name: 'Projects',
                component: () => import('../views/projects/ProjectList.vue')
            },
            {
                path: 'projects/:id/environments',
                name: 'ProjectEnvironments',
                component: () => import('../views/projects/ProjectEnvironment.vue')
            },
            {
                path: 'api-testing/navigation',
                name: 'APITestingNavigation',
                component: () => import('../views/api_testing/ApiNavigation.vue')
            },
            {
                path: 'api-testing/standard',
                name: 'APITestingStandard',
                component: () => import('../views/api_testing/ApiStandard.vue')
            },
            {
                path: 'api-testing/agent',
                name: 'APITestingAgentGenerator',
                component: () => import('../views/api_testing/ApiAgentGenerator.vue')
            },
            {
                path: 'api-testing/cases',
                name: 'APITestCases',
                component: () => import('../views/api_testing/APITestCaseList.vue')
            },
            {
                path: 'api-testing/suites',
                name: 'APITestSuites',
                component: () => import('../views/api_testing/APITestSuiteList.vue')
            },
            {
                path: 'api-testing/records',
                name: 'APITestingRecords',
                component: () => import('../views/api_testing/ApiExecutionRecords.vue')
            },
            {
                path: 'web-testing/agent-generator',
                name: 'WebUITestingAgentGenerator',
                component: () => import('../views/web_testing/AgentGenerator.vue')
            },
            {
                path: 'web-testing/agent-runner',
                name: 'WebUITestingAgentExecutor',
                component: () => import('../views/web_testing/AgentExecutor.vue')
            },
            {
                path: 'web-testing/cases',
                name: 'WebUITestCases',
                component: () => import('../views/web_testing/WebUITestCaseList.vue')
            },
            {
                path: 'web-testing/suites',
                name: 'WebUITestSuites',
                component: () => import('../views/web_testing/WebUITestSuiteList.vue')
            },
            {
                path: 'web-testing/records',
                name: 'WebUITestingRecords',
                component: () => import('../views/web_testing/ExecutionRecords.vue')
            },
            {
                path: 'ai-core/llm',
                name: 'LLMConfig',
                component: () => import('../views/ai_core/LLMConfigList.vue')
            },
            {
                path: 'ai-core/rag',
                name: 'RAGConfig',
                component: () => import('../views/ai_core/RAGConfigList.vue')
            },
            {
                path: 'ai-core/mcp',
                name: 'MCPConfig',
                component: () => import('../views/ai_core/MCPConfigList.vue')
            },
            {
                path: 'scheduled-tasks',
                name: 'ScheduledTasks',
                component: () => import('../views/scheduled_tasks/ScheduledTaskList.vue')
            },
            {
                path: 'common/ws-test',
                name: 'WebSocketTest',
                component: () => import('../views/common/WebSocketTest.vue')
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation Guard
router.beforeEach((to, from, next) => {
    const userStore = useUserStore()
    if (to.meta.requiresAuth && !userStore.token) {
        next('/login')
    } else if (to.path === '/login' && userStore.token) {
        next('/')
    } else {
        next()
    }
})

export default router
