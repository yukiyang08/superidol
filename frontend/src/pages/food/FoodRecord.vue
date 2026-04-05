<template>
  <div class="food-record-page">
    <div class="container">
      <h1 class="page-title">食物記錄</h1>

      <!-- 日期選擇器 -->
      <div class="date-navigation">
        <button class="date-nav-btn" @click="changeDate(-1)">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <div class="date-picker-container" style="position: relative;">
          <div class="current-date" style="position: relative;">
            <el-icon><DateIcon /></el-icon>
            <span>{{ formattedDate }}</span>
            <el-icon><ArrowDown /></el-icon>
            <input
              ref="dateInputRef"
              type="date"
              v-model="selectedDateString"
              class="date-picker-overlay"
              :max="todayString"
              @change="onDateChange"
              tabindex="0"
            >
          </div>
        </div>
        <button class="date-nav-btn" @click="changeDate(1)">
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>

      <!-- 每日卡路里摘要 -->
      <div class="nutrition-summary-card">
        <div class="summary-header">
          <h2 class="summary-title">今日營養摘要</h2>
        </div>
        <div class="calorie-summary">
          <div class="calorie-info">
            <div class="calorie-item calorie-consumed">
              <div class="calorie-value">{{ dailySummary.calories }}</div>
              <div class="calorie-label">已攝取卡路里</div>
            </div>
            <div class="calorie-divider"></div>
            <div class="calorie-item calorie-target">
              <div class="calorie-value">{{ calorieGoal }}</div>
              <div class="calorie-label">最多可攝取卡路里</div>
            </div>
            <div class="calorie-divider"></div>
            <div class="calorie-item calorie-remaining">
              <div class="calorie-value" :class="{ 'negative': calorieRemaining < 0 }">
                {{ calorieRemaining < 0 ? '+' + Math.abs(calorieRemaining) : calorieRemaining }}
              </div>
              <div class="calorie-label">{{ calorieRemaining < 0 ? '超出' : '尚可攝取' }}卡路里</div>
            </div>
          </div>
          <div class="progress-container">
            <div class="progress-bar" :style="{ width: calorieProgressPercentage + '%' }"
              :class="{ 'exceed': calorieProgressPercentage > 100 }"></div>
          </div>
        </div>
      </div>
      <!-- 全局自訂食物表單 -->
      <div class="custom-food-form-card">
        <h3 class="custom-form-title">自訂飲食紀錄</h3>
        <form class="custom-food-form" @submit.prevent="submitCustomFood">
          <div class="form-row">
            <input v-model="customForm.custom_name" type="text" placeholder="食物名稱*" required />
            <input v-model.number="customForm.custom_calories" type="number" min="0" placeholder="熱量(大卡)*" required />
            <input v-model.number="customForm.custom_price" type="number" min="0" placeholder="價格(元)" />
          </div>
          <div class="form-row">
            <input v-model="customForm.custom_type" type="text" placeholder="類型(如主食/飲料)" />
            <input v-model="customForm.custom_restaurant" type="text" placeholder="餐廳" />
            <input v-model.number="customForm.quantity" type="number" min="1" placeholder="數量*" required />
          </div>
          <div class="form-row">
            <select v-model="customForm.mealtime" required>
              <option value="">選擇餐別*</option>
              <option value="早餐">早餐</option>
              <option value="午餐">午餐</option>
              <option value="晚餐">晚餐</option>
              <option value="點心">點心</option>
            </select>
            <button class="submit-btn" type="submit">新增自訂紀錄</button>
          </div>
        </form>
      </div>

      <!-- 餐點記錄 -->
      <div class="meals-container">
        <!-- 早餐 -->
        <div class="meal-card">
          <div class="meal-header">
            <div class="meal-icon-container">
              <el-icon><Sunrise /></el-icon>
            </div>
            <h3 class="meal-title">早餐</h3>
            <button class="add-food-btn" @click="addFood('breakfast')">
              <el-icon><Plus /></el-icon>
              添加食物
            </button>
          </div>

          <div class="meal-content">
            <div v-if="isLoading" class="meal-loading">
              <div class="loading-spinner"></div>
            </div>
            <div v-else-if="!breakfastItems.length" class="empty-meal">
              <el-icon><FoodIcon /></el-icon>
              <p>尚未添加早餐食物</p>
            </div>
            <div v-else class="food-items">
              <div v-for="(item, index) in breakfastItems" :key="index" class="food-item-card">
                <div class="food-item-content">
                  <div v-if="item.ImageUrl" class="food-image-container">
                    <img :src="item.ImageUrl" :alt="item.name" class="food-image" @error="e => e.target.src = '/img/food-placeholder.png'" />
                    <div class="calorie-on-image-button">
                      <span class="calorie-value">{{ Math.round(item.calories) }}</span>
                      <span class="calorie-unit">大卡</span>
                    </div>
                  </div>
                  <div class="food-item-info">
                    <h4 class="food-item-name">{{ item.name }}</h4>
                    <div class="food-item-details">
                      <div class="detail-row">
                        <span class="detail-label">餐廳:</span>
                        <span class="detail-value">{{ item.restaurant || '未知' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">價格:</span>
                        <span class="detail-value">{{ item.price }} 元</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">熱量:</span>
                        <span class="detail-value">{{ item.calories }} 大卡</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">類型:</span>
                        <span class="detail-value">{{ item.type }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">數量:</span>
                        <span class="detail-value">{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div v-if="item.Protein || item.Fat || item.Sugar || item.Sodium || item.Carb || item.Caffeine" class="nutrition-info-block">
                      <table class="nutrition-table">
                        <tr v-if="item.Protein"><td>蛋白質</td><td>{{ item.Protein }}g</td></tr>
                        <tr v-if="item.Fat"><td>脂肪</td><td>{{ item.Fat }}g</td></tr>
                        <tr v-if="item.Sugar"><td>糖</td><td>{{ item.Sugar }}g</td></tr>
                        <tr v-if="item.Sodium"><td>鈉</td><td>{{ item.Sodium }}mg</td></tr>
                        <tr v-if="item.Carb"><td>碳水</td><td>{{ item.Carb }}g</td></tr>
                        <tr v-if="item.Caffeine"><td>咖啡因</td><td>{{ item.Caffeine }}mg</td></tr>
                      </table>
                    </div>
                    <div v-else class="no-nutrition-data">暫無詳細營養數據</div>
                  </div>
                  <div class="food-item-actions">
                    <button class="delete-btn" @click="deleteRecord(item.record_id)">刪除</button>
                    <button class="edit-btn" @click="openEditRecord(item)">編輯</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 午餐 -->
        <div class="meal-card">
          <div class="meal-header">
            <div class="meal-icon-container">
              <el-icon><Sunny /></el-icon>
            </div>
            <h3 class="meal-title">午餐</h3>
            <button class="add-food-btn" @click="addFood('lunch')">
              <el-icon><Plus /></el-icon>
              添加食物
            </button>
          </div>

          <div class="meal-content">
            <div v-if="isLoading" class="meal-loading">
              <div class="loading-spinner"></div>
            </div>
            <div v-else-if="!lunchItems.length" class="empty-meal">
              <el-icon><FoodIcon /></el-icon>
              <p>尚未添加午餐食物</p>
            </div>
            <div v-else class="food-items">
              <div v-for="(item, index) in lunchItems" :key="index" class="food-item-card">
                <div class="food-item-content">
                  <div v-if="item.ImageUrl" class="food-image-container">
                    <img :src="item.ImageUrl" :alt="item.name" class="food-image" @error="e => e.target.src = '/img/food-placeholder.png'" />
                    <div class="calorie-on-image-button">
                      <span class="calorie-value">{{ Math.round(item.calories) }}</span>
                      <span class="calorie-unit">大卡</span>
                    </div>
                  </div>
                  <div class="food-item-info">
                    <h4 class="food-item-name">{{ item.name }}</h4>
                    <div class="food-item-details">
                      <div class="detail-row">
                        <span class="detail-label">餐廳:</span>
                        <span class="detail-value">{{ item.restaurant || '未知' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">價格:</span>
                        <span class="detail-value">{{ item.price }} 元</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">熱量:</span>
                        <span class="detail-value">{{ item.calories }} 大卡</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">類型:</span>
                        <span class="detail-value">{{ item.type }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">數量:</span>
                        <span class="detail-value">{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div v-if="item.Protein || item.Fat || item.Sugar || item.Sodium || item.Carb || item.Caffeine" class="nutrition-info-block">
                      <table class="nutrition-table">
                        <tr v-if="item.Protein"><td>蛋白質</td><td>{{ item.Protein }}g</td></tr>
                        <tr v-if="item.Fat"><td>脂肪</td><td>{{ item.Fat }}g</td></tr>
                        <tr v-if="item.Sugar"><td>糖</td><td>{{ item.Sugar }}g</td></tr>
                        <tr v-if="item.Sodium"><td>鈉</td><td>{{ item.Sodium }}mg</td></tr>
                        <tr v-if="item.Carb"><td>碳水</td><td>{{ item.Carb }}g</td></tr>
                        <tr v-if="item.Caffeine"><td>咖啡因</td><td>{{ item.Caffeine }}mg</td></tr>
                      </table>
                    </div>
                    <div v-else class="no-nutrition-data">暫無詳細營養數據</div>
                  </div>
                  <div class="food-item-actions">
                    <button class="delete-btn" @click="deleteRecord(item.record_id)">刪除</button>
                    <button class="edit-btn" @click="openEditRecord(item)">編輯</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 晚餐 -->
        <div class="meal-card">
          <div class="meal-header">
            <div class="meal-icon-container">
              <el-icon><Sunset /></el-icon>
            </div>
            <h3 class="meal-title">晚餐</h3>
            <button class="add-food-btn" @click="addFood('dinner')">
              <el-icon><Plus /></el-icon>
              添加食物
            </button>
          </div>

          <div class="meal-content">
            <div v-if="isLoading" class="meal-loading">
              <div class="loading-spinner"></div>
            </div>
            <div v-else-if="!dinnerItems.length" class="empty-meal">
              <el-icon><FoodIcon /></el-icon>
              <p>尚未添加晚餐食物</p>
            </div>
            <div v-else class="food-items">
              <div v-for="(item, index) in dinnerItems" :key="index" class="food-item-card">
                <div class="food-item-content">
                  <div v-if="item.ImageUrl" class="food-image-container">
                    <img :src="item.ImageUrl" :alt="item.name" class="food-image" @error="e => e.target.src = '/img/food-placeholder.png'" />
                    <div class="calorie-on-image-button">
                      <span class="calorie-value">{{ Math.round(item.calories) }}</span>
                      <span class="calorie-unit">大卡</span>
                    </div>
                  </div>
                  <div class="food-item-info">
                    <h4 class="food-item-name">{{ item.name }}</h4>
                    <div class="food-item-details">
                      <div class="detail-row">
                        <span class="detail-label">餐廳:</span>
                        <span class="detail-value">{{ item.restaurant || '未知' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">價格:</span>
                        <span class="detail-value">{{ item.price }} 元</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">熱量:</span>
                        <span class="detail-value">{{ item.calories }} 大卡</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">類型:</span>
                        <span class="detail-value">{{ item.type }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">數量:</span>
                        <span class="detail-value">{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div v-if="item.Protein || item.Fat || item.Sugar || item.Sodium || item.Carb || item.Caffeine" class="nutrition-info-block">
                      <table class="nutrition-table">
                        <tr v-if="item.Protein"><td>蛋白質</td><td>{{ item.Protein }}g</td></tr>
                        <tr v-if="item.Fat"><td>脂肪</td><td>{{ item.Fat }}g</td></tr>
                        <tr v-if="item.Sugar"><td>糖</td><td>{{ item.Sugar }}g</td></tr>
                        <tr v-if="item.Sodium"><td>鈉</td><td>{{ item.Sodium }}mg</td></tr>
                        <tr v-if="item.Carb"><td>碳水</td><td>{{ item.Carb }}g</td></tr>
                        <tr v-if="item.Caffeine"><td>咖啡因</td><td>{{ item.Caffeine }}mg</td></tr>
                      </table>
                    </div>
                    <div v-else class="no-nutrition-data">暫無詳細營養數據</div>
                  </div>
                  <div class="food-item-actions">
                    <button class="delete-btn" @click="deleteRecord(item.record_id)">刪除</button>
                    <button class="edit-btn" @click="openEditRecord(item)">編輯</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 點心 -->
        <div class="meal-card">
          <div class="meal-header">
            <div class="meal-icon-container">
              <el-icon><Dessert /></el-icon>
            </div>
            <h3 class="meal-title">點心</h3>
            <button class="add-food-btn" @click="addFood('snacks')">
              <el-icon><Plus /></el-icon>
              添加食物
            </button>
          </div>

          <div class="meal-content">
            <div v-if="isLoading" class="meal-loading">
              <div class="loading-spinner"></div>
            </div>
            <div v-else-if="!snackItems.length" class="empty-meal">
              <el-icon><FoodIcon /></el-icon>
              <p>尚未添加點心食物</p>
            </div>
            <div v-else class="food-items">
              <div v-for="(item, index) in snackItems" :key="index" class="food-item-card">
                <div class="food-item-content">
                  <div v-if="item.ImageUrl" class="food-image-container">
                    <img :src="item.ImageUrl" :alt="item.name" class="food-image" @error="e => e.target.src = '/img/food-placeholder.png'" />
                    <div class="calorie-on-image-button">
                      <span class="calorie-value">{{ Math.round(item.calories) }}</span>
                      <span class="calorie-unit">大卡</span>
                    </div>
                  </div>
                  <div class="food-item-info">
                    <h4 class="food-item-name">{{ item.name }}</h4>
                    <div class="food-item-details">
                      <div class="detail-row">
                        <span class="detail-label">餐廳:</span>
                        <span class="detail-value">{{ item.restaurant || '未知' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">價格:</span>
                        <span class="detail-value">{{ item.price }} 元</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">熱量:</span>
                        <span class="detail-value">{{ item.calories }} 大卡</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">類型:</span>
                        <span class="detail-value">{{ item.type }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">數量:</span>
                        <span class="detail-value">{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div v-if="item.Protein || item.Fat || item.Sugar || item.Sodium || item.Carb || item.Caffeine" class="nutrition-info-block">
                      <table class="nutrition-table">
                        <tr v-if="item.Protein"><td>蛋白質</td><td>{{ item.Protein }}g</td></tr>
                        <tr v-if="item.Fat"><td>脂肪</td><td>{{ item.Fat }}g</td></tr>
                        <tr v-if="item.Sugar"><td>糖</td><td>{{ item.Sugar }}g</td></tr>
                        <tr v-if="item.Sodium"><td>鈉</td><td>{{ item.Sodium }}mg</td></tr>
                        <tr v-if="item.Carb"><td>碳水</td><td>{{ item.Carb }}g</td></tr>
                        <tr v-if="item.Caffeine"><td>咖啡因</td><td>{{ item.Caffeine }}mg</td></tr>
                      </table>
                    </div>
                    <div v-else class="no-nutrition-data">暫無詳細營養數據</div>
                  </div>
                  <div class="food-item-actions">
                    <button class="delete-btn" @click="deleteRecord(item.record_id)">刪除</button>
                    <button class="edit-btn" @click="openEditRecord(item)">編輯</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-if="breakfastItems.length === 0 && lunchItems.length === 0 && dinnerItems.length === 0 && snackItems.length === 0 && !isLoading" class="no-records-card">
        <el-icon><Notebook /></el-icon>
        <h3>今日尚未添加任何食物記錄</h3>
        <p>點擊各餐點區域的"添加食物"按鈕開始記錄您的飲食</p>
      </div>

      <!-- 載入中 -->
      <div v-if="isLoading && breakfastItems.length === 0 && lunchItems.length === 0 && dinnerItems.length === 0 && snackItems.length === 0" class="loading-state">
        <div class="loading-spinner"></div>
        <p>載入中...</p>
      </div>

      <FoodRecordModal
        v-if="showEditModal"
        :visible="showEditModal"
        :editMode="true"
        :record="editingRecord"
        @update:visible="closeEditModal"
        @saved="handleEditSaved"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import FoodRecordModal from '@/components/food/FoodRecordModal.vue'
import api from '@/services/api'
import { ArrowLeft, ArrowRight, ArrowDown, Sunrise, Sunny, Sunset, Dessert, Notebook, Calendar as DateIcon, Food as FoodIcon } from '@element-plus/icons-vue'

export default {
  name: 'FoodRecord',
  components: {
    FoodRecordModal,
    ArrowLeft, ArrowRight, ArrowDown,
    Sunrise, Sunny, Sunset, Dessert, Notebook,
    DateIcon, FoodIcon
  },
  setup() {
    const router = useRouter()
    
    // 當前選中的日期
    const selectedDate = ref(new Date())
    const selectedDateString = ref('')
    const dateInputRef = ref(null)
    const today = new Date()
    const todayString = computed(() => {
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    })

    // 卡路里目標 (從 API 取得 weekCalorieLimit/7)
    const calorieGoal = ref(2000)

    // 載入狀態
    const isLoading = ref(false)

    // 格式化日期
    const formattedDate = computed(() => {
      return new Date(selectedDate.value).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
      })
    })

    // 計算每日摘要
    const dailySummary = ref({
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0
    })

    // 計算剩餘卡路里
    const calorieRemaining = computed(() => {
      return calorieGoal.value - dailySummary.value.calories
    })

    // 計算卡路里進度百分比
    const calorieProgressPercentage = computed(() => {
      return Math.min((dailySummary.value.calories / calorieGoal.value) * 100, 120)
    })

    // 各餐食物數據
    const breakfastItems = ref([])
    const lunchItems = ref([])
    const dinnerItems = ref([])
    const snackItems = ref([])

    // 編輯彈窗狀態
    const showEditModal = ref(false)
    const editingRecord = ref(null)

    // 選擇日期時同步更新 selectedDate 並載入資料
    const onDateChange = (e) => {
      const newDate = new Date(selectedDateString.value)
      if (!isNaN(newDate)) {
        selectedDate.value = newDate
        loadFoodRecords()
      }
    }

    watch(selectedDate, (newDate) => {
      if (newDate instanceof Date) {
        const year = newDate.getFullYear()
        const month = String(newDate.getMonth() + 1).padStart(2, '0')
        const day = String(newDate.getDate()).padStart(2, '0')
        selectedDateString.value = `${year}-${month}-${day}`
      }
    }, { immediate: true })

    // 取得用戶每日熱量目標
    const fetchCalorieGoal = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return
        const res = await axios.get('/api/auth/user', {
          headers: { Authorization: `Bearer ${token}` }
        })
        const weekLimit = res.data.weekCalorieLimit
        if (weekLimit && !isNaN(Number(weekLimit))) {
          calorieGoal.value = Math.round(Number(weekLimit) / 7)
        }
      } catch (err) {
        // fallback 預設 2000
        calorieGoal.value = 2000
      }
    }

    // 加載食物記錄
    const loadFoodRecords = async () => {
      isLoading.value = true;
      
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入')
          isLoading.value = false
          return
        }
        
        // 使用 selectedDateString 作為日期參數
        const { data } = await api.get('/api/food/record', {
          params: { user_id: userId, start_date: selectedDateString.value, end_date: selectedDateString.value }
        })
        
        // 重置所有餐點數組
        breakfastItems.value = []
        lunchItems.value = []
        dinnerItems.value = []
        snackItems.value = []
        
        // 按餐點類型分類記錄
        if (Array.isArray(data)) {
          data.forEach(record => {
            const recordData = {
              record_id: record.record_id,
              name: record.name,
              restaurant: record.restaurant,
              calories: record.calories,
              price: record.price,
              type: record.type,
              food_type: record.food_type || '未分類',
              quantity: record.quantity,
              mealtime: record.mealtime,
              date: record.date
            }
            
            if (record.mealtime === '早餐') {
              breakfastItems.value.push(recordData)
            } else if (record.mealtime === '午餐') {
              lunchItems.value.push(recordData)
            } else if (record.mealtime === '晚餐') {
              dinnerItems.value.push(recordData)
            } else if (record.mealtime === '點心') {
              snackItems.value.push(recordData)
            }
          })
        }
        
        // 計算每日摘要
        calculateDailySummary()
      } catch (error) {
        console.error('載入食物記錄失敗:', error)
        ElMessage.error('無法載入食物記錄，請稍後再試')
      } finally {
        isLoading.value = false
      }
    }
    
    // 計算每日摘要
    const calculateDailySummary = () => {
      let totalCalories = 0
      
      // 計算所有餐點的卡路里總和
      const allItems = [
        ...breakfastItems.value, 
        ...lunchItems.value, 
        ...dinnerItems.value, 
        ...snackItems.value
      ]
      
      allItems.forEach(item => {
        totalCalories += (item.calories * item.quantity)
      })
      
      dailySummary.value.calories = Math.round(totalCalories)
    }

    // 添加食物到指定餐點
    const addFood = (mealType) => {
      // TODO: 導航到食物搜尋頁面或打開食物選擇彈窗
      router.push({
        path: '/food/search',
        query: {
          returnTo: '/food/record',
          mealType: mealType,
          date: selectedDateString.value
        }
      })
    }

    // 刪除食物記錄
    const deleteRecord = async (recordId) => {
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入')
          return
        }
        
        await api.delete(`/api/food/record/${recordId}`, { params: { user_id: userId } })
        
        ElMessage.success('記錄已成功刪除')
        
        // 重新加載食物記錄
        loadFoodRecords()
      } catch (error) {
        console.error('刪除記錄失敗:', error)
        ElMessage.error('刪除記錄失敗，請稍後再試')
      }
    }

    // 更改日期
    const changeDate = (days) => {
      const newDate = new Date(selectedDate.value)
      newDate.setDate(newDate.getDate() + days)
      // 限制不能超過今天
      if (newDate > today) {
        ElMessage.warning('只能記錄到今天，不能選擇未來日期')
        return
      }
      selectedDate.value = newDate
      // 加載所選日期的食物記錄
      loadFoodRecords()
    }

    const openEditRecord = (record) => {
      editingRecord.value = {
        ...record,
        mealtime: record.mealtime,
        quantity: record.quantity,
        date: record.date
      }
      showEditModal.value = true
    }

    const closeEditModal = () => {
      showEditModal.value = false
      editingRecord.value = null
    }

    const handleEditSaved = () => {
      closeEditModal()
      loadFoodRecords()
    }

    // 全局自訂食物表單
    const customForm = ref({
      custom_name: '',
      custom_calories: '',
      custom_price: '',
      custom_type: '',
      custom_restaurant: '',
      quantity: 1,
      mealtime: ''
    })
    const submitCustomFood = async () => {
      // 驗證
      if (!customForm.value.custom_name || !customForm.value.custom_calories || !customForm.value.mealtime) {
        ElMessage.error('請填寫必填欄位')
        return
      }
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入')
          return
        }
        const payload = {
          user_id: userId,
          food_id: null,
          custom_name: customForm.value.custom_name,
          custom_calories: customForm.value.custom_calories,
          custom_type: customForm.value.custom_type,
          custom_price: customForm.value.custom_price,
          custom_restaurant: customForm.value.custom_restaurant,
          quantity: customForm.value.quantity,
          mealtime: customForm.value.mealtime,
          date: selectedDateString.value
        }
        await axios.post('/api/food/record', payload)
        ElMessage.success('自訂飲食紀錄已新增')
        // 清空表單
        customForm.value = {
          custom_name: '',
          custom_calories: '',
          custom_price: '',
          custom_type: '',
          custom_restaurant: '',
          quantity: 1,
          mealtime: ''
        }
        // 重新載入紀錄
        loadFoodRecords()
      } catch (err) {
        ElMessage.error('新增失敗，請稍後再試')
      }
    }

    // 初始化
    onMounted(() => {
      // 加載當前日期的食物記錄
      loadFoodRecords()
      fetchCalorieGoal()
    })

    return {
      selectedDate,
      selectedDateString,
      dateInputRef,
      formattedDate,
      todayString,
      calorieGoal,
      dailySummary,
      calorieRemaining,
      calorieProgressPercentage,
      breakfastItems,
      lunchItems,
      dinnerItems,
      snackItems,
      changeDate,
      addFood,
      deleteRecord,
      isLoading,
      loadFoodRecords,
      showEditModal,
      editingRecord,
      openEditRecord,
      closeEditModal,
      handleEditSaved,
      onDateChange,
      customForm,
      submitCustomFood,
    }
  }
}
</script>

<style scoped>
.food-record-page {
  padding: 20px 0;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #333;
  text-align: center;
}

/* 日期導航 */
.date-navigation {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
}

.date-nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  border: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.date-nav-btn:hover {
  background: #f5f5f5;
}

.date-nav-btn i {
  color: #666;
  font-size: 18px;
}

.date-picker-container {
  position: relative;
  margin: 0 16px;
}

.current-date {
  padding: 10px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.current-date:hover {
  background: #f9f9f9;
}

.current-date i {
  color: #ffaa55;
}

.date-picker-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  width: 100%; height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.date-picker {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s;
  z-index: 10;
}

.date-picker.visible {
  opacity: 1;
  pointer-events: auto;
}

/* 營養摘要卡片 */
.nutrition-summary-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
  overflow: hidden;
}

.summary-header {
  padding: 16px 20px;
  background: #ffaa55;
  color: white;
}

.summary-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.calorie-summary {
  padding: 20px;
}

.calorie-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.calorie-item {
  flex: 1;
  text-align: center;
  padding: 0 10px;
}

.calorie-divider {
  width: 1px;
  background: #eee;
}

.calorie-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

.calorie-value.negative {
  color: #f56c6c;
}

.calorie-label {
  font-size: 14px;
  color: #666;
}

.progress-container {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #ffaa55;
  transition: width 0.3s ease;
}

.progress-bar.exceed {
  background: #f56c6c;
}

/* 餐點卡片 */
.meals-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  margin-bottom: 40px;
}

@media (max-width: 900px) {
  .meals-container {
    grid-template-columns: 1fr;
    gap: 18px;
  }
}

.meal-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.meal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #f9f9f9;
}

.meal-icon-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #ffaa55;
  display: flex;
  align-items: center;
  justify-content: center;
}

.meal-icon-container i {
  font-size: 20px;
  color: white;
}

.meal-title {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.add-food-btn {
  padding: 8px 16px;
  background: #ffaa55;
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.add-food-btn:hover {
  background: #ff9933;
}

.meal-content {
  padding: 20px;
}

.meal-loading {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ffaa55;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-meal {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  color: #999;
}

.empty-meal i {
  font-size: 32px;
  margin-bottom: 12px;
  color: #ddd;
}

.empty-meal p {
  margin: 0;
  font-size: 16px;
}

.food-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.food-item-card {
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.food-item-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.food-item-content {
  display: flex;
  padding: 16px;
}

.food-item-info {
  flex: 1;
}

.food-item-name {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.food-item-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px 16px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-label {
  color: #666;
  font-size: 14px;
}

.detail-value {
  font-weight: 500;
  font-size: 14px;
}

.food-item-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.delete-btn {
  width: auto;
  height: 36px;
  border-radius: 6px;
  background: #fff;
  border: 1.5px solid #fca5a5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(252, 165, 165, 0.08);
  padding: 0 18px;
  font-size: 1rem;
  color: #ef4444;
  font-weight: 600;
}
.delete-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

/* 無記錄狀態 */
.no-records-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 40px 20px;
  text-align: center;
  margin: 40px 0;
}

.no-records-card i {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 16px;
}

.no-records-card h3 {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.no-records-card p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

/* 載入狀態 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin: 40px 0;
}

.loading-state .loading-spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 16px;
}

.loading-state p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .calorie-info {
    flex-direction: column;
    gap: 20px;
  }

  .calorie-divider {
    display: none;
  }

  .food-item-details {
    grid-template-columns: 1fr;
  }
}

.edit-btn {
  margin-right: 8px;
  background: #e3f2fd;
  color: #1976d2;
  border: 1.5px solid #90caf9;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
  box-shadow: 0 2px 8px rgba(144, 202, 249, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}
.edit-btn i {
  color: #1976d2;
  font-size: 1.3em;
}
.edit-btn:hover {
  background: #bbdefb;
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
}

.custom-food-form-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 30px;
  padding: 24px 20px 18px 20px;
}
.custom-form-title {
  font-size: 18px;
  font-weight: 600;
  color: #ff7940;
  margin-bottom: 12px;
}
.custom-food-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.custom-food-form .form-row {
  display: flex;
  gap: 12px;
}
.custom-food-form input,
.custom-food-form select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  font-size: 15px;
  background: #f9f9f9;
  transition: border 0.2s;
}
.custom-food-form input:focus,
.custom-food-form select:focus {
  border-color: #ff8640;
  outline: none;
}
.submit-btn {
  background: #ffb340;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 18px;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:hover {
  background: #cc6933;
}

.food-image-container {
  width: 120px;
  height: 120px;
  background-color: #f5f5f5;
  border-radius: 10px;
  overflow: hidden;
  margin-right: 18px;
  position: relative;
  flex-shrink: 0;
}
.food-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}
.calorie-on-image-button {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 48px;
  height: 48px;
  background-color: rgba(230, 162, 60, 0.9);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(230,162,60,0.12);
  cursor: default;
  text-align: center;
  line-height: 1.1;
  font-size: 1rem;
}
.nutrition-info-block {
  margin-top: 10px;
}
.nutrition-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95em;
}
.nutrition-table td {
  padding: 2px 8px 2px 0;
  color: #666;
}
.nutrition-table td:first-child {
  color: #ffaa55;
  font-weight: 500;
  width: 60px;
}
.no-nutrition-data {
  color: #bbb;
  font-size: 0.95em;
  margin-top: 8px;
}
</style>



