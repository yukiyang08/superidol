<template>
  <div class="food-search-page">
    <div class="container">
      <h1 class="page-title">食物搜尋</h1>

      <!-- 搜尋表單 -->
      <div class="search-form-container">
        <div class="search-form-card" @keydown.enter="handleSearch">
          <div class="search-form-grid">
            <!-- 第一行 -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">食物名稱</label>
                <div class="input-with-icon">
                  <i class="el-icon-food"></i>
                  <input type="text" class="form-control" placeholder="輸入食物名稱" v-model="filters.name" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">食物類型</label>
                <div class="foodtype-chip-list">
                  <button
                    v-for="type in foodTypes"
                    :key="type"
                    type="button"
                    class="foodtype-chip-btn"
                    :class="{ active: filters.food_type.includes(type) }"
                    @click="toggleFoodType(type)"
                  >
                    {{ type }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 第二行 -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">價格範圍</label>
                <div class="range-inputs">
                  <input type="number" class="form-control form-control-sm" placeholder="最低" v-model="filters.priceMin" />
                  <span class="range-separator">~</span>
                  <input type="number" class="form-control form-control-sm" placeholder="最高" v-model="filters.priceMax" />
                  <span class="unit">元</span>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">熱量範圍</label>
                <div class="range-inputs">
                  <input type="number" class="form-control form-control-sm" placeholder="最低" v-model="filters.calMin" />
                  <span class="range-separator">~</span>
                  <input type="number" class="form-control form-control-sm" placeholder="最高" v-model="filters.calMax" />
                  <span class="unit">大卡</span>
                </div>
              </div>
            </div>
            
            <!-- 第三行 -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">餐廳</label>
                <div class="restaurant-logo-list">
                  <button 
                    v-for="r in restaurants"
                    :key="r.id"
                    type="button" 
                    class="restaurant-logo-btn"
                    :class="{ active: filters.restaurants.includes(r.name) }"
                    @click="toggleRestaurant(r.name)"
                  >
                    <img :src="r.logo" :alt="r.name" class="restaurant-logo-img" />
                    <span>{{ r.name }}</span>
                  </button>
                </div>
              </div>
              <div class="form-group search-btn-container">
                <button type="button" class="search-btn" @click="handleSearch">
                  <i class="el-icon-search"></i>
                  搜尋
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜尋結果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <h2 class="section-title">搜尋結果</h2>
        <div class="food-grid">
          <div class="food-card" v-for="(food, index) in searchResults" :key="index">
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
                <span class="calorie-value">{{ Math.round(food.calories) }}</span>
                <span class="calorie-unit">大卡</span>
              </div>
            </div>
            <div class="food-card-content">
              <div class="food-info">
                <div class="food-name-price-line">
                <h3 class="food-name">{{ food.name }}</h3>
                  <span class="food-price-prominent">${{ food.price.toFixed(2) }}</span>
                  <el-tooltip placement="top" effect="dark" :disabled="!hasNutritionInfo(food)">
                    <template #content>
                      <div class="nutrition-tooltip improved-tooltip">
                        <h4>營養資訊</h4>
                        <table class="nutrition-table">
                          <tr v-if="food.Protein !== null && food.Protein !== undefined">
                            <td><i class="el-icon-ice-cream"></i> 蛋白質</td>
                            <td><strong class="nutrient protein">{{ food.Protein }}g</strong></td>
                          </tr>
                          <tr v-if="food.Fat !== null && food.Fat !== undefined">
                            <td><i class="el-icon-milk-tea"></i> 脂肪</td>
                            <td><strong class="nutrient fat">{{ food.Fat }}g</strong></td>
                          </tr>
                          <tr v-if="food.Sugar !== null && food.Sugar !== undefined">
                            <td><i class="el-icon-sugar"></i> 糖</td>
                            <td><strong class="nutrient sugar">{{ food.Sugar }}g</strong></td>
                          </tr>
                          <tr v-if="food.Sodium !== null && food.Sodium !== undefined">
                            <td><i class="el-icon-coin"></i> 鈉</td>
                            <td><strong class="nutrient sodium">{{ food.Sodium }}mg</strong></td>
                          </tr>
                          <tr v-if="food.Carb !== null && food.Carb !== undefined">
                            <td><i class="el-icon-burger"></i> 碳水</td>
                            <td><strong class="nutrient carb">{{ food.Carb }}g</strong></td>
                          </tr>
                          <tr v-if="food.Caffeine !== null && food.Caffeine !== undefined">
                            <td><i class="el-icon-coffee"></i> 咖啡因</td>
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
                    <i class="el-icon-shop"></i>
                    <span>{{ food.restaurant || '未知餐廳' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-data-line"></i>
                    <span>{{ food.calories }} 大卡</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-food"></i>
                    <span>{{ food.food_type || '未分類' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-menu"></i>
                    <span>{{ food.type }}</span>
                  </div>
                </div>
              </div>
              <div class="food-actions">
                <button class="action-btn calculator-btn" @click="openExerciseModal(food)">
                  <i class="el-icon-data-analysis"></i>
                  運動計算
                </button>
                <button class="action-btn favorite-btn" :disabled="favoriteFoodIds.has(food.id)" @click="addToFavorites(food)" v-if="!favoriteFoodIds.has(food.id)">
                  <i class="el-icon-star-off"></i>
                  加入最愛
                </button>
                <button class="action-btn favorite-btn" disabled v-else>
                  <i class="el-icon-star-on" style="color: #E6A23C"></i>
                  已收藏
                </button>
                <button class="action-btn record-btn" @click="openFoodRecordModal(food)">
                  <i class="el-icon-plus"></i>
                  加入記錄
                </button>
              </div>
            </div>
          </div>
        </div>
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
                  <span class="calorie-value">{{ Math.round(food.calories) }}</span>
                  <span class="calorie-unit">大卡</span>
                </div>
              </div>
            <div class="food-card-content">
              <div class="food-info">
                  <div class="food-name-price-line">
                <h3 class="food-name">{{ food.name }}</h3>
                    <span class="food-price-prominent">${{ food.price ? food.price.toFixed(2) : '--' }}</span>
                    <el-tooltip placement="top" effect="dark" :disabled="!hasNutritionInfo(food)">
                      <template #content>
                        <div class="nutrition-tooltip improved-tooltip">
                          <h4>營養資訊</h4>
                          <table class="nutrition-table">
                            <tr v-if="food.Protein !== null && food.Protein !== undefined">
                              <td><i class="el-icon-ice-cream"></i> 蛋白質</td>
                              <td><strong class="nutrient protein">{{ food.Protein }}g</strong></td>
                            </tr>
                            <tr v-if="food.Fat !== null && food.Fat !== undefined">
                              <td><i class="el-icon-milk-tea"></i> 脂肪</td>
                              <td><strong class="nutrient fat">{{ food.Fat }}g</strong></td>
                            </tr>
                            <tr v-if="food.Sugar !== null && food.Sugar !== undefined">
                              <td><i class="el-icon-sugar"></i> 糖</td>
                              <td><strong class="nutrient sugar">{{ food.Sugar }}g</strong></td>
                            </tr>
                            <tr v-if="food.Sodium !== null && food.Sodium !== undefined">
                              <td><i class="el-icon-coin"></i> 鈉</td>
                              <td><strong class="nutrient sodium">{{ food.Sodium }}mg</strong></td>
                            </tr>
                            <tr v-if="food.Carb !== null && food.Carb !== undefined">
                              <td><i class="el-icon-burger"></i> 碳水</td>
                              <td><strong class="nutrient carb">{{ food.Carb }}g</strong></td>
                            </tr>
                            <tr v-if="food.Caffeine !== null && food.Caffeine !== undefined">
                              <td><i class="el-icon-coffee"></i> 咖啡因</td>
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
                    <i class="el-icon-shop"></i>
                    <span>{{ food.restaurant || '未知餐廳' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-food"></i>
                    <span>{{ food.food_type || '未分類' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-menu"></i>
                    <span>{{ food.type }}</span>
                  </div>
                </div>
              </div>
              <div class="food-actions">
                <button class="action-btn calculator-btn" @click="openExerciseModal(food)">
                  <i class="el-icon-data-analysis"></i>
                  運動計算
                </button>
                <button class="action-btn favorite-btn" :disabled="favoriteFoodIds.has(food.id)" @click="addToFavorites(food)" v-if="!favoriteFoodIds.has(food.id)">
                  <i class="el-icon-star-off"></i>
                    加入最愛
                </button>
                <button class="action-btn favorite-btn" disabled v-else>
                  <i class="el-icon-star-on" style="color: #E6A23C"></i>
                  已收藏
                </button>
                  <button class="action-btn record-btn" @click="openFoodRecordModal(food)">
                  <i class="el-icon-plus"></i>
                  加入記錄
                </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-if="hasSearched && searchResults.length === 0 && !isLoading" class="no-results">
        <i class="el-icon-search no-results-icon"></i>
        <p>未找到符合條件的食物</p>
      </div>

      <!-- 載入中 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- Exercise Calculator Modal -->
      <div v-if="exerciseModal" class="modal-overlay">
        <div class="modal modal-exercise">
          <div class="modal-header">
            <h3>運動計算機</h3>
            <button class="close-button" @click="closeExerciseModal">&times;</button>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import FoodRecordModal from '@/components/food/FoodRecordModal.vue'
import { InfoFilled } from '@element-plus/icons-vue'

const DEFAULT_EXERCISES = ['跑步', '游泳', '騎腳踏車', '健走']

// 新增：常見餐廳與 logo 對照表（如無後端 API 可用）
const RESTAURANT_LOGOS = [
  { name: '迷克夏', logo: '/logos/milkshop.png' },
  { name: '麥當勞', logo: '/logos/mcdonalds.png' },
  { name: '摩斯漢堡', logo: '/logos/mos.png' },
  { name: '50嵐', logo: '/logos/50lan.png' }
];

export default {
  name: 'FoodSearch',
  components: { FoodRecordModal, InfoFilled },
  setup() {
    const router = useRouter() // 取得 router 實例

    const searchResults = ref([])
    const food_from_database = ref([])
    const recommendedCategories = ref([])
    const isLoading = ref(false)
    const hasSearched = ref(false)
    const userPreferences = ref(null)
    const favoriteFoodIds = ref(new Set())

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

    const toggleType = (value) => {
      filters.value.type = filters.value.type === value ? '' : value
    }

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
      // 可選：儲存後自動跳轉或刷新
      router.push({ name: 'FoodRecord' })
    }

    const handleSearch = async () => {
      const { priceMin, priceMax, calMin, calMax, name, restaurants, type, food_type } = filters.value

      const allEmpty =
        priceMin === '' &&
        priceMax === '' &&
        calMin === '' &&
        calMax === '' &&
        name.trim() === '' &&
        restaurants.length === 0 &&
        type === '' &&
        food_type.length === 0

      if (allEmpty) return

      isLoading.value = true
      hasSearched.value = true

      try {
        // 構建API查詢參數
        const params = new URLSearchParams()
        
        if (priceMin !== '') params.append('priceMin', priceMin)
        if (priceMax !== '') params.append('priceMax', priceMax)
        if (calMin !== '') params.append('calMin', calMin)
        if (calMax !== '') params.append('calMax', calMax)
        if (name.trim() !== '') params.append('name', name.trim())
        if (restaurants.length > 0) params.append('restaurant', restaurants.join(','))
        if (type !== '') params.append('type', type)
        if (filters.value.food_type.length > 0) {
          params.append('food_type', filters.value.food_type.join(','))
        }
        
        // 發送請求到後端API
        const response = await fetch(`http://localhost:5000/api/food/?${params.toString()}`)
        
        if (!response.ok) {
          throw new Error(`API 請求失敗: ${response.status}`)
        }
        
        const data = await response.json()
        // DEBUG: 印出第一筆 food 物件
        if (data && data.length > 0) {
          console.log('[DEBUG] 第一筆 food:', data[0]);
        }
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
        console.error('搜尋食物失敗:', error)
        ElMessage.error('搜尋食物失敗，請稍後再試')
        searchResults.value = []
      } finally {
        isLoading.value = false
      }
    }

    const addToFavorites = async (food) => {
      try {
        // 從 localStorage 獲取 userId
        const userId = localStorage.getItem('userId')
        
        if (!userId) {
          ElMessage.warning('請先登入')
          return
        }
        
        await fetch('http://localhost:5000/api/myfavorite/favorites', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: parseInt(userId),
            food_id: food.id
          })
        })
        
        ElMessage.success('已添加到我的最愛')
        favoriteFoodIds.value = new Set([...favoriteFoodIds.value, food.id])
      } catch (error) {
        console.error('添加到最愛失敗:', error)
        ElMessage.error('添加到最愛失敗，請稍後再試')
      }
    }

    //Exercise Calculator  
    const openExerciseModal = (food) => {
      exerciseModal.value = true
      calculateExercise(food.calories)
    }

    // 運動名稱正規化（同 ExerciseRecord.vue）
    function normalizeExerciseName(name) {
      if (!name) return '';
      return name.replace(/\s+/g, '').replace(/[Ａ-Ｚａ-ｚ０-９]/g, s => String.fromCharCode(s.charCodeAt(0) - 0xFEE0)).toLowerCase();
    }

    const calculateExercise = async (calories) => {
      try {
        const userId = localStorage.getItem('userId')
        const response = await fetch(`http://localhost:5000/api/food/exercise/calculator?calories=${calories}&user_id=${userId}`)
        if (!response.ok) throw new Error(`API 請求失敗: ${response.status}`)
        const data = await response.json()
        // 依照用戶偏好組合結果
        const showExercises = userExercisePreferences.value.length > 0
          ? userExercisePreferences.value
          : DEFAULT_EXERCISES
        const result = {}
        showExercises.forEach(type => {
          const normType = normalizeExerciseName(type)
          // 找到第一個 normalize 後開頭一樣的（如「跑步」能對到「跑步(8km/hr)」）
          const found = data.exercises.find(e => normalizeExerciseName(e.type).startsWith(normType))
          result[type] = found ? found.duration : undefined
        })
        exerciseResults.value = result
        // 新增：整理所有運動
        allExerciseNames.value = data.exercises.map(e => e.type)
        allExerciseMap.value = Object.fromEntries(data.exercises.map(e => [e.type, e.duration]))
        // 預設選第一個
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
      'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=500&auto=format&fit=crop', // Salad
      'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?q=80&w=500&auto=format&fit=crop', // Pancakes
      'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=500&auto=format&fit=crop', // Pizza
      'https://images.unsplash.com/photo-1565958011703-44f9829ba187?q=80&w=500&auto=format&fit=crop', // Cake
      'https://images.unsplash.com/photo-1482049016688-2d3e1b311543?q=80&w=500&auto=format&fit=crop', // Breakfast
      'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=500&auto=format&fit=crop', // Healthy meal
      'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?q=80&w=500&auto=format&fit=crop', // Pasta
      'https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=500&auto=format&fit=crop'  // Main course
    ];

    const getDefaultFoodImage = (food) => {
      // Ensure food is an object and has id or name for pseudo-random selection
      if (food && typeof food === 'object' && (food.id || food.name)) {
        // Create a seed from food.id (if it's a number or string) or food.name length
        let seedValue = 0;
        if (typeof food.id === 'number' || (typeof food.id === 'string' && food.id.length > 0) ) {
          // Simple hash from id: sum of char codes or number itself
          seedValue = String(food.id).split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        } else if (food.name && typeof food.name === 'string') {
          seedValue = food.name.length;
        }
        const randomIndex = seedValue % foodImagePlaceholderLibrary.length;
        return foodImagePlaceholderLibrary[randomIndex];
      }
      // Fallback to pure random if no consistent seed can be generated
      return foodImagePlaceholderLibrary[Math.floor(Math.random() * foodImagePlaceholderLibrary.length)];
    };

    const setDefaultImageOnError = (event) => {
      // On error, also pick a random image from the library
      event.target.src = foodImagePlaceholderLibrary[Math.floor(Math.random() * foodImagePlaceholderLibrary.length)];
    };

    const logImageDebug = (food) => {
      console.log('[DEBUG] food:', food);
      console.log('[DEBUG] food.ImageUrl:', food.ImageUrl);
      console.log('[DEBUG] food.image_url:', food.image_url);
      console.log('[DEBUG] food.imageUrl:', food.imageUrl);
    };

    const imageLoaded = ref({});

    const onImageLoad = (food) => {
      if (food && food.id !== undefined && food.id !== null) {
        if (typeof imageLoaded.value !== 'object' || imageLoaded.value === null) {
          imageLoaded.value = {};
        }
        imageLoaded.value = {
          ...imageLoaded.value,
          [String(food.id)]: true // Use String(food.id) for safer object key
        };
      }
      // logImageDebug(food); // Assuming logImageDebug is defined elsewhere if used
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

    // 查詢用戶運動偏好
    const fetchExercisePreferences = async () => {
        if (!userId) {
        userExercisePreferences.value = [...DEFAULT_EXERCISES]
        exerciseOptions.value = [...DEFAULT_EXERCISES]
          return
        }
      try {
        const res = await axios.get('/api/preferences/user/exercise-preferences', { params: { user_id: userId } })
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

    // 儲存用戶運動偏好
    const saveExercisePreferences = async (newPrefs) => {
      if (!userId) return
      try {
        await axios.post('/api/preferences/user/exercise-preferences', {
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

    // 運動搜尋功能
    const filteredExerciseOptions = computed(() => {
      // 若有用戶偏好，僅顯示用戶偏好
      if (userExercisePreferences.value.length > 0) {
        if (!exerciseSearch.value) return userExercisePreferences.value
        return userExercisePreferences.value.filter(e => e.includes(exerciseSearch.value))
      }
      // 否則顯示 default
      if (!exerciseSearch.value) return exerciseOptions.value
      return exerciseOptions.value.filter(e => e.includes(exerciseSearch.value))
    })

    // 取得用戶收藏清單
    const fetchFavorites = async () => {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        favoriteFoodIds.value = new Set()
        return
      }
      try {
        const res = await axios.get('/api/food/favorites', { params: { user_id: userId } })
        if (Array.isArray(res.data)) {
          favoriteFoodIds.value = new Set(res.data.map(f => f.food_id || f.id))
        }
      } catch (err) {
        favoriteFoodIds.value = new Set()
      }
    }

    // 新增：食物類型與餐廳
    const foodTypes = ref([])
    const restaurants = ref([])

    onMounted(async () => {
      isLoading.value = true
      hasSearched.value = false
      await fetchFavorites()
      await fetchExercisePreferences()
      await loadUserPreferences()
      try {
        // 取得推薦分類
        const userId = localStorage.getItem('userId')
        if (!userId) {
          recommendedCategories.value = []
          isLoading.value = false
          return
        }
        const response = await fetch(`http://localhost:5000/api/food/recommend?user_id=${userId}`)
        if (!response.ok) throw new Error('推薦API失敗')
        const data = await response.json()
        recommendedCategories.value = Array.isArray(data.categories) ? data.categories : []
      } catch (error) {
        console.error('載入推薦失敗:', error)
        recommendedCategories.value = []
      } finally {
        isLoading.value = false
      }
      // 取得所有 food_type
      try {
        const res = await axios.get('/api/food/types')
        if (Array.isArray(res.data)) {
          foodTypes.value = res.data
        }
      } catch (e) {
        // fallback: 從現有資料動態生成
        foodTypes.value = Array.from(new Set((searchResults.value || []).map(f => f.food_type).filter(Boolean)))
      }
      try {
        const res = await axios.get('/api/food/restaurants');
        if (Array.isArray(res.data)) {
          restaurants.value = res.data.map(r => ({
            ...r,
            logo: `/img/logos/restaurant-${r.id}.png`
          }));
        }
      } catch (e) {
        restaurants.value = [];
      }
    })
    
    // 載入用戶偏好
    const loadUserPreferences = async () => {
      try {
        // 從localStorage讀取個人資料中的偏好信息
        const userId = localStorage.getItem('userId')
        
        if (!userId) {
          // 如果未登入，使用默認值
          userPreferences.value = {
            Food_Preferences: { singleDish: true, setMeal: true },
            dietaryRestrictions: {},
            spicyLevel: 1,
            priceRange: 3
          }
          return
        }
        
        // 未來可從API獲取用戶偏好，目前仍從localStorage取得
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
          // 如果沒有存儲的偏好，使用默認值
          userPreferences.value = {
            Food_Preferences: { singleDish: true, setMeal: true },
            dietaryRestrictions: {},
            spicyLevel: 1,
            priceRange: 3
          }
        }
      } catch (error) {
        console.error('載入用戶偏好失敗:', error)
        // 使用默認值
        userPreferences.value = {
          Food_Preferences: { singleDish: true, setMeal: true },
          dietaryRestrictions: {},
          spicyLevel: 1,
          priceRange: 3
        }
      }
    }
    
    // 根據用戶偏好產生推薦
    const generateRecommendations = () => {
      if (!userPreferences.value || food_from_database.value.length === 0) {
        recommendedCategories.value = food_from_database.value.slice(0, 4) // 如果沒有偏好，顯示前四筆
        return
      }
      
      // 根據用戶偏好計算每個食物的適配分數
      const foodWithScores = food_from_database.value.map(food => {
        let score = 0
        
        // 價格範圍評分 (1-5分)，越接近用戶偏好價格範圍得分越高
        const priceLevel = Math.ceil((food.price || 0) / 100) // 簡單轉換，每100元一個級別
        score += 5 - Math.abs(priceLevel - userPreferences.value.priceRange)
        
        // 根據食物類型給予分數
        if (food.type === '單點') {
          score += userPreferences.value.Food_Preferences.singleDish ? 3 : 0
        } else if (food.type === '套餐') {
          score += userPreferences.value.Food_Preferences.setMeal ? 3 : 0
        }
        
        // 營養考量 (卡路里打分，假設用戶想要中等卡路里的食物，偏離中值越遠分數越低)
        const idealCalories = 500 // 中等卡路里基準值
        const caloriesDiff = Math.abs((food.calories || 0) - idealCalories)
        score += caloriesDiff < 100 ? 2 : caloriesDiff < 200 ? 1 : 0
        
        return { ...food, score }
      })
      
      // 按分數排序並取前面的項目作為推薦
      const sortedFoods = [...foodWithScores].sort((a, b) => b.score - a.score)
      recommendedCategories.value = sortedFoods.slice(0, 6) // 取前6個作為推薦
    }

    // 多選 logo 按鈕
    const toggleRestaurant = (name) => {
      const idx = filters.value.restaurants.indexOf(name)
      if (idx === -1) {
        filters.value.restaurants.push(name)
      } else {
        filters.value.restaurants.splice(idx, 1)
      }
    }

    // 多選 food_type chip
    const toggleFoodType = (type) => {
      const idx = filters.value.food_type.indexOf(type)
      if (idx === -1) {
        filters.value.food_type.push(type)
      } else {
        filters.value.food_type.splice(idx, 1)
      }
    }

    const allExerciseNames = ref([]) // 所有運動名稱
    const allExerciseMap = ref({})   // 名稱對應分鐘數
    const selectedExercise = ref('')

    // 顯示分鐘數
    const getSelectedExerciseMinutes = computed(() => {
      const min = allExerciseMap.value[selectedExercise.value]
      return min !== undefined ? Number(min).toFixed(1) : '--'
    })

    // 加入偏好
    const addToPreference = async (exercise) => {
      if (!userId) return
      await saveExercisePreferences([...userExercisePreferences.value, exercise])
    }

    // 運動 icon 與強度對照表
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
    const getExerciseIcon = (name) => exerciseIconMap[name] || '🏋️'
    const getIntensityFlames = (name) => exerciseFlamesMap[name] || ''
    const getExerciseIntensity = (name) => exerciseIntensityMap[name] || ''

    return {
      filters,
      toggleType,
      recommendedCategories,
      searchResults,
      isLoading,
      hasSearched,
      handleSearch,
      addToFavorites,
      favoriteFoodIds,
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
      getDefaultFoodImage,
      setDefaultImageOnError,
      logImageDebug,
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
      getExerciseIntensity
    }
  }
}
</script>

<style scoped>
/* ----- 全局變量 (理想情況下在 main.css 或 App.vue style) ----- */
:root {
  --primary-color: #409EFF; /* Element Plus 主色藍 */
  --primary-color-light: #79bbff;
  --primary-color-dark: #337ecc;
  --warning-color: #E6A23C; /* 橘色 */
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --border-color-light: #e4e7ed;
  --border-color-lighter: #ebeef5;
  --bg-color: #f5f7fa;
  --card-shadow: 0 6px 16px -8px rgba(0,0,0,.08), 0 9px 28px 0 rgba(0,0,0,.05), 0 12px 48px 16px rgba(0,0,0,.03);
  --card-shadow-hover: 0 8px 20px -6px rgba(0,0,0,.1), 0 12px 32px 0 rgba(0,0,0,.07), 0 16px 52px 18px rgba(0,0,0,.04);
}

.food-search-page .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.page-title {
  font-size: 2.25rem; 
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 30px;
  text-align: center;
}

.search-form-container {
  margin-bottom: 30px;
}

.search-form-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-color-lighter);
}

.search-form-grid {
  display: grid;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  align-items: flex-end; /*  讓按鈕和輸入框底部對齊 */
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-regular);
  margin-bottom: 8px;
}

.input-with-icon {
  position: relative;
}

.input-with-icon .el-icon-food,
.input-with-icon .el-icon-shop {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1.1em;
}

.form-control {
  width:90%;
  padding: 12px 12px;
  padding-left: 36px; /*  為圖示留出空間 */
  font-size: 0.95rem;
  border: 1px solid var(--border-color-light);
  border-radius: 6px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-control:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
  outline: none;
}
.form-control-sm {
  padding-top: 8px;
  padding-bottom: 8px;
  font-size: 0.9rem;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}
.range-inputs .form-control {
  padding-left: 12px; /*  範圍輸入不需要圖示 */
}
.range-separator {
  color: var(--text-secondary);
}
.unit {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-left: 4px;
}

.type-selector .form-label {
  margin-bottom: 10px; /*  稍微增加類型選擇器的標籤間距 */
}
.type-buttons {
  display: flex;
  gap: 10px;
}
.type-btn {
  flex-grow: 1;
  padding: 9px 15px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  border: 1px solid #dcdfe6; /* Default grey border */
  background-color: #f5f7fa; /* Light grey background */
  color: #333; /* Dark text */
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.type-btn i {
  font-size: 1.1em;
  color: #909399; /* Default grey icon */
}
.type-btn:not(.active):hover {
  border-color: #E6A23C;
  color: #E6A23C;
  background-color: #fff7e6; /* Light orange background on hover */
}
.type-btn:not(.active):hover i {
  color: #E6A23C;
}
.type-btn.active {
  background-color: #E6A23C; /* Orange background when active */
  color: #fff;
  border-color: #E6A23C;
  box-shadow: 0 2px 6px rgba(230, 162, 60, 0.3);
}
.type-btn.active i {
  color: #fff;
}

.search-btn-container {
  display: flex;
  align-items: flex-end; /*  確保按鈕與其他輸入框底部對齊 */
}
.search-btn {
  width: 100%;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: 500;
  color: #fff;
  background-color: #E6A23C;
  border: 1px solid #E6A23C;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, transform 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.search-btn:hover {
  background-color: #cf9236;
  border-color: #cf9236;
  color: #fff;
  transform: translateY(-2px);
}
.search-btn .el-icon-search {
  font-size: 1.1em;
  color: #fff;
}

/* ----- 搜尋結果 & 推薦清單 ----- */
.search-results, .recommended-foods {
  margin-top: 40px;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 25px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color-lighter);
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.food-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  border: 1px solid var(--border-color-lighter);
}
.food-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--card-shadow-hover);
}

.food-image-container {
  width: 100%;
  height: 200px;
  background-color: var(--bg-color);
  position: relative;
  overflow: hidden;
}

.food-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.food-card:hover .food-image {
  transform: scale(1.05);
}

.calorie-on-image-button {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 68px; 
  height: 68px;
  background-color: rgba(230, 162, 60, 0.9);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0,0,0,0.25), 0 0 0 2px rgba(255,255,255,0.5);
  cursor: default;
  text-align: center;
  line-height: 1.1;
  transition: transform 0.2s ease-out;
}

.calorie-on-image-button:hover {
  transform: scale(1.05);
}

.calorie-on-image-button .calorie-value {
  font-size: 1.2rem; 
  display: block;
}

.calorie-on-image-button .calorie-unit {
  font-size: 0.7rem; 
  display: block;
  margin-top: 1px;
  opacity: 0.9;
}

.food-card-content {
  padding: 18px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.food-info {
  flex-grow: 1;
  margin-bottom: 15px;
}

.food-name-price-line {
  display: flex;
  align-items: center; /* Align items vertically */
  justify-content: space-between; /* Space out name, price and icon */
  margin-bottom: 8px; /* Adjust as needed */
}

.food-name {
  font-size: 1.25rem; /* Existing style */
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  margin-right: 10px; /* Space between name and price/icon */
  flex-grow: 1; /* Allow name to take available space */
  /* Text overflow properties from before, if still desired */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: calc(1.25rem * 1.3 * 2); 
}

.food-price-prominent {
  font-size: 1.2rem;
  font-weight: 700;
  color: #E6A23C; /* Orange color for price */
  margin-left: auto; /* Push price to the right if name is short */
  padding-left:10px; /* Add some space if it's next to the icon */
}

.nutrition-info-icon {
  font-size: 1.5rem;
  color: #ffaa55;
  cursor: pointer;
  margin-left: 10px;
  vertical-align: middle;
  transition: color 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(255, 170, 85, 0.08);
}

.nutrition-info-icon:hover {
  color: #E6A23C;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.18);
}

.nutrition-tooltip.improved-tooltip {
  min-width: 220px;
  background: #fffdfa;
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(230, 162, 60, 0.12);
  padding: 16px 18px 12px 18px;
  color: #f1b818;
}
.nutrition-table {
  width: 100%;
  border-collapse: collapse;
}
.nutrition-table td {
  padding: 4px 8px;
  font-size: 1rem;
  vertical-align: middle;
}
.nutrition-table td:first-child {
  color: #ffaa55;
  font-weight: 500;
  width: 80px;
}
.nutrient {
  font-weight: bold;
  font-size: 1.05em;
}
.nutrient.protein { color: #4caf50; }
.nutrient.fat { color: #e57373; }
.nutrient.sugar { color: #fbc02d; }
.nutrient.sodium { color: #64b5f6; }
.nutrient.carb { color: #8d6e63; }
.nutrient.caffeine { color: #6d4c41; }

.food-details {
  font-size: 0.88rem;
  color: var(--text-regular);
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}
.detail-item:last-child {
  margin-bottom: 0;
}
.detail-item i {
  color: var(--primary-color-light);
  font-size: 1.1em;
}

.detail-item .el-icon-money,
.detail-item .el-icon-data-line {
  color: var(--warning-color);
}

.food-actions {
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid var(--border-color-lighter);
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.action-btn {
  flex-grow: 1;
  padding: 10px 12px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background-color: #f5f7fa;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.action-btn i {
  font-size: 1.2em;
  color: #909399;
}

/* 運動計算按鈕樣式 */
.action-btn.calculator-btn {
  border-color: #dcdfe6;
}
.action-btn.calculator-btn:hover {
  border-color: #c0c4cc;
  background-color: #ebeef5;
  color: #303133;
}
.action-btn.calculator-btn:hover i {
  color: #303133;
}

/* 收藏按鈕樣式 */
.action-btn.favorite-btn {
  border-color: #f0c78a;
  background-color: #fdf6ec;
  color: #e6a23c;
}
.action-btn.favorite-btn i {
  color: #e6a23c;
}
.action-btn.favorite-btn:hover {
  border-color: #e6a23c;
  background-color: #faecd8;
  color: #d48d1f;
}
.action-btn.favorite-btn:hover i {
  color: #d48d1f;
}

/* 記錄按鈕樣式 - 主要按鈕 */
.action-btn.record-btn {
  background-color: #e6a23c;
  border-color: #e6a23c;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(230, 162, 60, 0.3);
}
.action-btn.record-btn i {
  color: #fff;
}
.action-btn.record-btn:hover {
  background-color: #d48d1f;
  border-color: #ca8309;
  color: #fff;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.4);
}
.action-btn.record-btn:hover i {
  color: #fff;
}

.no-results, .loading-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}
.no-results-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  color: var(--text-secondary);
}
.loading-spinner {
  border: 4px solid var(--bg-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: #fff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 500px;
}
.modal-exercise {
 max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color-lighter);
}
.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}
.close-button {
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  line-height: 1;
}
.close-button:hover {
  color: var(--text-primary);
}

.modal-body .search-box {
  display: flex;
  margin-bottom: 20px;
  gap:10px;
}
.modal-body .search-box input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid var(--border-color-light);
  border-radius: 6px;
}
.search-exercise-btn {
  padding: 10px 15px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.search-exercise-btn:hover{
   background-color: var(--primary-color-dark);
}

.exercise-results .exercise-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color-lighter);
}
.exercise-results .exercise-item:last-child {
  border-bottom: none;
}
.exercise-results .exercise-item i {
  margin-right: 12px;
  color: var(--primary-color);
  font-size: 1.3em;
}
.exercise-results .exercise-item p strong {
  font-weight: 600;
  color: var(--text-primary);
}

.exercise-list .exercise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color-lighter);
}
.exercise-list .exercise-item:last-child {
  border-bottom: none;
}
.exercise-list .exercise-item span {
  font-size: 0.9rem;
  color: var(--text-primary);
}
.exercise-list .exercise-item button {
  padding: 8px 15px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.exercise-list .exercise-item button:hover {
  background-color: var(--primary-color-dark);
}

/* 餐廳 logo 按鈕樣式 */
.restaurant-logo-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;
}
.restaurant-logo-btn {
  border: 1px solid #e4e7ed;
  background: #fff;
  border-radius: 8px;
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.restaurant-logo-btn.active, .restaurant-logo-btn:hover {
  border-color: #E6A23C;
  box-shadow: 0 2px 8px rgba(230,162,60,0.08);
}
.restaurant-logo-img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 4px;
  background: #f5f5f5;
}

/* 食物類型 chip 樣式 */
.foodtype-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
  margin-bottom: 8px;
  min-height: 40px;
}
.foodtype-chip-btn {
  border: 1px solid #e4e7ed;
  background: #fff;
  border-radius: 8px;
  padding: 6px 16px;
  font-size: 1rem;
  color: #606266;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.foodtype-chip-btn.active, .foodtype-chip-btn:hover {
  border-color: #E6A23C;
  background: #faecd8;
  color: #d48d1f;
  box-shadow: 0 2px 8px rgba(230,162,60,0.08);
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
}
  .search-form-grid, .form-row {
    grid-template-columns: 1fr;
}
  .food-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}
   .food-image-container {
    height: 160px; 
}
  .food-name {
    font-size: 1.1rem;
    min-height: calc(1.1rem * 1.3 * 2); 
}
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  .food-grid {
    grid-template-columns: 1fr;
  }
  .food-image-container {
    height: 150px; 
  }
   .food-name {
    font-size: 1.05rem;
    min-height: calc(1.05rem * 1.3 * 2);
}
  .action-btn {
    font-size: 0.85rem;
    padding: 8px 10px;
}
  .modal {
    width: 95%;
    padding: 20px;
  }
  .modal-header h3 {
    font-size: 1.3rem;
  }
}

.exercise-modal-body {
  padding: 10px 0 0 0;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #131618;
  margin-bottom: 8px;
  margin-top: 12px;
}
.exercise-pref-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}
.exercise-pref-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f4faff;
  border-radius: 6px;
  padding: 8px 12px;
}
.exercise-icon {
  font-size: 1.3em;
}
.exercise-name {
  font-weight: 500;
  color: #333;
}
.exercise-intensity {
  margin-left: 8px;
  color: #e6a23c;
  font-size: 1.1em;
}
.exercise-intensity-text {
  margin-left: 2px;
  color: #888;
  font-size: 0.95em;
}
.exercise-minutes {
  margin-left: auto;
  color: #e6a23c;
  font-weight: 400;
}
.empty-pref-tip {
  color: #aaa;
  font-size: 0.95em;
  margin-bottom: 8px;
}
.exercise-divider {
  border: none;
  border-top: 1px solid #eee;
  margin: 12px 0;
}
.all-exercise-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.all-exercise-select {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  font-size: 1em;
}
.add-pref-btn {
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.add-pref-btn:hover {
  background: #337ecc;
}
@media (max-width: 600px) {
  .exercise-pref-item, .all-exercise-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
    padding: 10px 8px;
  }
  .exercise-minutes {
    margin-left: 0;
    margin-top: 4px;
  }
}
</style>