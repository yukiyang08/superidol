<template>
  <div class="basic-info-page">
    <el-card class="profile-card">
      <div class="profile-header">
        <h2>
          <el-icon style="color:#4a4a4a;margin-right:8px"><User /></el-icon>
          個人基本資料
        </h2>
        <el-button
          v-if="!isEditing"
          type="warning"
          :icon="Edit"
          @click="startEdit"
          class="edit-btn"
        >編輯</el-button>
      </div>

      <div class="profile-hero">
        <div class="hero-avatar">{{ profileInitial }}</div>
        <div class="hero-content">
          <div class="hero-name">{{ profile.name || '未設定姓名' }}</div>
          <div class="hero-email">{{ profile.email || '未設定電子郵件' }}</div>
        </div>
        <div class="hero-stats">
          <div class="hero-stat">
            <span class="stat-label">每餐預算</span>
            <strong class="stat-value">{{ formatValue(profile.budget, '元') }}</strong>
          </div>
          <div class="hero-stat">
            <span class="stat-label">每週熱量</span>
            <strong class="stat-value">{{ formatValue(profile.weekcalorielimit, 'kcal') }}</strong>
          </div>
          <div class="hero-stat">
            <span class="stat-label">體重</span>
            <strong class="stat-value">{{ formatValue(profile.weight, 'kg') }}</strong>
          </div>
        </div>
      </div>
      <el-divider />
      <!-- 檢視模式 -->
      <template v-if="!isEditing">
        <div class="preference-view">
          <div class="pref-block">
            <span class="pref-title">食物偏好：</span>
            <el-tag
              v-for="type in selectedFoodTypes"
              :key="type"
              class="pref-tag food-tag"
              effect="dark"
              style="background:#fff9e6;color:#b8860b;border-color:#f0c040"
            >
              <span class="food-icon">{{ getFoodIcon(type) }}</span>
              {{ type }}
            </el-tag>
            <span v-if="!selectedFoodTypes.length" class="pref-empty">無</span>
              </div>
          <div class="pref-block">
            <span class="pref-title">運動偏好：</span>
            <el-tag
              v-for="item in selectedExerciseNames"
              :key="item"
              class="pref-tag exercise-tag"
              effect="dark"
              style="background:#fff9e6;color:#b8860b;border-color:#f0c040"
            >
              <span class="exercise-icon">{{ getExerciseIcon(item) }}</span>
              {{ item }}
              <span class="intensity-indicator">{{ getExerciseIntensity(item) }}</span>
            </el-tag>
            <span v-if="!selectedExerciseNames.length" class="pref-empty">無</span>
          </div>
          <div class="pref-block">
            <span class="pref-title">餐廳偏好：</span>
            <div class="restaurant-grid view-mode">
              <div 
              v-for="id in selectedRestaurantIds"
              :key="id"
                class="restaurant-card"
                :class="{ active: true }"
              >
                <div class="restaurant-icon-container" :style="{ backgroundImage: getRestaurantImage(id) }">
                  <span v-if="!hasRestaurantLogo(id)" class="restaurant-icon-large">{{ getRestaurantIcon(id) }}</span>
                </div>
                <div class="restaurant-details">
                  <div class="restaurant-name">{{ getRestaurantName(id) }}</div>
                  <div class="restaurant-type" v-if="getRestaurantType(id)">
                    {{ getRestaurantType(id) }}
                  </div>
                </div>
              </div>
              <div v-if="!selectedRestaurantIds.length" class="pref-empty">無</div>
            </div>
          </div>
            </div>
      </template>
      <!-- 編輯模式 -->
      <template v-else>
        <el-form :model="editProfile" label-width="110px" class="profile-form">
          <el-form-item label="姓名">
            <el-input v-model="editProfile.name" />
          </el-form-item>
          <el-form-item label="電子郵件">
            <el-input v-model="editProfile.email" />
          </el-form-item>
          <el-form-item label="每餐預算">
            <el-input-number v-model="editProfile.budget" :min="0" />
          </el-form-item>
          <el-form-item label="每週熱量限制">
            <div class="calorie-input-group">
            <el-input-number v-model="editProfile.weekcalorielimit" :min="0" />
              <el-tooltip content="點擊查看熱量計算說明" placement="top">
                <el-button 
                  type="warning"
                  class="help-btn"
                  @click="showCalorieHelp"
                  :icon="QuestionFilled"
                >
                  計算說明
                </el-button>
              </el-tooltip>
            </div>
          </el-form-item>
          <el-form-item label="體重">
            <el-input-number v-model="editProfile.weight" :min="0" />
          </el-form-item>
        </el-form>
        <el-divider />
        <section class="preference-section">
          <div class="preference-header">
            <h3 style="color:#4a4a4a">食物偏好</h3>
            <span class="preference-subtitle">選擇您喜愛的食物類型</span>
            <span class="preference-count">已選 {{ editSelectedFoodTypes.length }} 項</span>
          </div>
          <div class="food-grid">
            <div 
              v-for="type in foodTypes" 
              :key="type.name" 
              class="food-card"
              :class="{ active: editSelectedFoodTypes.includes(type.name) }"
              @click="toggleFood(type.name)"
            >
              <div class="food-icon-container">
                <span class="food-icon-large">{{ getFoodIcon(type.name) }}</span>
              </div>
              <div class="food-name">{{ type.name }}</div>
            </div>
          </div>
        </section>
        <section class="preference-section">
          <div class="preference-header">
            <h3 style="color:#4a4a4a">運動偏好</h3>
            <span class="preference-subtitle">選擇您喜愛的運動項目</span>
            <span class="preference-count">已選 {{ editSelectedExerciseNames.length }} 項</span>
          </div>
          <div class="exercise-grid">
            <div 
              v-for="item in exerciseItems" 
              :key="item.name" 
              class="exercise-card"
              :class="{ active: editSelectedExerciseNames.includes(item.name) }"
              @click="toggleExercise(item.name)"
            >
              <div class="exercise-icon-container">
                <span class="exercise-icon-large">{{ getExerciseIcon(item.name) }}</span>
              </div>
              <div class="exercise-info">
                <div class="exercise-name">{{ item.name }}</div>
                <div class="exercise-intensity">
                  <span class="flame-indicator">{{ getIntensityFlames(item.name) }}</span>
                  <span class="intensity-value">強度: {{ getExerciseIntensity(item.name) }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section class="preference-section">
          <div class="preference-header">
            <h3 style="color:#4a4a4a">餐廳偏好</h3>
            <span class="preference-subtitle">選擇您喜愛的餐廳</span>
            <span class="preference-count">已選 {{ editSelectedRestaurantIds.length }} 間</span>
          </div>
          <div class="restaurant-grid">
            <div 
              v-for="r in restaurants" 
              :key="r.id" 
              class="restaurant-card"
              :class="{ active: editSelectedRestaurantIds.includes(r.id) }"
              @click="toggleRestaurant(r.id)"
            >
              <div class="restaurant-icon-container" :style="{ backgroundImage: getRestaurantImage(r.id) }">
                <span v-if="!hasRestaurantLogo(r.id)" class="restaurant-icon-large">{{ getRestaurantIcon(r.id) }}</span>
              </div>
              <div class="restaurant-details">
                <div class="restaurant-name">{{ r.name }}</div>
                <div class="restaurant-type" v-if="getRestaurantType(r.id)">
                  {{ getRestaurantType(r.id) }}
                </div>
              </div>
            </div>
          </div>
        </section>
        <div class="form-actions">
          <el-button type="warning" :loading="isLoading" @click="saveEdit" class="save-btn">儲存</el-button>
          <el-button @click="cancelEdit">取消</el-button>
      </div>
      </template>
      <el-loading v-if="isLoading" lock text="載入中..." />
      <el-dialog
        v-model="calorieHelpVisible"
        title="每週熱量限制計算說明"
        width="500px"
        class="calorie-help-dialog"
      >
        <div class="calorie-help-content">
          <h4>如何計算您的每週熱量限制？</h4>
          <p>我們建議您根據以下因素來設定：</p>
          <ul>
            <li>基礎代謝率 (BMR)</li>
            <li>日常活動量</li>
            <li>運動習慣</li>
            <li>健康目標（減重/維持/增重）</li>
          </ul>
          
          <div class="calorie-calculator">
            <h4>快速計算器</h4>
            <el-form :model="calorieCalc" label-width="80px">
              <el-form-item label="性別">
                <el-radio-group v-model="calorieCalc.gender">
                  <el-radio label="male">男</el-radio>
                  <el-radio label="female">女</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="年齡">
                <el-input-number v-model="calorieCalc.age" :min="18" :max="100" />
              </el-form-item>
              <el-form-item label="身高(cm)">
                <el-input-number v-model="calorieCalc.height" :min="100" :max="250" />
              </el-form-item>
              <el-form-item label="活動量">
                <el-select v-model="calorieCalc.activityLevel">
                  <el-option label="久坐不動" value="sedentary" />
                  <el-option label="輕度活動" value="light" />
                  <el-option label="中度活動" value="moderate" />
                  <el-option label="重度活動" value="very" />
                  <el-option label="極度活動" value="extra" />
                </el-select>
              </el-form-item>
              <el-form-item label="目標">
                <el-select v-model="calorieCalc.goal">
                  <el-option label="減重" value="lose" />
                  <el-option label="維持體重" value="maintain" />
                  <el-option label="增重" value="gain" />
                </el-select>
              </el-form-item>
            </el-form>
            
            <div class="calorie-result">
              <h4>建議每週熱量限制</h4>
              <div class="result-value">{{ calculateCalories }} 大卡</div>
              <el-button 
                type="warning" 
                @click="applyCalorieSuggestion"
                :loading="isLoading"
              >
                套用建議值
              </el-button>
            </div>
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Edit, QuestionFilled } from '@element-plus/icons-vue'
import api from '@/services/api'

