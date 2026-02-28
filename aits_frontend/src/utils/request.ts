import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store/user'

const request = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1',
    timeout: 10000
})

// Request Interceptor
request.interceptors.request.use(
    config => {
        const userStore = useUserStore()
        if (userStore.token) {
            config.headers['Authorization'] = `Bearer ${userStore.token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// Response Interceptor
request.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        const message = error.response?.data?.detail || error.message || '请求失败'
        ElMessage.error(message)

        if (error.response?.status === 401) {
            const userStore = useUserStore()
            userStore.logout()
        }
        return Promise.reject(error)
    }
)

export default request
