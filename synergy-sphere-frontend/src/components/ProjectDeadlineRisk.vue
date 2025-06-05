<template>
  <div v-if="riskData" class="project-deadline-risk" :class="riskClass">
    <div class="risk-header">
      <span class="risk-icon">{{ riskIcon }}</span>
      <span class="risk-title">{{ riskTitle }}</span>
    </div>
    
    <div class="risk-content">
      <div class="progress-section">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${riskData.progress_percentage}%` }"
          ></div>
        </div>
        <span class="progress-text">Progress: {{ riskData.progress_percentage }}%</span>
      </div>
      
      <div class="deadline-info">
        <span class="days-remaining" :class="daysRemainingClass">
          {{ daysRemainingText }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '../axios'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  }
})

const riskData = ref(null)

// Fetch project deadline risk when component mounts
onMounted(async () => {
  try {
    const response = await axios.get(`/analytics/project/${props.projectId}/deadline-risk`)
    riskData.value = response.data
  } catch (error) {
    console.error('Failed to fetch project deadline risk:', error)
  }
})

// Computed properties for styling and text
const riskClass = computed(() => {
  if (!riskData.value) return ''
  return `risk-${riskData.value.risk_level}`
})

const riskIcon = computed(() => {
  if (!riskData.value) return ''
  const icons = {
    critical: '🚨',
    high: '⚠️',
    medium: '⚡',
    low: 'ℹ️'
  }
  return icons[riskData.value.risk_level] || 'ℹ️'
})

const riskTitle = computed(() => {
  if (!riskData.value) return ''
  const titles = {
    critical: 'Critical Deadline Risk',
    high: 'High Deadline Risk', 
    medium: 'Medium Deadline Risk',
    low: 'Low Deadline Risk'
  }
  return titles[riskData.value.risk_level] || 'Deadline Status'
})

const daysRemainingText = computed(() => {
  if (!riskData.value) return ''
  const days = riskData.value.days_remaining
  if (days < 0) return `Overdue by ${Math.abs(days)} day${Math.abs(days) === 1 ? '' : 's'}`
  if (days === 0) return 'Due today'
  if (days === 1) return 'Due tomorrow'
  return `Due in ${days} days`
})

const daysRemainingClass = computed(() => {
  if (!riskData.value) return ''
  const days = riskData.value.days_remaining
  if (days < 0) return 'overdue'
  if (days <= 1) return 'urgent'
  if (days <= 3) return 'warning'
  return 'normal'
})
</script>

<style scoped>
.project-deadline-risk {
  border-radius: 6px;
  padding: 12px;
  margin-top: 12px;
  font-size: 0.875rem;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.risk-title {
  font-weight: 600;
  font-size: 0.875rem;
}

.progress-section {
  margin: 8px 0;
}

.progress-bar {
  height: 6px;
  background: #eee;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #666;
}

.deadline-info {
  margin: 8px 0;
}

.days-remaining {
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.75rem;
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