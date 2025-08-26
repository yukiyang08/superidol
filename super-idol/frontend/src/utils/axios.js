import axios from 'axios';

// 設置 API 基礎 URL
axios.defaults.baseURL = 'http://localhost:5000';

// 請求攔截器
axios.interceptors.request.use(
  (config) => {
    // 從 localStorage 獲取 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 響應攔截器
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API 請求錯誤:', error.response || error.message);
    return Promise.reject(error);
  }
);

export default axios; 