<template>
  <div class="register-page">
    <el-card class="auth-container" shadow="hover">
      <div class="auth-header">
        <h1>Super Idol</h1>
        <p>創建新帳戶</p>
      </div>
      
      <el-alert v-if="authError" type="error" :title="authError" show-icon />
      
      <div class="progress-steps">
        <div class="step active">
          <div class="step-icon">1</div>
          <div class="step-label">基本資訊</div>
        </div>
        <div class="step">
          <div class="step-icon">2</div>
          <div class="step-label">偏好設定</div>
        </div>
        <div class="step">
          <div class="step-icon">3</div>
          <div class="step-label">完成</div>
        </div>
      </div>
      
      <el-form 
        @submit.native.prevent="handleRegister" 
        class="auth-form" 
        :model="form" 
        :rules="rules"
        ref="registerForm"
        status-icon
      >
        <div class="preference-card">
          <div class="card-header">
            <i class="el-icon-user"></i>
            <h3>個人資料</h3>
          </div>
          
          <el-form-item label="姓名 *" prop="name">
            <el-input 
              v-model="form.name"
              placeholder="請輸入您的姓名"
              prefix-icon="User"
              style="font-size: 18px;"
            />
          </el-form-item>
          
          <el-form-item label="體重 (kg) *" prop="weight">
            <el-input-number 
              v-model="form.weight" 
              :min="30" 
              :max="200"
              placeholder="請輸入您的體重（必填）" 
              controls-position="right"
              class="weight-input"
              style="font-size: 18px;"
            />
            <div class="form-hint">您的體重資訊將用於計算健康目標和熱量建議</div>
          </el-form-item>
          
          <el-form-item label="每週熱量限制 *" prop="weekcalorielimit">
            <div class="calorie-input-group">
              <el-input-number 
                v-model="form.weekcalorielimit" 
                :min="0" 
                placeholder="請輸入每週熱量限制（必填）" 
                controls-position="right"
                class="calorie-input"
                style="width: 200px;"
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
        
        <div class="preference-card">
          <div class="card-header">
            <i class="el-icon-lock"></i>
            <h3>帳號設定</h3>
          </div>
          
          <el-form-item label="電子郵件" prop="email">
            <el-input 
              v-model="form.email"
              type="email" 
              placeholder="請輸入電子郵件"
              prefix-icon="Message"
              @blur="validateEmail"
            />
          </el-form-item>
          
          <el-form-item label="密碼" prop="password">
            <el-input 
              v-model="form.password"
              type="password" 
              placeholder="請輸入密碼"
              prefix-icon="Lock"
              show-password
              @input="checkPasswordStrength"
            />
            <div v-if="passwordResult.isValid" class="password-strength" :class="passwordResult.strength">
              密碼強度: {{ passwordResult.message }}
            </div>
            <div v-else class="password-strength error">
              {{ passwordResult.message }}
            </div>
          </el-form-item>
          
          <el-form-item label="確認密碼" prop="confirmPassword">
            <el-input 
              v-model="form.confirmPassword"
              type="password" 
              placeholder="請再次輸入密碼"
              prefix-icon="Lock"
              show-password
              @input="validateConfirmPassword"
            />
          </el-form-item>
        </div>
        
        <div class="note">
          <i class="el-icon-info-filled"></i>
          <p>* 標示為必填欄位，其他資訊可於註冊後補充</p>
        </div>
        
        <div class="form-actions">
          <el-button 
            type="primary" 
            :loading="isLoading" 
            @click="submitForm" 
            class="submit-button"
          >
            <i class="el-icon-arrow-right" v-if="!isLoading"></i>
            {{ isLoading ? '提交中...' : '下一步' }}
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

