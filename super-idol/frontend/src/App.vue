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

<script>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from './store/auth'
import Header from './components/layout/Header.vue'
import Footer from './components/layout/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    Footer
  },
  setup() {
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

    return {
      isAuthenticated,
      isAuthPage
    }
  }
}
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
  --bg-light: #f8f9fa;
  --border-color: #e0e0e0;
  --font-tc: 'Noto Sans TC', sans-serif;
  --font-en: 'Poppins', 'Nunito Sans', sans-serif;
}

body {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  background-color: var(--bg-light);
  color: var(--text-color);
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