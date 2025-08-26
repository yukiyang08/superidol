import { defineStore } from 'pinia'
import api from '../services/api'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    isLoading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    hasError: (state) => !!state.error,
  },
  
  actions: {
    async login(credentials) {
      this.isLoading = true
      this.error = null
      
      try {
        // 修正API路徑，添加/api前綴
        const response = await api.post('/api/auth/login', credentials)
        
        // 儲存 token 到 localStorage
        const token = response.data.access_token
        localStorage.setItem('token', token)
        
        // 儲存用戶ID到localStorage
        if (response.data.user && response.data.user.id) {
          localStorage.setItem('userId', response.data.user.id)
        }
        
        // 更新 state
        this.token = token
        this.user = response.data.user
        
        return response.data
      } catch (error) {
        console.error('登入錯誤完整信息:', error);
        if (error.response?.status === 401) {
          this.error = '帳號或密碼錯誤，請重新輸入'
        } else {
          this.error = error.response?.data?.error || '登入失敗，請檢查您的憑證'
        }
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async register(userData) {
      this.isLoading = true
      this.error = null
      
      try {
        // 將欄位轉換為後端需要的格式
        const formattedData = {
          name: userData.name,
          email: userData.email,
          password: userData.password,
          weight: userData.weight,
          budget: userData.budget,
          weekcalorielimit: userData.calorieLimit,  // 欄位名轉換
          restaurant_preferences: userData.Food_Preference ? userData.Food_Preference.split(',').map(p => p.trim()) : [],  // 轉為陣列
          exercise_preferences: userData.exercisePreference ? userData.exercisePreference.split(',').map(p => p.trim()) : []  // 轉為陣列
        };
        
        console.log('正在發送註冊請求:', formattedData);
        const response = await api.post('/api/auth/signup', formattedData)
        
        console.log('註冊回應:', response.data);
        
        // 檢查回應中是否有 token 
        if (response.data && response.data.access_token) {
          // 儲存 token 到 localStorage
          const token = response.data.access_token
          localStorage.setItem('token', token)
          
          // 儲存用戶ID到localStorage
          if (response.data.user && response.data.user.id) {
            localStorage.setItem('userId', response.data.user.id)
          }
          
          // 更新 state
          this.token = token
          this.user = response.data.user || {
            name: userData.name,
            email: userData.email
          }
          
          return response.data
        } else {
          // 如果沒有 token，可能需要手動登入
          console.log('註冊成功但未返回 token，嘗試自動登入')
          // 嘗試登入
          try {
            return await this.login({
              email: userData.email,
              password: userData.password
            })
          } catch (loginError) {
            console.error('自動登入失敗:', loginError)
            // 雖然註冊成功，但登入失敗，提示用戶手動登入
            ElMessage.warning('註冊成功，但自動登入失敗，請手動登入')
            throw new Error('註冊成功，請手動登入')
          }
        }
      } catch (error) {
        console.error('註冊錯誤完整信息:', error);
        
        // 特別處理郵件已存在的情況
        if (error.response?.status === 409) {
          this.error = '這個電子郵件已經註冊過，請使用其他電子郵件或直接登入'
          // 清除sessionStorage避免資料殘留
          sessionStorage.removeItem('registrationData')
        } else {
          this.error = error.response?.data?.error || '註冊失敗，請稍後再試'
        }
        
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async logout() {
      try {
        // 可選：通知後端使 token 失效
        if (this.token) {
          await api.post('/api/auth/logout')
        }
      } catch (error) {
        console.error('登出 API 請求失敗:', error)
      } finally {
        // 無論 API 呼叫是否成功，都清除前端的 token 和使用者資訊
        localStorage.removeItem('token')
        localStorage.removeItem('userId')
        this.token = null
        this.user = null
      }
    },
    
    async fetchUserData() {
      if (!this.token) return
      
      this.isLoading = true
      
      try {
        const response = await api.get('/api/auth/user')
        this.user = response.data
        
        // 更新localStorage中的userId
        if (response.data && response.data.id) {
          localStorage.setItem('userId', response.data.id)
        }
        
        return response.data
      } catch (error) {
        console.error('獲取使用者資料失敗:', error)
        // 如果獲取用戶資料失敗，可能是 token 已失效
        if (error.response?.status === 401) {
          this.logout()
        }
      } finally {
        this.isLoading = false
      }
    },
    
    async updateUserProfile(profileData) {
      if (!this.token) return
      
      this.isLoading = true
      this.error = null
      
      try {
        const response = await api.put('/api/auth/profile', profileData)
        this.user = { ...this.user, ...response.data }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新個人資料失敗'
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    clearError() {
      this.error = null
    }
  }
}) 