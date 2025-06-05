<template>
  <div class="smart-dashboard">
    <div class="dashboard-header">
      <h1>🧠 Smart Task Prioritization Dashboard</h1>
      <p class="subtitle">AI-powered task management with multi-factor priority scoring</p>
    </div>

    <!-- Key Metrics Cards -->
    <div class="metrics-grid">
      <div class="metric-card urgent">
        <div class="metric-icon">🚨</div>
        <div class="metric-content">
          <h3>{{ urgentTasks }}</h3>
          <p>Urgent Tasks</p>
        </div>
      </div>
      
      <div class="metric-card blocked">
        <div class="metric-icon">⏸️</div>
        <div class="metric-content">
          <h3>{{ blockedTasks }}</h3>
          <p>Blocked Tasks</p>
        </div>
      </div>
      
      <div class="metric-card high-impact">
        <div class="metric-icon">🚀</div>
        <div class="metric-content">
          <h3>{{ highImpactTasks }}</h3>
          <p>High Impact Tasks</p>
        </div>
      </div>
      
      <div class="metric-card avg-priority">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>{{ averagePriority }}</h3>
          <p>Avg Priority Score</p>
        </div>
      </div>
    </div>

    <!-- Priority Algorithm Explanation -->
    <div class="algorithm-section">
      <h2>🔬 How Smart Prioritization Works</h2>
      <div class="algorithm-grid">
        <div class="factor-card">
          <div class="factor-icon">🕒</div>
          <h3>Urgency (35%)</h3>
          <p>Days until deadline with exponential decay for overdue tasks</p>
        </div>
        
        <div class="factor-card">
          <div class="factor-icon">💪</div>
          <h3>Effort (20%)</h3>
          <p>Task complexity (inverted - easier tasks get higher priority)</p>
        </div>
        
        <div class="factor-card">
          <div class="factor-icon">🔗</div>
          <h3>Dependencies (25%)</h3>
          <p>Number of tasks blocked by this task</p>
        </div>
        
        <div class="factor-card">
          <div class="factor-icon">🎯</div>
          <h3>Impact (20%)</h3>
          <p>Project criticality and business value</p>
        </div>
      </div>
    </div>

    <!-- My Priority Tasks -->
    <div class="priority-tasks-section">
      <div class="section-header">
        <h2>🎯 My Top Priority Tasks</h2>
        <button @click="refreshTasks" class="refresh-btn" :disabled="loading">
          {{ loading ? '🔄 Loading...' : '🔄 Refresh' }}
        </button>
      </div>
      
      <div v-if="myTasks.length > 0" class="priority-task-list">
        <div v-for="task in myTasks.slice(0, 5)" :key="task.id" class="priority-task-item">
          <div class="task-priority-info">
            <span class="priority-score">{{ task.priority_score || 0 }}</span>
          </div>
          
          <div class="task-details">
            <h4>{{ task.title }}</h4>
            <div class="task-meta">
              <span class="priority-badge" :class="getPriorityClass(task.priority)">
                {{ task.priority }}
              </span>
              <span class="project-info">{{ task.project_name }}</span>
              <span v-if="task.due_date" class="due-date">📅 {{ formatDate(task.due_date) }}</span>
            </div>
          </div>
          
          <div class="task-actions">
            <button @click="viewTaskInsights(task)" class="insights-btn">
              🧠 Insights
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="no-tasks-message">
        <div class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>No tasks assigned</h3>
          <p>You don't have any tasks assigned to you yet.</p>
        </div>
      </div>
    </div>

    <!-- Blocked Tasks Alert -->
    <div v-if="blockedTasksList.length > 0" class="blocked-section">
      <h2>⚠️ Attention: Blocked Tasks</h2>
      <div class="blocked-tasks-list">
        <div v-for="task in blockedTasksList" :key="task.id" class="blocked-task-item">
          <div class="blocked-task-info">
            <h4>{{ task.title }}</h4>
            <p>Blocked by {{ task.blocked_by_count }} task(s)</p>
          </div>
          <div class="blocking-tasks">
            <small>Waiting for:</small>
            <div class="blocking-list">
              <span v-for="blockingTask in task.blocking_tasks" :key="blockingTask.id" 
                    class="blocking-task">
                {{ blockingTask.title }} ({{ blockingTask.assignee }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Insights Modal -->
    <div v-if="showingInsights" class="modal-overlay" @click="closeInsights">
      <div class="modal insights-modal" @click.stop>
        <h3>🧠 Priority Insights: {{ insightsData?.title }}</h3>
        <div v-if="insightsData" class="insights-content">
          <div class="score-breakdown">
            <h4>Detailed Score Breakdown:</h4>
            <div class="score-item">
              <span class="score-label">🕒 Urgency:</span>
              <div class="score-details">
                <span class="score-value">{{ insightsData.scores.urgency.value }}/10</span>
                <div class="score-bar">
                  <div class="score-fill urgency" 
                       :style="{ width: (insightsData.scores.urgency.value * 10) + '%' }"></div>
                </div>
                <span class="score-weighted">Weighted: {{ insightsData.scores.urgency.weighted.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="score-item">
              <span class="score-label">💪 Effort:</span>
              <div class="score-details">
                <span class="score-value">{{ insightsData.scores.effort.value }}/10</span>
                <div class="score-bar">
                  <div class="score-fill effort" 
                       :style="{ width: (insightsData.scores.effort.value * 10) + '%' }"></div>
                </div>
                <span class="score-weighted">Weighted: {{ insightsData.scores.effort.weighted.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="score-item">
              <span class="score-label">🔗 Dependencies:</span>
              <div class="score-details">
                <span class="score-value">{{ insightsData.scores.dependency.value }}/10</span>
                <div class="score-bar">
                  <div class="score-fill dependency" 
                       :style="{ width: (insightsData.scores.dependency.value * 10) + '%' }"></div>
                </div>
                <span class="score-weighted">Weighted: {{ insightsData.scores.dependency.weighted.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="score-item">
              <span class="score-label">🚀 Impact:</span>
              <div class="score-details">
                <span class="score-value">{{ insightsData.scores.impact.value }}/10</span>
                <div class="score-bar">
                  <div class="score-fill impact" 
                       :style="{ width: (insightsData.scores.impact.value * 10) + '%' }"></div>
                </div>
                <span class="score-weighted">Weighted: {{ insightsData.scores.impact.weighted.toFixed(2) }}</span>
              </div>
            </div>
            
            <div class="total-score">
              <strong>🎯 Total Priority Score: {{ insightsData.total_score }}/10</strong>
            </div>
          </div>
          
          <div class="dependency-summary">
            <h4>Dependency Information:</h4>
            <p><strong>🚫 Blocking:</strong> {{ insightsData.blocking_tasks }} task(s)</p>
            <p><strong>⏸️ Blocked by:</strong> {{ insightsData.blocked_by_tasks }} task(s)</p>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="closeInsights" class="close-btn">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '../axios'

// Reactive data
const myTasks = ref([])
const blockedTasksList = ref([])
const loading = ref(false)
const showingInsights = ref(false)
const insightsData = ref(null)

// Computed metrics
const urgentTasks = computed(() => 
  myTasks.value.filter(task => task.priority === 'Urgent').length
)

const blockedTasks = computed(() => 
  myTasks.value.filter(task => task.is_blocked).length
)

const highImpactTasks = computed(() => 
  myTasks.value.filter(task => task.impact_score >= 4).length
)

const averagePriority = computed(() => {
  if (myTasks.value.length === 0) return '0.0'
  const sum = myTasks.value.reduce((acc, task) => acc + (task.priority_score || 0), 0)
  return (sum / myTasks.value.length).toFixed(1)
})

// Methods
const refreshTasks = async () => {
  loading.value = true
  try {
    // Fetch my tasks with smart sorting
    const tasksRes = await axios.get('/tasks/my?sort_by=smart')
    myTasks.value = tasksRes.data

    // Fetch blocked tasks
    const blockedRes = await axios.get('/tasks/blocked')
    blockedTasksList.value = blockedRes.data
  } catch (err) {
    console.error('Failed to load dashboard data', err)
  } finally {
    loading.value = false
  }
}

const viewTaskInsights = async (task) => {
  try {
    const res = await axios.get(`/tasks/priority/insights/${task.id}`)
    insightsData.value = res.data
    showingInsights.value = true
  } catch (err) {
    console.error('Failed to load priority insights', err)
    alert('Failed to load priority insights')
  }
}

const closeInsights = () => {
  showingInsights.value = false
  insightsData.value = null
}

const getPriorityClass = (priority) => {
  switch (priority?.toLowerCase()) {
    case 'urgent':
      return 'priority-urgent'
    case 'high':
      return 'priority-high'
    case 'medium':
      return 'priority-medium'
    case 'low':
      return 'priority-low'
    default:
      return 'priority-medium'
  }
}

const formatDate = (date) => {
  if (!date) return 'No due date'
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.smart-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header */
.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  font-size: 3rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #64748b;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.metric-card {
  padding: 2rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.metric-card.urgent {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-left: 4px solid #dc2626;
}

.metric-card.blocked {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-left: 4px solid #f59e0b;
}

.metric-card.high-impact {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border-left: 4px solid #3b82f6;
}

.metric-card.avg-priority {
  background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
  border-left: 4px solid #8b5cf6;
}

.metric-icon {
  font-size: 2.5rem;
}

.metric-content h3 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  color: #1f2937;
}

.metric-content p {
  margin: 0;
  color: #6b7280;
  font-weight: 500;
}

/* Algorithm Section */
.algorithm-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.algorithm-section h2 {
  text-align: center;
  color: #1e293b;
  margin-bottom: 2rem;
}

.algorithm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.factor-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease;
}

.factor-card:hover {
  transform: translateY(-2px);
}

.factor-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.factor-card h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.factor-card p {
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.factor-example {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #6366f1;
}

.factor-example small {
  color: #475569;
  font-weight: 500;
}

/* Priority Tasks Section */
.priority-tasks-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header h2 {
  color: #1e293b;
  margin: 0;
}

.refresh-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.priority-task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.priority-task-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.priority-task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.task-priority-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 80px;
}

.priority-score {
  font-size: 1.5rem;
  font-weight: 700;
  color: #6366f1;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 0.5rem;
  border-radius: 8px;
  min-width: 50px;
  text-align: center;
}

.priority-bars {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 60px;
}

.priority-bar {
  height: 4px;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.priority-bar.urgency { background: #dc2626; }
.priority-bar.effort { background: #10b981; }
.priority-bar.dependency { background: #6366f1; }
.priority-bar.impact { background: #f59e0b; }

.task-details {
  flex: 1;
}

.task-details h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.1rem;
}

.task-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.priority-badge.priority-urgent { background: #dc2626; }
.priority-badge.priority-high { background: #ea580c; }
.priority-badge.priority-medium { background: #d97706; }
.priority-badge.priority-low { background: #65a30d; }

.project-info, .due-date {
  font-size: 0.875rem;
  color: #64748b;
}

.task-indicators {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.indicator {
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

.indicator.blocked {
  background: #fef3c7;
  color: #92400e;
}

.indicator.blocking {
  background: #fee2e2;
  color: #991b1b;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
}

.insights-btn {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.insights-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

/* Empty State */
.no-tasks-message {
  text-align: center;
  padding: 3rem;
}

.empty-state {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #6b7280;
}

/* Blocked Section */
.blocked-section {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  padding: 2rem;
  border-radius: 12px;
  border-left: 4px solid #f59e0b;
  margin-bottom: 2rem;
}

.blocked-section h2 {
  color: #92400e;
  margin-bottom: 1.5rem;
}

.blocked-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.blocked-task-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.blocked-task-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
}

.blocked-task-info p {
  margin: 0 0 0.5rem 0;
  color: #92400e;
  font-weight: 500;
}

.blocking-tasks small {
  color: #6b7280;
  font-weight: 500;
}

.blocking-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.blocking-task {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #374151;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.insights-modal h3 {
  color: #1e293b;
  margin-bottom: 1.5rem;
  text-align: center;
}

.insights-content {
  margin: 1rem 0;
}

.score-breakdown h4, .dependency-summary h4 {
  color: #1e293b;
  margin-bottom: 1rem;
}

.score-item {
  background: #f8fafc;
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 8px;
  border-left: 3px solid #6366f1;
}

.score-label {
  font-weight: 600;
  color: #475569;
  display: block;
  margin-bottom: 0.5rem;
}

.score-details {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.score-value {
  font-weight: bold;
  color: #1e293b;
  min-width: 60px;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  min-width: 100px;
}

.score-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-fill.urgency { background: #dc2626; }
.score-fill.effort { background: #10b981; }
.score-fill.dependency { background: #6366f1; }
.score-fill.impact { background: #f59e0b; }

.score-weighted {
  font-size: 0.875rem;
  color: #64748b;
}

.total-score {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin: 1rem 0;
  font-size: 1.1rem;
}

.dependency-summary {
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.dependency-summary p {
  margin: 0.5rem 0;
  color: #475569;
}

.modal-actions {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.close-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.close-btn:hover {
  background: #4b5563;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .algorithm-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .priority-task-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .task-priority-info {
    flex-direction: row;
    align-items: center;
    width: 100%;
  }
  
  .priority-bars {
    flex-direction: row;
    width: auto;
    flex: 1;
  }
  
  .priority-bar {
    height: 6px;
    width: 25%;
  }
  
  .score-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .score-bar {
    width: 100%;
  }
}
</style> 