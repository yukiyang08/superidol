/**
 * 日期處理工具函數
 */

/**
 * 格式化日期為指定格式
 * @param {Date|string|number} date - 要格式化的日期
 * @param {string} format - 格式模板，例如 'YYYY-MM-DD'
 * @returns {string} 格式化後的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  const d = date ? new Date(date) : new Date()
  
  const year = d.getFullYear()
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hours = d.getHours()
  const minutes = d.getMinutes()
  const seconds = d.getSeconds()
  
  // 補零函數
  const pad = (n) => n < 10 ? `0${n}` : `${n}`
  
  return format
    .replace('YYYY', year)
    .replace('MM', pad(month))
    .replace('DD', pad(day))
    .replace('HH', pad(hours))
    .replace('mm', pad(minutes))
    .replace('ss', pad(seconds))
}

/**
 * 獲取今天的開始時間（零點）
 * @returns {Date} 今天的零點時間
 */
export function getStartOfDay(date = new Date()) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * 獲取今天的結束時間（23:59:59.999）
 * @returns {Date} 今天的結束時間
 */
export function getEndOfDay(date = new Date()) {
  const d = new Date(date)
  d.setHours(23, 59, 59, 999)
  return d
}

/**
 * 獲取本週的開始時間（週日零點）
 * @param {Date} date - 日期對象
 * @returns {Date} 本週的開始時間
 */
export function getStartOfWeek(date = new Date()) {
  const d = new Date(date)
  const day = d.getDay()
  d.setDate(d.getDate() - day)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * 獲取本週的結束時間（週六 23:59:59.999）
 * @param {Date} date - 日期對象
 * @returns {Date} 本週的結束時間
 */
export function getEndOfWeek(date = new Date()) {
  const d = new Date(date)
  const day = d.getDay()
  d.setDate(d.getDate() + (6 - day))
  d.setHours(23, 59, 59, 999)
  return d
}

/**
 * 獲取本月的開始時間
 * @param {Date} date - 日期對象
 * @returns {Date} 本月的開始時間
 */
export function getStartOfMonth(date = new Date()) {
  const d = new Date(date)
  d.setDate(1)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * 獲取本月的結束時間
 * @param {Date} date - 日期對象
 * @returns {Date} 本月的結束時間
 */
export function getEndOfMonth(date = new Date()) {
  const d = new Date(date)
  const nextMonth = d.getMonth() + 1
  const year = nextMonth === 12 ? d.getFullYear() + 1 : d.getFullYear()
  const month = nextMonth === 12 ? 0 : nextMonth
  const lastDay = new Date(year, month, 0)
  lastDay.setHours(23, 59, 59, 999)
  return lastDay
}

/**
 * 計算兩個日期之間的差異（天數）
 * @param {Date} date1 - 第一個日期
 * @param {Date} date2 - 第二個日期
 * @returns {number} 天數差異
 */
export function daysBetween(date1, date2) {
  const d1 = new Date(date1)
  const d2 = new Date(date2)
  d1.setHours(0, 0, 0, 0)
  d2.setHours(0, 0, 0, 0)
  return Math.abs(Math.round((d2 - d1) / (1000 * 60 * 60 * 24)))
}

/**
 * 獲取日期的中文星期表示
 * @param {Date} date - 日期對象
 * @returns {string} 中文星期表示
 */
export function getChineseWeekday(date = new Date()) {
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekdays[date.getDay()]
}

/**
 * 檢查日期是否為今天
 * @param {Date} date - 要檢查的日期
 * @returns {boolean} 是否為今天
 */
export function isToday(date) {
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

/**
 * 獲取相對於現在的友好時間描述
 * @param {Date|string|number} date - 日期
 * @returns {string} 友好的時間描述
 */
export function getRelativeTimeFromNow(date) {
  const now = new Date()
  const d = new Date(date)
  const diffInMs = now - d
  
  // 將毫秒轉換為秒、分鐘、小時、天
  const diffInSeconds = Math.floor(diffInMs / 1000)
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  
  if (diffInDays > 30) {
    return formatDate(d, 'YYYY-MM-DD')
  } else if (diffInDays > 0) {
    return `${diffInDays} 天前`
  } else if (diffInHours > 0) {
    return `${diffInHours} 小時前`
  } else if (diffInMinutes > 0) {
    return `${diffInMinutes} 分鐘前`
  } else {
    return '剛剛'
  }
} 