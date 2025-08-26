<template>
  <div class="login-page">
    <el-card class="auth-container" :body-style="{ padding: '36px' }">
      <div class="auth-header">
        <h1 class="main-title">Super Idol</h1>
        <p class="tagline">健康管理的最佳伙伴</p>
        
        <div class="features-overview">
          <div class="feature">
            <el-icon class="feature-icon"><IconFood /></el-icon>
            <span>飲食追蹤</span>
          </div>
          <div class="feature">
            <el-icon class="feature-icon"><IconSport /></el-icon>
            <span>運動紀錄</span>
          </div>
          <div class="feature">
            <el-icon class="feature-icon"><IconTrophy /></el-icon>
            <span>健康目標</span>
          </div>
        </div>
        
        <h2 class="welcome-text">歡迎回來</h2>
        <p class="subtitle">登入您的帳戶，繼續您的健康旅程</p>
      </div>
      
      <el-alert 
        v-if="authError" 
        type="error" 
        :title="authError" 
        show-icon 
        class="error-alert"
        :closable="false"
      />
      
      <el-form 
        @submit.prevent="handleLogin" 
        class="auth-form" 
        :model="form" 
        :rules="rules" 
        ref="loginForm" 
        status-icon
      >
        <el-form-item prop="email">
          <el-input 
            v-model="form.email" 
            placeholder="電子郵件"
            prefix-icon="Message"
            type="email"
            size="large"
            @keyup.enter="submitForm"
          />
        </el-form-item>
        
        <el-form-item prop="password" class="password-item">
          <el-input 
            v-model="form.password"
            type="password" 
            placeholder="密碼"
            prefix-icon="Lock"
            show-password
            size="large"
            @keyup.enter="submitForm"
          />
          <div class="forgot-password">
            <router-link to="/forgot-password" class="forgot-link">忘記密碼?</router-link>
          </div>
        </el-form-item>
        
        <el-form-item class="remember-item">
          <el-checkbox v-model="rememberMe">記住我</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="isLoading" 
            @click="submitForm" 
            class="login-btn"
            size="large"
          >
            <span v-if="!isLoading">登入</span>
            <span v-else class="loading-text">
              <el-icon class="loading-icon"><Loading /></el-icon>
              驗證中...
            </span>
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="auth-footer">
        <p>
          還沒有帳戶？
          <router-link to="/register">
            <el-link type="primary">立即註冊</el-link>
          </router-link>
        </p>
      </div>
      
      <div class="connection-status">
        <span v-if="connectionStatus === 'waiting'" class="status waiting">
          <el-icon class="status-icon"><Loading /></el-icon>
          正在連接服務器...
        </span>
        <span v-else-if="connectionStatus === 'success'" class="status success">
          <el-icon class="status-icon"><Check /></el-icon>
          伺服器連接正常
        </span>
        <span v-else-if="connectionStatus === 'error'" class="status error">
          <el-icon class="status-icon"><Warning /></el-icon>
          伺服器連接失敗，請檢查網路連接或聯絡客服
        </span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { Message, Lock, Loading, Check, Warning } from '@element-plus/icons-vue'
import { isValidEmail } from '../../utils/validation'
import api from '../../services/api'
import { ElMessage } from 'element-plus'
import IconFood from '../../components/icons/IconFood.vue'
import IconSport from '../../components/icons/IconSport.vue'
import IconTrophy from '../../components/icons/IconTrophy.vue'

// Router and Store
const router = useRouter()
const authStore = useAuthStore()

// Form refs and state
const loginForm = ref(null)
const isSubmitAttempted = ref(false)
const rememberMe = ref(false)
const connectionStatus = ref('waiting')

// Form data
const form = reactive({
  email: '',
  password: ''
})

