<template>
  <div class="weekly-report-page">
    <div class="container">
      <h1 class="page-title">
        <el-icon><DataAnalysis /></el-icon> 健康報告
      </h1>
      <div class="report-type-selector">
        <button :class="['btn', currentReportType === 'daily' ? 'btn-primary' : 'btn-secondary']" @click="changeReportType('daily')">
          <el-icon><Calendar /></el-icon> 日報告
        </button>
        <button :class="['btn', currentReportType === 'weekly' ? 'btn-primary' : 'btn-secondary']" @click="changeReportType('weekly')">
          <el-icon><Collection /></el-icon> 週報告
        </button>
        <button :class="['btn', currentReportType === 'monthly' ? 'btn-primary' : 'btn-secondary']" @click="changeReportType('monthly')">
          <el-icon><Calendar /></el-icon> 月報告
        </button>
        <button :class="['btn', currentReportType === 'custom' ? 'btn-primary' : 'btn-secondary']" @click="changeReportType('custom')">
          <el-icon><Calendar /></el-icon> 自訂
        </button>
      </div>

      <!-- 日期/週次/月/自訂範圍選擇器 -->
      <div class="calendar-selector-container" v-if="currentReportType === 'daily'">
        <Datepicker
          v-model="selectedDateForPicker"
          :key="'daily-' + selectedDateForPicker"
          :inline="true"
          :week-start="0"
          @update:model-value="onDatePicked"
          :enable-time-picker="false"
          placeholder="選擇日期"
          :allowed-dates="allowedDatesFn"
          :year-range="[2025, 2025]"
          prevent-min-max-navigation
        />
      </div>
      <div class="calendar-selector-container" v-if="currentReportType === 'weekly'">
        <Datepicker
          v-model="selectedDateForPicker"
          :key="'weekly-' + selectedDateForPicker"
          :inline="true"
          :week-start="0"
          @update:model-value="onDatePicked"
          :enable-time-picker="false"
          placeholder="選擇日期"
          :allowed-dates="allowedWeekDatesFn"
          :year-range="[2025, 2025]"
          prevent-min-max-navigation
        />
      </div>
      <div class="calendar-selector-container" v-if="currentReportType === 'monthly'">
        <div class="month-picker-label">
          <el-icon><Calendar /></el-icon>
          <span>請選擇要查詢的月份</span>
        </div>
        <Datepicker
          v-model="selectedMonth"
          :key="'monthly-' + selectedMonth"
          type="month"
          :inline="false"
          :year-range="[2025,2025]"
          :allowed-dates="allowedMonthsFn"
          @update:model-value="onMonthPicked"
          placeholder="選擇月份"
          :input-class="'month-picker-input'"
          prevent-min-max-navigation
        />
      </div>
      <div class="calendar-selector-container" v-if="currentReportType === 'custom'">
        <Datepicker
          v-model="customRange"
          :key="'custom-' + customRange"
          range
          :inline="true"
          :year-range="[2025,2025]"
          :allowed-dates="allowedCustomDatesFn"
          @update:model-value="onCustomRangePicked"
          placeholder="選擇日期範圍"
          prevent-min-max-navigation
        />
      </div>

      <!-- 新增：日期區間顯示 -->
      <div class="date-range-display" v-if="dateRangeText">
        <el-icon><Calendar /></el-icon>
        <span>{{ dateRangeText }}</span>
      </div>

      <!-- 摘要 (period-summary) -->
      <div class="period-summary" v-if="reportData">
        <div class="summary-row">
          <div class="summary-card">
            <div class="summary-title">
              <el-icon><Food /></el-icon> 卡路里攝取
            </div>
            <div class="summary-value">{{ periodSummary.totalCaloriesIntake }} <span class="unit">大卡</span></div>
            <div class="summary-description" v-if="currentReportType === 'weekly'">
              平均每日: {{ periodSummary.avgDailyCaloriesIntake }} <span class="unit-small">大卡</span>
            </div>
            <div class="summary-description">
              目標: {{ userGoals.daily_calories }} <span class="unit-small">大卡/天</span>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-title">
              <el-icon><MostlyCloudy /></el-icon> 卡路里消耗
            </div>
            <div class="summary-value">{{ periodSummary.totalCaloriesBurned }} <span class="unit">大卡</span></div>
            <div class="summary-description" v-if="currentReportType === 'weekly'">
              平均每日: {{ periodSummary.avgDailyCaloriesBurned }} <span class="unit-small">大卡</span>
            </div>
            <div class="summary-description">
              {{ periodSummary.exerciseCount }} 次運動
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-title">
              <el-icon><Timer /></el-icon> 運動時長
            </div>
            <div class="summary-value">{{ periodSummary.total_exercise_duration_minutes }} <span class="unit">分鐘</span></div>
            <div class="summary-description" v-if="currentReportType === 'weekly'">
              平均每日: {{ periodSummary.avgDailyExerciseDurationMinutes }} <span class="unit-small">分鐘</span>
            </div>
          </div>

          <div class="summary-card expense-card">
            <div class="summary-title">
              <el-icon><Money /></el-icon> 總支出
            </div>
            <div class="summary-value">{{ periodSummary.totalFoodExpense }} <span class="unit">元</span></div>
            <div class="summary-description">
              記錄 {{ periodSummary.foodDaysLogged }}/{{ reportData.report_info.num_days_in_period }} 天
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="isLoading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        載入報告中...
      </div>

      <div v-if="currentReportType==='monthly' && weeklySummaries.length" class="monthly-weekly-summary">
        <h2 class="section-title"><el-icon><Collection /></el-icon> 本月每週摘要</h2>
        <table class="weekly-summary-table">
          <thead>
            <tr>
              <th>週期</th>
              <th>卡路里攝取</th>
              <th>卡路里消耗</th>
              <th>運動時長</th>
              <th>總支出</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(w, idx) in weeklySummaries" :key="idx">
              <td>{{ w.week_start }} ~ {{ w.week_end }}</td>
              <td>{{ w.total_calories_intake }}</td>
              <td>{{ w.total_calories_burned }}</td>
              <td>{{ w.total_exercise_duration_minutes }}</td>
              <td>{{ w.total_food_expense }}</td>
            </tr>
          </tbody>
        </table>
            </div>

      <!-- 圖表區段 -->
      <div class="report-section-row" v-if="reportData">
        <div class="report-section full-width-section">
          <h2 class="section-title">
            <el-icon><TrendCharts /></el-icon> 卡路里趨勢
          </h2>
            <div class="chart-placeholder chart">
              <div class="chart-container">
              <canvas ref="calorieChartEl" id="calorieChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="report-sections-row-grid" v-if="reportData">
        <div class="report-section">
          <h2 class="section-title">
            <el-icon><Present /></el-icon> 運動紀錄
          </h2>
            <div class="chart-placeholder">
              <div class="chart-container">
              <canvas ref="exerciseTrendChartEl" id="exerciseTrendChart"></canvas>
            </div>
          </div>
        </div>

        <div class="report-section">
          <h2 class="section-title">
            <el-icon><Tickets /></el-icon> 支出紀錄
          </h2>
            <div class="chart-placeholder">
            <div class="chart-container">
              <canvas ref="expenseChartEl" id="expenseChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="report-section full-width-section" v-if="reportData">
        <h2 class="section-title">
          <el-icon><Opportunity /></el-icon> 建議與提示
        </h2>
        <div class="suggestion-card">
          <p v-if="reportData.suggestions && reportData.suggestions.length > 0">
            根據您這{{ currentReportType === 'daily' ? '日' : currentReportType === 'weekly' ? '週' : currentReportType === 'monthly' ? '月' : '自訂' }}的飲食和運動記錄，我們有以下建議：
          </p>
          <ul class="suggestion-list" v-if="reportData.suggestions && reportData.suggestions.length > 0">
            <li v-for="(suggestion, index) in reportData.suggestions" :key="index">
             <el-icon><Star /></el-icon> {{ suggestion }}
            </li>
          </ul>
           <p v-else>
            <el-icon><InfoFilled /></el-icon> 暫無特別建議，請繼續保持記錄！
           </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart } from 'chart.js/auto'
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { ElMessage, ElIcon } from 'element-plus'
import { 
  DataAnalysis, Calendar, Collection, ArrowLeftBold, ArrowRightBold, 
  Food, MostlyCloudy, Timer, Money, Loading, TrendCharts, 
  Present, Tickets, Opportunity, Star, InfoFilled 
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/date'
import api from '@/services/api'


export default {
  name: 'SummaryReportPage',
  components: {
    Datepicker,
    ElIcon, 
    DataAnalysis, Calendar, Collection, ArrowLeftBold, ArrowRightBold, 
    Food, MostlyCloudy, Timer, Money, Loading, TrendCharts, 
    Present, Tickets, Opportunity, Star, InfoFilled
  },
  setup() {
    const currentReportType = ref('weekly')
    const selectedDateForPicker = ref(new Date())
    const targetDate = ref(new Date())
    const reportData = ref(null)
    const isLoading = ref(false)
    const selectedMonth = ref(new Date())
    const customRange = ref([new Date(), new Date()])
    const weeklySummaries = ref([])

    const calorieChartEl = ref(null);
    const exerciseTrendChartEl = ref(null);
    const expenseChartEl = ref(null);

    const today = new Date();
    today.setHours(0,0,0,0);
    const thisYear = today.getFullYear();
    const thisMonth = today.getMonth();
    const yearRange = [thisYear, thisYear]
    // 本週週一
    const thisWeekMonday = new Date(today);
    thisWeekMonday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
    thisWeekMonday.setHours(0,0,0,0);
    // 本週週日
    const thisWeekSunday = new Date(thisWeekMonday);
    thisWeekSunday.setDate(thisWeekMonday.getDate() + 6);
    thisWeekSunday.setHours(0,0,0,0);

    // 日報告：只能查到今天
    const allowedDatesFn = (dateToCheck) => {
      const d = new Date(dateToCheck);
      d.setHours(0,0,0,0);
      const todayLocal = new Date();
      todayLocal.setHours(0,0,0,0);
      return d <= todayLocal && d.getFullYear() === thisYear;
    };
    // 週報告：只能查本週且不超過今天
    const allowedWeekDatesFn = (dateToCheck) => {
      const d = new Date(dateToCheck);
      d.setHours(0,0,0,0);
      const todayLocal = new Date();
      todayLocal.setHours(0,0,0,0);
      // 計算本週週一
      const monday = new Date(todayLocal);
      monday.setDate(todayLocal.getDate() - ((todayLocal.getDay() + 6) % 7));
      monday.setHours(0,0,0,0);
      return d >= monday && d <= todayLocal && d.getFullYear() === thisYear;
    };
    // 月報告：只能查本月
    const allowedMonthsFn = (dateToCheck) => {
      const d = new Date(dateToCheck);
      const todayLocal = new Date();
      return d.getFullYear() === todayLocal.getFullYear() && d.getMonth() === todayLocal.getMonth();
    };
    // 自訂：結束日不能超過今天
    const allowedCustomDatesFn = (dateToCheck) => {
      const d = new Date(dateToCheck);
      d.setHours(0,0,0,0);
      const todayLocal = new Date();
      todayLocal.setHours(0,0,0,0);
      return d <= todayLocal && d.getFullYear() === thisYear;
    };

    const initializeTargetDate = () => {
      let initialDisplayDate = new Date(); 
      initialDisplayDate.setHours(0,0,0,0);

      if (initialDisplayDate > today) {
        initialDisplayDate = new Date(today)
      }
      
      targetDate.value = new Date(initialDisplayDate);
      selectedDateForPicker.value = new Date(initialDisplayDate);
    };
    
    const canChangePeriod = (direction) => {
      const newDate = new Date(targetDate.value);
      if (currentReportType.value === 'daily') {
        newDate.setDate(newDate.getDate() + direction);
      } else if (currentReportType.value === 'weekly') {
        newDate.setDate(newDate.getDate() + direction * 7);
      }
      // Ensure the new date is within the allowed range (2025 and not future if today is 2025)
      return allowedDatesFn(newDate);
    };


    const fetchSummaryReport = async () => {
      isLoading.value = true
      reportData.value = null
      destroyCharts();
      try {
        const userId = localStorage.getItem('userId')
        if (!userId) {
          ElMessage.warning('請先登入以查看報告')
          isLoading.value = false
          return
        }

        let apiUrl = `/api/reports/summary?user_id=${userId}`
        if (currentReportType.value === 'daily') {
          const startDateStr = formatDate(targetDate.value, 'YYYY-MM-DD');
          apiUrl += `&report_type=daily&start_date=${startDateStr}`
        } else if (currentReportType.value === 'weekly') {
          const startDateStr = formatDate(targetDate.value, 'YYYY-MM-DD');
          apiUrl += `&report_type=weekly&start_date=${startDateStr}`
        } else if (currentReportType.value === 'monthly') {
          const y = selectedMonth.value.getFullYear()
          const m = selectedMonth.value.getMonth() + 1
          const startDateStr = `${y}-${String(m).padStart(2, '0')}-01`
          apiUrl += `&report_type=monthly&start_date=${startDateStr}`
        } else if (currentReportType.value === 'custom') {
          const start = customRange.value[0]
          const end = customRange.value[1]
          const startDateStr = formatDate(start, 'YYYY-MM-DD');
          const endDateStr = formatDate(end, 'YYYY-MM-DD');
          apiUrl += `&report_type=custom&start_date=${startDateStr}&end_date=${endDateStr}`
        }

        const { data } = await api.get(apiUrl)
        reportData.value = data
        if (currentReportType.value === 'monthly' && data.weekly_summaries) {
          weeklySummaries.value = data.weekly_summaries;
        } else {
          weeklySummaries.value = [];
        }
      } catch (error) {
        console.error('載入摘要報告數據失敗:', error)
        ElMessage.error(error.message || '載入摘要報告數據失敗，請稍後再試')
        reportData.value = null;
      } finally {
        isLoading.value = false
      }
    }

    const userGoals = computed(() => {
      return reportData.value?.user_goals || {
        daily_calories: 2000,
        daily_budget: 0,
      }
    })

    const reportDateText = computed(() => {
      if (!targetDate.value) return '選擇日期'; // Should not happen with proper init

      const dateToDisplay = new Date(targetDate.value);

      if (!reportData.value || !reportData.value.report_info || !reportData.value.report_info.actual_start_date) {
         // Fallback display based on targetDate if reportData is not yet loaded or incomplete
        if (currentReportType.value === 'daily') {
            return dateToDisplay.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' });
        } else if (currentReportType.value === 'weekly') {
            const start = new Date(dateToDisplay);
            const dayOfWeek = start.getDay() === 0 ? 6 : start.getDay() -1;
            start.setDate(start.getDate() - dayOfWeek);
            const end = new Date(start);
            end.setDate(start.getDate() + 6);
            
            // Ensure start and end of week are within 2025
            if (start.getFullYear() !== 2025) start.setFullYear(2025,0,1);
            if (end.getFullYear() !== 2025) end.setFullYear(2025,11,31);


            const startText = start.toLocaleDateString('zh-TW', { month: 'long', day: 'numeric' });
            const endText = end.toLocaleDateString('zh-TW', { month: 'long', day: 'numeric' });
            return `${startText} - ${endText}`;
        }
        return '選擇日期';
      }
      
      // Use actual dates from report if available
      const { actual_start_date, actual_end_date } = reportData.value.report_info
      const startDate = new Date(actual_start_date + 'T00:00:00')
      const endDate = new Date(actual_end_date + 'T00:00:00')

      if (currentReportType.value === 'daily') {
        return startDate.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
      } else if (currentReportType.value === 'weekly') {
        const startText = startDate.toLocaleDateString('zh-TW', { month: 'long', day: 'numeric' })
        const endText = endDate.toLocaleDateString('zh-TW', { month: 'long', day: 'numeric' })
        return `${startText} - ${endText}`
      }
      return '日期範圍'
    })

    const periodSummary = computed(() => {
      const summary = reportData.value?.period_summary
      const reportInfo = reportData.value?.report_info
      const numDays = reportInfo?.num_days_in_period > 0 ? reportInfo.num_days_in_period : 1; 

      return {
        totalCaloriesIntake: summary?.total_calories_intake || 0,
        totalCaloriesBurned: summary?.total_calories_burned || 0,
        foodDaysLogged: summary?.food_days_logged || 0,
        totalFoodExpense: summary?.total_food_expense || 0,
        exerciseCount: summary?.exercise_count || 0,
        total_exercise_duration_minutes: summary?.total_exercise_duration_minutes || 0,
        avgDailyCaloriesIntake: Math.round((summary?.total_calories_intake || 0) / numDays),
        avgDailyCaloriesBurned: Math.round((summary?.total_calories_burned || 0) / numDays),
        avgDailyExerciseDurationMinutes: Math.round((summary?.total_exercise_duration_minutes || 0) / numDays),
      }
    })

    const changeReportType = (newType) => {
      currentReportType.value = newType;
      if (newType === 'monthly') {
        const now = new Date();
        selectedMonth.value = new Date(now.getFullYear(), now.getMonth(), 1);
      } else if (newType === 'custom') {
        const end = new Date(today)
        const start = new Date(today)
        start.setDate(start.getDate() - 6)
        customRange.value = [start, end]
      } else if (newType === 'daily' || newType === 'weekly') {
        initializeTargetDate();
      }
      fetchSummaryReport();
    }

    const changePeriod = (direction) => {
      if (!canChangePeriod(direction)) return; // Prevent changing if new period is not allowed

      const newDate = new Date(targetDate.value)
      if (currentReportType.value === 'daily') {
        newDate.setDate(newDate.getDate() + direction)
      } else if (currentReportType.value === 'weekly') {
        newDate.setDate(newDate.getDate() + direction * 7)
      }
      targetDate.value = newDate
      selectedDateForPicker.value = new Date(newDate)
      fetchSummaryReport()
    }

    const onDatePicked = (date) => {
      if (!date) return;
      // Datepicker should only allow valid dates due to :allowed-dates
      // So, 'date' here should already be valid.
      targetDate.value = new Date(date) 
      selectedDateForPicker.value = new Date(date) // Sync picker's model explicitly
      fetchSummaryReport()
    }

    const onMonthPicked = (date) => {
      if (!date) return
      selectedMonth.value = new Date(date)
      fetchSummaryReport()
    }

    const onCustomRangePicked = (range) => {
      if (!range || !Array.isArray(range) || range.length !== 2) return
      customRange.value = [new Date(range[0]), new Date(range[1])]
      fetchSummaryReport()
    }

    let calorieChartInstance = null
    let exerciseTrendChartInstance = null
    let expenseChartInstance = null

    const destroyCharts = () => {
        if (calorieChartInstance) calorieChartInstance.destroy(); calorieChartInstance = null;
        if (exerciseTrendChartInstance) exerciseTrendChartInstance.destroy(); exerciseTrendChartInstance = null;
        if (expenseChartInstance) expenseChartInstance.destroy(); expenseChartInstance = null;
    }

    const initOrUpdateCharts = (dailyTrends) => {
      if (!dailyTrends || dailyTrends.length === 0) {
        destroyCharts();
        return;
      }

      const labels = dailyTrends.map(t => {
        const dateObj = new Date(t.date + 'T00:00:00');
        return dateObj.toLocaleDateString('zh-TW', { month: 'numeric', day: 'numeric', weekday: 'short' });
      });

      const chartOptionsBase = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top' }, tooltip: { mode: 'index', intersect: false } },
        interaction: { mode: 'index', intersect: false },
      };

      const intakeData = dailyTrends.map(t => t.calories_intake);
      const burnedData = dailyTrends.map(t => t.calories_burned);
      const netData = dailyTrends.map(t => t.calories_intake - t.calories_burned);

      if (calorieChartEl.value) {
        if (calorieChartInstance) {
          calorieChartInstance.data.labels = labels;
          calorieChartInstance.data.datasets[0].data = intakeData;
          calorieChartInstance.data.datasets[1].data = burnedData;
          calorieChartInstance.data.datasets[2].data = netData;
          calorieChartInstance.update();
        } else {
          calorieChartInstance = new Chart(calorieChartEl.value, {
        type: 'bar',
            data: { labels, datasets: [
                { type: 'bar', label: '卡路里攝取', data: intakeData, backgroundColor: 'rgba(66, 165, 245, 0.7)', borderColor: '#42a5f5', order: 2 },
                { type: 'bar', label: '卡路里消耗', data: burnedData, backgroundColor: 'rgba(102, 187, 106, 0.7)', borderColor: '#66bb6a', order: 3 },
                { type: 'line', label: '淨卡路里', data: netData, borderColor: '#ff7043', backgroundColor: 'rgba(255, 112, 67, 0.1)', borderWidth: 2, tension: 0.3, yAxisID: 'y', order: 1, pointBackgroundColor: '#ff7043' }
            ]},
            options: { ...chartOptionsBase, scales: { y: { beginAtZero: true, title: { display: true, text: '卡路里' }}, x: {title: {display: dailyTrends.length > 1, text: '日期' }} }}
          });
        }
      }

      const exerciseDurationData = dailyTrends.map(t => t.exercise_duration_minutes);
      if (exerciseTrendChartEl.value) { 
        if (exerciseTrendChartInstance) {
          exerciseTrendChartInstance.data.labels = labels;
          exerciseTrendChartInstance.data.datasets[0].data = exerciseDurationData;
          exerciseTrendChartInstance.update();
        } else {
           exerciseTrendChartInstance = new Chart(exerciseTrendChartEl.value, {
              type: 'line',
              data: { labels, datasets: [{ label: '運動時間 (分鐘)', data: exerciseDurationData, borderColor: '#42a5f5', backgroundColor: 'rgba(66, 165, 245, 0.2)', fill: true, tension: 0.3, pointBackgroundColor: '#42a5f5' }]},
              options: { ...chartOptionsBase, scales: { y: { beginAtZero: true, title: { display: true, text: '時間 (分鐘)' }}, x: { title: { display: dailyTrends.length > 1, text: '日期' }} }}
          });
        }
      }

      const expenseData = dailyTrends.map(t => t.food_expense);
      if (expenseChartEl.value) { 
        if (expenseChartInstance) {
          expenseChartInstance.data.labels = labels;
          expenseChartInstance.data.datasets[0].data = expenseData;
          expenseChartInstance.update();
        } else {
          expenseChartInstance = new Chart(expenseChartEl.value, {
              type: 'bar',
              data: { labels, datasets: [{ label: '每日支出 (元)', data: expenseData, backgroundColor: 'rgba(255, 202, 40, 0.7)', borderColor: '#ffca28', borderRadius: 4 }]},
              options: { ...chartOptionsBase, scales: { y: { beginAtZero: true, title: { display: true, text: '元' }}, x: { title: { display: dailyTrends.length > 1, text: '日期' }} }}
          });
        }
      }
    }

    const dateRangeText = computed(() => {
      if (!reportData.value || !reportData.value.report_info) return '';
      const { actual_start_date, actual_end_date, type } = reportData.value.report_info;
      if (type === 'monthly') {
        const d = new Date(actual_start_date + 'T00:00:00');
        return `查詢月份：${d.getFullYear()}年${d.getMonth() + 1}月`;
      }
      if (actual_start_date === actual_end_date) {
        return `查詢日期：${actual_start_date}`;
      }
      return `查詢區間：${actual_start_date} ~ ${actual_end_date}`;
    });

    onMounted(() => {
      initializeTargetDate()
      fetchSummaryReport()
    })

    watch(() => reportData.value, async (newData, oldData) => {
      if (newData && newData.daily_trends) {
         await nextTick();
         initOrUpdateCharts(newData.daily_trends)
      } else if (!newData && oldData) {
        destroyCharts()
      }
    }, { deep: true })


    return {
      currentReportType,
      selectedDateForPicker,
      targetDate,
      reportData,
      isLoading,
      userGoals,
      reportDateText,
      periodSummary,
      changeReportType,
      changePeriod,
      onDatePicked,
      allowedDatesFn, // Expose to template
      canChangePeriod, // Expose to template
      calorieChartEl,
      exerciseTrendChartEl,
      expenseChartEl,
      selectedMonth,
      customRange,
      allowedMonthsFn,
      onMonthPicked,
      onCustomRangePicked,
      dateRangeText,
      weeklySummaries,
    }
  }
}
</script>

