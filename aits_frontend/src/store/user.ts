import { defineStore } from 'pinia'
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export const useUserStore = defineStore('user', () => {
    const token = ref(localStorage.getItem('token') || '')
    const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))

    const login = async (loginForm: any) => {
        try {
            // 注意：登录接口在 django-rest-framework-simplejwt 默认在 /api/token/
            const res = await axios.post('http://127.0.0.1:8000/api/token/', loginForm)
            token.value = res.data.access
            localStorage.setItem('token', token.value)
            // 简单处理：将username存在本地来展示
            userInfo.value = { username: loginForm.username }
            localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
            return true
        } catch (error) {
            throw error
        }
    }

    const logout = () => {
        token.value = ''
        userInfo.value = {}
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        // 通常还需要在组件内跳转到登录页，这里交给拦截器/组件处理
    }

    return {
        token,
        userInfo,
        login,
        logout
    }
})
