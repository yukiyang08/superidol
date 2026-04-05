<template>
  <div class="preferences-page">
    <el-card class="auth-container" shadow="hover">
      <div class="auth-header">
        <h1>Super Idol</h1>
        <p>設定您的偏好</p>
      </div>
      
      <el-alert v-if="authError" type="error" :title="authError" show-icon />
      
      <div class="progress-steps">
        <div class="step completed">
          <div class="step-icon">1</div>
          <div class="step-label">基本資訊</div>
        </div>
        <div class="step active">
          <div class="step-icon">2</div>
          <div class="step-label">偏好設定</div>
        </div>
        <div class="step">
          <div class="step-icon">3</div>
          <div class="step-label">完成</div>
        </div>
      </div>
      
      <!-- 顯示載入中狀態 -->
      <div v-if="!dataLoaded" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>載入偏好資料中，請稍候...</p>
      </div>
      
      <!-- 已載入才顯示表單 -->
      <div v-if="dataLoaded">
        <el-form 
          class="preferences-form" 
          :model="preferences"
          ref="preferencesForm"
        >
          <!-- 預算和熱量限制 -->
          <div class="preference-card">
            <div class="card-header">
              <i class="el-icon-setting"></i>
              <h3>個人設定</h3>
            </div>
            
            <el-form-item label="每餐預算 *" prop="budget">
              <el-input-number 
                v-model="budget" 
                :min="0" 
                placeholder="請輸入預算（必填）" 
                controls-position="right"
                class="budget-input"
              />
              <div class="form-hint">設定每餐的預算上限</div>
            </el-form-item>

            <el-form-item label="每週熱量限制 *" prop="calorieLimit">
              <div class="calorie-input-group">
              <el-input-number 
                v-model="calorieLimit" 
                :min="0" 
                placeholder="請輸入每週熱量限制（必填）" 
                controls-position="right"
                class="calorie-input"
                  style="width: 200px;"
                />
                <CalorieCalculator 
                  v-if="registrationData && registrationData.weight"
                  v-model="calorieLimit"
                  :weight="Number(registrationData.weight)"
              />
              </div>
              <div class="form-hint">設定每週攝取熱量的最大值</div>
            </el-form-item>
          </div>
          
          <!-- 食物偏好 -->
          <div class="preference-card">
            <div class="card-header">
              <i class="el-icon-food"></i>
              <h3>飲食偏好</h3>
            </div>
            <el-form-item label="食物類型偏好">
              <div class="form-hint">選擇您喜愛的食物類型，幫助我們提供更好的推薦</div>
              <div class="button-group">
                <el-button
                  v-for="type in foodTypes"
                  :key="type.name"
                  :type="preferences.foodTypePreferences[type.name] ? 'primary' : 'info'"
                  :plain="!preferences.foodTypePreferences[type.name]"
                  @click="preferences.foodTypePreferences[type.name] = !preferences.foodTypePreferences[type.name]"
                  style="margin: 4px"
                >
                  <i class="el-icon-ice-cream" style="margin-right:4px;color:#67c23a"></i>{{ type.name }}
                </el-button>
              </div>
            </el-form-item>
          </div>
          
          <!-- 餐廳偏好 -->
          <div class="preference-card">
            <div class="card-header">
              <i class="el-icon-office-building"></i>
              <h3>餐廳偏好</h3>
            </div>
            <el-form-item label="喜好的餐廳">
              <div class="form-hint">選擇您喜愛的餐廳，以便我們提供合適的建議</div>
              <div class="button-group restaurant-list">
                <el-button
                  v-for="restaurant in restaurants"
                  :key="restaurant.id"
                  :type="preferences.restaurantPreferences[restaurant.id] ? 'primary' : 'info'"
                  :plain="!preferences.restaurantPreferences[restaurant.id]"
                  @click="preferences.restaurantPreferences[restaurant.id] = !preferences.restaurantPreferences[restaurant.id]"
                  style="margin: 4px"
                >
                  <i class="el-icon-office-building" style="margin-right:4px;color:#f08c00"></i>
                  {{ restaurant.name }}
                </el-button>
              </div>
            </el-form-item>
          </div>
          
          <!-- 運動偏好 -->
          <div class="preference-card">
            <div class="card-header">
              <i class="el-icon-basketball"></i>
              <h3>運動偏好</h3>
            </div>
            <el-form-item label="喜好的運動類型">
              <div class="form-hint">選擇您喜愛的運動，以便計算熱量消耗</div>
              <div class="button-group">
                <el-button
                  v-for="item in exerciseItems"
                  :key="item.name"
                  :type="preferences.exercisePreferences[item.name] ? 'primary' : 'info'"
                  :plain="!preferences.exercisePreferences[item.name]"
                  @click="preferences.exercisePreferences[item.name] = !preferences.exercisePreferences[item.name]"
                  style="margin: 4px"
                >
                  <i class="el-icon-basketball" style="margin-right:4px;color:#409eff"></i>{{ item.name }}
                </el-button>
              </div>
            </el-form-item>
          </div>
          
          <div class="note">
            <i class="el-icon-info-filled"></i>
            <p>* 標示為必填欄位，其他偏好設定均為選填，我們會根據您的偏好為您推薦內容</p>
          </div>
          
          <div class="form-actions">
            <el-button @click="goBack" class="back-button">
              <i class="el-icon-arrow-left"></i> 返回
            </el-button>
            <el-button 
              type="primary" 
              :loading="isLoading" 
              @click="submitForm"
              class="submit-button"
            >
              <i class="el-icon-check" v-if="!isLoading"></i>
              {{ isLoading ? '提交中...' : '完成註冊' }}
            </el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import api from '../../services/api'
