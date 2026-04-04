<template>
  <div class="app-header">
    <div class="container header-container">
      <div class="logo-container">
        <router-link to="/food/search" class="logo">
          <i class="fas fa-hamburger logo-icon pulse-animation"></i>
          <span class="logo-text">速per Idol</span>
        </router-link>
      </div>
      
    <!-- Desktop Navigation -->
      <div class="nav-desktop">
        <nav class="main-nav">
          <router-link to="/food/search" class="nav-link">
            <i class="fas fa-search"></i>
            <span>Food Search</span>
          </router-link>
          <router-link to="/food/record" class="nav-link">
            <i class="fas fa-utensils"></i>
            <span>Food Record</span>
          </router-link>
          <router-link to="/exercise/record" class="nav-link">
            <i class="fas fa-running"></i>
            <span>Exercise</span>
          </router-link>
          <router-link to="/reports/weekly" class="nav-link">
            <i class="fas fa-chart-line"></i>
            <span>Reports</span>
          </router-link>
        </nav>
        
        <div class="user-menu">
          <button class="user-toggle" @click="isMenuOpen = !isMenuOpen">
            <i class="fas fa-user-circle avatar-icon"></i>
            <span class="user-name">{{ userName }}</span>
            <i class="fas fa-chevron-down" :class="{ 'rotate-icon': isMenuOpen }"></i>
          </button>
          
          <transition name="fade-scale">
            <div v-if="isMenuOpen" class="dropdown-menu">
              <router-link to="/profile/basic-info" class="dropdown-item">
                <i class="fas fa-id-card"></i>
                <span>Basic Information</span>
              </router-link>
              <router-link to="/profile/myfavorite" class="dropdown-item">
                <i class="fas fa-sliders-h"></i>
                <span>Preferences</span>
              </router-link>
              <button class="dropdown-item" @click="logout">
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
              </button>
            </div>
          </transition>
        </div>
      </div>

      <!-- Mobile Navigation -->
      <button class="mobile-toggle" @click="toggleMobileMenu">
        <i :class="isMobileMenuOpen ? 'fas fa-times swing-animation' : 'fas fa-bars'"></i>
      </button> 
    </div>
    
    <transition name="slide-left">
      <div v-if="isMobileMenuOpen" class="mobile-menu-overlay" @click="closeMobileMenu">
        <div class="mobile-menu" @click.stop>
          <div class="mobile-user-info">
            <i class="fas fa-user-circle mobile-avatar"></i>
            <span>{{ userName }}</span>
          </div>
          <nav class="mobile-nav">
            <router-link to="/food/search" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-search"></i>
              <span>Food Search</span>
            </router-link>
            <router-link to="/food/record" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-utensils"></i>
              <span>Food Record</span>
            </router-link>
            <router-link to="/exercise/record" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-running"></i>
              <span>Exercise Record</span>
            </router-link>
            <router-link to="/reports/weekly" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-chart-line"></i>
              <span>Weekly Report</span>
            </router-link>
            <router-link to="/profile/basic-info" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-id-card"></i>
              <span>Basic Information</span>
            </router-link>
            <router-link to="/profile/myfavorite" class="mobile-nav-link" @click="closeMobileMenu">
              <i class="fas fa-sliders-h"></i>
              <span>Preferences</span>
            </router-link>
            <button class="mobile-nav-link logout-button" @click="logoutMobile">
              <i class="fas fa-sign-out-alt"></i>
              <span>Logout</span>
            </button>
          </nav>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'

export default {
  name: 'AppHeader',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    const isMenuOpen = ref(false)
    const isMobileMenuOpen = ref(false)
    
    const userName = computed(() => {
      return authStore.user?.name || 'User'
    })
    
    const toggleMobileMenu = () => {
      isMobileMenuOpen.value = !isMobileMenuOpen.value
      if (isMobileMenuOpen.value) {
        document.body.style.overflow = 'hidden' // Prevent background scrolling
      } else {
        document.body.style.overflow = '' // Restore background scrolling
      }
    }
    
    const closeMobileMenu = () => {
      isMobileMenuOpen.value = false
      document.body.style.overflow = '' // Restore background scrolling
    }
    
    const logout = async () => {
      isMenuOpen.value = false
      await authStore.logout()
      router.push('/login')
    }
    
    const logoutMobile = async () => {
      closeMobileMenu()
      await authStore.logout()
      router.push('/login')
    }
    
    // Listen for route changes to close menu
    watch(router.currentRoute, () => {
      isMenuOpen.value = false
    })
    
    return {
      isMenuOpen,
      isMobileMenuOpen,
      userName,
      toggleMobileMenu,
      closeMobileMenu,
      logout,
      logoutMobile
    }
  }
}
</script>

