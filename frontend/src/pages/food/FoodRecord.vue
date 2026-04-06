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
          <div class="photo-estimate-panel">
            <div class="photo-estimate-copy">
              <h4>拍照估算熱量與營養</h4>
              <p>選擇照片後會自動上傳，你可直接儲存，或再點 AI 估算熱量與蛋白質、碳水等營養資訊。</p>
            </div>
            <div class="photo-estimate-actions">
              <label class="photo-picker-btn">
                <input type="file" accept="image/*" capture="environment" class="photo-input" @change="handlePhotoFileChange" />
                選擇照片
              </label>
              <button
                type="button"
                class="estimate-btn"
                :disabled="(!photoFile && !customForm.photo_url) || photoUploadLoading || photoEstimateLoading"
                @click="estimateCustomFoodFromPhoto"
              >
                {{ photoEstimateLoading ? '辨識中...' : 'AI 辨識營養' }}
              </button>
            </div>
            <div v-if="photoPreviewUrl" class="photo-preview-block">
              <div class="photo-preview-column">
                <img :src="photoPreviewUrl" alt="預覽餐點照片" class="photo-preview-image" />
              </div>

              <div class="photo-estimate-column">
                <div v-if="photoEstimateResult" class="photo-estimate-result">
                  <div class="estimate-result-title">AI 建議（可手動調整）</div>
                  <div class="estimate-result-row">
                    <span>名稱</span>
                    <strong>{{ photoEstimateResult.estimated_name || '未辨識' }}</strong>
                  </div>
                  <div class="estimate-result-row">
                    <span>熱量</span>
                    <strong>{{ photoEstimateResult.estimated_calories ?? '--' }} 大卡</strong>
                  </div>
                  <div class="estimate-nutrient-grid">
                    <div class="estimate-result-row compact" v-if="photoEstimateResult.estimated_protein !== null && photoEstimateResult.estimated_protein !== undefined">
                      <span>蛋白質</span>
                      <strong>{{ photoEstimateResult.estimated_protein }} g</strong>
                    </div>
                    <div class="estimate-result-row compact" v-if="photoEstimateResult.estimated_fat !== null && photoEstimateResult.estimated_fat !== undefined">
                      <span>脂肪</span>
                      <strong>{{ photoEstimateResult.estimated_fat }} g</strong>
                    </div>
                    <div class="estimate-result-row compact" v-if="photoEstimateResult.estimated_carb !== null && photoEstimateResult.estimated_carb !== undefined">
                      <span>碳水</span>
                      <strong>{{ photoEstimateResult.estimated_carb }} g</strong>
                    </div>
                    <div class="estimate-result-row compact" v-if="photoEstimateResult.estimated_sugar !== null && photoEstimateResult.estimated_sugar !== undefined">
                      <span>糖</span>
                      <strong>{{ photoEstimateResult.estimated_sugar }} g</strong>
                    </div>
                    <div class="estimate-result-row compact" v-if="photoEstimateResult.estimated_sodium !== null && photoEstimateResult.estimated_sodium !== undefined">
                      <span>鈉</span>
                      <strong>{{ photoEstimateResult.estimated_sodium }} mg</strong>
                    </div>
                  </div>
                  <div class="estimate-result-row" v-if="photoEstimateResult.estimation_confidence !== null && photoEstimateResult.estimation_confidence !== undefined">
                    <span>信心值</span>
                    <strong>{{ Math.round(photoEstimateResult.estimation_confidence * 100) }}%</strong>
                  </div>
                  <p v-if="photoEstimateResult.estimation_notes" class="estimate-notes">{{ photoEstimateResult.estimation_notes }}</p>
                </div>

                <div v-else class="photo-estimate-placeholder">
                  <div class="estimate-result-title">等待 AI 辨識</div>
                  <p class="estimate-notes">照片已準備完成，按下「AI 辨識營養」即可填入名稱、熱量與營養素。</p>
                </div>
              </div>
            </div>
          </div>
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
            <button class="submit-btn" type="submit" :disabled="photoUploadLoading || submitCustomLoading">
              {{ submitCustomLoading ? '新增中...' : '新增自訂紀錄' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 餐點記錄（單一瀏覽區） -->
      <div class="records-toolbar">
        <h3 class="records-title">飲食紀錄</h3>
        <button class="add-food-btn" @click="addFood()">
          <el-icon><Plus /></el-icon>
          添加食物
        </button>
      </div>

      <div class="meals-container" v-if="sortedFoodRecords.length">
        <div class="meal-card">
          <div class="meal-content">
            <div class="food-items">
              <div v-for="item in sortedFoodRecords" :key="item.record_id" class="food-item-card">
                <div class="food-item-content">
                  <div v-if="item.photo_url || item.image_url" class="food-image-container">
                    <div class="food-image-primary">
                      <img :src="item.photo_url || item.image_url" :alt="item.name" class="food-image" @error="e => e.target.src = '/img/food-placeholder.png'" />
                      <span v-if="item.photo_url" class="image-source-badge user-photo">我的照片</span>
                      <div class="calorie-on-image-button">
                        <span class="calorie-value">{{ Math.round(item.calories) }}</span>
                        <span class="calorie-unit">大卡</span>
                      </div>
                    </div>
                    <div v-if="item.photo_url && item.image_url" class="food-image-secondary">
                      <img :src="item.image_url" :alt="item.name" class="food-image-thumb" @error="e => e.target.style.display='none'" />
                      <span class="image-source-badge db-image">品項圖</span>
                    </div>
                  </div>
                  <div class="food-item-info">
                    <div class="food-item-topline">
                      <span class="mealtime-chip" :class="mealLabelClass(item.mealtime)">{{ item.mealtime || '未分類' }}</span>
                    </div>
                    <h4 class="food-item-name">{{ item.name }}</h4>
                    <div class="food-item-details">
                      <div class="detail-row">
                        <span class="detail-label">餐廳:</span>
                        <span class="detail-value">{{ item.restaurant || '未知' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">價格:</span>
                        <span class="detail-value">{{ item.price ?? '-' }} 元</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">熱量:</span>
                        <span class="detail-value">{{ item.calories }} 大卡</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">類型:</span>
                        <span class="detail-value">{{ item.type || '-' }}</span>
                      </div>
                      <div class="detail-row">
                        <span class="detail-label">數量:</span>
                        <span class="detail-value">{{ item.quantity }}</span>
                      </div>
                    </div>
                    <div v-if="item.protein || item.fat || item.sugar || item.sodium || item.carb || item.caffeine" class="nutrition-info-block">
                      <table class="nutrition-table">
                        <tr v-if="item.protein"><td>蛋白質</td><td>{{ item.protein }}g</td></tr>
                        <tr v-if="item.fat"><td>脂肪</td><td>{{ item.fat }}g</td></tr>
                        <tr v-if="item.sugar"><td>糖</td><td>{{ item.sugar }}g</td></tr>
                        <tr v-if="item.sodium"><td>鈉</td><td>{{ item.sodium }}mg</td></tr>
                        <tr v-if="item.carb"><td>碳水</td><td>{{ item.carb }}g</td></tr>
                        <tr v-if="item.caffeine"><td>咖啡因</td><td>{{ item.caffeine }}mg</td></tr>
                      </table>
                    </div>
                    <div v-else class="no-nutrition-data">暫無詳細營養數據</div>
                  </div>
                  <div class="food-item-actions">
                    <button class="delete-btn icon-only" @click="deleteRecord(item.record_id)" :aria-label="`刪除 ${item.name}`" title="刪除">
                      <el-icon><Delete /></el-icon>
                    </button>
                    <button class="edit-btn icon-only" @click="openEditRecord(item)" :aria-label="`編輯 ${item.name}`" title="編輯">
                      <el-icon><EditPen /></el-icon>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-if="!hasAnyRecords && !isLoading" class="no-records-card">
        <el-icon><Notebook /></el-icon>
        <h3>目前尚無飲食紀錄</h3>
        <p>點擊上方「添加食物」開始記錄今日飲食</p>
      </div>

      <!-- 載入中 -->
      <div v-if="isLoading && !hasAnyRecords" class="loading-state">
        <PlateSpiritLoader
          message="餐盤小精靈整理今日飲食中..."
          submessage="正在把今天的卡路里、餐別和營養資訊擺上餐盤。"
        />
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

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PlateSpiritLoader from '@/components/common/PlateSpiritLoader.vue'
import FoodRecordModal from '@/components/food/FoodRecordModal.vue'
import api from '@/services/api'
import { ArrowLeft, ArrowRight, ArrowDown, Plus, Delete, EditPen, Notebook, Calendar as DateIcon } from '@element-plus/icons-vue'

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

    // 食物紀錄（單一列表）
    const foodRecords = ref([])
    const mealOrder = { 早餐: 0, 午餐: 1, 晚餐: 2, 點心: 3 }

    const sortedFoodRecords = computed(() => {
      return [...foodRecords.value].sort((a, b) => {
        const mealDiff = (mealOrder[a.mealtime] ?? 99) - (mealOrder[b.mealtime] ?? 99)
        if (mealDiff !== 0) {
          return mealDiff
        }
        return Number(b.record_id || 0) - Number(a.record_id || 0)
      })
    })

    const hasAnyRecords = computed(() => sortedFoodRecords.value.length > 0)

    const mealLabelClass = (mealtime) => {
      if (mealtime === '早餐') return 'meal-breakfast'
      if (mealtime === '午餐') return 'meal-lunch'
      if (mealtime === '晚餐') return 'meal-dinner'
      if (mealtime === '點心') return 'meal-snack'
      return 'meal-unknown'
    }

    // 編輯彈窗狀態
    const showEditModal = ref(false)
    const editingRecord = ref(null)
    const photoFile = ref(null)
    const photoPreviewUrl = ref('')
    const photoUploadLoading = ref(false)
    const photoEstimateLoading = ref(false)
    const photoEstimateResult = ref(null)
    const submitCustomLoading = ref(false)

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
        const res = await api.get('/api/auth/user')
        const weekLimit = res.data.weekCalorieLimit
        if (weekLimit && !isNaN(Number(weekLimit))) {
          calorieGoal.value = Math.round(Number(weekLimit) / 7)
        }
      } catch (err) {
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
          return
        }
        
        // 使用 selectedDateString 作為日期參數
        const { data } = await api.get('/api/food/record', {
          params: { user_id: userId, start_date: selectedDateString.value, end_date: selectedDateString.value }
        })
        
        foodRecords.value = Array.isArray(data)
          ? data.map(record => ({
              record_id: record.record_id,
              name: record.name,
              restaurant: record.restaurant,
              calories: record.calories,
              price: record.price,
              photo_url: record.photo_url || null,   // Supabase user upload
              image_url: record.image_url || null,   // DB food image
              type: record.type,
              food_type: record.food_type || '未分類',
              quantity: record.quantity,
              estimated_calories: record.estimated_calories,
              estimation_confidence: record.estimation_confidence,
              protein: record.protein,
              fat: record.fat,
              sugar: record.sugar,
              sodium: record.sodium,
              carb: record.carb,
              caffeine: record.caffeine,
              mealtime: record.mealtime,
              date: record.date
            }))
          : []
        
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
      
      foodRecords.value.forEach(item => {
        totalCalories += (item.calories * item.quantity)
      })
      
      dailySummary.value.calories = Math.round(totalCalories)
    }

    // 添加食物到指定餐點
    const addFood = () => {
      // TODO: 導航到食物搜尋頁面或打開食物選擇彈窗
      router.push({
        path: '/food/search',
        query: {
          returnTo: '/food/record',
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

    const getDefaultMealtime = () => {
      const hour = new Date().getHours()
      if (hour < 10) return '早餐'
      if (hour < 15) return '午餐'
      if (hour < 21) return '晚餐'
      return '點心'
    }

    const createEmptyCustomForm = () => ({
      custom_name: '',
      custom_calories: '',
      custom_price: '',
      custom_type: '',
      custom_restaurant: '',
      quantity: 1,
      mealtime: getDefaultMealtime(),
      photo_url: '',
      photo_path: '',
      photo_mime_type: '',
      estimated_name: '',
      estimated_calories: null,
      estimated_protein: null,
      estimated_fat: null,
      estimated_carb: null,
      estimated_sugar: null,
      estimated_sodium: null,
      estimation_provider: '',
      estimation_confidence: null,
      estimation_notes: ''
    })

    const resetPhotoEstimate = () => {
      photoFile.value = null
      photoUploadLoading.value = false
      photoEstimateLoading.value = false
      photoEstimateResult.value = null
      if (photoPreviewUrl.value) {
        URL.revokeObjectURL(photoPreviewUrl.value)
      }
      photoPreviewUrl.value = ''
    }

    const handlePhotoFileChange = async (event) => {
      const [file] = event.target.files || []
      if (!file) {
        return
      }

      resetPhotoEstimate()
      photoFile.value = file
      photoPreviewUrl.value = URL.createObjectURL(file)
      customForm.value.photo_url = ''
      customForm.value.photo_path = ''
      customForm.value.photo_mime_type = ''
      customForm.value.estimated_name = ''
      customForm.value.estimated_calories = null
      customForm.value.estimated_protein = null
      customForm.value.estimated_fat = null
      customForm.value.estimated_carb = null
      customForm.value.estimated_sugar = null
      customForm.value.estimated_sodium = null
      customForm.value.estimation_provider = ''
      customForm.value.estimation_confidence = null
      customForm.value.estimation_notes = ''
      await uploadCustomFoodPhoto(file)
    }

    const applyPhotoEstimateToForm = (estimate) => {
      customForm.value.custom_name = estimate.estimated_name || customForm.value.custom_name
      customForm.value.custom_calories = estimate.estimated_calories ?? customForm.value.custom_calories
      customForm.value.custom_type = estimate.estimated_type || customForm.value.custom_type
      customForm.value.custom_restaurant = estimate.estimated_restaurant || customForm.value.custom_restaurant
      customForm.value.custom_price = estimate.estimated_price ?? customForm.value.custom_price
      customForm.value.photo_url = estimate.photo_url || ''
      customForm.value.photo_path = estimate.photo_path || ''
      customForm.value.photo_mime_type = estimate.photo_mime_type || ''
      customForm.value.estimated_name = estimate.estimated_name || ''
      customForm.value.estimated_calories = estimate.estimated_calories
      customForm.value.estimated_protein = estimate.estimated_protein ?? null
      customForm.value.estimated_fat = estimate.estimated_fat ?? null
      customForm.value.estimated_carb = estimate.estimated_carb ?? null
      customForm.value.estimated_sugar = estimate.estimated_sugar ?? null
      customForm.value.estimated_sodium = estimate.estimated_sodium ?? null
      customForm.value.estimation_provider = estimate.estimation_provider || ''
      customForm.value.estimation_confidence = estimate.estimation_confidence
      customForm.value.estimation_notes = estimate.estimation_notes || ''
    }

    const applyUploadedPhotoToForm = (uploadResult) => {
      customForm.value.photo_url = uploadResult.photo_url || ''
      customForm.value.photo_path = uploadResult.photo_path || ''
      customForm.value.photo_mime_type = uploadResult.photo_mime_type || ''
    }

    const uploadCustomFoodPhoto = async (fileToUpload = null) => {
      const uploadTarget = fileToUpload || photoFile.value
      if (!uploadTarget) {
        ElMessage.warning('請先選擇餐點照片')
        return false
      }

      const userId = localStorage.getItem('userId')
      if (!userId) {
        ElMessage.warning('請先登入')
        return false
      }

      photoUploadLoading.value = true
      try {
        const formData = new FormData()
        formData.append('user_id', userId)
        formData.append('image', uploadTarget)

        const { data } = await api.post('/api/food/record/photo-upload', formData)
        applyUploadedPhotoToForm(data)
        ElMessage.success('照片已自動上傳，可直接儲存或再做 AI 估算')
        return true
      } catch (error) {
        console.error('照片上傳失敗:', error)
        ElMessage.error(error.response?.data?.error || '照片上傳失敗，請稍後再試')
        return false
      } finally {
        photoUploadLoading.value = false
      }
    }

    const estimateCustomFoodFromPhoto = async () => {
      if (!photoFile.value && !customForm.value.photo_url) {
        ElMessage.warning('請先選擇或上傳餐點照片')
        return
      }

      const userId = localStorage.getItem('userId')
      if (!userId) {
        ElMessage.warning('請先登入')
        return
      }

      photoEstimateLoading.value = true
      try {
        const formData = new FormData()
        formData.append('user_id', userId)
        if (customForm.value.photo_url) {
          formData.append('photo_url', customForm.value.photo_url)
          if (customForm.value.photo_path) {
            formData.append('photo_path', customForm.value.photo_path)
          }
          if (customForm.value.photo_mime_type) {
            formData.append('photo_mime_type', customForm.value.photo_mime_type)
          }
        } else {
          formData.append('image', photoFile.value)
        }

        const { data } = await api.post('/api/food/record/photo-estimate', formData, {
          timeout: 70000
        })
        photoEstimateResult.value = data
        applyPhotoEstimateToForm(data)
        ElMessage.success('已完成照片辨識，請確認內容後再儲存')
      } catch (error) {
        console.error('照片辨識失敗:', error)
        if (error.code === 'ECONNABORTED') {
          ElMessage.error('照片辨識逾時，請稍後重試（AI 分析通常需要 10 到 60 秒）')
        } else {
          ElMessage.error(error.response?.data?.error || '照片辨識失敗，請稍後再試')
        }
      } finally {
        photoEstimateLoading.value = false
      }
    }

    // 全局自訂食物表單
    const customForm = ref(createEmptyCustomForm())
    const submitCustomFood = async () => {
      // 驗證
      if (!customForm.value.custom_name || !customForm.value.custom_calories || !customForm.value.mealtime) {
        ElMessage.error('請填寫必填欄位')
        return
      }

      if (photoUploadLoading.value) {
        ElMessage.warning('照片仍在上傳中，請稍候再送出')
        return
      }

      try {
        submitCustomLoading.value = true
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入')
          return
        }

        // If user selected a photo but auto-upload did not complete, retry before submit.
        if (photoFile.value && !customForm.value.photo_url) {
          const uploaded = await uploadCustomFoodPhoto(photoFile.value)
          if (!uploaded || !customForm.value.photo_url) {
            ElMessage.error('照片上傳尚未完成，請稍後再試')
            return
          }
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
          date: selectedDateString.value,
          photo_url: customForm.value.photo_url,
          photo_path: customForm.value.photo_path,
          photo_mime_type: customForm.value.photo_mime_type,
          estimated_name: customForm.value.estimated_name,
          estimated_calories: customForm.value.estimated_calories,
          estimated_protein: customForm.value.estimated_protein,
          estimated_fat: customForm.value.estimated_fat,
          estimated_carb: customForm.value.estimated_carb,
          estimated_sugar: customForm.value.estimated_sugar,
          estimated_sodium: customForm.value.estimated_sodium,
          estimation_provider: customForm.value.estimation_provider,
          estimation_confidence: customForm.value.estimation_confidence,
          estimation_notes: customForm.value.estimation_notes
        }
        await api.post('/api/food/record', payload)
        ElMessage.success('自訂飲食紀錄已新增')
        // 清空表單
        customForm.value = createEmptyCustomForm()
        resetPhotoEstimate()
        // 重新載入紀錄
        loadFoodRecords()
      } catch (err) {
        ElMessage.error(err.response?.data?.error || '新增失敗，請稍後再試')
      } finally {
        submitCustomLoading.value = false
      }
    }

// 初始化
onMounted(() => {
  // 加載當前日期的食物記錄
  loadFoodRecords()
  fetchCalorieGoal()
})
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
  gap: 12px;
  flex-wrap: wrap;
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
  margin: 0;
}

.current-date {
  min-width: min(100%, 320px);
  padding: 10px 20px;
  background: white;
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: center;
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
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
  margin-bottom: 30px;
  overflow: hidden;
}

.summary-header {
  padding: 16px 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
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
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-bar.exceed {
  background: #f56c6c;
}

/* 餐點卡片 */
.records-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.records-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #2b2b2b;
}

.meals-container {
  display: block;
  margin-bottom: 40px;
}

@media (max-width: 900px) {
  .records-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }
}

.meal-card {
  background: white;
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.add-food-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
  color: white;
  border: none;
  border-radius: var(--btn-radius);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: var(--shadow-button);
}

.add-food-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
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
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #edf1f5;
  overflow: hidden;
  transition: all 0.3s;
}

.food-item-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.food-item-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
}

.food-item-info {
  flex: 1;
  min-width: 0;
}

.food-item-topline {
  margin-bottom: 8px;
}

.mealtime-chip {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.mealtime-chip.meal-breakfast {
  background: #fff0dc;
  color: #ab6a0f;
}

.mealtime-chip.meal-lunch {
  background: #ffe8dd;
  color: #b2531d;
}

.mealtime-chip.meal-dinner {
  background: #e7eefc;
  color: #2e5394;
}

.mealtime-chip.meal-snack {
  background: #efe7ff;
  color: #6642a8;
}

.mealtime-chip.meal-unknown {
  background: #f1f5f9;
  color: #64748b;
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
  flex-direction: column;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
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
.delete-btn.icon-only {
  width: 34px;
  height: 34px;
  padding: 0;
  border-radius: 8px;
}
.delete-btn:hover {
  background: #fee2e2;
  border-color: #ef4444;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

/* 無記錄狀態 */
.no-records-card {
  background: white;
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
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
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
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
.edit-btn.icon-only {
  width: 34px;
  height: 34px;
  margin-right: 0;
  padding: 0;
  border-radius: 8px;
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
  border-radius: var(--surface-radius-md);
  box-shadow: var(--shadow-card);
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
.photo-estimate-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px dashed #f0c78f;
  border-radius: 14px;
  background: #fff8ef;
}
.photo-estimate-copy h4 {
  margin: 0 0 6px;
  font-size: 16px;
  color: #9a5a00;
}
.photo-estimate-copy p {
  margin: 0;
  color: #7a6a52;
  line-height: 1.5;
  font-size: 14px;
}
.photo-estimate-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.photo-input {
  display: none;
}
.photo-picker-btn,
.estimate-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid #efc78b;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}
.photo-picker-btn {
  background: #fff;
  color: #b76b00;
}
.estimate-btn {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: var(--shadow-button);
}
.estimate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
.photo-picker-btn:hover,
.estimate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}
.photo-preview-block {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  align-items: stretch;
  padding: 4px 0;
}
.photo-preview-column {
  display: grid;
  gap: 10px;
}
.photo-preview-image {
  width: 220px;
  height: 168px;
  object-fit: cover;
  border-radius: 12px;
  background: #f1f5f9;
  border: 1px solid #ead9bd;
}
.photo-status-group {
  display: grid;
  gap: 6px;
}
.photo-estimate-column {
  display: grid;
  align-content: start;
}
.photo-estimate-result {
  padding: 4px 2px;
}
.photo-estimate-placeholder {
  padding: 4px 2px;
  min-height: 116px;
  display: grid;
  align-content: center;
}
.estimate-result-title {
  font-size: 13px;
  font-weight: 700;
  color: #a45f00;
  margin-bottom: 10px;
}
.estimate-result-row {
  display: grid;
  grid-template-columns: auto auto;
  justify-content: start;
  column-gap: 10px;
  margin-bottom: 8px;
  color: #5b6472;
  font-size: 14px;
}
.estimate-result-row.compact {
  margin-bottom: 6px;
  font-size: 13px;
}
.estimate-result-row strong {
  color: #1f2937;
  font-weight: 700;
}
.estimate-nutrient-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2px 12px;
  margin-bottom: 6px;
}
.estimate-notes {
  margin: 8px 0 0;
  color: #7b7280;
  font-size: 13px;
  line-height: 1.5;
}
.estimate-notes.status-ok {
  margin: 0;
  color: #27764f;
  font-weight: 600;
}
.custom-food-form .form-row {
  display: flex;
  gap: 12px;
}
.custom-food-form input,
.custom-food-form select {
  flex: 1;
  min-width: 0;
  min-height: 44px;
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
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-darker) 100%);
  color: #fff;
  border: none;
  border-radius: var(--btn-radius);
  min-height: 44px;
  white-space: nowrap;
  padding: 8px 18px;
  font-weight: 600;
  font-size: 15px;
  transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: var(--shadow-button);
  transition: background 0.2s;
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}

@media (max-width: 768px) {
  .photo-preview-block,
  .custom-food-form .form-row {
    display: grid;
    grid-template-columns: 1fr;
  }

  .photo-preview-image {
    width: 100%;
    max-width: 100%;
    height: 180px;
  }

  .estimate-nutrient-grid {
    grid-template-columns: 1fr;
  }
}


.food-image-container {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-right: 18px;
  flex-shrink: 0;
  width: 120px;
}
.food-image-primary {
  width: 120px;
  height: 120px;
  background-color: #f5f5f5;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}
.food-image-secondary {
  width: 120px;
  height: 64px;
  background-color: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}
.food-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}
.food-image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
.image-source-badge {
  position: absolute;
  bottom: 4px;
  left: 4px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 999px;
  line-height: 1.4;
  pointer-events: none;
  z-index: 3;
}
.image-source-badge.user-photo {
  background: rgba(230, 130, 0, 0.88);
  color: #fff;
}
.image-source-badge.db-image {
  background: rgba(60, 120, 210, 0.82);
  color: #fff;
}
.calorie-on-image-button {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 38px;
  height: 38px;
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
  font-size: 0.82rem;
}

.calorie-on-image-button .calorie-value {
  margin-bottom: 0;
  font-size: 0.85rem;
  color: white;
}

.calorie-on-image-button .calorie-unit {
  font-size: 0.6rem;
  opacity: 0.95;
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

@media (max-width: 1024px) {
  .container {
    padding: 0 18px 28px;
  }

  .photo-preview-block {
    grid-template-columns: minmax(180px, 220px) 1fr;
  }

  .food-item-content {
    gap: 14px;
  }

  .food-item-details {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 14px 24px;
  }

  .page-title {
    font-size: 24px;
    margin-bottom: 20px;
  }

  .date-navigation {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr) 44px;
    gap: 10px;
    align-items: center;
    margin-bottom: 22px;
  }

  .date-picker-container {
    width: 100%;
  }

  .current-date {
    width: 100%;
    min-width: 0;
    padding: 12px 14px;
    font-size: 14px;
  }

  .nutrition-summary-card {
    margin-bottom: 22px;
  }

  .summary-header {
    padding: 14px 16px;
  }

  .summary-title {
    font-size: 16px;
  }

  .calorie-summary {
    padding: 16px;
  }

  .calorie-info {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .calorie-item {
    padding: 0;
  }

  .calorie-divider {
    display: none;
  }

  .calorie-value {
    font-size: 24px;
    margin-bottom: 6px;
  }

  .custom-food-form-card {
    padding: 18px 16px 16px;
    margin-bottom: 24px;
  }

  .custom-form-title {
    font-size: 17px;
    margin-bottom: 10px;
  }

  .photo-estimate-panel {
    padding: 14px;
    border-radius: 12px;
  }

  .photo-estimate-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .photo-picker-btn,
  .estimate-btn,
  .submit-btn,
  .add-food-btn {
    width: 100%;
    justify-content: center;
  }

  .photo-preview-block,
  .custom-food-form .form-row {
    display: grid;
    grid-template-columns: 1fr;
  }

  .photo-preview-image {
    width: 100%;
    max-width: 100%;
    height: 200px;
  }

  .estimate-nutrient-grid {
    grid-template-columns: 1fr;
  }

  .records-toolbar {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
  }

  .records-title {
    font-size: 18px;
  }

  .meal-content {
    padding: 14px;
  }

  .food-items {
    gap: 12px;
  }

  .food-item-content {
    flex-direction: column;
    padding: 14px;
  }

  .food-image-container {
    width: 100%;
    margin-right: 0;
    flex-direction: row;
    align-items: stretch;
  }

  .food-image-primary {
    width: 100%;
    height: 180px;
    flex: 1;
  }

  .food-image-secondary {
    width: 84px;
    height: 84px;
    align-self: flex-end;
  }

  .food-item-name {
    font-size: 17px;
    margin-bottom: 10px;
  }

  .food-item-details {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .detail-row {
    justify-content: space-between;
    gap: 10px;
    padding-bottom: 6px;
    border-bottom: 1px dashed #edf1f5;
  }

  .detail-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .detail-value {
    text-align: right;
  }

  .nutrition-table td {
    padding: 4px 6px 4px 0;
  }

  .food-item-actions {
    width: 100%;
    flex-direction: row;
    justify-content: flex-end;
    padding-top: 4px;
  }

  .delete-btn.icon-only,
  .edit-btn.icon-only {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 560px) {
  .food-record-page {
    padding: 14px 0;
  }

  .date-navigation {
    grid-template-columns: 40px minmax(0, 1fr) 40px;
  }

  .date-nav-btn {
    width: 40px;
    height: 40px;
  }

  .current-date {
    gap: 6px;
    padding: 11px 12px;
    border-radius: 12px;
  }

  .current-date span {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .photo-estimate-copy h4 {
    font-size: 15px;
  }

  .photo-estimate-copy p,
  .detail-label,
  .detail-value,
  .calorie-label {
    font-size: 13px;
  }

  .photo-preview-image,
  .food-image-primary {
    height: 168px;
  }

  .food-image-container {
    flex-direction: column;
  }

  .food-image-secondary {
    width: 100%;
    height: 68px;
    align-self: auto;
  }

  .calorie-on-image-button {
    width: 42px;
    height: 42px;
  }

  .food-item-card {
    border-radius: 12px;
  }

  .food-item-content {
    padding: 12px;
    gap: 12px;
  }

  .custom-food-form-card,
  .meal-content,
  .no-records-card,
  .loading-state {
    border-radius: 14px;
  }

  .no-records-card,
  .loading-state {
    margin: 28px 0;
    padding: 28px 16px;
  }
}
</style>