<style scoped>
/* ----- 全局變量 (理想情況下在 main.css 或 App.vue style) ----- */
:root {
  --primary-color: #409EFF; /* Element Plus 主色藍 */
  --primary-color-dark: #337ecc;
  --success-color: #67C23A;
  --warning-color: #E6A23C; /* 橘色 */
  --danger-color: #F56C6C;
  --info-color: #909399;
  --text-primary: #303133;
  --text-regular: #606266;
  --text-secondary: #909399;
  --border-color-light: #e4e7ed;
  --bg-color: #f5f7fa;
}

/* ----- 整體與間距 ----- */
.weekly-report-page .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.page-title {
  font-size: 2.25rem; 
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 30px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-title .el-icon {
  margin-right: 10px;
  font-size: 2.5rem;
}

.report-type-selector,
.time-selector,
.calendar-selector-container,
.period-summary,
.report-section-row,
.report-sections-row-grid, 
.report-section {
  margin-bottom: 30px;
}

/* ----- 按鈕 ----- */
.report-type-selector {
  display: flex;
  justify-content: center;
  gap: 15px; 
  margin-bottom: 25px;
}
.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px; 
}
.btn .el-icon {
  font-size: 1.1em;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}
.btn-primary:hover {
  background-color: var(--primary-color-dark);
  border-color: var(--primary-color-dark);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.btn-secondary {
  background-color: #f0f2f5;
  color: var(--text-regular);
  border-color: #dcdfe6;
}
.btn-secondary:hover {
  background-color: #e4e7ed;
  border-color: #c8c9cc;
  color: var(--primary-color);
}

.time-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
.current-period-text {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 20px;
  min-width: 200px; 
  text-align: center;
}
.btn-icon {
  background: transparent;
  border: none;
  padding: 8px;
  color: var(--primary-color);
  cursor: pointer;
}
.btn-icon .el-icon {
  font-size: 1.8rem; 
}
.btn-icon:hover:not(:disabled) { /* Apply hover only if not disabled */
  color: var(--primary-color-dark);
}
.btn-icon:disabled { /* Style for disabled arrow buttons */
  color: var(--text-secondary);
  cursor: not-allowed;
  opacity: 0.6;
}


/* ----- 日曆選擇器 ----- */
.calendar-selector-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 18px;
  width: 100%;
  padding: 0;
}

