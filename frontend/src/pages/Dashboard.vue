<template>
  <div class="dashboard">
    <div class="container">
      <h1 class="page-title">儀表板</h1>
      
      <div class="welcome-card card">
        <template v-if="isLoading && !hasLoaded">
          <div class="skeleton-line skeleton-title"></div>
          <div class="skeleton-line skeleton-subtitle"></div>
        </template>
        <template v-else>
          <h2>歡迎回來，{{ user.name }}</h2>
          <p>今天是 {{ currentDate }}，這是您的健康飲食摘要</p>
        </template>
      </div>
      
      <div v-if="isLoading && !hasLoaded" class="dashboard-grid">
        <div v-for="index in 4" :key="index" class="card dashboard-card skeleton-card">
          <div class="dashboard-card-title-skeleton"></div>
          <div class="card-content">
            <div class="skeleton-line skeleton-block"></div>
            <div class="skeleton-line skeleton-block short"></div>
            <div class="skeleton-line skeleton-block medium"></div>
          </div>
        </div>
      </div>

      <div v-else class="dashboard-grid">
        <!-- 卡路里摘要卡片 -->
        <div class="card dashboard-card">
          <h3>今日熱量</h3>
          <div class="card-content">
            <div class="calorie-info">
              <div class="calorie-consumed">
                <span class="value">{{ todaySummary.caloriesConsumed }}</span>
                <span class="label">已攝取</span>
              </div>
              <div class="calorie-target">
                <span class="value">{{ userGoals.dailyCalories }}</span>
                <span class="label">目標</span>
              </div>
              <div class="calorie-remaining">
                <span class="value">{{ caloriesRemaining }}</span>
                <span class="label">剩餘</span>
              </div>
            </div>
            <div class="progress-container">
              <div 
                class="progress-bar" 
                :style="{ width: calorieProgressPercentage + '%' }"
                :class="{ 'exceed': calorieProgressPercentage > 100 }"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- 營養素摘要卡片 -->
        <div class="card dashboard-card">
          <h3>營養素攝取</h3>
          <div class="card-content">
            <div class="nutrient-grid">
              <div class="nutrient-item">
                <span class="nutrient-value">{{ formatNutrient(todaySummary.protein) }}</span>
                <span class="nutrient-label">蛋白質</span>
              </div>
              <div class="nutrient-item">
                <span class="nutrient-value">{{ formatNutrient(todaySummary.carbs) }}</span>
                <span class="nutrient-label">碳水化合物</span>
              </div>
              <div class="nutrient-item">
                <span class="nutrient-value">{{ formatNutrient(todaySummary.fat) }}</span>
                <span class="nutrient-label">脂肪</span>
              </div>
              <div class="nutrient-item">
                <span class="nutrient-value">{{ formatNutrient(todaySummary.sugar) }}</span>
                <span class="nutrient-label">糖</span>
              </div>
            </div>
            <p class="nutrient-note">營養素細項整合中，目前以熱量追蹤為主。</p>
          </div>
        </div>
        
        <!-- 最近食物記錄卡片 -->
        <div class="card dashboard-card">
          <h3>最近食物記錄</h3>
          <div class="card-content">
            <div v-if="recentFoods.length > 0" class="recent-food-list">
              <div v-for="food in recentFoods" :key="food.id" class="recent-food-item">
                <div class="food-info">
                  <span class="food-name">{{ food.name }}</span>
                  <span class="food-calories">{{ food.calories }} 卡路里</span>
                </div>
                <span class="food-time">{{ food.timeLabel }}</span>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>尚未有食物記錄</p>
              <router-link to="/food/search" class="btn btn-primary">添加食物</router-link>
            </div>
          </div>
        </div>
        
        <!-- 運動記錄卡片 -->
        <div class="card dashboard-card">
          <h3>今日運動</h3>
          <div class="card-content">
            <div v-if="todayExercises.length > 0" class="exercise-list">
              <div v-for="exercise in todayExercises" :key="exercise.id" class="exercise-item">
                <div class="exercise-info">
                  <span class="exercise-name">{{ exercise.name }}</span>
                  <span class="exercise-duration">{{ exercise.duration }} 分鐘</span>
                </div>
                <span class="exercise-calories">-{{ exercise.caloriesBurned }} 卡路里</span>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>今天還沒有運動記錄</p>
              <router-link to="/exercise/record" class="btn btn-primary">記錄運動</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const authStore = useAuthStore()
const user = computed(() => authStore.user || {})
const isLoading = ref(false)
const hasLoaded = ref(false)
    
