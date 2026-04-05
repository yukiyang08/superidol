import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../pages/Dashboard.vue'
import Login from '../pages/auth/Login.vue'
import Register from '../pages/auth/Register.vue'
import UserPreferences from '../pages/auth/UserPreferences.vue'
import BasicInfo from '../pages/profile/BasicInfo.vue'
import MyFavorite from '../pages/profile/MyFavorite.vue'
import FoodSearch from '../pages/food/FoodSearch.vue'
import FoodRecord from '../pages/food/FoodRecord.vue'
import ExerciseRecord from '../pages/exercise/ExerciseRecord.vue'
import WeeklyReport from '../pages/reports/WeeklyReport.vue'
import ApiTest from '../pages/ApiTest.vue'



const routes = [
  {
    path: '/',
    redirect: '/food/search'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/preferences',
    name: 'UserPreferences',
    component: UserPreferences,
    meta: { requiresAuth: false }
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: ApiTest,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/basic-info',
    name: 'BasicInfo',
    component: BasicInfo,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/myfavorite',
    name: 'MyFavorite',
    component: MyFavorite,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile/myfavorite',
    name: 'MyFavorite',
    component: MyFavorite,
    meta: { requiresAuth: true }
  },
  {
    path: '/food/search',
    name: 'FoodSearch',
    component: FoodSearch,
    meta: { requiresAuth: false }
  },
  {
    path: '/food/record',
    name: 'FoodRecord',
    component: FoodRecord,
    meta: { requiresAuth: true }
  },
  {
    path: '/exercise/record',
    name: 'ExerciseRecord',
    component: ExerciseRecord,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports/weekly',
    name: 'WeeklyReport',
    component: WeeklyReport,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 導航守衛
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 