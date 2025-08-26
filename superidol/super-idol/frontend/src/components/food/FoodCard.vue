<template>
  <div class="food-card" :class="{ 'selected': isSelected, 'selectable': selectable }">
    <div class="food-image-container">
      <img 
        :src="food.image || defaultImage" 
        :alt="food.name"
        class="food-image"
      />
    </div>
    <div class="food-details">
      <h3 class="food-name">{{ food.name }}</h3>
      <div class="food-info">
        <span class="food-calories">{{ food.calories }} 卡路里</span>
        <span class="food-serving">{{ food.servingSize }}</span>
      </div>
      <div class="food-nutrition">
        <div class="nutrition-item">
          <span class="nutrition-value">{{ food.protein }}g</span>
          <span class="nutrition-label">蛋白質</span>
        </div>
        <div class="nutrition-item">
          <span class="nutrition-value">{{ food.carbs }}g</span>
          <span class="nutrition-label">碳水</span>
        </div>
        <div class="nutrition-item">
          <span class="nutrition-value">{{ food.fat }}g</span>
          <span class="nutrition-label">脂肪</span>
        </div>
      </div>
    </div>
    <div class="food-actions">
      <slot name="actions">
        <!-- 默認操作按鈕 -->
        <button 
          v-if="selectable" 
          class="btn btn-primary" 
          @click="$emit('select', food)"
        >
          {{ isSelected ? '已選擇' : '選擇' }}
        </button>
        <button 
          v-else 
          class="btn btn-primary" 
          @click="$emit('view-details', food)"
        >
          詳情
        </button>
      </slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FoodCard',
  props: {
    food: {
      type: Object,
      required: true,
      default: () => ({
        id: 0,
        name: '',
        calories: 0,
        servingSize: '100g',
        protein: 0,
        carbs: 0,
        fat: 0,
        image: null
      })
    },
    isSelected: {
      type: Boolean,
      default: false
    },
    selectable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['select', 'view-details'],
  data() {
    return {
      defaultImage: '/src/assets/images/default-food.jpg'
    }
  }
}
</script>

<style scoped>
.food-card {
  display: flex;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.food-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.food-card.selected {
  border: 2px solid var(--primary-color);
}

.food-card.selectable {
  cursor: pointer;
}

.food-image-container {
  width: 120px;
  height: 120px;
  overflow: hidden;
}

.food-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.food-details {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.food-name {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-color);
}

.food-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.food-nutrition {
  display: flex;
  gap: 16px;
}

.nutrition-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nutrition-value {
  font-weight: 600;
  font-size: 14px;
}

.nutrition-label {
  font-size: 12px;
  color: #666;
}

.food-actions {
  display: flex;
  align-items: center;
  padding: 12px;
}

@media (max-width: 480px) {
  .food-card {
    flex-direction: column;
  }
  
  .food-image-container {
    width: 100%;
    height: 160px;
  }
  
  .food-actions {
    padding-top: 0;
  }
}
</style> 