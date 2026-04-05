<template>
  <div class="food-search-page">
    <div class="container">
      <h1 class="page-title">食物搜尋</h1>

      <div v-if="isGuest" class="guest-mode-banner" role="status" aria-live="polite">
        <div class="guest-mode-text">
          <strong>訪客模式：</strong>你可以先看推薦與搜尋食物，登入後可使用最愛、記錄與報表功能。
        </div>
        <button type="button" class="guest-login-btn" @click="goToLogin">立即登入</button>
      </div>

      <!-- 搜尋表單 -->
      <div class="search-form-container">
        <div class="search-form-card" @keydown.enter="handleSearch">
          <div class="search-form-grid">
            <!-- 第一行：名稱 / 類型 -->
            <div class="form-group col-6">
                <label class="form-label">食物名稱</label>
                <div class="input-with-icon">
                  <el-icon class="form-icon"><Food /></el-icon>
                  <input 
                    type="text" 
                    class="form-control search-prominent" 
                    placeholder="輸入食物名稱" 
                    v-model="filters.name"
                    @input="handleFilterChange"
                    aria-label="食物名稱關鍵字"
                  />
                </div>
              </div>
              <div class="form-group col-6">
                <label class="form-label">食物類型</label>
                <div class="foodtype-chip-list">
                  <button
                    v-for="type in foodTypes"
                    :key="type"
                    type="button"
                    class="foodtype-chip-btn"
                    :class="{ active: filters.food_type.includes(type) }"
                    @click="toggleFoodType(type)"
                    :aria-pressed="filters.food_type.includes(type)"
                    :aria-label="`切換類型 ${type}`"
                  >
                    {{ type }}
                  </button>
                </div>
              </div>
            
            <!-- 第二行：價格 / 熱量 -->
            <div class="form-group col-6">
                <label class="form-label">價格範圍</label>
                <div class="range-slider" role="group" aria-label="價格範圍選擇">
                  <div class="range-summary">目前：{{ priceRangeLabel }}</div>
                  <div class="range-values">
                    <div class="range-input-group">
                      <span class="range-unit-prefix">$</span>
                      <input
                        type="number"
                        class="range-number-input"
                        v-model.number="priceMinValue"
                        :min="priceRangeMin"
                        :max="priceMaxValue"
                        :step="priceStep"
                        @change="handlePriceMinInput"
                        aria-label="最低價格"
                      />
                    </div>
                    <span class="value-sep">—</span>
                    <div class="range-input-group">
                      <span class="range-unit-prefix">$</span>
                      <input
                        type="number"
                        class="range-number-input"
                        v-model.number="priceMaxValue"
                        :min="priceMinValue"
                        :max="priceRangeMax"
                        :step="priceStep"
                        @change="handlePriceMaxInput"
                        aria-label="最高價格"
                      />
                    </div>
                  </div>
                  <div class="slider-track-wrapper">
                    <span class="track-bound">$0</span>
                    <div class="slider-track">
                      <div class="slider-fill" :style="{ left: priceLeftPercent + '%', right: priceRightPercent + '%' }"></div>
                      <input
                        type="range"
                        class="slider-input"
                        :min="priceRangeMin"
                        :max="priceRangeMax"
                        :step="priceStep"
                        v-model.number="priceMinValue"
                        @input="handlePriceMinInput"
                        aria-label="最低價格滑桿"
                      />
                      <input
                        type="range"
                        class="slider-input"
                        :min="priceRangeMin"
                        :max="priceRangeMax"
                        :step="priceStep"
                        v-model.number="priceMaxValue"
                        @input="handlePriceMaxInput"
                        aria-label="最高價格滑桿"
                      />
                    </div>
                    <span class="track-bound">${{ priceRangeMax }}</span>
                  </div>
                  <div class="preset-chip-list" aria-label="價格快速篩選">
                    <button
                      v-for="preset in pricePresets"
                      :key="preset.label"
                      type="button"
                      class="preset-chip"
                      :class="{ active: priceMinValue === preset.min && priceMaxValue === preset.max }"
                      @click="applyPricePreset(preset)"
                    >
                      {{ preset.label }}
                    </button>
                  </div>
                </div>
              </div>
              <div class="form-group col-6">
                <label class="form-label">熱量範圍</label>
                <div class="range-slider" role="group" aria-label="熱量範圍選擇">
                  <div class="range-summary">目前：{{ calRangeLabel }}</div>
                  <div class="range-values">
                    <div class="range-input-group">
                      <input
                        type="number"
                        class="range-number-input"
                        v-model.number="calMinValue"
                        :min="calRangeMin"
                        :max="calMaxValue"
                        :step="calStep"
                        @change="handleCalMinInput"
                        aria-label="最低熱量"
                      />
                      <span class="range-unit-suffix">kcal</span>
                    </div>
                    <span class="value-sep">—</span>
                    <div class="range-input-group">
                      <input
                        type="number"
                        class="range-number-input"
                        v-model.number="calMaxValue"
                        :min="calMinValue"
                        :max="calRangeMax"
                        :step="calStep"
                        @change="handleCalMaxInput"
                        aria-label="最高熱量"
                      />
                      <span class="range-unit-suffix">kcal</span>
                    </div>
                  </div>
                  <div class="slider-track-wrapper">
                    <span class="track-bound">0</span>
                    <div class="slider-track">
                      <div class="slider-fill" :style="{ left: calLeftPercent + '%', right: calRightPercent + '%' }"></div>
                      <input
                        type="range"
                        class="slider-input"
                        :min="calRangeMin"
                        :max="calRangeMax"
                        :step="calStep"
                        v-model.number="calMinValue"
                        @input="handleCalMinInput"
                        aria-label="最低熱量滑桿"
                      />
                      <input
                        type="range"
                        class="slider-input"
                        :min="calRangeMin"
                        :max="calRangeMax"
                        :step="calStep"
                        v-model.number="calMaxValue"
                        @input="handleCalMaxInput"
                        aria-label="最高熱量滑桿"
                      />
                    </div>
                    <span class="track-bound">{{ calRangeMax }}</span>
                  </div>
                  <div class="preset-chip-list" aria-label="熱量快速篩選">
                    <button
                      v-for="preset in calPresets"
                      :key="preset.label"
                      type="button"
                      class="preset-chip"
                      :class="{ active: calMinValue === preset.min && calMaxValue === preset.max }"
                      @click="applyCalPreset(preset)"
                    >
                      {{ preset.label }}
                    </button>
                  </div>
                </div>
              </div>
            
            <!-- 第三行：餐廳 / 搜尋按鈕 -->
            <div class="form-group col-12">
                <label class="form-label">餐廳</label>
                <div class="restaurant-logo-list">
                  <button 
                    v-for="r in restaurants"
                    :key="r.id"
                    type="button" 
                    class="restaurant-logo-btn"
                    :class="{ active: filters.restaurants.includes(r.name) }"
                    @click="toggleRestaurant(r.name)"
                    :aria-pressed="filters.restaurants.includes(r.name)"
                    :aria-label="`切換餐廳 ${r.name}`"
                  >
                    <img :src="r.logo" :alt="r.name" class="restaurant-logo-img" />
                    <span>{{ r.name }}</span>
                  </button>
                </div>
              </div>
              <div class="form-group search-btn-container col-12 align-right">
                <button type="button" class="search-btn" @click="handleSearch" aria-label="執行搜尋">
                  <el-icon><Search /></el-icon>
                  搜尋
                </button>
              </div>
            
          </div>
        </div>
      </div>

      <!-- 搜尋結果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <h2 class="section-title">
          搜尋結果 
          <span class="result-count">({{ searchResults.length }} 筆)</span>
          <span v-if="isLoading" class="loading-indicator">載入中...</span>
        </h2>
        <div class="food-grid" role="list">
          <div 
            class="food-card" 
            v-for="(food, index) in visibleResults" 
            :key="food.id || index"
            v-intersection-observer="onIntersection"
            role="listitem"
            tabindex="0"
            :aria-label="`食物卡片 ${food.name}`"
          >
            <div class="food-image-container" v-if="food.ImageUrl || food.image_url || food.imageUrl">
              <div class="image-loader" 
                   v-if="food && food.id !== undefined && food.id !== null && imageLoaded && typeof imageLoaded === 'object' && !imageLoaded[String(food.id)]">
                <div class="loading-spinner"></div>
              </div>
              <img
                :src="food.ImageUrl || food.image_url || food.imageUrl"
                :data-src="food.ImageUrl || food.image_url || food.imageUrl"
                @error="setDefaultImageOnError"
                :alt="food.name"
                class="food-image lazy"
                @load="onImageLoad(food)"
                loading="lazy"
              >
              <div class="calorie-on-image-button">
                <span class="calorie-value">{{ formatCalories(food.calories) }}</span>
                <span class="calorie-unit">大卡</span>
              </div>
            </div>
            <div class="food-card-content">
              <div class="food-info">
                <div class="food-name-price-line">
                <h3 class="food-name">{{ food.name }}</h3>
                  <span class="food-price-prominent">${{ formatPrice(food.price) }}</span>
                  <el-tooltip placement="top" effect="dark" :disabled="!hasNutritionInfo(food)">
                    <template #content>
                      <div class="nutrition-tooltip improved-tooltip">
                        <h4>營養資訊</h4>
                        <table class="nutrition-table">
                          <tr v-if="food.Protein !== null && food.Protein !== undefined">
                            <td><el-icon class="icon"><IceCream /></el-icon> 蛋白質</td>
                            <td><strong class="nutrient protein">{{ food.Protein }}g</strong></td>
                          </tr>
                          <tr v-if="food.Fat !== null && food.Fat !== undefined">
                            <td><el-icon class="icon"><MilkTea /></el-icon> 脂肪</td>
                            <td><strong class="nutrient fat">{{ food.Fat }}g</strong></td>
                          </tr>
                          <tr v-if="food.Sugar !== null && food.Sugar !== undefined">
                            <td><el-icon class="icon"><Sugar /></el-icon> 糖</td>
                            <td><strong class="nutrient sugar">{{ food.Sugar }}g</strong></td>
                          </tr>
                          <tr v-if="food.Sodium !== null && food.Sodium !== undefined">
                            <td><el-icon class="icon"><Coin /></el-icon> 鈉</td>
                            <td><strong class="nutrient sodium">{{ food.Sodium }}mg</strong></td>
                          </tr>
                          <tr v-if="food.Carb !== null && food.Carb !== undefined">
                            <td><el-icon class="icon"><Burger /></el-icon> 碳水</td>
                            <td><strong class="nutrient carb">{{ food.Carb }}g</strong></td>
                          </tr>
                          <tr v-if="food.Caffeine !== null && food.Caffeine !== undefined">
                            <td><el-icon class="icon"><Coffee /></el-icon> 咖啡因</td>
                            <td><strong class="nutrient caffeine">{{ food.Caffeine }}mg</strong></td>
                          </tr>
                        </table>
                        <div v-if="!hasNutritionInfo(food)" class="no-nutrition-data">暫無詳細營養數據</div>
                      </div>
                    </template>
                    <el-icon class="nutrition-info-icon" v-if="hasNutritionInfo(food)"><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <div class="food-details">
                  <div class="detail-item">
                    <el-icon class="icon"><Shop /></el-icon>
                    <span>{{ food.restaurant || '未知餐廳' }}</span>
                  </div>
                  <div class="detail-item">
                    <el-icon class="icon"><DataLine /></el-icon>
                    <span>{{ food.calories }} 大卡</span>
                  </div>
                  <div class="detail-item">
                    <el-icon class="icon"><Food /></el-icon>
                    <span>{{ food.food_type || '未分類' }}</span>
                  </div>
                  <div class="detail-item">
                    <el-icon class="icon"><Menu /></el-icon>
                    <span>{{ food.type }}</span>
                  </div>
                </div>
              </div>
              <div class="food-actions">
                <button class="action-btn calculator-btn" @click="openExerciseModal(food)" aria-label="開啟運動計算" title="運動計算">
                  <el-icon><DataAnalysis /></el-icon>
                </button>
                <button class="action-btn favorite-btn" :disabled="favoriteFoodIds.has(food.id)" @click="addToFavorites(food)" v-if="!favoriteFoodIds.has(food.id)" aria-label="加入最愛" title="加入最愛">
                  <el-icon><Star /></el-icon>
                </button>
                <button class="action-btn favorite-btn" disabled v-else aria-label="已收藏" title="已收藏">
                  <el-icon style="color: #E6A23C"><StarFilled /></el-icon>
                </button>
                <button class="action-btn record-btn" @click="openFoodRecordModal(food)" aria-label="加入記錄" title="加入記錄">
                  <el-icon><Plus /></el-icon>
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- 無限滾動 sentinel -->
        <div v-if="canLoadMore" ref="infiniteSentinel" class="infinite-sentinel" aria-hidden="true"></div>
      </div>

      <!-- 推薦清單 -->
      <div v-if="!hasSearched && recommendedCategories.length > 0" class="recommended-foods">
        <h2 class="section-title">推薦清單</h2>
        <div v-for="(category, idx) in recommendedCategories" :key="idx" class="recommend-category-block">
          <div class="recommend-category-header">
            <h3 class="recommend-category-title">{{ category.title }}</h3>
            <span class="recommend-category-reason">{{ category.reason }}</span>
          </div>
        <div class="food-grid">
            <div class="food-card" v-for="(food, index) in category.foods" :key="food.id || food.food_id || index">
              <div class="food-image-container" v-if="food.ImageUrl || food.image_url || food.imageUrl">
                <div class="image-loader" 
                     v-if="food && food.id !== undefined && food.id !== null && imageLoaded && typeof imageLoaded === 'object' && !imageLoaded[String(food.id)]">
                  <div class="loading-spinner"></div>
                </div>
                <img
                  :src="food.ImageUrl || food.image_url || food.imageUrl"
                  @error="setDefaultImageOnError"
                  :alt="food.name"
                  class="food-image"
                  @load="onImageLoad(food)"
                >
                <div class="calorie-on-image-button">
                  <span class="calorie-value">{{ formatCalories(food.calories) }}</span>
                  <span class="calorie-unit">大卡</span>
                </div>
              </div>
            <div class="food-card-content">
              <div class="food-info">
                  <div class="food-name-price-line">
                <h3 class="food-name">{{ food.name }}</h3>
                    <span class="food-price-prominent">${{ formatPrice(food.price) }}</span>
                    <el-tooltip placement="top" effect="dark" :disabled="!hasNutritionInfo(food)">
                      <template #content>
                        <div class="nutrition-tooltip improved-tooltip">
                          <h4>營養資訊</h4>
                          <table class="nutrition-table">
                            <tr v-if="food.Protein !== null && food.Protein !== undefined">
                              <td><el-icon class="icon"><IceCream /></el-icon> 蛋白質</td>
                              <td><strong class="nutrient protein">{{ food.Protein }}g</strong></td>
                            </tr>
                            <tr v-if="food.Fat !== null && food.Fat !== undefined">
                              <td><el-icon class="icon"><MilkTea /></el-icon> 脂肪</td>
                              <td><strong class="nutrient fat">{{ food.Fat }}g</strong></td>
                            </tr>
                            <tr v-if="food.Sugar !== null && food.Sugar !== undefined">
                              <td><el-icon class="icon"><Sugar /></el-icon> 糖</td>
                              <td><strong class="nutrient sugar">{{ food.Sugar }}g</strong></td>
                            </tr>
                            <tr v-if="food.Sodium !== null && food.Sodium !== undefined">
                              <td><el-icon class="icon"><Coin /></el-icon> 鈉</td>
                              <td><strong class="nutrient sodium">{{ food.Sodium }}mg</strong></td>
                            </tr>
                            <tr v-if="food.Carb !== null && food.Carb !== undefined">
                              <td><el-icon class="icon"><Burger /></el-icon> 碳水</td>
                              <td><strong class="nutrient carb">{{ food.Carb }}g</strong></td>
                            </tr>
                            <tr v-if="food.Caffeine !== null && food.Caffeine !== undefined">
                              <td><el-icon class="icon"><Coffee /></el-icon> 咖啡因</td>
                              <td><strong class="nutrient caffeine">{{ food.Caffeine }}mg</strong></td>
                            </tr>
                          </table>
                          <div v-if="!hasNutritionInfo(food)" class="no-nutrition-data">暫無詳細營養數據</div>
                        </div>
                      </template>
                      <el-icon class="nutrition-info-icon" v-if="hasNutritionInfo(food)"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                <div class="food-details">
                  <div class="detail-item">
                    <el-icon class="icon"><Shop /></el-icon>
                    <span>{{ food.restaurant || '未知餐廳' }}</span>
                  </div>
                  <div class="detail-item">
                    <el-icon class="icon"><Food /></el-icon>
                    <span>{{ food.food_type || '未分類' }}</span>
                  </div>
                  <div class="detail-item">
                    <el-icon class="icon"><Menu /></el-icon>
                    <span>{{ food.type }}</span>
                  </div>
                </div>
              </div>
              <div class="food-actions">
                <button class="action-btn calculator-btn" @click="openExerciseModal(food)" aria-label="開啟運動計算" title="運動計算">
                  <el-icon><DataAnalysis /></el-icon>
                </button>
                <button class="action-btn favorite-btn" :disabled="favoriteFoodIds.has(food.id)" @click="addToFavorites(food)" v-if="!favoriteFoodIds.has(food.id)" aria-label="加入最愛" title="加入最愛">
                  <el-icon><Star /></el-icon>
                </button>
                <button class="action-btn favorite-btn" disabled v-else aria-label="已收藏" title="已收藏">
                  <el-icon style="color: #E6A23C"><StarFilled /></el-icon>
                </button>
                  <button class="action-btn record-btn" @click="openFoodRecordModal(food)" aria-label="加入記錄" title="加入記錄">
                  <el-icon><Plus /></el-icon>
                </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-if="hasSearched && searchResults.length === 0 && !isLoading" class="no-results">
        <el-icon class="el-icon-search no-results-icon"></el-icon>
        <p>未找到符合條件的食物</p>
      </div>

      <!-- 載入中骨架 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>載入中...</p>
        <div class="food-grid">
          <div class="food-card skeleton" v-for="i in 6" :key="i">
            <div class="food-image-container skeleton-box"></div>
            <div class="food-card-content">
              <div class="skeleton-line w-3of4"></div>
              <div class="skeleton-line w-1of2"></div>
              <div class="skeleton-line w-full"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Exercise Calculator Modal -->
      <div v-if="exerciseModal" class="modal-overlay">
        <div class="modal modal-exercise">
          <div class="modal-header">
            <h3>運動計算機</h3>
            <button class="close-button" @click="closeExerciseModal" aria-label="關閉運動計算modal">&times;</button>
          </div>
          <div class="modal-body exercise-modal-body">
            <h4 class="section-title">收藏的運動</h4>
            <div v-if="userExercisePreferences.length > 0" class="exercise-pref-list">
              <div v-for="type in userExercisePreferences" :key="type" class="exercise-pref-item">
                <span class="exercise-icon">{{ getExerciseIcon(type) }}</span>
                <span class="exercise-name">{{ type }}</span>
                <span class="exercise-intensity">{{ getIntensityFlames(type) }}</span>
                <span class="exercise-intensity-text">{{ getExerciseIntensity(type) }}</span>
                <span class="exercise-minutes">
                  需 <strong>{{ exerciseResults[type] !== undefined && exerciseResults[type] !== null && exerciseResults[type] !== '' ? Number(exerciseResults[type]).toFixed(1) : '--' }}</strong> 分鐘
                </span>
              </div>
            </div>
            <div v-else class="empty-pref-tip">尚未設定偏好運動，可於下方查詢並加入！</div>
            <hr class="exercise-divider" />
            <h4 class="section-title">查詢所有運動</h4>
            <div class="all-exercise-row">
              <select v-model="selectedExercise" class="all-exercise-select">
                <option disabled value="">請選擇運動</option>
                <option v-for="ex in allExerciseNames" :key="ex" :value="ex">
                  {{ getExerciseIcon(ex) }} {{ ex }}
                </option>
              </select>
              <span v-if="selectedExercise" class="exercise-intensity">{{ getIntensityFlames(selectedExercise) }}</span>
              <span v-if="selectedExercise" class="exercise-intensity-text">{{ getExerciseIntensity(selectedExercise) }}</span>
              <span v-if="selectedExercise" class="exercise-minutes">
                需 <strong>{{ getSelectedExerciseMinutes }}</strong> 分鐘
              </span>
              <button
                v-if="selectedExercise && !userExercisePreferences.includes(selectedExercise)"
                @click="addToPreference(selectedExercise)"
                class="add-pref-btn"
              >加入偏好</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Add to Record Modal -->
      <FoodRecordModal v-model:visible="showRecordModal" :food="currentFood" @saved="onRecordSaved" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import FoodRecordModal from '@/components/food/FoodRecordModal.vue'