/* ----- 摘要卡片 ----- */
.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
  gap: 20px;
}
.summary-card {
  position: relative;
  background-color: #fff;
  border-radius: 12px;
  padding: 20px 20px 20px 28px;
  box-shadow: 0 6px 16px -8px rgba(0,0,0,.08), 0 9px 28px 0 rgba(0,0,0,.05), 0 12px 48px 16px rgba(0,0,0,.03);
  border: 1px solid var(--border-color-light);
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 6px solid var(--warning-color); /* 橘色強調線 */
}
.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px -6px rgba(0,0,0,.1), 0 12px 32px 0 rgba(0,0,0,.07), 0 16px 52px 18px rgba(0,0,0,.04);
}
.summary-card:not(.expense-card) .summary-title .el-icon {
  color: var(--primary-color);
}
.summary-card.expense-card .summary-title .el-icon {
  color: var(--warning-color);
}
.summary-title {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
}
.summary-title .el-icon {
  font-size: 2.2rem;
  margin-right: 10px;
  font-weight: bold;
  vertical-align: middle;
}
.summary-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  line-height: 1.2;
  display: flex;
  align-items: baseline;
}
.summary-value .unit {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-left: 6px;
}
.summary-description {
  font-size: 0.85rem;
  color: var(--text-regular);
}
.summary-description .unit-small {
   font-size: 0.8rem;
   color: var(--text-secondary);
}

