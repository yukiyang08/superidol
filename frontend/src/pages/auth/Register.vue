<template>
  <div class="register-page">
    <el-card class="auth-container" shadow="hover">
      <div class="auth-header">
        <h1>Super Idol</h1>
        <p>創建新帳戶</p>
      </div>
      
      <el-alert v-if="authError" type="error" :title="authError" show-icon class="error-alert" />
      
      <el-form 
        @submit.prevent="submitForm" 
        class="auth-form" 
        :model="form" 
        :rules="rules"
        ref="registerForm"
        status-icon
      >
        <!-- 基本資訊區塊 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><User /></el-icon>
            <h3>基本資訊</h3>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="姓名 *" prop="name">
                <el-input 
                  v-model="form.name"
                  placeholder="請輸入您的姓名"
                  prefix-icon="User"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="體重 (kg) *" prop="weight">
                <el-input-number 
                  v-model="form.weight" 
                  :min="30" 
                  :max="200"
                  placeholder="體重" 
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="每週熱量限制 *" prop="weekcalorielimit">
            <div class="calorie-input-group">
              <el-input-number 
                v-model="form.weekcalorielimit" 
                :min="0" 
                placeholder="每週熱量限制" 
                controls-position="right"
                style="width: 200px"
              />
              <CalorieCalculator 
                v-if="form.weight"
                v-model="form.weekcalorielimit"
                :weight="form.weight"
              />
            </div>
            <div class="form-hint">設定每週攝取熱量的最大值</div>
          </el-form-item>
        </div>
        
        <!-- 帳號設定區塊 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><Lock /></el-icon>
            <h3>帳號設定</h3>
          </div>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="電子郵件 *" prop="email">
                <el-input 
                  v-model="form.email"
                  type="email" 
                  placeholder="請輸入電子郵件"
                  prefix-icon="Message"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="密碼 *" prop="password">
                <el-input 
                  v-model="form.password"
                  type="password" 
                  placeholder="請輸入密碼"
                  prefix-icon="Lock"
                  show-password
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="確認密碼 *" prop="confirmPassword">
            <el-input 
              v-model="form.confirmPassword"
              type="password" 
              placeholder="請再次輸入密碼"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
        </div>
        
        <!-- 偏好設定區塊 -->
        <div class="form-section">
          <div class="section-header">
            <el-icon><Star /></el-icon>
            <h3>偏好設定</h3>
          </div>
          
          <el-form-item label="食物偏好">
            <div class="preference-chips">
              <el-checkbox-group v-model="form.foodPreferences">
                <el-checkbox label="singleDish">單點</el-checkbox>
                <el-checkbox label="setMeal">套餐</el-checkbox>
              </el-checkbox-group>
            </div>
          </el-form-item>
          
          <el-form-item label="辣度偏好">
            <el-radio-group v-model="form.spicyLevel">
              <el-radio :label="0">不辣</el-radio>
              <el-radio :label="1">微辣</el-radio>
              <el-radio :label="2">中辣</el-radio>
              <el-radio :label="3">重辣</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="價格範圍">
            <el-radio-group v-model="form.priceRange">
              <el-radio :label="1">經濟實惠</el-radio>
              <el-radio :label="2">中等價位</el-radio>
              <el-radio :label="3">高級精緻</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>
        
        <div class="note">
          <el-icon><InfoFilled /></el-icon>
          <p>* 標示為必填欄位，其他資訊可於註冊後補充</p>
        </div>
        
        <div class="form-actions">
          <el-button 
            type="primary" 
            :loading="isLoading" 
            @click="submitForm" 
            class="submit-button"
          >
            <el-icon v-if="!isLoading"><ArrowRight /></el-icon>
            {{ isLoading ? '註冊中...' : '立即註冊' }}
          </el-button>
        </div>
      </el-form>
      
      <div class="auth-footer">
        <p>
          已有帳戶？
          <router-link to="/login">
            <el-link type="primary">立即登入</el-link>
          </router-link>
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, Star, InfoFilled, ArrowRight } from '@element-plus/icons-vue'
import CalorieCalculator from '../../components/CalorieCalculator.vue'

const router = useRouter()
const authStore = useAuthStore()
const registerForm = ref(null)

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  weight: null,
  weekcalorielimit: 12000,
  foodPreferences: ['singleDish', 'setMeal'],
  spicyLevel: 1,
  priceRange: 2,
})

