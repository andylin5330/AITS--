import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// Import Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Import Plugins
import { createPinia } from 'pinia'
import router from './router'

const app = createApp(App)

// Register Element Plus Icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

const pinia = createPinia()

app.use(ElementPlus)
app.use(pinia)
app.use(router)

app.mount('#app')