/* Specific style for Expense Card */
.summary-card.expense-card .summary-value {
  color: var(--warning-color);
}


/* ----- 區塊標題 ----- */
.report-section {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 6px 16px -8px rgba(0,0,0,.08), 0 9px 28px 0 rgba(0,0,0,.05), 0 12px 48px 16px rgba(0,0,0,.03);
  border: 1px solid var(--border-color-light);
}
.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color-light);
  display: flex;
  align-items: center;
}
.section-title .el-icon {
  margin-right: 8px;
  color: var(--primary-color);
}
.full-width-section { 
  grid-column: 1 / -1; 
}

/* ----- 圖表區塊網格佈局 ----- */
.report-sections-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr; 
  gap: 20px;
}

/* ----- 圖表容器 ----- */
.chart-container {
  height: 350px;
  position: relative; 
}
.chart-placeholder { 
  width: 100%;
  height: 100%;
}


/* ----- 建議區塊 ----- */
.suggestion-card {
   background-color: var(--bg-color);
   border-left: 4px solid var(--primary-color);
   padding: 20px;
   border-radius: 8px;
   margin-top: 10px; 
}
.suggestion-card p {
  color: var(--text-regular);
  line-height: 1.7;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}
.suggestion-card p .el-icon {
  margin-right: 8px;
  color: var(--info-color);
  font-size: 1.2em;
}
.suggestion-list {
  list-style: none;
  padding-left: 0;
}
.suggestion-list li {
  color: var(--text-regular);
  line-height: 1.8;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}
