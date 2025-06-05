<template>
  <div v-if="insights" class="deadline-warning" :class="warningClass">
    <div class="warning-header">
      <i class="fas" :class="warningIcon"></i>
      <span class="warning-title">{{ warningTitle }}</span>
    </div>
    
    <div class="warning-content">
      <div class="progress-section">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${insights.progress_score * 100}%` }"
          ></div>
        </div>
        <span class="progress-text">Progress: {{ Math.round(insights.progress_score * 100) }}%</span>
      </div>
      
      <div class="deadline-info">
        <span class="days-remaining" :class="daysRemainingClass">
          {{ daysRemainingText }}
        </span>
      </div>
      
      <div v-if="insights.recommendations.length" class="recommendations">
        <h4>Recommendations:</h4>
        <ul>
          <li v-for="(rec, index) in insights.recommendations" :key="index">
            {{ rec }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '../store/notifications'

const props = defineProps({
  taskId: {
    type: Number,
    required: true
  }
})

const notificationsStore = useNotificationsStore()
const insights = ref(null)

// Fetch deadline insights when component mounts
onMounted(async () => {
  insights.value = await notificationsStore.getTaskDeadlineInsights(props.taskId)
})

// Computed properties for styling and text
const warningClass = computed(() => {
  if (!insights.value) return ''
  return `risk-${insights.value.risk_level}`
})

const warningIcon = computed(() => {
  if (!insights.value) return ''
  const icons = {
    critical: 'fa-exclamation-circle',
    high: 'fa-exclamation-triangle',
    medium: 'fa-clock',
    low: 'fa-info-circle'
  }
  return icons[insights.value.risk_level] || 'fa-info-circle'
})

const warningTitle = computed(() => {
  if (!insights.value) return ''
  const titles = {
    critical: '🚨 Critical Deadline Risk',
    high: '⚠️ High Deadline Risk',
    medium: '⚡ Medium Deadline Risk',
    low: 'ℹ️ Low Deadline Risk'
  }
  return titles[insights.value.risk_level] || 'Deadline Status'
})

const daysRemainingText = computed(() => {
  if (!insights.value) return ''
  const days = insights.value.days_remaining
  if (days < 0) return `Overdue by ${Math.abs(days)} day${Math.abs(days) === 1 ? '' : 's'}`
  if (days === 0) return 'Due today'
  if (days === 1) return 'Due tomorrow'
  return `Due in ${days} days`
})

const daysRemainingClass = computed(() => {
  if (!insights.value) return ''
  const days = insights.value.days_remaining
  if (days < 0) return 'overdue'
  if (days <= 1) return 'urgent'
  if (days <= 3) return 'warning'
  return 'normal'
})
</script>

<style scoped>
.deadline-warning {
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.warning-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.warning-title {
  font-weight: 600;
  font-size: 1.1em;
}

.progress-section {
  margin: 12px 0;
}

.progress-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.deadline-info {
  margin: 12px 0;
}

.days-remaining {
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
}

.recommendations {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.recommendations h4 {
  margin-bottom: 8px;
  color: #666;
}

.recommendations ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recommendations li {
  margin: 4px 0;
  padding-left: 20px;
  position: relative;
}

.recommendations li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #666;
}

/* Risk level styles */
.risk-critical {
  background: #ffebee;
  border: 1px solid #ffcdd2;
}

.risk-high {
  background: #fff3e0;
  border: 1px solid #ffe0b2;
}

.risk-medium {
  background: #e8f5e9;
  border: 1px solid #c8e6c9;
}

.risk-low {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
}

/* Days remaining styles */
.overdue {
  background: #ffebee;
  color: #c62828;
}

.urgent {
  background: #fff3e0;
  color: #ef6c00;
}

.warning {
  background: #fff8e1;
  color: #f57f17;
}

.normal {
  background: #e8f5e9;
  color: #2e7d32;
}
</style> 