import { InfoFilled, Food, Shop, DataLine, Menu, IceCream, MilkTea, Sugar, Coin, Coffee, Burger, DataAnalysis, Star, StarFilled, Plus, Search } from '@element-plus/icons-vue'
import api from '@/services/api'

const DEFAULT_EXERCISES = ['跑步', '游泳', '騎腳踏車', '健走']

// 新增：防抖函數
function debounce(func, wait) {
  let timeout
  const debounced = function executedFunction(...args) {
    const later = () => {
      timeout = null
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
  debounced.cancel = () => {
    clearTimeout(timeout)
    timeout = null
  }
  return debounced
}

export default {
  name: 'FoodSearch',
  components: { FoodRecordModal, InfoFilled, Food, Shop, DataLine, Menu, IceCream, MilkTea, Sugar, Coin, Coffee, Burger, DataAnalysis, Star, StarFilled, Plus, Search },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const searchResults = ref([])
    const recommendedCategories = ref([])
    const isLoading = ref(false)
    const hasSearched = ref(false)
    const userPreferences = ref(null)
    const favoriteFoodIds = ref(new Set())
    const searchTimeout = ref(null)

    const filters = ref({
      priceMin: '',
      priceMax: '',
      calMin: '',
      calMax: '',
      name: '',
      restaurants: [],
      type: '',
      food_type: []
    })

    // 熱量滑桿設定
    const calRangeMin = 0
    const calRangeMax = 1500
    const calStep = 10
    const calMinValue = ref(calRangeMin)
    const calMaxValue = ref(800)
    const calPresets = [
      { label: '低卡 0-300', min: 0, max: 300 },
      { label: '輕食 300-600', min: 300, max: 600 },
      { label: '主餐 600-900', min: 600, max: 900 },
      { label: '高熱量 900-1500', min: 900, max: 1500 }
    ]

    const parseFilterNumber = (value) => {
      if (value === '' || value === null || value === undefined) return null
      const n = Number(value)
      return Number.isFinite(n) ? n : null
    }

    const syncCalValuesFromFilters = () => {
      const min = parseFilterNumber(filters.value.calMin)
      const max = parseFilterNumber(filters.value.calMax)
      calMinValue.value = min !== null ? Math.max(calRangeMin, Math.min(min, calRangeMax)) : calRangeMin
      calMaxValue.value = max !== null ? Math.max(calRangeMin, Math.min(max, calRangeMax)) : Math.min(calRangeMax, Math.max(calMinValue.value, 800))
      if (calMinValue.value > calMaxValue.value) {
        const t = calMinValue.value
        calMinValue.value = calMaxValue.value
        calMaxValue.value = t
      }
    }

    const commitCalRange = () => {
      filters.value.calMin = calMinValue.value
      filters.value.calMax = calMaxValue.value
      handleFilterChange()
    }

    const handleCalMinInput = () => {
      if (calMinValue.value > calMaxValue.value) calMinValue.value = calMaxValue.value
      commitCalRange()
    }
    const handleCalMaxInput = () => {
      if (calMaxValue.value < calMinValue.value) calMaxValue.value = calMinValue.value
      commitCalRange()
    }

    const applyCalPreset = (preset) => {
      calMinValue.value = preset.min
      calMaxValue.value = preset.max
      commitCalRange()
    }

    const calLeftPercent = computed(() => {
      const span = calRangeMax - calRangeMin
      return ((calMinValue.value - calRangeMin) / span) * 100
    })
    const calRightPercent = computed(() => {
      const span = calRangeMax - calRangeMin
      return 100 - ((calMaxValue.value - calRangeMin) / span) * 100
    })
    const calRangeLabel = computed(() => `${calMinValue.value} - ${calMaxValue.value} kcal`)

    // 價格滑桿設定
    const priceRangeMin = 0
    const priceRangeMax = 1000
    const priceStep = 10
    const priceMinValue = ref(priceRangeMin)
    const priceMaxValue = ref(300)
    const pricePresets = [
      { label: '銅板 0-100', min: 0, max: 100 },
      { label: '平價 100-200', min: 100, max: 200 },
      { label: '中價 200-350', min: 200, max: 350 },
      { label: '不限 0-1000', min: 0, max: 1000 }
    ]

    const syncPriceValuesFromFilters = () => {
      const min = parseFilterNumber(filters.value.priceMin)
      const max = parseFilterNumber(filters.value.priceMax)
      priceMinValue.value = min !== null ? Math.max(priceRangeMin, Math.min(min, priceRangeMax)) : priceRangeMin
      priceMaxValue.value = max !== null ? Math.max(priceRangeMin, Math.min(max, priceRangeMax)) : Math.min(priceRangeMax, Math.max(priceMinValue.value, 300))
      if (priceMinValue.value > priceMaxValue.value) {
        const t = priceMinValue.value
        priceMinValue.value = priceMaxValue.value
        priceMaxValue.value = t
      }
    }

    const commitPriceRange = () => {
      filters.value.priceMin = priceMinValue.value
      filters.value.priceMax = priceMaxValue.value
      handleFilterChange()
    }

    const handlePriceMinInput = () => {
      if (priceMinValue.value > priceMaxValue.value) priceMinValue.value = priceMaxValue.value
      commitPriceRange()
    }
    const handlePriceMaxInput = () => {
      if (priceMaxValue.value < priceMinValue.value) priceMaxValue.value = priceMinValue.value
      commitPriceRange()
    }

    const applyPricePreset = (preset) => {
      priceMinValue.value = preset.min
      priceMaxValue.value = preset.max
      commitPriceRange()
    }

    const priceLeftPercent = computed(() => {
      const span = priceRangeMax - priceRangeMin
      return ((priceMinValue.value - priceRangeMin) / span) * 100
    })
    const priceRightPercent = computed(() => {
      const span = priceRangeMax - priceRangeMin
      return 100 - ((priceMaxValue.value - priceRangeMin) / span) * 100
    })
    const priceRangeLabel = computed(() => `$${priceMinValue.value} - $${priceMaxValue.value}`)

    // 無限滾動顯示數量
    const itemsToShow = ref(20)
    const pageSize = 20
    const infiniteSentinel = ref(null)
    const canLoadMore = computed(() => searchResults.value.length > itemsToShow.value)

    // 防抖搜尋（單一 400ms 延遲，避免雙重 debounce 疊加至 800ms）
    const debouncedSearch = debounce(async () => {
      if (hasActiveFilters()) {
        itemsToShow.value = pageSize
        await performSearch()
      }
    }, 400)

    const handleFilterChange = () => {
      debouncedSearch()
    }

    const hasActiveFilters = () => {
      const { priceMin, priceMax, calMin, calMax, name, restaurants, type, food_type } = filters.value
      return (
        priceMin !== '' ||
        priceMax !== '' ||
        calMin !== '' ||
        calMax !== '' ||
        name.trim() !== '' ||
        restaurants.length > 0 ||
        type !== '' ||
        food_type.length > 0
      )
    }

    // 正規化快取鍵
    const normalizeFilters = (raw) => {
      const f = { ...raw }
      if (Array.isArray(f.restaurants)) f.restaurants = [...f.restaurants].sort()
      if (Array.isArray(f.food_type)) f.food_type = [...f.food_type].sort()
      return f
    }

    // 追蹤進行中的請求，供取消使用
    let currentAbortController = null

    const performSearch = async () => {
      if (!hasActiveFilters()) return

      const cached = getCachedResults(normalizeFilters(filters.value))
      if (cached) {
        searchResults.value = cached.results
        hasSearched.value = true
        return
      }

      // 取消上一個尚未完成的請求
      if (currentAbortController) {
        currentAbortController.abort()
      }
      currentAbortController = new AbortController()
      const signal = currentAbortController.signal

      isLoading.value = true
      hasSearched.value = true

      try {
        const params = {}
        if (filters.value.priceMin !== '') params.priceMin = filters.value.priceMin
        if (filters.value.priceMax !== '') params.priceMax = filters.value.priceMax
        if (filters.value.calMin !== '') params.calMin = filters.value.calMin
        if (filters.value.calMax !== '') params.calMax = filters.value.calMax
        if (filters.value.name.trim() !== '') params.name = filters.value.name.trim()
        if (filters.value.restaurants.length > 0) params.restaurant = filters.value.restaurants.join(',')
        if (filters.value.type !== '') params.type = filters.value.type
        if (filters.value.food_type.length > 0) params.food_type = filters.value.food_type.join(',')

        const { data } = await api.get('/api/food/', { params, signal })

        setCachedResults(normalizeFilters(filters.value), data)
        preloadImages(data)
        
        searchResults.value = data.map(item => ({
          id: item.id,
          name: item.name,
          calories: item.calories,
          price: item.price,
          type: item.type || '未分類',
          food_type: item.food_type || '未分類',
          restaurant: item.restaurant || '未知餐廳',
          ImageUrl: item.ImageUrl,
          Protein: item.Protein,
          Fat: item.Fat,
          Sugar: item.Sugar,
          Sodium: item.Sodium,
          Carb: item.Carb,
          Caffeine: item.Caffeine
        }))
      } catch (error) {
        if (error.code === 'ERR_CANCELED') return  // 被新請求取消，靜默忽略
        console.error('搜尋食物失敗:', error)
        ElMessage.error('搜尋食物失敗，請稍後再試')
        searchResults.value = []
      } finally {
        isLoading.value = false
      }
    }

    const handleSearch = async () => {
      debouncedSearch.cancel()
      itemsToShow.value = pageSize
      await performSearch()
    }

    const addToFavorites = async (food) => {
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入')
          return
        }
        await api.post('/api/myfavorite/favorites', {
            user_id: parseInt(userId),
            food_id: food.id
          })
        ElMessage.success('已添加到我的最愛')
        favoriteFoodIds.value = new Set([...favoriteFoodIds.value, food.id])
      } catch (error) {
        if (error?.response?.status === 409) {
          favoriteFoodIds.value = new Set([...favoriteFoodIds.value, food.id])
          ElMessage.info('此食物已在我的最愛')
          return
        }
        console.error('添加到最愛失敗:', error)
        ElMessage.error('添加到最愛失敗，請稍後再試')
      }
    }

    // Exercise Calculator  
    const exerciseModal = ref(false)
    const exerciseResults = ref({})
    const exerciseSearch = ref('')

    const showRecordModal = ref(false)
    const currentFood = ref(null)
    const openFoodRecordModal = (food) => {
      currentFood.value = food
      showRecordModal.value = true
    }
    const onRecordSaved = () => {
      router.push({ name: 'FoodRecord' })
    }

    const openExerciseModal = (food) => {
      exerciseModal.value = true
      calculateExercise(food.calories)
    }

    function normalizeExerciseName(name) {
      if (!name) return '';
      return name.replace(/\s+/g, '').replace(/[Ａ-Ｚａ-ｚ０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0)).toLowerCase();
    }

    const calculateExercise = async (calories) => {
      try {
        const userId = localStorage.getItem('userId')
        const { data } = await api.get('/api/food/exercise/calculator', { params: { calories, user_id: userId } })
        const showExercises = userExercisePreferences.value.length > 0
          ? userExercisePreferences.value
          : DEFAULT_EXERCISES
        const result = {}
        showExercises.forEach(type => {
          const normType = normalizeExerciseName(type)
          const found = data.exercises.find(e => normalizeExerciseName(e.type).startsWith(normType))
          result[type] = found ? found.duration : undefined
        })
        exerciseResults.value = result
        allExerciseNames.value = data.exercises.map(e => e.type)
        allExerciseMap.value = Object.fromEntries(data.exercises.map(e => [e.type, e.duration]))
        if (allExerciseNames.value.length > 0) selectedExercise.value = allExerciseNames.value[0]
      } catch (error) {
        ElMessage.error('無法計算運動時間，請稍後再試')
        const showExercises = userExercisePreferences.value.length > 0
          ? userExercisePreferences.value
          : DEFAULT_EXERCISES
        const result = {}
        showExercises.forEach(type => {
          result[type] = '計算失敗'
        })
        exerciseResults.value = result
        allExerciseNames.value = []
        allExerciseMap.value = {}
        selectedExercise.value = ''
      }
    }

    const closeExerciseModal = () => {
      exerciseModal.value = false
      exerciseResults.value = {}
      exerciseSearch.value = ''
    }

    const foodImagePlaceholderLibrary = [
      'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1565958011703-44f9829ba187?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?q=80&w=500&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=500&auto=format&fit=crop'
    ];

    const setDefaultImageOnError = (event) => {
      event.target.src = foodImagePlaceholderLibrary[Math.floor(Math.random() * foodImagePlaceholderLibrary.length)];
    };

    const formatPrice = (value) => {
      const num = Number(value)
      return Number.isFinite(num) ? num.toFixed(2) : '--'
    }

    const formatCalories = (value) => {
      const num = Number(value)
      return Number.isFinite(num) && !isNaN(num) ? Math.round(num) : '--'
    }

    const imageLoaded = ref({});

    const onImageLoad = (food) => {
      if (food && food.id !== undefined && food.id !== null) {
        if (typeof imageLoaded.value !== 'object' || imageLoaded.value === null) {
          imageLoaded.value = {};
        }
        imageLoaded.value = {
          ...imageLoaded.value,
          [String(food.id)]: true
        };
      }
    };

    const hasNutritionInfo = (food) => {
      return (
        (food.Protein !== null && food.Protein !== undefined) ||
        (food.Fat !== null && food.Fat !== undefined) ||
        (food.Sugar !== null && food.Sugar !== undefined) ||
        (food.Sodium !== null && food.Sodium !== undefined) ||
        (food.Carb !== null && food.Carb !== undefined) ||
        (food.Caffeine !== null && food.Caffeine !== undefined)
      );
    };

        const userId = localStorage.getItem('userId')
    const userExercisePreferences = ref([])
    const exerciseOptions = ref([...DEFAULT_EXERCISES])

    const fetchExercisePreferences = async () => {
        if (!userId) {
        userExercisePreferences.value = [...DEFAULT_EXERCISES]
        exerciseOptions.value = [...DEFAULT_EXERCISES]
          return
        }
      try {
        const res = await api.get('/api/preferences/user/exercise-preferences', { params: { user_id: userId } })
        if (res.data && Array.isArray(res.data.exercise_names) && res.data.exercise_names.length > 0) {
          userExercisePreferences.value = res.data.exercise_names
          exerciseOptions.value = res.data.exercise_names
        } else {
          userExercisePreferences.value = []
          exerciseOptions.value = [...DEFAULT_EXERCISES]
        }
      } catch (err) {
        userExercisePreferences.value = []
        exerciseOptions.value = [...DEFAULT_EXERCISES]
      }
    }

    const saveExercisePreferences = async (newPrefs) => {
      if (!userId) return
      try {
        await api.post('/api/preferences/user/exercise-preferences', {
          user_id: userId,
          exercise_names: newPrefs
        })
        userExercisePreferences.value = [...newPrefs]
        exerciseOptions.value = [...newPrefs]
        ElMessage.success('運動偏好已儲存')
      } catch (err) {
        ElMessage.error('儲存運動偏好失敗')
      }
    }

    const filteredExerciseOptions = computed(() => {
      if (userExercisePreferences.value.length > 0) {
        if (!exerciseSearch.value) return userExercisePreferences.value
        return userExercisePreferences.value.filter(e => e.includes(exerciseSearch.value))
      }
      if (!exerciseSearch.value) return exerciseOptions.value
      return exerciseOptions.value.filter(e => e.includes(exerciseSearch.value))
    })

    const fetchFavorites = async () => {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        favoriteFoodIds.value = new Set()
        return
      }
      try {
        const res = await api.get('/api/myfavorite/favorites', { params: { user_id: userId } })
        if (Array.isArray(res.data)) {
          favoriteFoodIds.value = new Set(res.data.map(f => f.food_id || f.id))
        }
      } catch (err) {
        favoriteFoodIds.value = new Set()
      }
    }

    const foodTypes = ref([])
    const restaurants = ref([])

    // 無限滾動 observer
    let sentinelObserver = null
    const setupInfiniteScroll = () => {
      if (!('IntersectionObserver' in window)) return
      sentinelObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && canLoadMore.value && !isLoading.value) {
            itemsToShow.value += pageSize
          }
        })
      }, { rootMargin: '200px 0px', threshold: 0 })
      if (infiniteSentinel.value) {
        sentinelObserver.observe(infiniteSentinel.value)
      }
    }

    onMounted(async () => {
      isLoading.value = true
      hasSearched.value = false

      // 定期清理過期快取
      setInterval(cleanExpiredCache, 60000)

      const userId = localStorage.getItem('userId')

      const bootstrapTasks = [
        fetchFavorites(),
        fetchExercisePreferences(),
        loadUserPreferences(),
        (async () => {
          if (!userId) {
            recommendedCategories.value = []
            return
          }
          try {
            const { data } = await api.get('/api/food/recommend', { params: { user_id: userId } })
            recommendedCategories.value = Array.isArray(data.categories) ? data.categories : []
          } catch (error) {
            console.error('載入推薦失敗:', error)
            recommendedCategories.value = []
          }
        })(),
        (async () => {
          try {
            const res = await api.get('/api/food/types')
            if (Array.isArray(res.data)) {
              foodTypes.value = res.data
            }
          } catch (e) {
            foodTypes.value = Array.from(new Set((searchResults.value || []).map(f => f.food_type).filter(Boolean)))
          }
        })(),
        (async () => {
          try {
            const res = await api.get('/api/food/restaurants')
            if (Array.isArray(res.data)) {
              restaurants.value = res.data.map(r => ({
                ...r,
                logo: `/img/logos/restaurant-${r.id}.png`
              }))
            }
          } catch (e) {
            restaurants.value = []
          }
        })()
      ]

      await Promise.allSettled(bootstrapTasks)
      isLoading.value = false

      // 初始化熱量滑桿
      syncCalValuesFromFilters()
     // 初始化價格滑桿
     syncPriceValuesFromFilters()
      setupInfiniteScroll()
    })

    onBeforeUnmount(() => {
      if (sentinelObserver && infiniteSentinel.value) {
        sentinelObserver.unobserve(infiniteSentinel.value)
      }
      if (sentinelObserver) {
        sentinelObserver.disconnect()
      }
    })

    const loadUserPreferences = async () => {
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          userPreferences.value = {
            Food_Preferences: { singleDish: true, setMeal: true },
            dietaryRestrictions: {},
            spicyLevel: 1,
            priceRange: 3
          }
          return
        }
        const storedProfile = localStorage.getItem('userProfile')
        if (storedProfile) {
          const profileData = JSON.parse(storedProfile)
          userPreferences.value = {
            Food_Preferences: profileData.Food_Preferences || { singleDish: true, setMeal: true },
            dietaryRestrictions: profileData.dietaryRestrictions || {},
            spicyLevel: profileData.spicyLevel || 0,
            priceRange: profileData.priceRange || 3
          }
        } else {
          userPreferences.value = {
            Food_Preferences: { singleDish: true, setMeal: true },
            dietaryRestrictions: {},
            spicyLevel: 1,
            priceRange: 3
          }
        }
      } catch (error) {
        console.error('載入用戶偏好失敗:', error)
        userPreferences.value = {
          Food_Preferences: { singleDish: true, setMeal: true },
          dietaryRestrictions: {},
          spicyLevel: 1,
          priceRange: 3
        }
      }
    }
    
    const toggleRestaurant = (name) => {
      const idx = filters.value.restaurants.indexOf(name)
      if (idx === -1) {
        filters.value.restaurants.push(name)
      } else {
        filters.value.restaurants.splice(idx, 1)
      }
      handleFilterChange()
    }

    const toggleFoodType = (type) => {
      const idx = filters.value.food_type.indexOf(type)
      if (idx === -1) {
        filters.value.food_type.push(type)
      } else {
        filters.value.food_type.splice(idx, 1)
      }
      handleFilterChange()
    }

    const allExerciseNames = ref([])
    const allExerciseMap = ref({})
    const selectedExercise = ref('')

    const getSelectedExerciseMinutes = computed(() => {
      const min = allExerciseMap.value[selectedExercise.value]
      return min !== undefined ? Number(min).toFixed(1) : '--'
    })

    const addToPreference = async (exercise) => {
      if (!userId) return
      await saveExercisePreferences([...userExercisePreferences.value, exercise])
    }

    const getExerciseIcon = (name) => exerciseIconMap[name] || '🏋️'
    const getIntensityFlames = (name) => exerciseFlamesMap[name] || ''
    const getExerciseIntensity = (name) => exerciseIntensityMap[name] || ''

    // 與 v-intersection-observer 相容的回呼（目前不做額外處理）
    const onIntersection = () => {}

    const exerciseIconMap = {
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
    const exerciseFlamesMap = {
      '伏地挺身': '🔥🔥',
      '划船': '🔥🔥🔥',
      '太極': '🔥🔥',
      '快走': '🔥🔥',
      '慢走': '🔥',
      '攀岩': '🔥🔥🔥',
      '游泳': '🔥🔥🔥',
      '爬山': '🔥🔥',
      '瑜珈': '🔥🔥',
      '籃球': '🔥🔥🔥',
      '足球': '🔥🔥🔥',
      '跑步(10km/hr)': '🔥🔥🔥🔥',
      '跑步(8km/hr)': '🔥🔥🔥',
      '騎腳踏車': '🔥🔥'
    }
    const exerciseIntensityMap = {
      '伏地挺身': '中度',
      '划船': '高度',
      '太極': '中度',
      '快走': '中度',
      '慢走': '輕度',
      '攀岩': '高度',
      '游泳': '高度',
      '爬山': '中度',
      '瑜珈': '中度',
      '籃球': '高度',
      '足球': '高度',
      '跑步(10km/hr)': '高度',
      '跑步(8km/hr)': '高度',
      '騎腳踏車': '中度'
    }

    // 圖片預載
    const preloadImages = (foods) => {
      if (!foods || foods.length === 0) return
      const imagesToPreload = foods.slice(0, 5)
      imagesToPreload.forEach(food => {
        if (food.ImageUrl || food.image_url || food.imageUrl) {
          const img = new Image()
          img.src = food.ImageUrl || food.image_url || food.imageUrl
        }
      })
    }

    // 搜尋結果快取
    const searchCache = ref(new Map())
    const getCachedResults = (filters) => {
      const cacheKey = JSON.stringify(filters)
      return searchCache.value.get(cacheKey)
    }
    const setCachedResults = (filters, results) => {
      const cacheKey = JSON.stringify(filters)
      searchCache.value.set(cacheKey, {
        results,
        timestamp: Date.now()
      })
    }

    const cleanExpiredCache = () => {
      const now = Date.now()
      const maxAge = 5 * 60 * 1000
      for (const [key, value] of searchCache.value.entries()) {
        if (now - value.timestamp > maxAge) {
          searchCache.value.delete(key)
        }
      }
    }

    const visibleResults = computed(() => {
      if (searchResults.value.length <= itemsToShow.value) {
        return searchResults.value
      }
      return searchResults.value.slice(0, itemsToShow.value)
    })

    const isGuest = computed(() => !authStore.isAuthenticated)
    const goToLogin = () => {
      router.push('/login')
    }

    return {
      filters,
      recommendedCategories,
      searchResults,
      isLoading,
      hasSearched,
      handleSearch,
      handleFilterChange,
      hasActiveFilters,
      addToFavorites,
      favoriteFoodIds,
      // 熱量滑桿
      calRangeMin,
      calRangeMax,
      calStep,
      calMinValue,
      calMaxValue,
      calLeftPercent,
      calRightPercent,
      calRangeLabel,
      calPresets,
      handleCalMinInput,
      handleCalMaxInput,
      applyCalPreset,
      // 價格滑桿
      priceRangeMin,
      priceRangeMax,
      priceStep,
      priceMinValue,
      priceMaxValue,
      priceLeftPercent,
      priceRightPercent,
      priceRangeLabel,
      pricePresets,
      handlePriceMinInput,
      handlePriceMaxInput,
      applyPricePreset,
      // exercise
      exerciseModal,
      exerciseResults,
      exerciseSearch,
      openExerciseModal,
      calculateExercise,
      closeExerciseModal,
      showRecordModal,
      currentFood,
      openFoodRecordModal,
      onRecordSaved,
      setDefaultImageOnError,
      formatPrice,
      formatCalories,
      imageLoaded,
      onImageLoad,
      hasNutritionInfo,
      userExercisePreferences,
      exerciseOptions,
      fetchExercisePreferences,
      saveExercisePreferences,
      filteredExerciseOptions,
      foodTypes,
      restaurants,
      toggleRestaurant,
      toggleFoodType,
      allExerciseNames,
      allExerciseMap,
      selectedExercise,
      getSelectedExerciseMinutes,
      addToPreference,
      getExerciseIcon,
      getIntensityFlames,
      getExerciseIntensity,
      preloadImages,
      searchCache,
      getCachedResults,
      setCachedResults,
      cleanExpiredCache,
      // infinite scroll
      itemsToShow,
      infiniteSentinel,
      canLoadMore,
      visibleResults,
      isGuest,
      goToLogin
    }
  }
}
</script>