.suggestion-list li .el-icon {
  margin-right: 8px;
  color: var(--warning-color); 
  font-size: 1.1em;
}


/* ----- Loading 狀態 ----- */
.loading-state {
  display: flex;
  flex-direction: column; 
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
  font-size: 1.1rem;
  color: var(--text-secondary);
}
.loading-state .el-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  color: var(--primary-color);
}



/* ----- 響應式調整 ----- */
@media (max-width: 992px) {
  .report-sections-row-grid {
    grid-template-columns: 1fr; 
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.8rem;
  }
  .summary-row {
    grid-template-columns: 1fr; 
  }
  .current-period-text {
    font-size: 1.2rem;
    min-width: 150px;
  }
  .btn {
    padding: 8px 15px;
    font-size: 0.9rem;
  }
  .section-title {
    font-size: 1.3rem;
  }
  .chart-container {
    height: 300px; 
  }
}

@media (max-width: 480px) {
  .container {
    padding: 15px;
  }
  .report-type-selector {
    flex-direction: column;
    gap: 10px;
  }
  .time-selector {
    flex-wrap: wrap; 
  }
  .current-period-text {
     order: -1; 
     width: 100%;
     margin-bottom: 10px;
  }
  .page-title .el-icon {
    font-size: 2rem;
  }
  .dp__main, .dp__menu {
    width: 100% !important;
    min-width: 0 !important;
    max-width: 100vw !important;
  }
}

