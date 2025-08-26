/**
 * 表單驗證工具函數
 */

/**
 * 驗證電子郵件
 * @param {string} email - 電子郵件地址
 * @returns {boolean} 是否有效
 */
export function isValidEmail(email) {
  if (!email) return false
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return pattern.test(email)
}

/**
 * 驗證密碼強度
 * @param {string} password - 密碼
 * @returns {object} 包含有效性和強度描述的對象
 */
export function validatePassword(password) {
  if (!password) {
    return {
      isValid: false,
      message: '請輸入密碼',
      strength: 'weak'
    }
  }
  
  // 檢查密碼長度
  if (password.length < 8) {
    return {
      isValid: false,
      message: '密碼長度必須至少為 8 個字符',
      strength: 'weak'
    }
  }
  
  // 檢查密碼複雜性
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumbers = /\d/.test(password)
  const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  
  const strength = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChars].filter(Boolean).length
  
  if (strength === 1) {
    return {
      isValid: true,
      message: '密碼強度弱',
      strength: 'weak'
    }
  } else if (strength === 2) {
    return {
      isValid: true,
      message: '密碼強度中等',
      strength: 'medium'
    }
  } else if (strength === 3) {
    return {
      isValid: true,
      message: '密碼強度良好',
      strength: 'good'
    }
  } else if (strength === 4) {
    return {
      isValid: true,
      message: '密碼強度極佳',
      strength: 'strong'
    }
  }
  
  return {
    isValid: true,
    message: '密碼可接受',
    strength: 'medium'
  }
}

/**
 * 驗證兩個密碼是否匹配
 * @param {string} password - 密碼
 * @param {string} confirmPassword - 確認密碼
 * @returns {boolean} 是否匹配
 */
export function doPasswordsMatch(password, confirmPassword) {
  return password === confirmPassword
}

/**
 * 驗證姓名
 * @param {string} name - 姓名
 * @returns {boolean} 是否有效
 */
export function isValidName(name) {
  if (!name) return false
  return name.trim().length >= 2
}

/**
 * 驗證手機號碼
 * @param {string} phone - 手機號碼
 * @returns {boolean} 是否有效
 */
export function isValidPhone(phone) {
  if (!phone) return false
  const pattern = /^09\d{8}$/
  return pattern.test(phone.replace(/[-\s]/g, ''))
}

/**
 * 驗證數值在指定範圍內
 * @param {number} value - 要驗證的數值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {boolean} 是否在範圍內
 */
export function isInRange(value, min, max) {
  if (value === null || value === undefined) return false
  const numValue = Number(value)
  return !isNaN(numValue) && numValue >= min && numValue <= max
}

/**
 * 驗證身高（厘米）
 * @param {number} height - 身高
 * @returns {boolean} 是否有效
 */
export function isValidHeight(height) {
  return isInRange(height, 50, 250)
}

/**
 * 驗證體重（公斤）
 * @param {number} weight - 體重
 * @returns {boolean} 是否有效
 */
export function isValidWeight(weight) {
  return isInRange(weight, 20, 300)
}

/**
 * 驗證年齡
 * @param {number} age - 年齡
 * @returns {boolean} 是否有效
 */
export function isValidAge(age) {
  return isInRange(age, 1, 120)
}

/**
 * 驗證日期格式
 * @param {string} dateStr - 日期字符串 (格式: YYYY-MM-DD)
 * @returns {boolean} 是否有效
 */
export function isValidDate(dateStr) {
  if (!dateStr) return false
  
  // 檢查日期格式是否匹配 YYYY-MM-DD
  const pattern = /^\d{4}-\d{2}-\d{2}$/
  if (!pattern.test(dateStr)) return false
  
  // 嘗試創建日期對象
  const date = new Date(dateStr)
  return date instanceof Date && !isNaN(date)
}

/**
 * 驗證表單對象
 * @param {Object} formData - 表單數據
 * @param {Object} validationRules - 驗證規則
 * @returns {Object} 驗證結果，包含錯誤消息
 */
export function validateForm(formData, validationRules) {
  const errors = {}
  let isValid = true
  
  for (const field in validationRules) {
    if (validationRules.hasOwnProperty(field)) {
      const rules = validationRules[field]
      const value = formData[field]
      
      // 檢查必填字段
      if (rules.required && (!value && value !== 0)) {
        errors[field] = rules.requiredMessage || '此字段為必填項'
        isValid = false
        continue // 如果必填字段為空，無需進行其他驗證
      }
      
      // 如果字段有值，檢查其他規則
      if (value !== undefined && value !== null && value !== '') {
        // 檢查最小長度
        if (rules.minLength && String(value).length < rules.minLength) {
          errors[field] = rules.minLengthMessage || `最少需要 ${rules.minLength} 個字符`
          isValid = false
        }
        
        // 檢查最大長度
        if (rules.maxLength && String(value).length > rules.maxLength) {
          errors[field] = rules.maxLengthMessage || `最多允許 ${rules.maxLength} 個字符`
          isValid = false
        }
        
        // 檢查模式匹配
        if (rules.pattern && !rules.pattern.test(String(value))) {
          errors[field] = rules.patternMessage || '格式不正確'
          isValid = false
        }
        
        // 檢查最小值
        if (rules.min !== undefined && Number(value) < rules.min) {
          errors[field] = rules.minMessage || `不能小於 ${rules.min}`
          isValid = false
        }
        
        // 檢查最大值
        if (rules.max !== undefined && Number(value) > rules.max) {
          errors[field] = rules.maxMessage || `不能大於 ${rules.max}`
          isValid = false
        }
        
        // 檢查自定義驗證函數
        if (rules.validator && typeof rules.validator === 'function') {
          const validatorResult = rules.validator(value, formData)
          if (validatorResult !== true) {
            errors[field] = validatorResult || '驗證失敗'
            isValid = false
          }
        }
      }
    }
  }
  
  return { isValid, errors }
} 