<style scoped>
/* ----- 全局變量 ----- */
:root {
  --primary-color: #409EFF;
  --primary-color-light: #79bbff;
  --primary-color-dark: #337ecc;
  --warning-color: #E6A23C;
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --border-color-light: #e4e7ed;
  --border-color-lighter: #ebeef5;
  --bg-color: #f5f7fa;
  --card-shadow: 0 6px 16px -8px rgba(0,0,0,.08), 0 9px 28px 0 rgba(0,0,0,.05), 0 12px 48px 16px rgba(0,0,0,.03);
  --card-shadow-hover: 0 8px 20px -6px rgba(0,0,0,.1), 0 12px 32px 0 rgba(0,0,0,.07), 0 16px 52px 18px rgba(0,0,0,.04);
}

/* skeleton */
.skeleton { animation: pulse 1.2s ease-in-out infinite; }
.skeleton-box { background: #eef1f6; }
.skeleton-line { height: 12px; background: #eef1f6; border-radius: 6px; margin: 8px 0; }
.w-full { width: 100%; }
.w-3of4 { width: 75%; }
.w-1of2 { width: 50%; }
@keyframes pulse { 0% { opacity: .9 } 50% { opacity: .5 } 100% { opacity: .9 } }

.infinite-sentinel { height: 1px; }

/* 其餘樣式保持不變 */
/* ----- 以下保留原樣式定義 ----- */
.food-search-page {
  background: linear-gradient(180deg, #fafcff 0%, #f7fbff 35%, #fefcf8 100%);
}
.food-search-page .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px 40px;
}

.page-title {
  font-size: 2.25rem; 
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 18px;
  text-align: center;
  letter-spacing: .5px;
}
.page-title + .section-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 22px;
  font-size: .95rem;
}

.guest-mode-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fff6e8;
  border: 1px solid #f7d7a5;
  color: #8a5200;
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
}