// 狀態
const profile = ref({
      name: '',
      email: '',
      budget: null,
      weekcalorielimit: null,
      weight: null
    })
    const isLoading = ref(false)
    const isEditing = ref(false)
    const errorMsg = ref('')
    // 偏好選項
    const foodTypes = ref([])
    const exerciseItems = ref([])
    const restaurants = ref([])
    // 使用者已選偏好
    const selectedFoodTypes = ref([])
    const selectedExerciseNames = ref([])
    const selectedRestaurantIds = ref([])
    // 編輯用暫存
    const editProfile = reactive({
      name: '',
      email: '',
      budget: null,
      weekcalorielimit: null,
      weight: null
    })
    const editSelectedFoodTypes = ref([])
    const editSelectedExerciseNames = ref([])
    const editSelectedRestaurantIds = ref([])
    const calorieHelpVisible = ref(false)
    const calorieCalc = reactive({
      gender: 'male',
      age: 25,
      height: 170,
      activityLevel: 'moderate',
      goal: 'maintain'
    })

    const profileInitial = computed(() => {
      const name = (profile.value.name || '').trim()
      return name ? name.charAt(0).toUpperCase() : 'U'
    })

    const formatValue = (value, unit = '') => {
      if (value === null || value === undefined || value === '') return '未設定'
      return unit ? `${value} ${unit}` : String(value)
    }

    // 為每種運動類型提供對應的圖示
    const getExerciseIcon = (exerciseName) => {
      const iconMap = {
        '伏地挺身': '💪',
        '划船': '🚣',
        '太極': '🧘',
        '快走': '🚶',
        '慢走': '🚶‍♀️',
        '攀岩': '🧗',
        '游泳': '🏊',
        '爬山': '🏔️',
        '瑜珈': '🧘‍♀️',
        '籃球': '🏀',
        '足球': '⚽',
        '跑步(10km/hr)': '🏃',
        '跑步(8km/hr)': '🏃‍♀️',
        '騎腳踏車': '🚲'
      }
      return iconMap[exerciseName] || '🏋️'
    }

    const EXERCISE_MET = {
      '伏地挺身': 5, '划船': 7, '太極': 4, '快走': 4, '慢走': 3,
      '攀岩': 8, '游泳': 7, '爬山': 6, '瑜珈': 5, '籃球': 7,
      '足球': 7, '跑步(10km/hr)': 10, '跑步(8km/hr)': 8, '騎腳踏車': 6
    }
    const getExerciseMET = (name) => EXERCISE_MET[name] || 0

    const getExerciseIntensity = (name) => {
      const met = getExerciseMET(name)
      if (met <= 3) return '輕度'
      if (met <= 6) return '中度'
      return '高度'
    }

    const getIntensityFlames = (name) => {
      const met = getExerciseMET(name)
      if (met <= 0) return ''
      if (met <= 3) return '🔥'
      if (met <= 6) return '🔥🔥'
      if (met <= 8) return '🔥🔥🔥'
      return '🔥🔥🔥🔥'
    }
    
    const toggleItem = (arr, val) => {
      const i = arr.value.indexOf(val)
      i === -1 ? arr.value.push(val) : arr.value.splice(i, 1)
    }

    const toggleExercise = (name) => toggleItem(editSelectedExerciseNames, name)

    // 載入所有可選項目
    const fetchOptions = async () => {
      try {
      const [foodRes, exerciseRes, restaurantRes] = await Promise.all([
          api.get('/api/preferences/food-types'),
          api.get('/api/preferences/exercise-items'),
          api.get('/api/preferences/restaurants')
      ])
        foodTypes.value = foodRes.data || []
        exerciseItems.value = exerciseRes.data || []
        restaurants.value = restaurantRes.data || []
      } catch (error) {
        console.error('載入選項失敗:', error)
        errorMsg.value = '載入選項失敗，請重新整理頁面'
      }
    }

    // 載入目前使用者偏好
    const fetchUserPreferences = async (userId) => {
      try {
        const [foodPref, exercisePref, restaurantPref] = await Promise.all([
          api.get('/api/preferences/user/food-preferences', { params: { user_id: userId } }),
          api.get('/api/preferences/user/exercise-preferences', { params: { user_id: userId } }),
          api.get('/api/preferences/user/restaurant-preferences', { params: { user_id: userId } })
        ])
        selectedFoodTypes.value = foodPref.data.food_types || []
        selectedExerciseNames.value = exercisePref.data.exercise_names || []
        selectedRestaurantIds.value = restaurantPref.data.restaurant_ids || []
      } catch (err) {
        console.error('載入用戶偏好失敗:', err)
        // 若查無偏好可忽略
      }
    }
    
    // 載入個人資料
    const fetchProfile = async () => {
      isLoading.value = true
      errorMsg.value = ''
      try {
        const res = await api.get('/api/auth/user')
        profile.value.name = res.data.name
        profile.value.email = res.data.email
        profile.value.budget = res.data.budget
        profile.value.weekcalorielimit = res.data.weekCalorieLimit
        profile.value.weight = res.data.weight
      } catch (err) {
        errorMsg.value = err.response?.data?.error || '載入個人資料失敗'
      } finally {
        isLoading.value = false
      }
    }

    // 進入編輯模式
    const startEdit = () => {
      editProfile.name = profile.value.name
      editProfile.email = profile.value.email
      editProfile.budget = profile.value.budget
      editProfile.weekcalorielimit = profile.value.weekcalorielimit
      editProfile.weight = profile.value.weight
      editSelectedFoodTypes.value = [...selectedFoodTypes.value]
      editSelectedExerciseNames.value = [...selectedExerciseNames.value]
      editSelectedRestaurantIds.value = [...selectedRestaurantIds.value]
      isEditing.value = true
    }

    // 儲存編輯
    const saveEdit = async () => {
      isLoading.value = true
      errorMsg.value = ''
      try {
        const userId = Number(localStorage.getItem('userId'))
        if (!userId) {
          errorMsg.value = '找不到使用者 ID，請重新登入'
          return
        }
        await api.put('/api/auth/profile', {
          name: editProfile.name,
          email: editProfile.email,
          budget: editProfile.budget,
          weekcalorielimit: editProfile.weekcalorielimit,
          weight: editProfile.weight
        })
        await Promise.all([
          api.post('/api/preferences/user/food-preferences', {
            user_id: userId,
            food_types: editSelectedFoodTypes.value
          }),
          api.post('/api/preferences/user/exercise-preferences', {
            user_id: userId,
            exercise_names: editSelectedExerciseNames.value
          }),
          api.post('/api/preferences/user/restaurant-preferences', {
            user_id: userId,
            restaurant_ids: editSelectedRestaurantIds.value.map(Number)
          })
        ])
        profile.value.name = editProfile.name
        profile.value.email = editProfile.email
        profile.value.budget = editProfile.budget
        profile.value.weekcalorielimit = editProfile.weekcalorielimit
        profile.value.weight = editProfile.weight
        selectedFoodTypes.value = [...editSelectedFoodTypes.value]
        selectedExerciseNames.value = [...editSelectedExerciseNames.value]
        selectedRestaurantIds.value = [...editSelectedRestaurantIds.value]
        isEditing.value = false
        showNotification('個人偏好已成功更新！')
      } catch (err) {
        errorMsg.value = err.response?.data?.error || '儲存失敗'
        showNotification(errorMsg.value, 'error')
      } finally {
        isLoading.value = false
      }
    }

    // 取消編輯
    const cancelEdit = () => {
      isEditing.value = false
      errorMsg.value = ''
    }

    // 餐廳名稱查找
    const getRestaurantName = (id) => {
      const r = restaurants.value.find(r => r.id === id)
      return r ? r.name : id
    }

    // 為食物類型提供對應的圖標
    const getFoodIcon = (foodType) => {
      const iconMap = {
        '中式': '🥢',
        '日式': '🍱',
        '美式': '🍔',
        '義式': '🍝',
        '泰式': '🍲',
        '素食': '🥗',
        '海鮮': '🦞',
        '燒烤': '🍖',
        '甜點': '🍰',
        '飲料': '🥤',
        '麵食': '🍜',
        '韓式': '🍚',
        '餃子': '🥟',
        '火鍋': '🍲'
      }
      return iconMap[foodType] || '🍽️'
    }

    // 改進餐廳圖標函數
    const getRestaurantIcon = (restaurantId) => {
      const iconMap = {
        1: '🧋', // 50嵐
        2: '🍔', // 麥當勞
        4: '🍔', // 摩斯
        5: '🧋'  // 迷克夏
      }
      
      // 根據餐廳類型提供默認圖標
      if (!iconMap[restaurantId]) {
        const type = getRestaurantType(restaurantId)
        if (type === '手搖') return '🧋'
        if (type === '速食') return '🍔'
        if (type === '咖啡') return '☕'
        if (type === '餐廳') return '🍽️'
      }
      
      return iconMap[restaurantId] || '🏠'
    }

    // 獲取餐廳類型
    const getRestaurantType = (restaurantId) => {
      const typeMap = {
        1: '手搖',
        2: '速食',
        4: '速食',
        5: '手搖'
      }
      return typeMap[restaurantId] || ''
    }

    const toggleFood       = (name) => toggleItem(editSelectedFoodTypes, name)
    const toggleRestaurant = (id)   => toggleItem(editSelectedRestaurantIds, id)

    const showNotification = (message, type = 'success') => {
      ElMessage({
        message,
        type,
        duration: type === 'error' ? 5000 : 3000,
        showClose: true
      })
    }

    // 獲取餐廳圖片背景
    const getRestaurantImage = (restaurantId) => {
      // 根據餐廳ID映射到具體的文件名
      const imageMap = {
        1: '/img/logos/restaurant-1.png', // 50嵐
        2: '/img/logos/restaurant-2.jpg', // 麥當勞
        4: '/img/logos/restaurant-4.png', // 摩斯
        5: '/img/logos/restaurant-5.png' // 迷克夏
      };
      
      return imageMap[restaurantId] ? `url("${imageMap[restaurantId]}")` : '';
    }

    // 判斷是否有餐廳LOGO
    const hasRestaurantLogo = (restaurantId) => {
      // 目前只有這四家餐廳有logo
      return [1, 2, 4, 5].includes(Number(restaurantId));
    }

    const showCalorieHelp = () => {
      calorieHelpVisible.value = true
    }
    
    const calculateCalories = computed(() => {
      // 使用Harris-Benedict公式計算BMR
      let bmr = 0
      if (calorieCalc.gender === 'male') {
        bmr = 66 + (13.7 * editProfile.weight) + (5 * calorieCalc.height) - (6.8 * calorieCalc.age)
      } else {
        bmr = 655 + (9.6 * editProfile.weight) + (1.8 * calorieCalc.height) - (4.7 * calorieCalc.age)
      }
      
      // 根據活動量調整
      const activityMultipliers = {
        sedentary: 1.2,
        light: 1.375,
        moderate: 1.55,
        very: 1.725,
        extra: 1.9
      }
      
      let tdee = bmr * activityMultipliers[calorieCalc.activityLevel]
      
      // 根據目標調整
      const goalAdjustments = {
        lose: 0.85,
        maintain: 1,
        gain: 1.15
      }
      
      tdee = tdee * goalAdjustments[calorieCalc.goal]
      
      // 轉換為每週熱量
      return Math.round(tdee * 7)
    })
    
    const applyCalorieSuggestion = () => {
      if (calculateCalories.value) {
        editProfile.weekcalorielimit = calculateCalories.value
        showNotification('已套用建議的熱量限制！')
        calorieHelpVisible.value = false
      }
    }

