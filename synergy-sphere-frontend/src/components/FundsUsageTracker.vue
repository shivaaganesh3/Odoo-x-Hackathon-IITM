<template>
  <div class="funds-usage-tracker">
    <div class="funds-header">
      <h3>💸 Funds Usage Analysis</h3>
      <button @click="refreshData" class="refresh-btn" :disabled="loading">
        🔄 {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Analyzing funds usage...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button @click="refreshData" class="retry-btn">Try Again</button>
    </div>

    <div v-else-if="fundsData" class="funds-content">
      <!-- Overview Cards -->
      <div class="overview-cards">
        <div class="overview-card budget">
          <div class="card-icon">💰</div>
          <div class="card-content">
            <div class="card-value">{{ formatCurrency(fundsData.total_budget) }}</div>
            <div class="card-label">Total Budget</div>
          </div>
        </div>

        <div class="overview-card expenses">
          <div class="card-icon">💳</div>
          <div class="card-content">
            <div class="card-value">{{ formatCurrency(fundsData.total_expenses) }}</div>
            <div class="card-label">Total Expenses</div>
          </div>
        </div>

        <div class="overview-card remaining" :class="remainingFundsClass">
          <div class="card-icon">{{ remainingFundsIcon }}</div>
          <div class="card-content">
            <div class="card-value">{{ formatCurrency(fundsData.remaining_funds) }}</div>
            <div class="card-label">Remaining Funds</div>
          </div>
        </div>

        <div class="overview-card usage" :class="usageStatusClass">
          <div class="card-icon">📊</div>
          <div class="card-content">
            <div class="card-value">{{ fundsData.usage_percentage }}%</div>
            <div class="card-label">Budget Used</div>
          </div>
        </div>
      </div>

      <!-- Status Alert -->
      <div v-if="fundsData.status !== 'healthy'" class="status-alert" :class="fundsData.status">
        <div class="alert-icon">
          {{ getStatusIcon(fundsData.status) }}
        </div>
        <div class="alert-content">
          <div class="alert-message">{{ fundsData.status_message }}</div>
          <div class="alert-details">
            Budget utilization: {{ fundsData.usage_percentage }}%
          </div>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="usage-progress">
        <div class="progress-header">
          <span class="progress-label">Budget Utilization</span>
          <span class="progress-percentage">{{ fundsData.usage_percentage }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :class="usageStatusClass"
            :style="{ width: Math.min(fundsData.usage_percentage, 100) + '%' }"
          ></div>
        </div>
        <div class="progress-markers">
          <span class="marker" style="left: 50%">50%</span>
          <span class="marker" style="left: 75%">75%</span>
          <span class="marker" style="left: 90%">90%</span>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div v-if="Object.keys(fundsData.category_breakdown).length > 0" class="category-breakdown">
        <h4>💼 Expenses by Category</h4>
        <div class="category-list">
          <div 
            v-for="(amount, category) in fundsData.category_breakdown" 
            :key="category"
            class="category-item"
          >
            <div class="category-info">
              <span class="category-name">{{ category }}</span>
              <span class="category-amount">{{ formatCurrency(amount) }}</span>
            </div>
            <div class="category-bar">
              <div 
                class="category-fill"
                :style="{ 
                  width: (amount / fundsData.total_expenses * 100) + '%' 
                }"
              ></div>
            </div>
            <div class="category-percentage">
              {{ Math.round(amount / fundsData.total_expenses * 100) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Breakdown (for project level) -->
      <div v-if="fundsData.monthly_breakdown && fundsData.monthly_breakdown.length > 0" class="monthly-breakdown">
        <h4>📅 Monthly Budget vs Expenses</h4>
        <div class="monthly-chart">
          <div 
            v-for="month in fundsData.monthly_breakdown" 
            :key="month.month"
            class="month-item"
          >
            <div class="month-label">{{ formatMonth(month.month) }}</div>
            <div class="month-bars">
              <div class="budget-bar" :style="{ height: getBarHeight(month.budget, maxMonthlyAmount) }">
                <span class="bar-value">{{ formatShortCurrency(month.budget) }}</span>
              </div>
              <div class="expense-bar" :style="{ height: getBarHeight(month.expenses, maxMonthlyAmount) }">
                <span class="bar-value">{{ formatShortCurrency(month.expenses) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-color budget"></div>
            <span>Budget</span>
          </div>
          <div class="legend-item">
            <div class="legend-color expense"></div>
            <span>Expenses</span>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="summary-stats">
        <div class="stat-item">
          <span class="stat-label">Budget Items:</span>
          <span class="stat-value">{{ fundsData.budget_count }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Expense Records:</span>
          <span class="stat-value">{{ fundsData.expense_count }}</span>
        </div>
        <div v-if="fundsData.task_title" class="stat-item">
          <span class="stat-label">Task:</span>
          <span class="stat-value">{{ fundsData.task_title }}</span>
        </div>
      </div>
    </div>

    <div v-else class="no-data">
      <div class="no-data-icon">📊</div>
      <p>No budget or expense data available for analysis.</p>
      <p class="no-data-hint">
        Add budgets and track expenses to see funds usage analysis.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from '../axios'

const props = defineProps({
  projectId: {
    type: Number,
    required: false,
    default: null
  },
  taskId: {
    type: Number,
    required: false,
    default: null
  }
})

// State
const fundsData = ref(null)
const loading = ref(false)
const error = ref(null)

// Computed
const remainingFundsClass = computed(() => {
  if (!fundsData.value) return ''
  if (fundsData.value.remaining_funds < 0) return 'negative'
  if (fundsData.value.usage_percentage >= 90) return 'critical'
  if (fundsData.value.usage_percentage >= 75) return 'warning'
  return 'positive'
})

const remainingFundsIcon = computed(() => {
  if (!fundsData.value) return '💰'
  if (fundsData.value.remaining_funds < 0) return '⚠️'
  if (fundsData.value.usage_percentage >= 90) return '🔴'
  if (fundsData.value.usage_percentage >= 75) return '🟡'
  return '🟢'
})

const usageStatusClass = computed(() => {
  if (!fundsData.value) return ''
  return fundsData.value.status
})

const maxMonthlyAmount = computed(() => {
  if (!fundsData.value?.monthly_breakdown) return 0
  return Math.max(
    ...fundsData.value.monthly_breakdown.map(m => Math.max(m.budget, m.expenses))
  )
})

// Methods
const fetchFundsUsage = async () => {
  loading.value = true
  error.value = null
  
  try {
    let url
    if (props.taskId) {
      url = `/budget/funds-usage/task/${props.taskId}`
    } else if (props.projectId) {
      url = `/budget/funds-usage/project/${props.projectId}`
    } else {
      throw new Error('Either projectId or taskId is required')
    }
    
    const response = await axios.get(url)
    fundsData.value = response.data
  } catch (err) {
    console.error('Error fetching funds usage:', err)
    error.value = err.response?.data?.error || 'Failed to load funds usage data'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchFundsUsage()
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(amount)
}

const formatShortCurrency = (amount) => {
  if (amount >= 1000000) {
    return '$' + (amount / 1000000).toFixed(1) + 'M'
  } else if (amount >= 1000) {
    return '$' + (amount / 1000).toFixed(1) + 'K'
  }
  return '$' + amount.toFixed(0)
}

const formatMonth = (monthStr) => {
  const [year, month] = monthStr.split('-')
  const date = new Date(year, month - 1)
  return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
}

const getBarHeight = (value, maxValue) => {
  if (!maxValue) return '0px'
  const percentage = (value / maxValue) * 100
  return Math.max(percentage, 5) + '%'
}

const getStatusIcon = (status) => {
  switch (status) {
    case 'critical': return '🚨'
    case 'warning': return '⚠️'
    case 'moderate': return '📊'
    default: return '✅'
  }
}

// Lifecycle
onMounted(() => {
  fetchFundsUsage()
})

// Watch for prop changes
watch([() => props.projectId, () => props.taskId], () => {
  fetchFundsUsage()
})
</script>

<style scoped>
.funds-usage-tracker {
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
}

.funds-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.funds-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.refresh-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #2563eb;
}

.refresh-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.loading-state, .error-state, .no-data {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #dc2626;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.no-data-hint {
  font-size: 0.875rem;
  color: #9ca3af;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  font-size: 2rem;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.card-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.overview-card.positive { border-left: 4px solid #10b981; }
.overview-card.warning { border-left: 4px solid #f59e0b; }
.overview-card.critical { border-left: 4px solid #ef4444; }
.overview-card.negative { border-left: 4px solid #dc2626; }
.overview-card.healthy { border-left: 4px solid #10b981; }
.overview-card.moderate { border-left: 4px solid #3b82f6; }

.status-alert {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.status-alert.warning {
  background: #fef3c7;
  border: 1px solid #f59e0b;
}

.status-alert.critical {
  background: #fee2e2;
  border: 1px solid #ef4444;
}

.status-alert.moderate {
  background: #dbeafe;
  border: 1px solid #3b82f6;
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-message {
  font-weight: 600;
  color: #1f2937;
}

.alert-details {
  font-size: 0.875rem;
  color: #6b7280;
}

.usage-progress {
  margin-bottom: 32px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label {
  font-weight: 600;
  color: #1f2937;
}

.progress-percentage {
  font-weight: 600;
  color: #6b7280;
}

.progress-bar {
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.progress-fill.healthy { background: #10b981; }
.progress-fill.moderate { background: #3b82f6; }
.progress-fill.warning { background: #f59e0b; }
.progress-fill.critical { background: #ef4444; }

.progress-markers {
  position: relative;
  height: 20px;
}

.marker {
  position: absolute;
  top: 4px;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: #9ca3af;
}

.category-breakdown, .monthly-breakdown {
  background: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.category-breakdown h4, .monthly-breakdown h4 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 1.125rem;
}

.category-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 500;
  color: #1f2937;
}

.category-amount {
  font-weight: 600;
  color: #6b7280;
}

.category-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  min-width: 100px;
}

.category-fill {
  height: 100%;
  background: #3b82f6;
}

.category-percentage {
  font-size: 0.875rem;
  color: #6b7280;
  text-align: right;
}

.monthly-chart {
  display: flex;
  gap: 12px;
  align-items: end;
  margin-bottom: 16px;
  min-height: 150px;
}

.month-item {
  flex: 1;
  text-align: center;
}

.month-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 8px;
}

.month-bars {
  display: flex;
  gap: 4px;
  align-items: end;
  height: 120px;
}

.budget-bar, .expense-bar {
  flex: 1;
  position: relative;
  min-height: 20px;
  border-radius: 4px 4px 0 0;
}

.budget-bar {
  background: #3b82f6;
}

.expense-bar {
  background: #ef4444;
}

.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.625rem;
  color: #6b7280;
  white-space: nowrap;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.budget {
  background: #3b82f6;
}

.legend-color.expense {
  background: #ef4444;
}

.summary-stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-item {
  display: flex;
  gap: 8px;
}

.stat-label {
  color: #6b7280;
  font-size: 0.875rem;
}

.stat-value {
  color: #1f2937;
  font-weight: 600;
  font-size: 0.875rem;
}
</style> 