.guest-mode-text {
  font-size: .92rem;
  line-height: 1.45;
}

.guest-login-btn {
  border: none;
  border-radius: 9px;
  background: #f59e0b;
  color: #fff;
  font-weight: 600;
  padding: 8px 14px;
  cursor: pointer;
  white-space: nowrap;
}

.guest-login-btn:hover {
  background: #d97706;
}

@media (max-width: 768px) {
  .guest-mode-banner {
    flex-direction: column;
    align-items: flex-start;
  }
}

.search-form-container { margin-bottom: 26px; }
.search-form-card {
  background: rgba(255,255,255,.8);
  backdrop-filter: saturate(1.2) blur(6px);
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 14px;
  padding: 22px;
  box-shadow: var(--card-shadow);
}
.search-form-grid { display: grid; gap: 18px; }
.form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; align-items: end; }

.form-group { margin-bottom: 12px; }
.form-label { font-size: .95rem; font-weight: 600; color: var(--text-regular); margin-bottom: 6px; letter-spacing: .3px; }

.input-with-icon { position: relative; }
.input-with-icon .form-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); font-size: 1.1em; }

.form-control {
  width:90%;
  padding: 12px 12px;
  padding-left: 36px;
  font-size: .95rem;
  border: 1px solid var(--border-color-light);
  border-radius: 10px;
  transition: border-color .2s, box-shadow .2s, transform .06s;
  background: #fff;
}
.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.18);
  outline: none;
  transform: translateY(-1px);
}
.form-control-sm { padding-top: 10px; padding-bottom: 10px; font-size: .9rem; border-radius: 10px; }