import CalorieCalculator from '../../components/CalorieCalculator.vue'

const router = useRouter()
const authStore = useAuthStore()
const preferencesForm = ref(null)
const localError = ref('')
    
    // 表單數據
  const budget = ref(200) // 預設值
  const calorieLimit = ref(12000) // 預設值
  const dataLoaded = ref(false)
  const registrationData = ref(null)
    
    // 偏好選項
  const restaurants = ref([])
  const foodTypes = ref([])
  const exerciseItems = ref([])
    
    // 偏好設置
const preferences = reactive({
  storePreferences: {},
  foodTypePreferences: {}, // key: name
  exercisePreferences: {}, // key: name
  restaurantPreferences: {} // key: id
})

    // loading 狀態
  const isLoading = ref(false)

    // 從後端取得偏好選項
  const fetchData = async () => {
      try {
        const restaurantsRes = await api.get('/api/preferences/restaurants')
        restaurants.value = restaurantsRes.data
        // 初始化餐廳偏好
        restaurants.value.forEach(r => {
          preferences.restaurantPreferences[r.id] = false
        })

        const foodTypesRes = await api.get('/api/preferences/food-types')
        foodTypes.value = foodTypesRes.data
        // 初始化食物類型偏好（用 name）
        foodTypes.value.forEach(f => {
          preferences.foodTypePreferences[f.name] = false
        })

        const exerciseItemsRes = await api.get('/api/preferences/exercise-items')
        exerciseItems.value = exerciseItemsRes.data
        // 初始化運動偏好（用 name）
        exerciseItems.value.forEach(e => {
          preferences.exercisePreferences[e.name] = false
        })

        dataLoaded.value = true
      } catch (err) {
        console.error('載入偏好選項失敗:', err)
        dataLoaded.value = false
        ElMessage.error('載入偏好選項失敗，請稍後再試')
      }
  }
    
    // 初始化數據
  onMounted(async () => {
      try {
        // 檢查是否有註冊數據
        const storedData = sessionStorage.getItem('registrationData')
        if (!storedData) {
          ElMessage.warning('請先完成基本資訊設定')
          router.push('/register')
          return
        }
        const parsedData = JSON.parse(storedData)
        console.log('解析後的註冊數據:', parsedData) // 添加日誌
        registrationData.value = parsedData
        await fetchData()
      } catch (error) {
        console.error('載入註冊數據失敗:', error)
        ElMessage.error('載入數據失敗，請重新填寫基本資訊')
        router.push('/register')
      }
  })
    
    // 提交表單
  const submitForm = async () => {
      if (isLoading.value) return
      isLoading.value = true
      try {
        // 驗證必填欄位
        if (budget.value === null || budget.value === '' || budget.value === 0) {
          ElMessage.warning('請填寫每餐預算')
          isLoading.value = false
          return
        }
        if (calorieLimit.value === null || calorieLimit.value === '' || calorieLimit.value === 0) {
          ElMessage.warning('請填寫每週熱量限制')
          isLoading.value = false
          return
        }
        // 收集偏好
        const Food_PreferencesList = []
        for (const [key, value] of Object.entries(preferences.foodTypePreferences)) {
          if (value) Food_PreferencesList.push(key)
        }
        const exercisePreferencesList = []
        for (const [key, value] of Object.entries(preferences.exercisePreferences)) {
          if (value) exercisePreferencesList.push(key)
        }
        const restaurantPreferencesList = []
        for (const [key, value] of Object.entries(preferences.restaurantPreferences)) {
          if (value) restaurantPreferencesList.push(Number(key))
        }
        // Debug log
        console.log('foodTypePreferences', preferences.foodTypePreferences)
        console.log('exercisePreferences', preferences.exercisePreferences)
        // 1. 註冊（只送 user 基本資料）
        const userPayload = {
          name: registrationData.value.name,
          email: registrationData.value.email,
          password: registrationData.value.password,
          weight: registrationData.value.weight,
          budget: budget.value,
          weekcalorielimit: calorieLimit.value
        }
        let userId = null
        try {
          const signupRes = await api.post('/api/auth/signup', userPayload)
          userId = signupRes.data.user_id
          if (!userId) {
            ElMessage.error('註冊失敗，未取得 user_id，請稍後再試')
            isLoading.value = false
            return
          }
        } catch (error) {
          if (error.response && error.response.status === 409) {
            ElMessage.warning('這個電子郵件已經註冊過，請直接登入')
            isLoading.value = false
            return
          }
          ElMessage.error('註冊失敗，請稍後再試')
          isLoading.value = false
          return
        }
        // 2. 送偏好（只要註冊成功且 user_id 存在才送）
        try {
          await api.post('/api/preferences/user/food-preferences', { user_id: userId, food_types: Food_PreferencesList })
          await api.post('/api/preferences/user/exercise-preferences', { user_id: userId, exercise_names: exercisePreferencesList })
          await api.post('/api/preferences/user/restaurant-preferences', { user_id: userId, restaurant_ids: restaurantPreferencesList })
        } catch (error) {
          ElMessage.error('偏好設定失敗，請稍後再試')
          isLoading.value = false
          return
        }
        // 清除臨時數據
        sessionStorage.removeItem('registrationData')
        // 顯示成功訊息
        ElMessage.success('註冊成功！')
        setTimeout(() => {
          isLoading.value = false
          router.push('/dashboard')
        }, 1000)
      } catch (error) {
        isLoading.value = false
        ElMessage.error('註冊或偏好設定失敗，請稍後再試')
      }
  }
    
    // 返回上一頁