const userGoals = ref({
  dailyCalories: 2000,
  protein: 150,
  carbs: 200,
  fat: 65
})
    
const todaySummary = ref({
  caloriesConsumed: 0,
  protein: null,
  carbs: null,
  fat: null,
  sugar: null
})
    
  const recentFoods = ref([])

  const todayExercises = ref([])
    
// 計算剩餘卡路里
const caloriesRemaining = computed(() => {
  return Math.max(0, userGoals.value.dailyCalories - todaySummary.value.caloriesConsumed)
})
    
// 計算卡路里進度百分比
const calorieProgressPercentage = computed(() => {
  if (!userGoals.value.dailyCalories) return 0
  return Math.min(100, (todaySummary.value.caloriesConsumed / userGoals.value.dailyCalories) * 100)
})
    
// 格式化日期
const currentDate = computed(() => {
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return new Date().toLocaleDateString('zh-TW', options)
})
    
const formatNutrient = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '--'
  return `${Math.round(Number(value))}g`
}

const getTodayString = () => {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const getUserId = () => {
  return user.value?.id || localStorage.getItem('userId')
}

const loadDashboardData = async () => {
  const userId = getUserId()
  if (!userId) return

  isLoading.value = true
  const today = getTodayString()

  try {
    const [summaryResult, foodResult, exerciseResult] = await Promise.allSettled([
      api.get('/api/reports/summary', {
        params: { user_id: userId, report_type: 'daily', start_date: today }
      }),
      api.get('/api/food/record', { params: { user_id: userId } }),
      api.get('/api/exercise/records', {
        params: { user_id: userId, start_date: today, end_date: today }
      })
    ])

    if (summaryResult.status === 'fulfilled') {
      const summaryData = summaryResult.value?.data || {}
      userGoals.value.dailyCalories = summaryData.user_goals?.daily_calories || 2000
      todaySummary.value.caloriesConsumed = summaryData.period_summary?.total_calories_intake || 0
    }

    if (foodResult.status === 'fulfilled') {
      const records = Array.isArray(foodResult.value?.data) ? foodResult.value.data : []
      recentFoods.value = records.slice(0, 3).map((item) => ({
        id: item.record_id,
        name: item.name || '未命名食物',
        calories: Math.round(Number(item.calories || 0)),
        timeLabel: [item.date, item.mealtime].filter(Boolean).join(' ')
      }))
    }

    if (exerciseResult.status === 'fulfilled') {
      const records = Array.isArray(exerciseResult.value?.data?.records)
        ? exerciseResult.value.data.records
        : []
      todayExercises.value = records.slice(0, 3).map((item) => ({
        id: item.RecordID || item.record_id,
        name: item.Exercise_Name || item.exercise_name || '未知運動',
        duration: Math.round(Number(item.Duration || item.duration || 0)),
        caloriesBurned: Math.round(Number(item.calories_burned || 0))
      }))
    }
  } catch (error) {
    console.error('載入 Dashboard 資料失敗:', error)
  } finally {
    isLoading.value = false
    hasLoaded.value = true
  }
}

onMounted(() => {
  loadDashboardData()
})

watch(
  () => user.value?.id,
  (newId) => {
    if (newId && hasLoaded.value) {
      loadDashboardData()
    }
  }
)
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.page-title {
  margin-bottom: 32px;
  font-size: 32px;
  font-weight: 600;
  color: var(--text-color);
  font-family: var(--font-tc), var(--font-en);
  position: relative;
}

.page-title:after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  width: 80px;
  height: 4px;
  background-color: var(--primary-color);
  border-radius: 2px;
}

.welcome-card {
  margin-bottom: 32px;
  padding: 24px 28px;
  border-radius: var(--surface-radius-lg);
  background-color: #fff;
  box-shadow: var(--shadow-card);
  border: none;
}

.welcome-card h2 {
  font-size: 26px;
  margin-bottom: 12px;
  color: var(--primary-color);
  font-family: var(--font-tc), var(--font-en);
  font-weight: 600;
}

.welcome-card p {
  font-family: var(--font-tc), var(--font-en);
  font-size: 16px;
  color: var(--text-light);
  margin: 0;
  line-height: 1.6;
}

