<template>
  <div class="my-favorite-page">
    <div class="container">
      <h1 class="page-title">我的最愛</h1>
      
      <!-- 載入中狀態 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>載入中...</p>
      </div>

      <!-- 無最愛提示 -->
      <div v-if="!isLoading && favoriteFoods.length === 0" class="no-results">
        <i class="el-icon-star-off no-results-icon"></i>
        <p>尚未收藏任何食物</p>
        <p class="no-results-subtitle">到食物搜尋頁面尋找喜歡的食物並加入最愛吧！</p>
      </div>

      <!-- 最愛列表 -->
      <div v-if="favoriteFoods.length > 0" class="favorites-section">
        <div class="favorites-count">
          <p>共 {{ favoriteFoods.length }} 項最愛</p>
        </div>
        <div class="food-grid">
          <div class="food-card" v-for="(food, index) in favoriteFoods" :key="food.food_id">
            <div class="food-card-content">
              <div class="food-info">
                <h3 class="food-name">{{ food.name }}</h3>
                <div class="food-details">
                  <div class="detail-item">
                    <i class="el-icon-shop"></i>
                    <span>{{ food.restaurant || '未知餐廳' }}</span>
                  </div>
                  <div class="detail-item">
                    <i class="el-icon-money"></i>
                    <span>{{ food.price }} 元</span>
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
                <button class="action-btn record-btn" @click="openFoodRecordModal(food)">
                  <i class="el-icon-plus"></i>
                  加入紀錄
                </button>
                <button class="action-btn remove-btn" @click="confirmRemoveFavorite(food)" :disabled="isRemoving">
                  <i class="el-icon-star-off"></i>
                  {{ isRemoving ? '移除中...' : '移除最愛' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 確認刪除 Modal -->
      <div v-if="showConfirmModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h3>確認移除最愛</h3>
          </div>
          <div class="modal-body">
            <p>確定要移除 <strong>{{ selectedFood?.name }}</strong> 的最愛嗎？</p>
          </div>
          <div class="modal-actions">
            <button class="modal-btn cancel-btn" @click="cancelRemove">取消</button>
            <button class="modal-btn confirm-btn" @click="removeFavorite" :disabled="isRemoving">
              {{ isRemoving ? '移除中...' : '確認移除' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 加入紀錄 Modal -->
      <FoodRecordModal v-model:visible="showRecordModal" :food="currentFood" @saved="onRecordSaved" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import FoodRecordModal from '@/components/food/FoodRecordModal.vue'
import api from '@/services/api'

export default {
  name: 'MyFavorite',
  components: { FoodRecordModal },
  setup() {
    const favoriteFoods = ref([])
    const isLoading = ref(false)
    const isRemoving = ref(false)
    const showConfirmModal = ref(false)
    const selectedFood = ref(null)
    const showRecordModal = ref(false)
    const currentFood = ref(null)

    // 載入最愛資料
    const fetchFavorites = async () => {
      const userId = localStorage.getItem('userId')
      if (!userId) {
        ElMessage.warning('請先登入')
        return
      }

      isLoading.value = true
      try {
        const { data } = await api.get('/api/myfavorite/favorites', { params: { user_id: userId } })
        if (Array.isArray(data)) {
          favoriteFoods.value = data.map(item => ({
            food_id: item.food_id ?? item.id,
            name: item.name || '未知食物',
            calories: item.calories || 0,
            price: item.price || 0,
            type: item.type || '未分類',
            food_type: item.food_type || '未分類',
            restaurant: item.restaurant || '未知餐廳'
          }))
        } else {
          throw new Error('API 回傳資料格式錯誤')
        }
      } catch (error) {
        ElMessage.error(`載入最愛失敗: ${error.message}`)
        favoriteFoods.value = []
      } finally {
        isLoading.value = false
      }
    }

    // 確認移除最愛
    const confirmRemoveFavorite = (food) => {
      selectedFood.value = food
      showConfirmModal.value = true
    }

    // 取消移除
    const cancelRemove = () => {
      showConfirmModal.value = false
      selectedFood.value = null
    }

    // 刪除最愛
    const removeFavorite = async () => {
      if (!selectedFood.value) return
      const userId = localStorage.getItem('userId')
      if (!userId) {
        ElMessage.warning('請先登入')
        return
      }
      isRemoving.value = true
      try {
        await api.delete('/api/myfavorite/favorites', {
          data: { user_id: parseInt(userId), food_id: selectedFood.value.food_id }
        })
        ElMessage.success('已移除最愛')
        favoriteFoods.value = favoriteFoods.value.filter(food => food.food_id !== selectedFood.value.food_id)
        showConfirmModal.value = false
        selectedFood.value = null
      } catch (error) {
        ElMessage.error(`移除最愛失敗: ${error.message}`)
      } finally {
        isRemoving.value = false
      }
    }

    // 加入紀錄功能
    const openFoodRecordModal = (food) => {
      currentFood.value = food
      showRecordModal.value = true
    }

    const onRecordSaved = () => {
      ElMessage.success('已成功添加到食物記錄')
    }

    onMounted(() => {
      fetchFavorites()
    })
    
    return {
      favoriteFoods,
      isLoading,
      isRemoving,
      showConfirmModal,
      selectedFood,
      confirmRemoveFavorite,
      cancelRemove,
      removeFavorite,
      showRecordModal,
      currentFood,
      openFoodRecordModal,
      onRecordSaved
    }
  }
}
</script>

<style scoped>
.my-favorite-page {
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

.favorites-section {
  margin-bottom: 40px;
}

.favorites-count {
  margin-bottom: 20px;
  text-align: right;
}

.favorites-count p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.food-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.food-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.food-card-content {
  padding: 20px;
}

.food-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #333;
}

.food-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.detail-item i {
  color: #ffaa55;
}

.food-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.record-btn {
  background: #ffaa55;
  color: white;
  margin-right: 8px;
}

.record-btn:hover {
  background: #ff9933;
}

.remove-btn {
  background: #ff6b6b;
  color: white;
}

.remove-btn:hover:not(:disabled) {
  background: #ff5252;
}

.remove-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin: 40px 0;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ffaa55;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin: 40px 0;
  text-align: center;
}

.no-results-icon {
  font-size: 48px;
  color: #ccc;
  margin-bottom: 16px;
}

.no-results p {
  margin: 0 0 8px;
  color: #666;
  font-size: 18px;
}

.no-results-subtitle {
  color: #999 !important;
  font-size: 14px !important;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 20px 24px 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.modal-body {
  padding: 16px 24px;
}

.modal-body p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding: 0 24px 24px;
}

.modal-btn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.confirm-btn {
  background: #ff6b6b;
  color: white;
}

.confirm-btn:hover:not(:disabled) {
  background: #ff5252;
}

.modal-record {
  width: 80%;
  max-width: 600px;
}

.meal-type-selector {
  margin-bottom: 20px;
}

.meal-type-options {
  display: flex;
  gap: 12px;
}

.meal-type-option {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.meal-type-option input {
  margin-bottom: 8px;
}

.meal-type-label {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.quantity-selector {
  margin-bottom: 20px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.quantity-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.quantity-input {
  width: 50px;
  text-align: center;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
}
</style> 