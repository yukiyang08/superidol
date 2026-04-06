<template>
  <div id="app">
    <header v-if="isAuthenticated && !isAuthPage">
      <Header />
    </header>
    <div class="main-container">
      <main class="content">
        <router-view />
      </main>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './store/auth'
import Header from './components/layout/Header.vue'
import Footer from './components/layout/Footer.vue'

const route = useRoute()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// 初始化應用時嘗試載入用戶資料
onMounted(async () => {
  if (authStore.token) {
    try {
      await authStore.fetchUserData()
    } catch (error) {
      console.error('初始化時載入用戶資料失敗:', error)
    }
  }
})

</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Noto Sans TC', 'Poppins', 'Nunito Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: 0.015em;
}

:root {
  --primary-color: #ffaa55;
  --primary-darker: #f89b3c;
  --primary-lighter: #ffd0a0;
  --text-color: #333333;
  --text-light: #666666;
  --bg-light: #faf7f4;
  --border-color: #e0e0e0;
  --font-tc: 'Noto Sans TC', sans-serif;
  --font-en: 'Poppins', 'Nunito Sans', sans-serif;
  --surface-radius-lg: 16px;
  --surface-radius-md: 12px;
  --surface-radius-sm: 10px;
  --shadow-card: 0 8px 24px rgba(0, 0, 0, 0.06);
  --shadow-card-hover: 0 14px 28px rgba(0, 0, 0, 0.10);
  --shadow-button: 0 6px 16px rgba(255, 170, 85, 0.28);
  --shadow-button-hover: 0 10px 22px rgba(255, 170, 85, 0.36);
  --btn-radius: 10px;
  --el-font-family: 'Noto Sans TC', 'Poppins', 'Nunito Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}
/* Override Element Plus primary to match brand orange */
:root {
  --el-color-primary: #ffaa55;
  --el-color-primary-dark-2: #e09640;
  --el-color-primary-light-3: #ffc07d;
  --el-color-primary-light-5: #ffd4a0;
  --el-color-primary-light-7: #ffe5c3;
  --el-color-primary-light-9: #fff4e8;
}

body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  background-color: var(--bg-light);
  color: var(--text-color);
  font-family: var(--el-font-family);
}

button,
input,
select,
textarea {
  font: inherit;
}

.el-message,
.el-message-box,
.el-notification {
  font-family: var(--el-font-family);
}

.main-container {
  display: flex;
  flex: 1;
}

.content {
  flex: 1;
  padding-top: 84px;
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding-left: 32px;
  padding-right: 32px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .content {
    padding-left: 24px;
    padding-right: 24px;
    padding-top: 76px;
  }
}

@media (max-width: 480px) {
  .content {
    padding-left: 16px;
    padding-right: 16px;
    padding-top: 72px;
  }
}
</style> 