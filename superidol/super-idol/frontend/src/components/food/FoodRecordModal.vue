<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal modal-record">
      <div class="modal-header">
        <h3>添加食物記錄</h3>
        <button class="close-button" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <div class="meal-type-selector">
          <h4>選擇餐點類型</h4>
          <div class="meal-type-options">
            <label class="meal-type-option">
              <input type="radio" value="早餐" v-model="selectedMealType" />
              <span class="meal-type-label">
                <i class="el-icon-sunrise"></i>
                早餐
              </span>
            </label>
            <label class="meal-type-option">
              <input type="radio" value="午餐" v-model="selectedMealType" />
              <span class="meal-type-label">
                <i class="el-icon-sunny"></i>
                午餐
              </span>
            </label>
            <label class="meal-type-option">
              <input type="radio" value="晚餐" v-model="selectedMealType" />
              <span class="meal-type-label">
                <i class="el-icon-sunset"></i>
                晚餐
              </span>
            </label>
            <label class="meal-type-option">
              <input type="radio" value="點心" v-model="selectedMealType" />
              <span class="meal-type-label">
                <i class="el-icon-dessert"></i>
                點心
              </span>
            </label>
          </div>
        </div>
        <div class="quantity-selector">
          <h4>選擇數量</h4>
          <div class="quantity-controls">
            <button class="quantity-btn" @click="quantity > 1 && quantity--">-</button>
            <input type="number" v-model="quantity" min="1" class="quantity-input" />
            <button class="quantity-btn" @click="quantity++">+</button>
          </div>
        </div>
        <div class="date-selector">
          <h4>選擇紀錄日期</h4>
          <input type="date" v-model="selectedDateString" :max="todayString" class="date-input" />
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel-btn" @click="close">取消</button>
          <button class="modal-btn save-btn" @click="saveRecord">{{ editMode ? '更新' : '儲存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: { type: Boolean, required: true },
  food: { type: Object, default: null },
  editMode: { type: Boolean, default: false },
  record: { type: Object, default: null },
})
const emit = defineEmits(['update:visible', 'saved'])

const selectedMealType = ref('')
const quantity = ref(1)
const today = new Date()
const year = today.getFullYear()
const month = String(today.getMonth() + 1).padStart(2, '0')
const day = String(today.getDate()).padStart(2, '0')
const todayString = `${year}-${month}-${day}`
const selectedDateString = ref(todayString)

watch(() => props.visible, (val) => {
  if (val) {
    if (props.editMode && props.record) {
      selectedMealType.value = props.record.mealtime || ''
      quantity.value = props.record.quantity || 1
      selectedDateString.value = props.record.date || todayString
    } else {
      selectedMealType.value = ''
      quantity.value = 1
      selectedDateString.value = todayString
    }
  }
})

const close = () => {
  emit('update:visible', false)
}

const saveRecord = async () => {
  if (!selectedMealType.value) {
    ElMessage.warning('請選擇餐點類型')
    return
  }
  if (!selectedDateString.value) {
    ElMessage.warning('請選擇紀錄日期')
    return
  }
  try {
    const userId = localStorage.getItem('userId')
    if (!userId) {
      ElMessage.warning('請先登入')
      return
    }
    if (props.editMode && props.record) {
      const response = await fetch(`http://localhost:5000/api/food/record/${props.record.record_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: parseInt(userId),
          mealtime: selectedMealType.value,
          quantity: quantity.value,
          date: selectedDateString.value
        })
      })
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`API 請求失敗: ${response.status} ${response.statusText} - ${errorText}`)
      }
      ElMessage.success('已成功更新食物記錄')
      emit('saved')
      close()
    } else {
      const food_id = props.food?.food_id ?? props.food?.id
      const response = await fetch('http://localhost:5000/api/food/record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: parseInt(userId),
          food_id,
          mealtime: selectedMealType.value,
          quantity: quantity.value,
          date: selectedDateString.value
        })
      })
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`API 請求失敗: ${response.status} ${response.statusText} - ${errorText}`)
      }
      ElMessage.success('已成功添加到食物記錄')
      emit('saved')
      close()
    }
  } catch (error) {
    ElMessage.error(props.editMode ? '更新食物記錄失敗，請稍後再試' : '添加食物記錄失敗，請稍後再試')
  }
}
</script>

<style scoped>
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}
.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #333;
}
.close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  transition: color 0.3s;
}
.close-button:hover {
  color: #333;
}
.modal-body {
  padding: 20px;
}
.meal-type-selector,
.quantity-selector,
.date-selector {
  margin-bottom: 24px;
}
.meal-type-selector h4,
.quantity-selector h4,
.date-selector h4 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
.meal-type-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.meal-type-option {
  position: relative;
  cursor: pointer;
}
.meal-type-option input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}
.meal-type-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  transition: all 0.3s;
}
.meal-type-option input:checked + .meal-type-label {
  background: #fff3e0;
  color: #ff9800;
}
.meal-type-label i {
  font-size: 24px;
}
.quantity-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}
.quantity-btn {
  width: 40px;
  height: 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}
.quantity-btn:hover {
  background: #f5f5f5;
}
.quantity-input {
  width: 60px;
  padding: 8px;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}
.date-input {
  width: 100%;
  padding: 8px 12px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.modal-btn {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}
.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
}
.cancel-btn:hover {
  background: #e0e0e0;
}
.save-btn {
  background: #ffaa55;
  color: white;
  border: none;
}
.save-btn:hover {
  background: #ff9933;
}
@media (max-width: 768px) {
  .meal-type-options {
    grid-template-columns: 1fr;
  }
}
</style> 