<template>
  <div class="natural-task-input">
    <!-- Toggle Button -->
    <div class="input-mode-toggle">
      <button 
        @click="toggleInputMode" 
        class="mode-toggle-btn"
        :class="{ 'active': isNaturalMode }"
      >
        <span v-if="!isNaturalMode">🧠 Switch to AI Task Input</span>
        <span v-else">📝 Switch to Manual Input</span>
      </button>
    </div>

    <!-- Natural Language Input Mode -->
    <div v-if="isNaturalMode" class="nl-input-section">
      <div class="nl-header">
        <h3>🧠 Describe Your Task Naturally</h3>
        <p class="nl-description">
          Type something like: "Remind John to finalize the pitch deck by Friday" 
          or "High priority - Sarah needs to review the budget this week"
        </p>
      </div>

      <div class="nl-form">
        <div class="input-group">
          <textarea
            v-model="naturalLanguageText"
            placeholder="Describe your task... (e.g., 'Remind John to finish the presentation by Friday - high priority')"
            class="nl-textarea"
            rows="3"
            @keydown.ctrl.enter="parseTask"
          ></textarea>
          
          <div class="nl-actions">
            <button 
              @click="parseTask" 
              :disabled="!naturalLanguageText.trim() || isLoading"
              class="parse-btn"
            >
              <span v-if="isLoading">🔄 Parsing...</span>
              <span v-else>🧠 Parse Task</span>
            </button>
            
            <button 
              v-if="parsedTask"
              @click="clearParsedTask"
              class="clear-btn"
            >
              🗑️ Clear
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Analyzing your task with AI...</p>
        </div>

        <!-- Error State -->
        <div v-if="parseError" class="error-state">
          <p class="error-message">❌ {{ parseError }}</p>
          <button @click="parseError = null" class="dismiss-error">Dismiss</button>
        </div>

        <!-- Parsed Result -->
        <div v-if="parsedTask && !isLoading" class="parsed-result">
          <div class="result-header">
            <h4>🎯 Parsed Task Information</h4>
            <div class="confidence-indicator">
              <span class="confidence-label">Confidence:</span>
              <span :class="getConfidenceClass(parsedTask.parsing_info?.confidence)">
                {{ parsedTask.parsing_info?.confidence || 'Unknown' }}
              </span>
            </div>
          </div>

          <!-- Editable Parsed Fields -->
          <div class="parsed-fields">
            <div class="field-group">
              <label>📝 Task Title:</label>
              <input 
                v-model="parsedTask.title" 
                class="parsed-input title-input"
                placeholder="Task title"
              />
            </div>

            <div class="field-group">
              <label>📄 Description:</label>
              <input 
                v-model="parsedTask.description" 
                class="parsed-input"
                placeholder="Task description (optional)"
              />
            </div>

            <div class="field-row">
              <div class="field-group">
                <label>👤 Assigned To:</label>
                <div class="assignee-info">
                  <input 
                    v-model="parsedTask.assigned_to" 
                    type="number"
                    class="parsed-input assignee-input"
                    placeholder="User ID"
                  />
                  <div v-if="parsedTask.parsing_info?.resolved_assignee" class="resolved-assignee">
                    ✅ {{ parsedTask.parsing_info.resolved_assignee.name }}
                  </div>
                  <div v-else-if="parsedTask.parsing_info?.assignee_name" class="unresolved-assignee">
                    ⚠️ "{{ parsedTask.parsing_info.assignee_name }}" not found in project
                  </div>
                </div>
              </div>

              <div class="field-group">
                <label>📅 Due Date:</label>
                <input 
                  v-model="parsedTask.due_date" 
                  type="date"
                  class="parsed-input"
                />
              </div>
            </div>

            <div class="field-row">
              <div class="field-group">
                <label>⚡ Priority:</label>
                <select v-model="parsedTask.priority" class="parsed-select">
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>

              <div class="field-group">
                <label>💪 Effort Score:</label>
                <select v-model="parsedTask.effort_score" class="parsed-select">
                  <option value="1">⚡ Very Easy</option>
                  <option value="2">🌟 Easy</option>
                  <option value="3">📊 Medium</option>
                  <option value="4">💪 Hard</option>
                  <option value="5">🔥 Very Hard</option>
                </select>
              </div>

              <div class="field-group">
                <label>🚀 Impact Score:</label>
                <select v-model="parsedTask.impact_score" class="parsed-select">
                  <option value="1">📉 Low</option>
                  <option value="2">📈 Medium-Low</option>
                  <option value="3">🎯 Medium</option>
                  <option value="4">🚀 High</option>
                  <option value="5">💥 Critical</option>
                </select>
              </div>
            </div>

            <!-- Status Selection -->
            <div class="field-group">
              <label>📊 Status:</label>
              <select v-model="parsedTask.status_id" class="parsed-select status-select">
                <option value="">Select Status</option>
                <option 
                  v-for="status in customStatuses" 
                  :key="status.id" 
                  :value="status.id"
                >
                  {{ status.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Warnings -->
          <div v-if="parsedTask.warnings?.length" class="warnings-section">
            <h5>⚠️ Warnings:</h5>
            <ul class="warnings-list">
              <li v-for="warning in parsedTask.warnings" :key="warning" class="warning-item">
                {{ warning }}
              </li>
            </ul>
          </div>

          <!-- Action Buttons -->
          <div class="result-actions">
            <button 
              @click="createTaskFromParsed" 
              :disabled="!canCreateTask"
              class="create-task-btn"
            >
              ✅ Create Task
            </button>
            
            <button 
              @click="fillManualForm" 
              class="fill-manual-btn"
            >
              📝 Fill Manual Form
            </button>
            
            <button 
              @click="clearParsedTask" 
              class="cancel-btn"
            >
              ❌ Cancel
            </button>
          </div>

          <!-- Debug Information -->
          <div class="debug-section">
            <button @click="showDebugInfo = !showDebugInfo" class="debug-toggle">
              {{ showDebugInfo ? 'Hide' : 'Show' }} Debug Info
            </button>
            <div v-if="showDebugInfo" class="debug-content">
              <pre>{{ JSON.stringify(parsedTask, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from '../axios.js'

// Props
const props = defineProps({
  projectId: {
    type: [String, Number],
    required: true
  },
  customStatuses: {
    type: Array,
    default: () => []
  },
  onTaskCreated: {
    type: Function,
    default: () => {}
  },
  onFillManualForm: {
    type: Function,
    default: () => {}
  }
})

// Reactive data
const isNaturalMode = ref(false)
const naturalLanguageText = ref('')
const parsedTask = ref(null)
const isLoading = ref(false)
const parseError = ref(null)
const showDebugInfo = ref(false)

// Computed properties
const canCreateTask = computed(() => {
  return parsedTask.value && 
         parsedTask.value.title && 
         parsedTask.value.status_id
})

// Methods
const toggleInputMode = () => {
  isNaturalMode.value = !isNaturalMode.value
  if (!isNaturalMode.value) {
    clearParsedTask()
  }
}

const parseTask = async () => {
  if (!naturalLanguageText.value.trim()) return
  
  isLoading.value = true
  parseError.value = null
  
  try {
    const response = await axios.post('/tasks/parse-nl-task', {
      text: naturalLanguageText.value,
      project_id: props.projectId
    })
    
    parsedTask.value = response.data
    
    // Auto-select default status if not set
    if (!parsedTask.value.status_id && props.customStatuses.length > 0) {
      const defaultStatus = props.customStatuses.find(s => s.is_default) || props.customStatuses[0]
      parsedTask.value.status_id = defaultStatus.id
    }
    
  } catch (error) {
    console.error('Parse error:', error)
    parseError.value = error.response?.data?.error || 'Failed to parse task. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const clearParsedTask = () => {
  parsedTask.value = null
  naturalLanguageText.value = ''
  parseError.value = null
}

const createTaskFromParsed = async () => {
  if (!canCreateTask.value) return
  
  try {
    await axios.post('/tasks/', {
      ...parsedTask.value,
      project_id: props.projectId
    })
    
    // Success
    props.onTaskCreated()
    clearParsedTask()
    alert('Task created successfully! 🎉')
    
  } catch (error) {
    console.error('Create task error:', error)
    alert(error.response?.data?.error || 'Failed to create task')
  }
}

const fillManualForm = () => {
  props.onFillManualForm(parsedTask.value)
  clearParsedTask()
  isNaturalMode.value = false
}

const getConfidenceClass = (confidence) => {
  switch (confidence?.toLowerCase()) {
    case 'high':
      return 'confidence-high'
    case 'medium':
      return 'confidence-medium'
    case 'low':
      return 'confidence-low'
    default:
      return 'confidence-unknown'
  }
}
</script>

<style scoped>
.natural-task-input {
  margin-bottom: 2rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}

.input-mode-toggle {
  margin-bottom: 1rem;
}

.mode-toggle-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.mode-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.mode-toggle-btn.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.nl-input-section {
  margin-top: 1rem;
}

.nl-header {
  margin-bottom: 1.5rem;
}

.nl-header h3 {
  color: #1f2937;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.nl-description {
  color: #6b7280;
  font-size: 0.9rem;
  font-style: italic;
}

.input-group {
  margin-bottom: 1rem;
}

.nl-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s ease;
}

.nl-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.nl-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.parse-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.parse-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.clear-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  margin: 1rem 0;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  background: #fef2f2;
  border: 1px solid #ef4444;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.error-message {
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.dismiss-error {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.parsed-result {
  background: white;
  border: 2px solid #10b981;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}

.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-high { color: #10b981; font-weight: bold; }
.confidence-medium { color: #f59e0b; font-weight: bold; }
.confidence-low { color: #ef4444; font-weight: bold; }
.confidence-unknown { color: #6b7280; }

.parsed-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.field-group label {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.parsed-input, .parsed-select {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
}

.title-input {
  font-weight: 600;
  font-size: 1rem;
}

.assignee-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.resolved-assignee {
  color: #10b981;
  font-size: 0.8rem;
  font-weight: 500;
}

.unresolved-assignee {
  color: #f59e0b;
  font-size: 0.8rem;
  font-weight: 500;
}

.warnings-section {
  background: #fffbeb;
  border: 1px solid #f59e0b;
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
}

.warnings-section h5 {
  color: #92400e;
  margin-bottom: 0.5rem;
}

.warnings-list {
  margin: 0;
  padding-left: 1.5rem;
}

.warning-item {
  color: #92400e;
  font-size: 0.9rem;
}

.result-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.create-task-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.create-task-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.fill-manual-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.debug-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.debug-toggle {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.debug-content {
  margin-top: 0.5rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 1rem;
}

.debug-content pre {
  font-size: 0.7rem;
  color: #374151;
  white-space: pre-wrap;
  margin: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .field-row {
    grid-template-columns: 1fr;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style> 