.date-range-display {
  display: flex;
  align-items: center;
  background: #fffbe6;
  border: 1.5px solid var(--warning-color);
  border-radius: 8px;
  padding: 10px 18px;
  margin: 0 auto 18px auto;
  max-width: 340px;
  font-size: 1.08rem;
  color: #b26a00;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(255, 202, 40, 0.08);
}
.date-range-display .el-icon {
  margin-right: 8px;
  color: var(--warning-color);
  font-size: 1.3em;
}

.month-picker-label {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 10px;
}
.month-picker-label .el-icon {
  margin-right: 8px;
  font-size: 1.3em;
}
.month-picker-input {
  font-size: 1.15rem;
  text-align: center;
  border-radius: 8px;
  border: 1.5px solid var(--primary-color);
  padding: 8px 16px;
  width: 180px;
  margin: 0 auto;
  display: block;
}

.report-type-hint {
  text-align: center;
  color: var(--primary-color);
  font-size: 1.08rem;
  font-weight: 500;
  margin-bottom: 8px;
}

.monthly-weekly-summary {
  margin-top: 32px;
}
.weekly-summary-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.weekly-summary-table th, .weekly-summary-table td {
  padding: 10px 8px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
}
.weekly-summary-table th {
  background: #f7fafc;
  color: var(--primary-color);
  font-weight: 600;
}
.weekly-summary-table tr:last-child td {
  border-bottom: none;
}