// Form validation rules
const rules = {
  email: [
    {
      required: true,
      message: '請輸入電子郵件',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback()
          return
        }
        if (!isValidEmail(value)) {
          callback(new Error('請輸入有效的電子郵件地址'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: '請輸入密碼',
      trigger: 'blur'
    },
    {
      min: 8,
      message: '密碼長度必須至少為8個字符',
      trigger: 'blur'
    }
  ]
}

// 表單有效性狀態
const formIsValid = computed(() => {
  if (!form.email || !form.password) return false
  if (!isValidEmail(form.email) || form.password.length < 8) return false
  return true
})

// 提交表單
const submitForm = () => {
  isSubmitAttempted.value = true
  loginForm.value?.validate(async valid => {
    if (valid) {
      try {
        await handleLogin()
      } catch (error) {
        console.error('表單驗證通過，但登入失敗:', error)
      }
    } else {
      ElMessage.warning('請檢查表單填寫是否正確')
    }
  })
}

// 處理登入邏輯
const handleLogin = async () => {
  try {
    await authStore.login({
      email: form.email,
      password: form.password
    })

    // 處理記住我功能
    if (rememberMe.value) {
      localStorage.setItem('rememberedEmail', form.email)
    } else {
      localStorage.removeItem('rememberedEmail')
    }
    
    ElMessage.success('登入成功！正在前往儀表板...')
    // 使用 setTimeout 給用戶一個視覺反饋的時間
    setTimeout(() => {
      router.push('/dashboard')
    }, 500)
  } catch (error) {
    console.error('登入失敗:', error)
    ElMessage.error('登入失敗，請檢查帳號密碼是否正確')
  }
}

// 測試API連接
const testApiConnection = async () => {
  connectionStatus.value = 'waiting'
  try {
    await api.get('/api') // 測試基本API連接
    connectionStatus.value = 'success'
  } catch (error) {
    console.error('API連接測試失敗:', error)
    connectionStatus.value = 'error'
  }
}

// 監聽 auth store 中的錯誤
const authError = computed(() => authStore.error)

// 自動填充記住的帳號
onMounted(() => {
  const savedEmail = localStorage.getItem('rememberedEmail')
  if (savedEmail) {
    form.email = savedEmail
    rememberMe.value = true
  }
  
  // 測試API連接
  testApiConnection()
})
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 500px;
  border: none;
  box-shadow: 0 0 30px rgba(0,0,0,0.1);
  border-radius: 16px;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  color: #f97316;
  margin-bottom: 8px;
  letter-spacing: -1px;
}

.tagline {
  color: #64748b;
  font-size: 1.2rem;
  margin-bottom: 24px;
}

.features-overview {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin: 24px 0;
}

.feature {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #475569;
  font-size: 0.9rem;
  padding: 10px;
  border-radius: 8px;
  background-color: #f1f5f9;
  width: 90px;
}

.feature-icon {
  font-size: 24px;
  margin-bottom: 8px;
  color: #f97316;
}

.welcome-text {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin: 24px 0 8px;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
  margin-bottom: 16px;
}

.auth-form {
  margin-top: 24px;
}

.error-alert {
  margin-bottom: 16px;
}

.password-item {
  margin-bottom: 4px;
}

.forgot-password {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.forgot-link {
  color: #f59e0b;
  font-size: 0.875rem;
  text-decoration: none;
}

.forgot-link:hover {
  color: #d97706;
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-weight: 600;
  font-size: 1rem;
  background-color: #f97316;
  border-color: #f97316;
  margin-top: 16px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.login-btn:hover:not([disabled]) {
  background-color: #ea580c;
  border-color: #ea580c;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-icon {
  margin-right: 8px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.auth-footer {
  margin-top: 32px;
  text-align: center;
  color: #64748b;
}

.auth-footer .el-link {
  color: #f59e0b !important;
  font-weight: 600;
}

.connection-status {
  text-align: center;
  margin-top: 24px;
  font-size: 0.75rem;
}

.status {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  font-weight: 500;
}

.status-icon {
  margin-right: 6px;
  font-size: 14px;
}

.status.waiting {
  background-color: #f1f5f9;
  color: #64748b;
}

.status.success {
  background-color: #ecfdf5;
  color: #059669;
}

.status.error {
  background-color: #fef2f2;
  color: #dc2626;
}

.remember-item {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .auth-container {
    margin: 10px;
  }
  
  .features-overview {
    flex-wrap: wrap;
  }
  
  .main-title {
    font-size: 2.5rem;
  }
}
</style>  