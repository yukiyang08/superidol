import axios from 'axios'

const configuredBaseURL = (import.meta.env.VITE_API_BASE || '').trim().replace(/\/$/, '')

const baseURL = configuredBaseURL || (
  import.meta.env.PROD
    ? 'https://superidol-i0t9.onrender.com'
    : 'http://localhost:5000'
)

// 創建 axios 實例
export const api = axios.create({
  baseURL,
  timeout: 20000, // 預設請求超時時間 20 秒
  headers: {
    'Accept': 'application/json'
  }
})

// 打印詳細的請求信息以便調試
api.interceptors.request.use(
  (config) => {
    console.log(`API請求: ${config.method.toUpperCase()} ${config.baseURL}${config.url}`, config.data || {});

    // Let the browser set multipart boundaries for FormData uploads.
    if (config.data instanceof FormData) {
      if (config.headers?.['Content-Type']) {
        delete config.headers['Content-Type']
      }
      if (config.headers?.common?.['Content-Type']) {
        delete config.headers.common['Content-Type']
      }
    } else if (!config.headers?.['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }

    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('請求錯誤:', error);
    return Promise.reject(error)
  }
)

// 響應攔截器 - 處理常見錯誤
api.interceptors.response.use(
  (response) => {
    console.log(`API回應 [${response.status}]:`, response.data);
    return response
  },
  (error) => {
    console.error('回應錯誤詳情:', error.response?.data || error.message);
    const { response } = error
    
    // 未驗證 (401) - 清除 token 並重新導向到登入頁面
    if (response && response.status === 401) {
      localStorage.removeItem('token')
      // 避免在登入頁面時重新導向
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    // 伺服器錯誤 (500) - 通用錯誤處理
    if (response && response.status >= 500) {
      console.error('服務器錯誤:', error)
      // 可以在這裡顯示通用錯誤提示
    }
    
    return Promise.reject(error)
  }
)

// 添加默認導出，同時支持命名導入和默認導入
export default api; 