/* Datepicker 主體更融合主題 */
.dp__main, .dp__menu {
  border-radius: 12px !important;
  background: #fff !important;
  border: 1.5px solid #e0e7ef !important;
  box-shadow: 0 4px 16px rgba(64,158,255,0.07) !important;
  min-width: 0 !important;
  width: auto !important;
  max-width: 100% !important;
}
.dp__header {
  background: var(--primary-color);
  color: #fff;
  border-radius: 10px 10px 0 0;
  font-weight: 600;
  letter-spacing: 1px;
}
.dp__month_year_select {
  color: #fff !important;
}
.dp__input, .month-picker-input {
  border-radius: 8px !important;
  border: 1.5px solid #e0e7ef !important;
  font-size: 1.08rem;
  padding: 8px 16px 8px 38px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(64,158,255,0.04);
  background: #fff;
  transition: border 0.2s;
}
.dp__input:focus, .month-picker-input:focus {
  border-color: var(--primary-color) !important;
  outline: none;
}
/* input icon (如有自訂 icon 字型可啟用)
.dp__input::before, .month-picker-input::before {
  content: '\e6a0';
  font-family: 'element-icons' !important;
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--primary-color);
  font-size: 1.2em;
  pointer-events: none;
}
*/
.dp__cell_inner.dp__active, .dp__cell_inner.dp__range_start, .dp__cell_inner.dp__range_end {
  background: var(--primary-color) !important;
  color: #fff !important;
  border-radius: 8px !important;
}
.dp__cell_inner:hover {
  background: #e3f0fd !important;
  color: var(--primary-color) !important;
}
.dp__cell_inner.dp__today {
  border: 1.5px solid var(--primary-color) !important;
  border-radius: 8px !important;
}
.dp__cell_inner.dp__disabled {
  color: #ccc !important;
  background: #f7f7f7 !important;
  cursor: not-allowed !important;
}
</style>




