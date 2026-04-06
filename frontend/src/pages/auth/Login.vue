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
        @submit.prevent="submitForm" 
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
            <span v-else>驗證中...</span>
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
        <span v-if="connectionState" class="status" :class="connectionState.type">
          <el-icon class="status-icon"><component :is="connectionState.icon" /></el-icon>
          {{ connectionState.text }}
        </span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { Loading, Check, Warning } from '@element-plus/icons-vue'
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

// 提交表單
const submitForm = async () => {
  const isValid = await loginForm.value?.validate().catch(() => false)
  if (!isValid) {
    ElMessage.warning('請檢查表單填寫是否正確')
    return
  }

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
    setTimeout(() => {
      router.push('/dashboard')
    }, 500)
  } catch (error) {
    console.error('登入失敗:', error)
  }
}

// 測試API連接
const testApiConnection = async () => {
  connectionStatus.value = 'waiting'
  try {
    await api.get('/') // 測試基本API連接，使用根路徑
    connectionStatus.value = 'success'
  } catch (error) {
    console.error('API連接測試失敗:', error)
    connectionStatus.value = 'error'
  }
}

// 監聽 auth store 中的錯誤
const authError = computed(() => authStore.error)
const isLoading = computed(() => authStore.isLoading)
const connectionState = computed(() => {
  const states = {
    waiting: {
      icon: Loading,
      text: '正在連接服務器...',
      type: 'waiting'
    },
    success: {
      icon: Check,
      text: '伺服器連接正常',
      type: 'success'
    },
    error: {
      icon: Warning,
      text: '伺服器連接失敗，請檢查網路連接或聯絡客服',
      type: 'error'
    }
  }

  return states[connectionStatus.value] || null
})

watch(
  () => [form.email, form.password],
  () => {
    if (authStore.error) {
      authStore.clearError()
    }
  }
)

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
  background: linear-gradient(150deg, #fff4e8 0%, #ffe0c0 55%, #ffd0a0 100%);
  padding: 40px 20px;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-top: -84px;
  margin-bottom: -40px;
  box-sizing: border-box;
}

@media (min-width: 769px) {
  .login-page {
    background-image: linear-gradient(rgba(255, 249, 240, 0.7), rgba(255, 237, 212, 0.72)), url('/img/logos/background.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
  }
}

.auth-container {
  width: 100%;
  max-width: 500px;
  border: none;
  box-shadow: var(--shadow-card-hover);
  border-radius: var(--surface-radius-lg);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.main-title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #e06000 0%, #ffaa55 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
  color: #7c4a00;
  font-size: 0.9rem;
  padding: 10px;
  border-radius: 8px;
  background-color: #fff4e8;
  border: 1px solid #fde8cc;
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

.error-alert :deep(.el-alert__title),
.error-alert :deep(.el-alert__description) {
  font-family: var(--font-tc), var(--font-en);
}

.password-item {
  margin-bottom: 4px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-weight: 600;
  font-size: 1rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
  border-color: transparent;
  margin-top: 16px;
  border-radius: var(--btn-radius);
  box-shadow: var(--shadow-button);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-btn:hover:not([disabled]) {
  box-shadow: var(--shadow-button-hover);
  transform: translateY(-2px);
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
  .login-page {
    background: #ffffff;
    padding: 16px 0 24px;
  }

  .auth-container {
    margin: 0;
    max-width: none;
    border-radius: 0;
    box-shadow: none;
    border: none;
    background: #ffffff;
  }

  .auth-container :deep(.el-card__body) {
    padding: 24px 20px !important;
  }
  
  .features-overview {
    flex-wrap: wrap;
  }
  
  .main-title {
    font-size: 2.5rem;
  }
}
</style>  