onMounted(async () => {
  const userId = Number(localStorage.getItem('userId'))
  await Promise.all([fetchOptions(), fetchProfile()])
  if (userId) await fetchUserPreferences(userId)
})
</script>

<style scoped>
.basic-info-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 0;
  background: linear-gradient(135deg, #f7f9fc 0%, #edf1f7 100%);
  min-height: calc(100vh - 60px);
  font-family: var(--font-tc), 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', sans-serif;
}
.profile-card {
  width: 100%;
  max-width: 700px;
  border-radius: var(--surface-radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  padding: 32px 24px 24px 24px;
  border: 1px solid #eceff3;
  background: #fff;
  transition: all 0.3s ease;
}
.profile-card,
.profile-card * {
  font-family: inherit;
}
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.profile-header h2 {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
  color: #333;
  margin: 0;
  letter-spacing: 0.01em;
}
.profile-header h2 i {
  color: #4a4a4a;
  margin-right: 10px;
}
.edit-btn, .save-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600;
  padding: 10px 24px;
  border-radius: var(--btn-radius);
  box-shadow: var(--shadow-button);
  transition: all 0.3s ease;
}
.edit-btn:hover, .save-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}
.profile-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff8e8 0%, #fff4d2 100%);
  border: 1px solid #f5e5b8;
}
.hero-avatar {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #8a5f09;
  background: #ffe8ab;
  box-shadow: 0 6px 18px rgba(138, 95, 9, 0.18);
}
.hero-content {
  min-width: 0;
}
.hero-name {
  font-size: 17px;
  font-weight: 700;
  color: #2f2f2f;
  line-height: 1.2;
  letter-spacing: 0.01em;
}
.hero-email {
  margin-top: 4px;
  color: #686868;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}
.hero-stats {
  margin-left: auto;
  display: flex;
  gap: 10px;
}
.hero-stat {
  min-width: 108px;
  border-radius: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(212, 172, 73, 0.2);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.stat-label {
  font-size: 12px;
  color: #85642b;
}
.stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #47340f;
}
.preference-view,
.preference-section {
  margin: 24px 0 0 0;
  padding: 18px 0 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  border: 0;
  border-top: 1px solid #eef1f5;
}
.preference-view {
  padding-top: 0;
  border-top: 0;
}
.preference-header {
  margin-bottom: 14px;
  font-weight: 600;
  color: #333;
  display: flex;
  flex-direction: column;
}
.preference-count {
  display: inline-flex;
  width: fit-content;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #7a5b1c;
  background: #fff2c8;
  border: 1px solid #f0d385;
  border-radius: 999px;
  padding: 4px 10px;
}
.preference-header h3 {
  color: #4a4a4a;
  margin: 0 0 6px 0;
  letter-spacing: 0.01em;
}
.preference-subtitle {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
  font-weight: normal;
}
.pref-block {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
}
.pref-title {
  font-weight: 600;
  color: #4a4a4a;
  margin-right: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  flex-basis: 100px;
}
.pref-tag {
  margin-right: 10px;
  margin-bottom: 10px;
  font-size: 14px;
  border-radius: 8px;
  padding: 8px 16px;
  background: #f5f5f5;
  color: #4a4a4a;
  border: 1px solid rgba(74, 74, 74, 0.2);
  display: flex;
  align-items: center;
  box-shadow: none;
}
.pref-empty {
  color: #999;
  font-style: italic;
  background: #f5f5f5;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px dashed rgba(74, 74, 74, 0.2);
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
}
.form-actions :deep(.el-button) {
  min-height: 40px;
  padding-inline: 20px;
  border-radius: 12px;
  font-weight: 600;
}

/* 運動偏好卡片樣式 */
.exercise-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 20px;
}
.exercise-card {
  padding: 14px 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
  border: 1px solid #e4e9f1;
  box-shadow: none;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.exercise-card:hover {
  transform: translateY(-2px);
  border-color: #c8d2df;
  background: #ffffff;
}
.exercise-card.active {
  box-shadow: none;
  background: linear-gradient(180deg, #fff8e8 0%, #fff3d5 100%);
  border: 1px solid #c78f2a;
}
.exercise-icon-container {
  width: 50px;
  height: 50px;
  border-radius: 16px;
  background: #f2f5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;
}
.exercise-card.active .exercise-icon-container {
  background: linear-gradient(135deg, #f4ca72 0%, #e7b14b 100%);
  color: #5c3f08;
  box-shadow: 0 6px 18px rgba(219, 168, 63, 0.28);
}
.exercise-name {
  font-weight: 600;
  margin-bottom: 8px;
  color: #2f2f2f;
}
.exercise-intensity {
  font-size: 12px;
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.flame-indicator {
  margin-bottom: 6px;
  letter-spacing: -3px;
}
.intensity-value {
  font-weight: 500;
}
.exercise-icon {
  margin-right: 8px;
  font-size: 16px;
}
.intensity-indicator {
  margin-left: 6px;
  font-size: 12px;
  background: rgba(74, 74, 74, 0.1);
  border-radius: 6px;
  padding: 2px 8px;
  color: #4a4a4a;
}

/* 食物偏好卡片樣式 */
.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
  margin-top: 20px;
}
.food-card {
  padding: 14px 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
  border: 1px solid #e4e9f1;
  box-shadow: none;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.food-card:hover {
  transform: translateY(-2px);
  border-color: #c8d2df;
  background: #ffffff;
}
.food-card.active {
  box-shadow: none;
  background: linear-gradient(180deg, #fff8e8 0%, #fff3d5 100%);
  border: 1px solid #c78f2a;
}
.food-icon-container {
  width: 50px;
  height: 50px;
  border-radius: 14px;
  background: #f2f5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s;
}
.food-card.active .food-icon-container {
  background: linear-gradient(135deg, #f4ca72 0%, #e7b14b 100%);
  color: #5c3f08;
  box-shadow: 0 6px 18px rgba(219, 168, 63, 0.28);
}
.food-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  line-height: 1.3;
  word-break: break-word;
}

/* 餐廳偏好卡片樣式 */
.restaurant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.restaurant-grid.view-mode {
  margin-top: 10px;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.restaurant-grid.view-mode .restaurant-card {
  margin-bottom: 0;
  cursor: default;
  box-shadow: none;
  height: 130px;
  background: #fafbfd;
  border: 1px solid #eceff3;
  position: relative;
}
.restaurant-grid.view-mode .restaurant-icon-container {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-size: contain !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}
.restaurant-grid.view-mode .restaurant-icon-large {
  display: none;
}
.restaurant-grid.view-mode .restaurant-name {
  color: #4a4a4a;
}
.restaurant-grid.view-mode .restaurant-type {
  background: rgba(74, 74, 74, 0.1);
  color: #4a4a4a;
}
.restaurant-card {
  position: relative;
  padding: 16px 12px;
  border-radius: 12px;
  background: white;
  border: 1px solid #eceff3;
  box-shadow: none;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 140px;
}
.restaurant-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
}
.restaurant-card.active {
  box-shadow: none;
  background: #fbfbfc;
  border: 1px solid #4a4a4a;
}
.restaurant-icon-container {
  width: 70px;
  height: 70px;
  border-radius: 14px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  overflow: hidden;
}
.restaurant-card.active .restaurant-icon-container {
  box-shadow: 0 6px 18px rgba(74, 74, 74, 0.15);
}
.restaurant-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  flex: 1;
}
.restaurant-name {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

:deep(.el-form-item__label),
:deep(.el-input__inner),
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase),
:deep(.el-select__placeholder),
:deep(.el-select__selected-item),
:deep(.el-button),
:deep(.el-tag),
:deep(.el-radio__label),
:deep(.el-dialog__title),
:deep(.el-descriptions-item__label),
:deep(.el-descriptions-item__content) {
  font-family: inherit !important;
}
.restaurant-type {
  font-size: 12px;
  color: #4a4a4a;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(74, 74, 74, 0.1);
  border-radius: 12px;
  padding: 2px 8px;
  margin: 0 auto;
  width: fit-content;
}
.restaurant-tag {
  position: relative;
  padding: 6px 14px 6px 10px;
  margin-bottom: 10px;
}
.restaurant-type-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(255,255,255,0.9);
  color: #333;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

/* 新增的餐廳品牌標誌文字樣式 */
.restaurant-brand-initial {
  font-size: 26px;
  font-weight: bold;
  color: #4a4a4a;
  text-shadow: none;
}

/* 描述列表樣式優化 */
:deep(.el-descriptions) {
  padding: 0;
  border-radius: 10px;
}
:deep(.el-descriptions__body) {
  background-color: transparent;
  border-radius: 10px;
}
:deep(.el-descriptions-item__label) {
  color: #555;
  font-weight: 600;
  background-color: transparent;
  width: 140px;
}
:deep(.el-descriptions-item__content) {
  color: #2f2f2f;
  font-weight: 500;
}
:deep(.el-divider) {
  margin: 24px 0;
}

/* 響應式設計優化 */
@media (max-width: 1200px) {
  .exercise-grid,
  .restaurant-grid.view-mode {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 900px) {
  .exercise-grid,
  .restaurant-grid.view-mode {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .exercise-grid,
  .restaurant-grid.view-mode {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 700px) {
  .profile-card { 
    padding: 20px 16px; 
    margin: 0 16px;
  }
  .profile-header {
    flex-wrap: wrap;
    gap: 10px;
  }
  .profile-hero {
    flex-wrap: wrap;
    gap: 12px;
  }
  .hero-email {
    max-width: 100%;
  }
  .hero-stats {
    width: 100%;
    margin-left: 0;
    flex-wrap: wrap;
  }
  .hero-stat {
    flex: 1;
    min-width: 100px;
  }
  .food-grid, .restaurant-grid {
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 12px;
  }
  .food-icon-container, .restaurant-icon-container {
    width: 45px;
    height: 45px;
    font-size: 20px;
  }
  .food-name, .restaurant-name {
    font-size: 13px;
  }
}
.calorie-input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.help-btn {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.25);
  transition: all 0.3s ease;
}
.help-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4);
}
.help-btn i {
  margin-right: 4px;
}
.calorie-help-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}
.calorie-help-content {
  color: #333;
}
.calorie-help-content h4 {
  margin: 16px 0 12px;
  color: #4a4a4a;
}
.calorie-help-content p {
  margin: 12px 0;
  line-height: 1.6;
}
.calorie-help-content ul {
  margin: 12px 0;
  padding-left: 20px;
}
.calorie-help-content li {
  margin: 8px 0;
  line-height: 1.5;
}
.calorie-calculator {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}
.calorie-result {
  margin-top: 20px;
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.result-value {
  font-size: 24px;
  font-weight: bold;
  color: #ff9800;
  margin: 12px 0;
}
</style> 