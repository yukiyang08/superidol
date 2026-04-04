import { defineStore } from 'pinia'
import api from '../services/api'

export const useFoodStore = defineStore('food', {
  state: () => ({
    foodItems: [],
    searchResults: [],
    recentFoods: [],
    userFoodRecords: [],
    loading: false,
    error: null,
    filters: {
      category: null,
      sortBy: 'name',
      searchQuery: ''
    },
    pagination: {
      page: 1,
      limit: 10,
      total: 0
    }
  }),
  
  getters: {
    // 獲取已經過濾和排序的食物列表
    filteredFoodItems: (state) => {
      // 首先應用搜索條件
      let filtered = state.searchResults.length > 0 
        ? [...state.searchResults] 
        : [...state.foodItems]
      
      // 應用分類過濾
      if (state.filters.category) {
        filtered = filtered.filter(item => item.category === state.filters.category)
      }
      
      // 根據排序條件排序
      switch (state.filters.sortBy) {
        case 'calories':
          filtered.sort((a, b) => a.calories - b.calories)
          break
        case 'protein':
          filtered.sort((a, b) => a.protein - b.protein)
          break
        case 'name':
          filtered.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'recent':
          // 按最近添加的順序排序
          break
        default:
          filtered.sort((a, b) => a.name.localeCompare(b.name))
      }
      
      return filtered
    },
    
    // 獲取分頁後的食物
    paginatedFoodItems: (state) => {
      const start = (state.pagination.page - 1) * state.pagination.limit
      const end = start + state.pagination.limit
      return state.filteredFoodItems.slice(start, end)
    },
    
    // 獲取用戶最近的食物記錄
    todaysFoodRecords: (state) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      return state.userFoodRecords.filter(record => {
        const recordDate = new Date(record.timestamp)
        recordDate.setHours(0, 0, 0, 0)
        return recordDate.getTime() === today.getTime()
      })
    },
    
    // 計算今日營養摘要
    todayNutritionSummary: (state, getters) => {
      return getters.todaysFoodRecords.reduce((summary, record) => {
        summary.calories += record.calories || 0
        summary.protein += record.protein || 0
        summary.carbs += record.carbs || 0
        summary.fat += record.fat || 0
        summary.sugar += record.sugar || 0
        return summary
      }, { calories: 0, protein: 0, carbs: 0, fat: 0, sugar: 0 })
    },
    
    // 按餐點獲取今日食物記錄
    foodRecordsByMeal: (state, getters) => {
      const result = {
        breakfast: [],
        lunch: [],
        dinner: [],
        snacks: []
      }
      
      getters.todaysFoodRecords.forEach(record => {
        if (record.meal && result[record.meal]) {
          result[record.meal].push(record)
        } else {
          result.snacks.push(record)
        }
      })
      
      return result
    },
    
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error
  },
  
  actions: {
    // 獲取所有食物資料
    async fetchFoodItems() {
      this.loading = true
      this.error = null
      
      try {
        // 這裡應該使用實際的 API 服務獲取數據
        const response = await api.get('/food')
        this.foodItems = response.data
        this.pagination.total = response.data.length
        return this.foodItems
      } catch (error) {
        this.error = error.message || '獲取食物數據失敗'
        console.error('獲取食物數據失敗:', error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    // 搜索食物
    async searchFood(query) {
      this.loading = true
      this.error = null
      this.filters.searchQuery = query
      
      try {
        // 檢查查詢字符串是否為空
        if (!query.trim()) {
          this.searchResults = []
          return []
        }
        
        // 調用 API 進行搜索
        const response = await api.get('/food/search', { params: { q: query } })
        this.searchResults = response.data
        return this.searchResults
      } catch (error) {
        this.error = error.message || '搜索食物失敗'
        console.error('搜索食物失敗:', error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    // 獲取食物詳情
    async getFoodDetails(foodId) {
      this.loading = true
      
      try {
        const response = await api.get(`/food/${foodId}`)
        
        // 更新本地緩存
        const index = this.foodItems.findIndex(food => food.id === foodId)
        if (index >= 0) {
          this.foodItems[index] = response.data
        } else {
          this.foodItems.push(response.data)
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '獲取食物詳情失敗'
        console.error('獲取食物詳情失敗:', error)
        return null
      } finally {
        this.loading = false
      }
    },
    
    // 添加食物記錄
    async addFoodRecord(record) {
      this.loading = true
      
      try {
        const response = await api.post('/user/food-records', record)
        
        // 添加到本地狀態
        this.userFoodRecords.unshift(response.data)
        
        // 添加到最近食物
        const existingIndex = this.recentFoods.findIndex(food => food.id === record.foodId)
        if (existingIndex >= 0) {
          // 如果食物已存在於最近列表，則移至頂部
          const existing = this.recentFoods.splice(existingIndex, 1)[0]
          this.recentFoods.unshift(existing)
        } else {
          // 否則添加到最近食物列表
          const foodItem = this.foodItems.find(food => food.id === record.foodId)
          if (foodItem) {
            this.recentFoods.unshift(foodItem)
            // 保持最近食物列表的長度
            if (this.recentFoods.length > 10) {
              this.recentFoods.pop()
            }
          }
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '添加食物記錄失敗'
        console.error('添加食物記錄失敗:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 獲取用戶食物記錄
    async fetchUserFoodRecords(params = {}) {
      this.loading = true
      
      try {
        const response = await api.get('/user/food-records', { params })
        this.userFoodRecords = response.data
        return this.userFoodRecords
      } catch (error) {
        this.error = error.message || '獲取食物記錄失敗'
        console.error('獲取食物記錄失敗:', error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    // 更新食物記錄
    async updateFoodRecord(recordId, updates) {
      this.loading = true
      
      try {
        const response = await api.put(`/user/food-records/${recordId}`, updates)
        
        // 更新本地狀態
        const index = this.userFoodRecords.findIndex(record => record.id === recordId)
        if (index >= 0) {
          this.userFoodRecords[index] = { ...this.userFoodRecords[index], ...response.data }
        }
        
        return response.data
      } catch (error) {
        this.error = error.message || '更新食物記錄失敗'
        console.error('更新食物記錄失敗:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 刪除食物記錄
    async deleteFoodRecord(recordId) {
      this.loading = true
      
      try {
        await api.delete(`/user/food-records/${recordId}`)
        
        // 從本地狀態中移除
        const index = this.userFoodRecords.findIndex(record => record.id === recordId)
        if (index >= 0) {
          this.userFoodRecords.splice(index, 1)
        }
        
        return true
      } catch (error) {
        this.error = error.message || '刪除食物記錄失敗'
        console.error('刪除食物記錄失敗:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    // 設置篩選條件
    setFilter(filterName, value) {
      if (Object.prototype.hasOwnProperty.call(this.filters, filterName)) {
        this.filters[filterName] = value
        
        // 重置分頁
        this.pagination.page = 1
      }
    },
    
    // 設置分頁
    setPage(page) {
      this.pagination.page = page
    },
    
    // 重置篩選條件
    resetFilters() {
      this.filters = {
        category: null,
        sortBy: 'name',
        searchQuery: ''
      }
      this.searchResults = []
      this.pagination.page = 1
    }
  }
}) 