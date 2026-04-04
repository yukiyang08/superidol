<template>
  <div class="api-test">
    <h1>API 測試頁面</h1>
    
    <div class="test-form">
      <h2>註冊測試</h2>
      <el-form>
        <el-form-item label="姓名">
          <el-input v-model="register.name" placeholder="請輸入姓名" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="register.email" placeholder="請輸入電子郵件" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="register.password" type="password" placeholder="請輸入密碼" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="testSignup">測試註冊</el-button>
        </el-form-item>
      </el-form>

      <h2>登入測試</h2>
      <el-form>
        <el-form-item label="Email">
          <el-input v-model="login.email" placeholder="請輸入電子郵件" />
        </el-form-item>
        <el-form-item label="密碼">
          <el-input v-model="login.password" type="password" placeholder="請輸入密碼" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="testLogin">測試登入</el-button>
        </el-form-item>
      </el-form>
      
      <h2>測試結果</h2>
      <div v-if="loading" class="result">
        <el-alert title="載入中..." type="info" :closable="false" />
      </div>
      <div v-else-if="error" class="result">
        <el-alert :title="error" type="error" :closable="false" />
      </div>
      <div v-else-if="result" class="result">
        <el-alert title="請求成功!" type="success" :closable="false" />
        <pre>{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue';
import axios from 'axios';

export default {
  name: 'ApiTest',
  setup() {
    const register = reactive({
      name: 'Test User',
      email: `test${Date.now()}@example.com`,
      password: 'password123'
    });

    const login = reactive({
      email: '',
      password: 'password123'
    });

    const result = ref(null);
    const error = ref(null);
    const loading = ref(false);

    // 直接使用axios而非現有api服務，以排除可能的配置問題
    const testSignup = async () => {
      loading.value = true;
      error.value = null;
      result.value = null;
      
      try {
        // 嘗試直接訪問，不使用api服務的baseURL
        const response = await axios.post('/api/auth/signup', {
          name: register.value.name,
          email: register.value.email,
          password: register.value.password
        });
        
        result.value = response.data;
        login.email = register.email; // 設置為剛註冊的郵箱
        
        console.log('註冊API測試成功:', response);
      } catch (err) {
        console.error('註冊API測試失敗:', err);
        error.value = err.response?.data?.message || err.message || '未知錯誤';
      } finally {
        loading.value = false;
      }
    };

    const testLogin = async () => {
      loading.value = true;
      error.value = null;
      result.value = null;
      
      try {
        // 嘗試直接訪問，不使用api服務的baseURL
        const response = await axios.post('/api/auth/login', {
          email: login.email,
          password: login.password
        });
        
        result.value = response.data;
        console.log('登入API測試成功:', response);
      } catch (err) {
        console.error('登入API測試失敗:', err);
        error.value = err.response?.data?.message || err.message || '未知錯誤';
      } finally {
        loading.value = false;
      }
    };

    return {
      register,
      login,
      result,
      error,
      loading,
      testSignup,
      testLogin
    };
  }
}
</script>

<style scoped>
.api-test {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.test-form {
  margin-top: 20px;
}

.result {
  margin-top: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 15px;
  background: #fafafa;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}
</style> 