<script>
import { reactive, computed, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { User, Message, Lock } from '@element-plus/icons-vue'
import { isValidEmail, validatePassword, isValidName, doPasswordsMatch } from '../../utils/validation'
import api from '../../services/api'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import CalorieCalculator from '../../components/CalorieCalculator.vue'

export default {
  name: 'RegisterPage',
  components: { User, Message, Lock, CalorieCalculator },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const registerForm = ref(null)
    const formIsValid = ref(true) // 設為true以允許提交
    const isSubmitAttempted = ref(false)
    const passwordResult = ref({
      isValid: false,
      message: '',
      strength: 'weak'
    })
    
    const form = reactive({
      name: '',           // 必填
      email: '',          // 必填
      password: '',       // 必填
      confirmPassword: '',
      weight: null,       // 必填
      weekcalorielimit: 12000, // 設定預設值
    })
    
    const localError = ref('')
    
    const rules = {
      name: [
        {
          validator: (rule, value, callback) => {
            if (!isSubmitAttempted.value && !value) {
              callback()
              return
            }
            if (!value) {
              callback(new Error('請輸入姓名'))
            } else if (value.length < 2) {
              callback(new Error('姓名至少需要2個字符'))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      weight: [
        {
          validator: (rule, value, callback) => {
            if (!isSubmitAttempted.value && value == null) {
              callback()
              return
            }
            if (value == null || value === '') {
              callback(new Error('請輸入體重'))
            } else if (value < 20 || value > 200) {
              callback(new Error('體重需在合理範圍內'))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      email: [
        {
          validator: (rule, value, callback) => {
            if (!isSubmitAttempted.value && !value) {
              callback()
              return
            }
            if (!value) {
              callback(new Error('請輸入電子郵件'))
            } else if (!isValidEmail(value)) {
              callback(new Error('請輸入有效的電子郵件地址'))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      password: [
        {
          validator: (rule, value, callback) => {
            if (!isSubmitAttempted.value && !value) {
              callback()
              return
            }
            if (!value) {
              callback(new Error('請輸入密碼'))
            } else {
              const result = validatePassword(value)
              if (!result.isValid) {
                callback(new Error(result.message))
              } else {
                callback()
              }
            }
          },
          trigger: ['blur', 'change']
        }
      ],
      confirmPassword: [
        {
          validator: (rule, value, callback) => {
            if (!isSubmitAttempted.value && !value) {
              callback()
              return
            }
            if (!value) {
              callback(new Error('請再次輸入密碼'))
            } else if (!doPasswordsMatch(form.password, value)) {
              callback(new Error('兩次輸入的密碼不一致'))
            } else {
              callback()
            }
          },
          trigger: ['blur', 'change']
        }
      ]
    }
    
    // 檢查密碼強度
    const checkPasswordStrength = () => {
      passwordResult.value = validatePassword(form.password)
      if (form.confirmPassword) {
        validateConfirmPassword()
      }
    }
    
    // 驗證確認密碼
    const validateConfirmPassword = () => {
      if (registerForm.value) {
        registerForm.value.validateField('confirmPassword')
      }
    }
    
    // 驗證電子郵件
    const validateEmail = () => {
      if (registerForm.value) {
        registerForm.value.validateField('email')
      }
    }
    
    const submitForm = () => {
      isSubmitAttempted.value = true
      if (!registerForm.value) {
        handleRegister()
        return
      }
      registerForm.value.validate(valid => {
        if (valid) {
          handleRegister()
        } else {
          console.log('表單驗證失敗，顯示錯誤訊息')
        }
      })
    }
    
    const checkEmailExists = async (email) => {
      try {
        const res = await axios.post('/api/auth/check-email', { email })
        return res.data.exists
      } catch (e) {
        return false // 若 API 失敗，預設不阻擋
      }
    }
    
    const handleRegister = async () => {
      if (form.password !== form.confirmPassword) {
        localError.value = '兩次輸入的密碼不一致'
        return
      }
      
      // 驗證所有必填欄位
      if (!form.name || !form.email || !form.password) {
        localError.value = '請填寫基本資料（姓名、電子郵件、密碼）'
        return
      }
      
      // 特別檢查體重
      if (form.weight === null || form.weight === '') {
        localError.value = '請填寫您的體重'
        if (registerForm.value) registerForm.value.validateField('weight')
        return
      }
      
      // 檢查 email 是否已註冊
      const exists = await checkEmailExists(form.email)
      if (exists) {
        localError.value = '此電子郵件已經註冊，請使用其他電子郵件或直接登入'
        return
      }
      
      localError.value = ''
      
      // 創建包含必要註冊資訊的物件
      const registrationData = {
        name: form.name,
        email: form.email,
        password: form.password,
        weight: form.weight,
        weekcalorielimit: form.weekcalorielimit
      }
      
      // 將註冊資料保存到會話存儲
      sessionStorage.setItem('registrationData', JSON.stringify(registrationData))
      
      // 簡單導向偏好設置頁面，不通過路由參數傳遞數據
      router.push('/preferences')
    }
    
    const authError = computed(() => {
      return localError.value || authStore.error
    })
    
    // 監聽表單變化以更新表單有效性
    const validateForm = () => {
      if (registerForm.value) {
        registerForm.value.validate((valid) => {
          formIsValid.value = true; // 始終允許提交
        })
      }
    }
    
    // 監聽密碼變化
    watch(() => form.password, () => {
      checkPasswordStrength()
    })
    
    onMounted(() => {
      // 初始驗證表單
      validateForm()
    })
    
    return {
      form,
      rules,
      registerForm,
      handleRegister,
      submitForm,
      validateEmail,
      validateConfirmPassword,
      checkPasswordStrength,
      passwordResult,
      isSubmitAttempted,
      formIsValid,
      isLoading: computed(() => authStore.isLoading),
      authError
    }
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
}

.auth-container {
  width: 100%;
  max-width: 700px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border: none;
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f8f9fa;
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

/* 新的步驟指示器樣式 */
.progress-steps {
  display: flex;
  justify-content: space-between;
  margin: 30px 0;
  position: relative;
}

.progress-steps::before {
  content: "";
  position: absolute;
  top: 20px;
  left: 10%;
  right: 10%;
  height: 2px;
  background-color: #e0e0e0;
  z-index: 0;
}

.step {
  position: relative;
  width: 33.33%;
  text-align: center;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  border: 2px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 8px;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.step.completed .step-icon {
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
}

.step.completed .step-label {
  color: #67c23a;
}

.step.active .step-icon {
  background-color: #f08c00;
  border-color: #f08c00;
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(240, 140, 0, 0.25);
}

.step.active .step-label {
  color: #f08c00;
  font-weight: 600;
}

/* 卡片式表單區塊 */
.preference-card {
  margin-bottom: 24px;
  padding: 20px;
  border-radius: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.preference-card:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header i {
  font-size: 22px;
  color: #f08c00;
}

.card-header h3 {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

/* 表單元素樣式 */
.auth-form {
  margin-top: 20px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  font-size: 18px;
  font-weight: 600;
}

.form-hint {
  font-size: 15px;
  color: #909399;
  margin: 4px 0 0;
}

.weight-input {
  width: 100%;
  max-width: 300px;
}

/* 密碼強度提示 */
.password-strength {
  margin-top: 5px;
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
}

.password-strength.weak {
  background-color: #fff0f0;
  color: #f56c6c;
}

.password-strength.medium {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.password-strength.good {
  background-color: #f0f9eb;
  color: #67c23a;
}

.password-strength.strong {
  background-color: #fff0d6;
  color: #f08c00;
}

.password-strength.error {
  background-color: #fff0f0;
  color: #f56c6c;
}

/* 精緻備註樣式 */
.note {
  font-size: 14px;
  color: #909399;
  margin: 20px 0;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.note i {
  color: #f08c00;
  font-size: 16px;
  margin-top: 2px;
}

/* 按鈕樣式改進 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}

.submit-button {
  background: linear-gradient(135deg, #f08c00 0%, #ffb347 100%);
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  padding: 12px 40px;
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(240, 140, 0, 0.25);
  transition: all 0.3s ease;
  min-width: 180px;
}

.submit-button:hover {
  box-shadow: 0 6px 16px rgba(240, 140, 0, 0.35);
  transform: translateY(-2px);
}

.submit-button i {
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

/* 響應式調整 */
@media (max-width: 600px) {
  .register-page {
    padding: 20px 10px;
  }
  
  .auth-container {
    border-radius: 8px;
  }
  
  .card-header h3 {
    font-size: 18px;
  }
  
  .preference-card {
    padding: 15px;
    margin-bottom: 16px;
  }
  
  .form-actions {
    justify-content: center;
  }
  
  .submit-button {
    width: 100%;
  }
  
  .progress-steps::before {
    left: 15%;
    right: 15%;
  }
}

.calorie-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
}

.calorie-input {
  flex-shrink: 0;
}
</style>