const rules = {
  name: [
    { required: true, message: '請輸入姓名', trigger: 'blur' },
    { min: 2, message: '姓名至少需要2個字符', trigger: 'blur' }
  ],
  weight: [
    { required: true, message: '請輸入體重', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value < 30 || value > 200) {
          callback(new Error('體重需在30-200kg範圍內'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  weekcalorielimit: [
    { required: true, message: '請輸入每週熱量限制', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value <= 0) {
          callback(new Error('熱量限制必須大於0'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  email: [
    { required: true, message: '請輸入電子郵件', trigger: 'blur' },
    { type: 'email', message: '請輸入有效的電子郵件地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '請輸入密碼', trigger: 'blur' },
    { min: 6, message: '密碼至少需要6個字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '請再次輸入密碼', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) {
          callback(new Error('兩次輸入的密碼不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const submitForm = async () => {
  const isValid = await registerForm.value?.validate().catch(() => false)
  if (!isValid) {
    return
  }

  try {
    await authStore.register({
      name: form.name,
      email: form.email,
      password: form.password,
      weight: form.weight,
      weekcalorielimit: form.weekcalorielimit,
      foodPreferences: form.foodPreferences,
      spicyLevel: form.spicyLevel,
      priceRange: form.priceRange
    })

    ElMessage.success('註冊成功！正在跳轉到登入頁面...')
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    console.error('註冊失敗:', error)
    if (authStore.error) {
      return
    }
    ElMessage.error(error.response?.data?.detail || '註冊失敗，請稍後再試')
  }
}

const authError = computed(() => authStore.error)
const isLoading = computed(() => authStore.isLoading)

watch(
  () => [form.name, form.email, form.password, form.confirmPassword, form.weight],
  () => {
    if (authStore.error) {
      authStore.clearError()
    }
  }
)
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(150deg, #fff4e8 0%, #ffe0c0 55%, #ffd0a0 100%);
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-top: -84px;
  margin-bottom: -40px;
  box-sizing: border-box;
}

.auth-container {
  width: 100%;
  max-width: 700px;
  border-radius: var(--surface-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  border: none;
}

.error-alert {
  margin-bottom: 16px;
}

.error-alert :deep(.el-alert__title),
.error-alert :deep(.el-alert__description) {
  font-family: var(--font-tc), var(--font-en);
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 8px;
}

.auth-header h1 {
  margin-bottom: 8px;
  color: #f08c00;
  font-weight: 700;
  font-size: 2.8rem;
  letter-spacing: -0.5px;
}

.auth-header p {
  color: #f08c00;
  font-weight: 600;
  font-size: 1.4rem;
  opacity: 0.9;
}

.auth-form {
  margin-top: 12px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  font-size: 18px;
  font-weight: 600;
}

/* 表單區塊樣式 */
.form-section {
  background: transparent;
  border-radius: 0;
  padding: 18px 0;
  margin-bottom: 12px;
  border: none;
  border-top: 1px solid #f1e7d7;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 0;
  border-bottom: none;
}

.section-header :deep(.el-icon) {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: #d97706;
  background: #fff4e8;
}

.section-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #374151;
}

/* 偏好設定樣式 */
.preference-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}

.preference-chips .el-checkbox {
  margin-right: 0;
}

.form-hint {
  font-size: 0.9rem;
  color: #6c757d;
  margin-top: 6px;
  font-style: italic;
}

.calorie-input-group {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.calorie-input-group .el-input-number {
  flex-shrink: 0;
}

.note {
  font-size: 13px;
  color: #8a6b43;
  margin: 12px 0 18px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background-color: #fff8ef;
  border-radius: 10px;
  border: 1px solid #f3dfbf;
}

.note :deep(.el-icon) {
  color: #d97706;
  font-size: 16px;
  margin-top: 2px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}

.submit-button {
  background: linear-gradient(135deg, #f08c00 0%, #ffb347 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  padding: 12px 30px;
  border-radius: 10px;
  border: none;
  box-shadow: 0 4px 12px rgba(240, 140, 0, 0.25);
  transition: all 0.3s ease;
  min-width: 160px;
}

.submit-button:hover {
  box-shadow: 0 6px 16px rgba(240, 140, 0, 0.35);
  transform: translateY(-2px);
}

.submit-button .el-icon {
  margin-right: 6px;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.auth-footer .el-link {
  color: #f08c00 !important;
  font-weight: 600;
  transition: color 0.3s;
}

.auth-footer .el-link:hover {
  color: #d48806 !important;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .register-page {
    padding: 20px 10px;
  }
  
  .auth-container {
    border-radius: 8px;
  }
  
  .form-actions {
    justify-content: center;
  }
  
  .submit-button {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .form-section {
    padding: 16px 0;
  }
  
  .preference-chips {
    flex-direction: column;
    gap: 12px;
  }
  
  .calorie-input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .calorie-input-group .el-input-number {
    width: 100% !important;
  }
}
</style>