.skeleton-line {
  border-radius: 999px;
  background: linear-gradient(90deg, #f1f1f1 0%, #f7f7f7 50%, #f1f1f1 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.2s ease-in-out infinite;
}

.skeleton-title {
  width: 220px;
  height: 28px;
  margin-bottom: 14px;
}

.skeleton-subtitle {
  width: 360px;
  max-width: 100%;
  height: 16px;
}

.skeleton-card {
  pointer-events: none;
}

.dashboard-card-title-skeleton {
  height: 24px;
  width: 120px;
  margin: 20px 24px;
  border-radius: 999px;
  background: linear-gradient(90deg, #f1f1f1 0%, #f7f7f7 50%, #f1f1f1 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.2s ease-in-out infinite;
}

.skeleton-block {
  width: 100%;
  height: 18px;
  margin-bottom: 14px;
}

.skeleton-block.short {
  width: 42%;
}

.skeleton-block.medium {
  width: 68%;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 24px;
}

.card {
  background-color: #fff;
  border-radius: var(--surface-radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  border: none;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-card-hover);
}

.welcome-card {
  background: linear-gradient(135deg, #ff7c1f 0%, #ffaa55 60%, #ffc880 100%);
  padding: 32px;
  color: white;
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: -48px;
  right: -48px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  pointer-events: none;
}

.welcome-card::after {
  content: '';
  position: absolute;
  bottom: -60px;
  left: 20%;
  width: 260px;
  height: 260px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
  pointer-events: none;
}

.welcome-card:hover {
  transform: none;
  box-shadow: var(--shadow-card);
}

.welcome-card h2 {
  font-size: 1.7rem;
  font-weight: 700;
  color: white;
  margin: 0 0 8px;
  font-family: var(--font-tc), var(--font-en);
  position: relative;
  z-index: 1;
}

.welcome-card p {
  color: rgba(255, 255, 255, 0.88);
  font-size: 0.95rem;
  margin: 0;
  font-family: var(--font-tc), var(--font-en);
  position: relative;
  z-index: 1;
}

.welcome-card .skeleton-line {
  background: linear-gradient(90deg, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.32) 50%, rgba(255,255,255,0.18) 100%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.2s ease-in-out infinite;
}

.dashboard-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-card h3 {
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 18px;
  font-family: var(--font-tc), var(--font-en);
  font-weight: 600;
  color: #444;
}

.card-content {
  padding: 20px 24px;
  flex: 1;
}

/* 卡路里卡片樣式 */
.calorie-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.calorie-consumed,
.calorie-target,
.calorie-remaining {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.value {
  font-size: 28px;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  margin-bottom: 6px;
}

.calorie-consumed .value {
  color: var(--primary-color);
}

.calorie-remaining .value {
  color: #4caf50;
}

.label {
  font-size: 14px;
  color: var(--text-light);
  font-family: var(--font-tc), var(--font-en);
}

.progress-container {
  height: 12px;
  background-color: #f0ebe3;
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.06);
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ffaa55 0%, #ff7c1f 100%);
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(255, 124, 31, 0.35);
}

.progress-bar.exceed {
  background-color: #ff6b6b;
}

/* 營養素卡片樣式 */
.nutrient-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 20px;
}

.nutrient-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px;
  border-radius: 12px;
  background-color: #fff8f0;
  border: 1px solid #fde8cc;
}

.nutrient-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
  font-family: 'Poppins', sans-serif;
}

.nutrient-label {
  font-size: 14px;
  color: var(--text-light);
  font-family: var(--font-tc), var(--font-en);
}

.nutrient-note {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-light);
  text-align: center;
}

/* 食物記錄和運動卡片樣式 */
.recent-food-list,
.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-food-item,
.exercise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #fff8f0;
  border: 1px solid #fde8cc;
  border-radius: 10px;
  font-family: 'Nunito Sans', sans-serif;
  transition: background-color 0.2s;
}

.recent-food-item:hover,
.exercise-item:hover {
  background-color: #fff1e0;
}

.food-info,
.exercise-info {
  display: flex;
  flex-direction: column;
}

.food-name,
.exercise-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  color: var(--text-color);
  font-family: var(--font-tc), var(--font-en);
}

.food-calories,
.exercise-duration {
  font-size: 13px;
  color: var(--text-light);
  font-family: var(--font-tc), var(--font-en);
}

.food-time,
.exercise-calories {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 600;
}

.exercise-calories {
  color: #4caf50;
}

/* 空狀態樣式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.empty-state p {
  margin-bottom: 16px;
  color: var(--text-light);
  font-family: var(--font-tc), var(--font-en);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--btn-radius);
  border: none;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--font-tc), var(--font-en);
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
  color: white;
  box-shadow: var(--shadow-button);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}

/* 響應式調整 */
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .value {
    font-size: 24px;
  }
}

@media (max-width: 600px) {
  .page-title {
    font-size: 28px;
  }
  
  .welcome-card h2 {
    font-size: 22px;
  }
  
  .calorie-info {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }
  
  .nutrient-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style> 