.range-inputs { display: flex; align-items: center; gap: 8px; }
.range-inputs .form-control { padding-left: 12px; }
.range-separator, .unit { color: var(--text-secondary); font-size: .9rem; }

.foodtype-chip-list, .restaurant-logo-list { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 6px; }
.foodtype-chip-btn, .restaurant-logo-btn {
  border: 1px solid #e4e7ed;
  background: #fff;
  border-radius: 9999px;
  padding: 8px 14px;
  font-size: .95rem;
  color: #606266;
  cursor: pointer;
  transition: all .2s ease;
  display: inline-flex; align-items: center; gap: 8px;
}
.foodtype-chip-btn.active, .foodtype-chip-btn:hover,
.restaurant-logo-btn.active, .restaurant-logo-btn:hover { border-color: #E6A23C; background: #fff7e6; color: #cf9236; box-shadow: 0 2px 10px rgba(230,162,60,.12); }
.restaurant-logo-img { width: 28px; height: 28px; object-fit: contain; border-radius: 50%; background: #f5f5f5; }

.search-btn-container { display: flex; align-items: end; }
.search-btn {
  width: 100%;
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #f8b84a 0%, #e6a23c 100%);
  border: 1px solid #e3a03b;
  border-radius: 12px;
  cursor: pointer;
  transition: all .2s ease;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  position: relative; overflow: hidden;
}
.search-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(230,162,60,.28); }
.search-btn:active { transform: translateY(0); }

/* 標題與結果區 */
.section-title { font-size: 1.75rem; font-weight: 700; color: var(--text-primary); margin: 20px 0 16px; display: flex; align-items: center; gap: 12px; }
.section-title:after { content: ""; flex: 1; height: 2px; background: linear-gradient(90deg, #ffe5bf, rgba(0,0,0,0)); border-radius: 2px; }

.result-count { font-size: .95rem; color: var(--text-secondary); font-weight: 500; }
.loading-indicator { font-size: .9rem; color: var(--primary-color); display: inline-flex; align-items: center; gap: 6px; }
.loading-indicator::before { content: ''; width: 12px; height: 12px; border: 2px solid var(--primary-color); border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 卡片與圖片 */
.food-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
.food-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  display: flex; flex-direction: column;
  transition: transform .18s ease, box-shadow .18s ease;
  border: 1px solid var(--border-color-lighter);
}
.food-card:hover { transform: translateY(-6px); box-shadow: var(--card-shadow-hover); }
.food-card:focus-within { outline: 2px solid var(--primary-color); outline-offset: 2px; }

.food-image-container { width: 100%; height: 220px; background: #f3f6fb; position: relative; overflow: hidden; }
.food-image { width: 100%; height: 100%; object-fit: cover; transition: transform .25s ease; }
.food-card:hover .food-image { transform: scale(1.06); }

.calorie-on-image-button { position: absolute; top: 12px; right: 12px; width: 68px; height: 68px; background: rgba(230,162,60,.95); color: #fff; border-radius: 50%; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,.2), 0 0 0 2px rgba(255,255,255,.5); }
.calorie-on-image-button .calorie-value { font-size: 1.2rem; }
.calorie-on-image-button .calorie-unit { font-size: .7rem; opacity: .95; margin-top: 1px; }

.food-card-content { padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.food-name-price-line { display: flex; align-items: center; gap: 10px; }
.food-name { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); line-height: 1.3; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: calc(1.2rem * 1.3 * 2); }
.food-price-prominent { font-size: 1.15rem; font-weight: 800; color: #E6A23C; }

/* tooltip icon */
.nutrition-info-icon { font-size: 1.5rem; color: #ffaa55; cursor: pointer; margin-left: 6px; transition: color .2s, box-shadow .2s; box-shadow: 0 2px 8px rgba(255,170,85,.08); }
.nutrition-info-icon:hover { color: #E6A23C; box-shadow: 0 4px 12px rgba(230,162,60,.18); }

/* 細節列以柔和標籤呈現 */
.food-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.detail-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border: 1px solid var(--border-color-lighter); background: #fff; border-radius: 9999px; color: var(--text-regular); font-size: .9rem; }
.detail-item .icon { color: var(--primary-color-light); }

/* 操作列 */
.food-actions { margin-top: 6px; padding-top: 12px; border-top: 1px solid var(--border-color-lighter); display: flex; gap: 10px; justify-content: flex-end; }
.action-btn { flex: 0 0 42px; width: 42px; height: 42px; padding: 0; border-radius: 12px; border: 1px solid #e6e8ef; background: #f8fafc; color: #475569; cursor: pointer; transition: all .16s ease; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,.04); }
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 14px rgba(0,0,0,.08); }
.action-btn .el-icon { font-size: 1.15rem; color: #8b95a5; }
.action-btn.record-btn { background: linear-gradient(135deg, #f8b84a 0%, #e6a23c 100%); border-color: #e3a03b; color: #fff; box-shadow: 0 4px 10px rgba(230,162,60,.25); }
.action-btn.record-btn .el-icon { color: #fff; }
.action-btn.record-btn:hover { box-shadow: 0 10px 24px rgba(230,162,60,.35); }

/* 無結果/載入 */
.no-results, .loading-state { text-align: center; padding: 80px 20px; color: var(--text-secondary); }
.no-results-icon { font-size: 4rem; margin-bottom: 12px; color: var(--text-secondary); opacity: .8; }
.loading-spinner { border: 4px solid var(--bg-color); border-top: 4px solid var(--primary-color); border-radius: 50%; width: 48px; height: 48px; animation: spin 1s linear infinite; margin: 0 auto 16px; }

/* 響應式優化 */
@media (max-width: 992px) {
  .food-image-container { height: 200px; }
}
@media (max-width: 768px) {
  .page-title { font-size: 1.6rem; }
  .food-grid { gap: 18px; }
  .food-details { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .food-grid { grid-template-columns: 1fr; }
  .food-image-container { height: 160px; }
  .action-btn { font-size: .88rem; padding: 9px 10px; }
}

/* 明顯化搜尋框 */
.search-prominent {
  border: 2px solid #e6eefc;
  background: #fbfdff;
  padding-top: 14px;
  padding-bottom: 14px;
  border-radius: 12px;
  box-shadow: 0 1px 0 rgba(64,158,255,.06) inset;
}
.search-prominent:focus {
  border-color: #86b7ff;
  box-shadow: 0 0 0 3px rgba(64,158,255,.2);
}

/* 雙滑桿樣式 */
.range-slider { display: flex; flex-direction: column; gap: 10px; }
.range-summary {
  font-size: .84rem;
  color: #6b7280;
  font-weight: 600;
}
.range-values { display: flex; align-items: center; gap: 10px; }
.range-input-group {
  display: flex; align-items: center;
  background: #f5f7ff; border: 1px solid #e6e8f0;
  border-radius: 8px; padding: 4px 8px; gap: 3px;
  transition: border-color .2s, box-shadow .2s;
}
.range-input-group:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(255,170,85,.2);
}
.range-unit-prefix, .range-unit-suffix { color: #909399; font-size: .82rem; white-space: nowrap; user-select: none; }
.range-number-input {
  width: 56px; border: none; background: transparent;
  outline: none; font-size: .9rem; color: #2c3e50;
  text-align: center; -moz-appearance: textfield;
}
.range-number-input::-webkit-inner-spin-button,
.range-number-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.value-sep { color: #c0c4cc; font-size: 1rem; flex-shrink: 0; }
.slider-track-wrapper { display: flex; align-items: center; gap: 6px; }
.track-bound { font-size: .72rem; color: #c0c4cc; white-space: nowrap; min-width: 26px; text-align: center; flex-shrink: 0; }
.slider-track { flex: 1; position: relative; height: 8px; background: #edf2f7; border-radius: 9999px; }
.slider-fill { position: absolute; top: 0; bottom: 0; background: linear-gradient(90deg, var(--primary-lighter), var(--primary-color)); border-radius: 9999px; transition: left .08s, right .08s; }
.slider-input { position: absolute; top: 50%; transform: translateY(-50%); left: 0; width: 100%; -webkit-appearance: none; background: none; pointer-events: none; height: 20px; margin: 0; }
.slider-input::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #fff; border: 2px solid var(--primary-color); box-shadow: 0 2px 8px rgba(255,170,85,.4); pointer-events: auto; cursor: pointer; transition: transform .15s, box-shadow .15s; }
.slider-input::-webkit-slider-thumb:hover { transform: scale(1.2); box-shadow: 0 3px 12px rgba(255,170,85,.6); }
.slider-input::-moz-range-thumb { width: 20px; height: 20px; border-radius: 50%; background: #fff; border: 2px solid var(--primary-color); box-shadow: 0 2px 8px rgba(255,170,85,.4); pointer-events: auto; cursor: pointer; }
.slider-input::-webkit-slider-runnable-track { height: 8px; background: transparent; }
.slider-input::-moz-range-track { height: 8px; background: transparent; }

.preset-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 2px;
}

.preset-chip {
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #6b7280;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: .78rem;
  cursor: pointer;
  transition: all .2s ease;
}

.preset-chip:hover {
  border-color: #f8b84a;
  background: #fff8eb;
  color: #b87915;
}

.preset-chip.active {
  border-color: #e6a23c;
  background: linear-gradient(135deg, #f8b84a 0%, #e6a23c 100%);
  color: #fff;
}

/* 調整表單為 12 欄格線 */
.search-form-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
.col-6 { grid-column: span 6; }
.col-12 { grid-column: span 12; }
.align-right { display: flex; justify-content: flex-end; }
@media (max-width: 768px) {
  .col-6 { grid-column: span 12; }
  .align-right .search-btn { width: 100%; }
}

/* 運動計算器模態框樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

.modal-exercise {
  width: 600px;
  max-height: 80vh;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: #475569;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}

.exercise-modal-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title:after {
  content: "";
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #e2e8f0, transparent);
}

.exercise-pref-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exercise-pref-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.exercise-pref-item:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.exercise-icon {
  font-size: 1.5rem;
  color: #3b82f6;
  width: 32px;
  text-align: center;
}

.exercise-name {
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.exercise-intensity {
  font-size: 1.2rem;
  color: #f59e0b;
}

.exercise-intensity-text {
  font-size: 0.9rem;
  color: #64748b;
  min-width: 60px;
  text-align: center;
}

.exercise-minutes {
  font-size: 0.95rem;
  color: #475569;
  font-weight: 500;
}

.exercise-minutes strong {
  color: #059669;
  font-weight: 700;
}

.empty-pref-tip {
  text-align: center;
  padding: 40px 20px;
  color: #64748b;
  font-style: italic;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
}

.exercise-divider {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin: 20px 0;
}

.all-exercise-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.all-exercise-select {
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #374151;
  background: white;
  min-width: 200px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.all-exercise-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.add-pref-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.add-pref-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .modal-exercise {
    width: 95vw;
    margin: 20px;
  }
  
  .modal-header {
    padding: 16px 20px;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .all-exercise-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .all-exercise-select {
    min-width: auto;
    width: 100%;
  }
  
  .exercise-pref-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .exercise-intensity, .exercise-intensity-text {
    order: -1;
  }
}
</style>