<style scoped>
/* Main Navigation Styles */
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background-image: linear-gradient(to right, #ff8c30, #ffaa55, #ffb870);
  color: white;
  z-index: 1000;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  max-width: 1280px;
  margin: 0 auto;
}

/* Logo Area */
.logo-container {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 5px 0;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: white;
  transition: transform 0.3s;
  height: 100%;
  padding: 5px 15px;
  border-radius: 30px;
}

.logo:hover {
  transform: scale(1.05);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.logo-icon {
  font-size: 26px;
  margin-right: 10px;
  color: white;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.2));
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
  font-family: 'Poppins', sans-serif;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

/* Desktop Navigation */
.nav-desktop {
  display: flex;
  align-items: center;
}

.main-nav {
  display: flex;
  margin-right: 24px;
}

.nav-link {
  padding: 8px 16px;
  color: white;
  text-decoration: none;
  opacity: 0.85;
  transition: all 0.3s;
  font-weight: 500;
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Nunito Sans', sans-serif;
  letter-spacing: 0.3px;
}

.nav-link span {
  font-size: 15px;
}

.nav-link i {
  font-size: 16px;
}

.nav-link:after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 3px;
  background-color: white;
  transition: width 0.3s ease;
}

.nav-link:hover:after,
.nav-link.router-link-active:after {
  width: 100%;
}

.nav-link:hover,
.nav-link.router-link-active {
  opacity: 1;
}

.nav-link:hover i {
  transform: scale(1.2);
  transition: transform 0.3s ease;
}

/* User Menu */
.user-menu {
  position: relative;
}

.user-toggle {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 30px;
  transition: all 0.3s;
  background-color: rgba(255, 255, 255, 0.1);
}

.user-toggle:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.avatar-icon {
  font-size: 20px;
  margin-right: 8px;
}

.user-name {
  margin-right: 8px;
  font-weight: 500;
  font-family: 'Nunito Sans', sans-serif;
}

.rotate-icon {
  transform: rotate(180deg);
  transition: transform 0.3s;
}

.dropdown-menu {
  position: absolute;
  top: 110%;
  right: 0;
  width: 220px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 1000;
  transform-origin: top right;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: #333;
  text-decoration: none;
  width: 100%;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-family: 'Nunito Sans', sans-serif;
  font-weight: 500;
  transition: all 0.2s;
  letter-spacing: 0.2px;
}

.dropdown-item i {
  width: 22px;
  color: #ffaa55;
}

.dropdown-item:hover {
  background-color: #fff4e8;
  transform: translateX(5px);
}

/* Mobile Menu Button */
.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  justify-content: center;
  align-items: center;
  transition: background-color 0.3s;
}

.mobile-toggle:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Mobile Menu */
.mobile-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1001;
  backdrop-filter: blur(2px);
}

.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 280px;
  height: 100%;
  background-color: white;
  box-shadow: -5px 0 20px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  z-index: 1002;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #ffaa55;
  color: white;
  gap: 10px;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
}

.mobile-avatar {
  font-size: 32px;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  padding: 10px 0;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  text-decoration: none;
  color: #333;
  border: none;
  background: none;
  font-size: 15px;
  font-family: 'Nunito Sans', sans-serif;
  text-align: left;
  gap: 15px;
  transition: all 0.3s;
  letter-spacing: 0.2px;
  font-weight: 500;
}

.mobile-nav-link i {
  width: 20px;
  color: #ffaa55;
  font-size: 18px;
}

.mobile-nav-link:hover, 
.mobile-nav-link.router-link-active {
  background-color: #fff4e8;
}

.logout-button {
  cursor: pointer;
  width: 100%;
}

.logout-button i {
  color: #ff6b6b;
}

/* Animation Effects */
.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.swing-animation {
  animation: swing 0.5s ease;
}

@keyframes swing {
  0% { transform: rotate(0deg); }
  30% { transform: rotate(15deg); }
  60% { transform: rotate(-10deg); }
  80% { transform: rotate(5deg); }
  100% { transform: rotate(0deg); }
}

/* Vue Transitions */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s;
}

.slide-left-enter-from,
.slide-left-leave-to {
  opacity: 0;
}

.slide-left-enter-from .mobile-menu,
.slide-left-leave-to .mobile-menu {
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.slide-left-enter-to .mobile-menu,
.slide-left-leave-from .mobile-menu {
  transform: translateX(0);
  transition: transform 0.3s ease;
}

/* Responsive Design */
@media (max-width: 900px) {
  .nav-desktop {
    display: none;
  }
  
  .mobile-toggle {
    display: flex;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: 20px;
  }
}
</style> 