const goBack = () => {
  router.push('/register')
}

const authError = computed(() => localError.value || authStore.error)
const registrationDataComputed = computed(() => registrationData.value)
</script>

<style scoped>
.preferences-page {
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
  font-size: 2.4rem;
  letter-spacing: -0.5px;
}

.auth-header p {
  color: #f08c00;
  font-weight: 600;
  font-size: 1.2rem;
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

/* 卡片式偏好區塊 */
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
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

/* 改進表單元素 */
.el-form-item {
  margin-bottom: 24px;
}

.form-hint {
  font-size: 13px;
  color: #909399;
  margin: 4px 0 10px;
}

.budget-input, .calorie-input {
  width: 100%;
  max-width: 300px;
}

/* 精美的複選框群組 */
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.restaurant-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
  justify-content: space-between;
  margin-top: 30px;
}

.back-button {
  font-weight: 500;
  border-radius: 8px;
  padding: 10px 20px;
  transition: all 0.2s ease;
}

.back-button:hover {
  background-color: #f0f0f0;
  transform: translateX(-2px);
}

.submit-button {
  background: linear-gradient(135deg, #f08c00 0%, #ffb347 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  padding: 10px 32px;
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(240, 140, 0, 0.25);
  transition: all 0.3s ease;
}

.submit-button:hover {
  box-shadow: 0 6px 16px rgba(240, 140, 0, 0.35);
  transform: translateY(-2px);
}

.submit-button i {
  margin-right: 6px;
}

/* 載入狀態優化 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-container .el-icon {
  font-size: 64px;
  color: #f08c00;
  margin-bottom: 24px;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.05); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

.loading-container p {
  color: #606266;
  font-size: 18px;
  font-weight: 500;
}

/* 響應式調整 */
@media (max-width: 600px) {
  .preferences-page {
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
  
  .button-group {
    gap: 10px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .back-button, .submit-button {
    width: 100%;
  }
  
  .progress-steps::before {
    left: 15%;
    right: 15%;
  }
}

/* 全域 CSS 樣式，影響所有 checkbox */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #f08c00 !important;
  border-color: #f08c00 !important;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #f08c00 !important;
}

:deep(.el-checkbox__input.is-focus .el-checkbox__inner) {
  border-color: #f08c00 !important;
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