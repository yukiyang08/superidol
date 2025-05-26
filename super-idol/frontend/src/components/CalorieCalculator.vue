<template>
  <div class="calorie-calculator-wrapper">
    <el-button 
      type="warning"
      class="help-btn"
      @click="showCalorieHelp"
    >
      <el-icon><QuestionFilled /></el-icon>
      計算說明
    </el-button>

    <el-dialog
      v-model="calorieHelpVisible"
      title="每週熱量限制計算說明"
      width="500px"
      class="calorie-help-dialog"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      :modal="true"
      :append-to-body="true"
    >
      <div class="calorie-help-content">
        <h4>如何計算您的每週熱量限制？</h4>
        <p>我們建議您根據以下因素來設定：</p>
        <ul>
          <li>基礎代謝率 (BMR)</li>
          <li>日常活動量</li>
          <li>運動習慣</li>
          <li>健康目標（減重/維持/增重）</li>
        </ul>
        
        <div class="calorie-calculator">
          <h4>快速計算器</h4>
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
            <h4>計算結果</h4>
            <div class="result-grid">
              <div class="result-item">
                <div class="result-label">基礎代謝率 (BMR)</div>
                <div class="result-value">{{ bmr }} 大卡/天</div>
                <div class="result-desc">維持基本生命活動所需的熱量</div>
              </div>
              <div class="result-item highlight">
                <div class="result-label">每週建議熱量限制</div>
                <div class="result-value">{{ calculateCalories }} 大卡/週</div>
                <div class="result-desc">建議的每週熱量攝取上限</div>
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

<script>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'

export default {
  name: 'CalorieCalculator',
  components: {
    QuestionFilled
  },
  props: {
    weight: {
      type: Number,
      required: true
    },
    modelValue: {
      type: Number,
      required: true
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
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

    return {
      calorieHelpVisible,
      calorieCalc,
      isLoading,
      showCalorieHelp,
      calculateCalories,
      bmr,
      applyCalorieSuggestion
    }
  }
}
</script>

<style scoped>
.calorie-calculator-wrapper {
  display: inline-block;
  position: relative;
}

.help-btn {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.25);
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
}

.help-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4);
}

.help-btn .el-icon {
  font-size: 16px;
  margin-right: 4px;
}

.calorie-help-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.calorie-help-content {
  color: #333;
}

.calorie-help-content h4 {
  margin: 16px 0 12px;
  color: #4a4a4a;
}

.calorie-help-content p {
  margin: 12px 0;
  line-height: 1.6;
}

.calorie-help-content ul {
  margin: 12px 0;
  padding-left: 20px;
}

.calorie-help-content li {
  margin: 8px 0;
  line-height: 1.5;
}

.calorie-calculator {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.calorie-result {
  margin-top: 20px;
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin: 16px 0;
}

.result-item {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.result-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-item.highlight {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border: 1px solid #ffb74d;
}

.result-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.result-value {
  font-size: 24px;
  font-weight: bold;
  color: #ff9800;
  margin: 8px 0;
}

.result-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}
</style> 
