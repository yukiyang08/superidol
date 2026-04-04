/**
 * 格式化工具函數
 */

/**
 * 格式化數字，加入千位分隔符
 * @param {number} num - 要格式化的數字
 * @param {number} [precision=0] - 小數點精度
 * @returns {string} 格式化後的數字字符串
 */
export function formatNumber(num, precision = 0) {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString('zh-TW', {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  })
}

/**
 * 格式化金額
 * @param {number} amount - 金額
 * @param {string} [currencySymbol='$'] - 貨幣符號
 * @param {number} [precision=2] - 小數點精度
 * @returns {string} 格式化後的金額字符串
 */
export function formatCurrency(amount, currencySymbol = '$', precision = 2) {
  if (amount === null || amount === undefined) return '-'
  return `${currencySymbol}${formatNumber(amount, precision)}`
}

/**
 * 格式化卡路里
 * @param {number} calories - 卡路里數
 * @returns {string} 格式化後的卡路里字符串
 */
export function formatCalories(calories) {
  if (calories === null || calories === undefined) return '-'
  return `${formatNumber(calories, 0)} kcal`
}

/**
 * 格式化體重
 * @param {number} weight - 體重（公斤）
 * @param {number} [precision=1] - 小數點精度
 * @returns {string} 格式化後的體重字符串
 */
export function formatWeight(weight, precision = 1) {
  if (weight === null || weight === undefined) return '-'
  return `${formatNumber(weight, precision)} kg`
}

/**
 * 格式化營養素（如蛋白質、碳水等）
 * @param {number} value - 數值（克）
 * @param {number} [precision=1] - 小數點精度
 * @returns {string} 格式化後的營養素字符串
 */
export function formatNutrient(value, precision = 1) {
  if (value === null || value === undefined) return '-'
  return `${formatNumber(value, precision)} g`
}

/**
 * 格式化能量百分比（如每日攝取量的百分比）
 * @param {number} percentage - 百分比值
 * @returns {string} 格式化後的百分比字符串
 */
export function formatPercentage(percentage) {
  if (percentage === null || percentage === undefined) return '-'
  return `${formatNumber(percentage, 1)}%`
}

/**
 * 縮短文本，超過指定長度時添加省略號
 * @param {string} text - 原始文本
 * @param {number} [maxLength=50] - 最大長度
 * @returns {string} 處理後的文本
 */
export function truncateText(text, maxLength = 50) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * 格式化電話號碼為常見格式
 * @param {string} phone - 電話號碼
 * @returns {string} 格式化後的電話號碼
 */
export function formatPhoneNumber(phone) {
  if (!phone) return ''
  
  // 移除所有非數字字符
  const cleaned = phone.replace(/\D/g, '')
  
  // 根據長度進行格式化
  if (cleaned.length === 10) {
    return `${cleaned.substring(0, 4)}-${cleaned.substring(4, 7)}-${cleaned.substring(7)}`
  } else if (cleaned.length === 11) {
    return `${cleaned.substring(0, 3)}-${cleaned.substring(3, 7)}-${cleaned.substring(7)}`
  }
  
  // 如果不符合上述規則，直接返回
  return phone
}

/**
 * 格式化身高
 * @param {number} height - 身高（厘米）
 * @returns {string} 格式化後的身高字符串
 */
export function formatHeight(height) {
  if (height === null || height === undefined) return '-'
  return `${formatNumber(height, 0)} cm`
}

/**
 * 格式化運動時長
 * @param {number} minutes - 分鐘數
 * @returns {string} 格式化後的時長字符串
 */
export function formatDuration(minutes) {
  if (minutes === null || minutes === undefined) return '-'
  
  if (minutes < 60) {
    return `${minutes} 分鐘`
  }
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (remainingMinutes === 0) {
    return `${hours} 小時`
  }
  
  return `${hours} 小時 ${remainingMinutes} 分鐘`
} 