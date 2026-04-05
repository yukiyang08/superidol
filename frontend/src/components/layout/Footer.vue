<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-logo">
          <span class="logo-text">Super Idol</span>
          <p class="slogan">從每一餐開始，養成更好的健康習慣</p>
        </div>
        
        <div class="footer-links">
          <div class="link-section">
            <h3>快速入口</h3>
            <ul>
              <li><router-link to="/food/search">食物搜尋</router-link></li>
              <li><router-link to="/food/record">飲食記錄</router-link></li>
              <li><router-link to="/reports/weekly">健康報告</router-link></li>
            </ul>
          </div>
          
          <div class="link-section">
            <h3>服務資訊</h3>
            <ul>
              <li><span>資料來源：使用者紀錄與餐點資料庫</span></li>
              <li><span>若有問題，請聯繫專案管理員</span></li>
              <li><span>版本：Web v1</span></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <div class="copyright">
          &copy; {{ currentYear }} Super Idol - DBMS Team 11302. All Rights Reserved.
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-footer {
  background-color: #333;
  color: #fff;
  padding: 40px 0 20px;
  margin-top: auto;
}

.footer-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 40px;
}

.footer-logo {
  margin-bottom: 30px;
  flex: 1 1 100%;
}

@media (min-width: 768px) {
  .footer-logo {
    flex: 0 0 30%;
  }
}

.logo-text {
  display: block;
  font-family: var(--font-tc), var(--font-en);
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.slogan {
  font-size: 14px;
  color: #aaa;
  font-family: var(--font-tc), var(--font-en);
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  flex: 1 1 100%;
}

@media (min-width: 768px) {
  .footer-links {
    flex: 0 0 60%;
    justify-content: flex-end;
  }
}

.link-section {
  flex: 1 1 200px;
}

.link-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #fff;
  font-family: var(--font-tc), var(--font-en);
}

.link-section ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.link-section li {
  margin-bottom: 10px;
}

.link-section a,
.link-section span {
  color: #bbb;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
  font-family: var(--font-tc), var(--font-en);
}

.link-section a:hover {
  color: var(--primary-color);
}

.footer-bottom {
  padding-top: 20px;
  border-top: 1px solid #4a2e18;
  display: flex;
  flex-direction: column;
  align-items: center;
}

@media (min-width: 768px) {
  .footer-bottom {
    flex-direction: row;
    justify-content: space-between;
  }
}

.copyright {
  font-size: 13px;
  color: #999;
  text-align: center;
  font-family: var(--font-tc), var(--font-en);
}
</style> 