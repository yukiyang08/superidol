<template>
  <div class="calorie-calculator-wrapper">
    <el-button 
      text
      class="help-btn"
      @click="showCalorieHelp"
    >
      <el-icon><QuestionFilled /></el-icon>
      協助估算
    </el-button>

    <el-dialog
      v-model="calorieHelpVisible"
      title="每週熱量估算"
      width="440px"
      class="calorie-help-dialog"
      :close-on-click-modal="true"
      :close-on-press-escape="true"
      :show-close="true"
      :modal="true"
      :append-to-body="true"
    >
      <div class="calorie-help-content">
        <p class="calculator-lead">輸入幾個基本條件，我們會估算較合理的每週熱量上限，之後你仍可自行調整。</p>
        
        <div class="calorie-calculator">
          <h4>快速估算</h4>
          <el-form :model="calorieCalc" label-width="80px">
            <el-form-item label="性別">
              <el-radio-group v-model="calorieCalc.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="年齡">
              <el-input-number v-model="calorieCalc.age" :min="18" :max="100" />
            </el-form-item>
            <el-form-item label="身高(cm)">
              <el-input-number v-model="calorieCalc.height" :min="100" :max="250" />
            </el-form-item>
            <el-form-item label="活動量">
              <el-select v-model="calorieCalc.activityLevel">
                <el-option label="久坐不動" value="sedentary" />
                <el-option label="輕度活動" value="light" />
                <el-option label="中度活動" value="moderate" />
                <el-option label="重度活動" value="very" />
                <el-option label="極度活動" value="extra" />
              </el-select>
            </el-form-item>
            <el-form-item label="目標">
              <el-select v-model="calorieCalc.goal">
                <el-option label="減重" value="lose" />
                <el-option label="維持體重" value="maintain" />
                <el-option label="增重" value="gain" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div class="calorie-result">
            <div class="result-summary">
              <div class="result-stat">
                <span class="result-label">BMR</span>
                <strong class="result-value">{{ bmr }}</strong>
                <span class="result-unit">大卡/天</span>
              </div>
              <div class="result-stat highlight">
                <span class="result-label">建議上限</span>
                <strong class="result-value">{{ calculateCalories }}</strong>
                <span class="result-unit">大卡/週</span>
              </div>
            </div>
            <div class="action-buttons">
              <el-button 
                type="warning" 
                @click="applyCalorieSuggestion"
                :loading="isLoading"
              >
                套用建議值
              </el-button>
              <el-button 
                @click="calorieHelpVisible = false"
              >
                關閉
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'

const props = defineProps({
  weight: {
    type: Number,
    required: true
  },
  modelValue: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const calorieHelpVisible = ref(false)
const isLoading = ref(false)
const calorieCalc = reactive({
  gender: 'male',
  age: 25,
  height: 170,
  activityLevel: 'moderate',
  goal: 'maintain'
})

const showCalorieHelp = () => {
  calorieHelpVisible.value = true
}

const calculateCalories = computed(() => {
  // 使用Harris-Benedict公式計算BMR
  let bmr = 0
  if (calorieCalc.gender === 'male') {
    bmr = 66 + (13.7 * props.weight) + (5 * calorieCalc.height) - (6.8 * calorieCalc.age)
  } else {
    bmr = 655 + (9.6 * props.weight) + (1.8 * calorieCalc.height) - (4.7 * calorieCalc.age)
  }

  // 根據活動量調整
  const activityMultipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    very: 1.725,
    extra: 1.9
  }

  let tdee = bmr * activityMultipliers[calorieCalc.activityLevel]

  // 根據目標調整
  const goalAdjustments = {
    lose: 0.85,
    maintain: 1,
    gain: 1.15
  }

  tdee = tdee * goalAdjustments[calorieCalc.goal]

  // 轉換為每週熱量
  return Math.round(tdee * 7)
})

const bmr = computed(() => {
  // 使用Harris-Benedict公式計算BMR
  let bmr = 0
  if (calorieCalc.gender === 'male') {
    bmr = 66 + (13.7 * props.weight) + (5 * calorieCalc.height) - (6.8 * calorieCalc.age)
  } else {
    bmr = 655 + (9.6 * props.weight) + (1.8 * calorieCalc.height) - (4.7 * calorieCalc.age)
  }
  return Math.round(bmr)
})

const applyCalorieSuggestion = () => {
  if (calculateCalories.value) {
    emit('update:modelValue', calculateCalories.value)
    ElMessage.success('已套用建議的熱量限制！')
    calorieHelpVisible.value = false
  }
}
</script>

<style scoped>
.calorie-calculator-wrapper {
  display: inline-block;
  position: relative;
}

.help-btn {
  padding: 6px 10px;
  font-size: 13px;
  border-radius: 999px;
  color: #c06b00 !important;
  background: rgba(255, 170, 85, 0.12) !important;
  border: 1px solid rgba(255, 170, 85, 0.28) !important;
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
}

.help-btn:hover {
  transform: translateY(-1px);
  background: rgba(255, 170, 85, 0.18) !important;
  border-color: rgba(255, 170, 85, 0.4) !important;
}

.help-btn .el-icon {
  font-size: 14px;
}

.calorie-help-dialog :deep(.el-dialog__body) {
  padding: 18px 22px 20px;
}

.calorie-help-content {
  color: #333;
}

.calculator-lead {
  margin: 0 0 16px;
  line-height: 1.6;
  color: #6b7280;
  font-size: 0.95rem;
}

.calorie-help-content h4 {
  margin: 0 0 12px;
  color: #4a4a4a;
}

.calorie-calculator {
  background: #faf7f2;
  padding: 18px;
  border-radius: 12px;
  border: 1px solid #f2e3cf;
}

.calorie-result {
  margin-top: 16px;
  padding: 14px;
  background: white;
  border-radius: 10px;
  border: 1px solid #f0e6d7;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.result-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  border-radius: 10px;
  background: #fcfaf7;
  border: 1px solid #efe4d4;
}

.result-label {
  font-size: 12px;
  color: #606266;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.result-value {
  font-size: 24px;
  font-weight: 700;
  color: #ff9800;
}

.result-unit {
  font-size: 12px;
  color: #8b93a1;
}

.result-stat.highlight {
  background: linear-gradient(135deg, #fff8ef 0%, #ffefd6 100%);
  border-color: #f4c486;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .result-summary {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    justify-content: stretch;
  }

  .action-buttons :deep(.el-button) {
    flex: 1 1 auto;
  }
}
</style> 
 