import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './utils/axios' // 引入 Axios 配置


// 創建 Vue 應用
const app = createApp(App)

// 使用 Pinia 狀態管理
const pinia = createPinia()
app.use(pinia)
app.use(ElementPlus) // 加入這行

// 使用路由
app.use(router)

// 掛載應用
app.mount('#app') 