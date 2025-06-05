<template>
    <div class="project-tasks">
      <div class="header-section">
        <h2>📋 Tasks for Project ID: {{ projectId }}</h2>
        
        <!-- Smart Priority Controls -->
        <div class="priority-controls">
          <button @click="recalculatePriorities" class="recalculate-btn" :disabled="recalculating">
            🧠 {{ recalculating ? 'Recalculating...' : 'Recalculate Smart Priorities' }}
          </button>
          <button @click="showDependencyGraph = !showDependencyGraph" class="dependency-btn">
            🔗 {{ showDependencyGraph ? 'Hide' : 'Show' }} Dependencies
          </button>
        </div>
      </div>

      <!-- Status Management Link -->
      <div class="status-management-link">
        <router-link :to="`/custom-status`" class="manage-status-btn">
          🎨 Manage Custom Statuses
        </router-link>
      </div>

      <!-- Load Custom Statuses First -->
      <div v-if="customStatuses.length === 0" class="no-statuses-warning">
        <p>⚠️ No custom statuses found for this project. Please create custom statuses first.</p>
        <button @click="createDefaultStatuses" class="create-defaults-btn">
          🎯 Create Default Statuses
        </button>
      </div>

      <div v-else>
        <!-- 🧠 Natural Language Task Input -->
        <NaturalTaskInput 
          :project-id="projectId"
          :custom-statuses="customStatuses"
          :on-task-created="handleAiTaskCreated"
          :on-fill-manual-form="handleFillManualForm"
        />

        <!-- ➕ Add New Task (Enhanced with Smart Prioritization) -->
        <form @submit.prevent="createTask" class="task-form">
          <div class="form-row">
            <input v-model="newTask.title" placeholder="Task title" required class="task-title-input" />
            <input v-model="newTask.description" placeholder="Description" class="task-desc-input" />
            <input v-model="newTask.due_date" type="date" class="date-input" />
          </div>
          
          <div class="form-row">
            <select v-model="newTask.status_id" required class="status-select">
              <option value="">Select Status</option>
              <option 
                v-for="status in customStatuses" 
                :key="status.id" 
                :value="status.id"
              >
                {{ status.name }}
              </option>
            </select>
            
            <select v-model="newTask.effort_score" class="effort-select">
              <option value="1">⚡ Very Easy</option>
              <option value="2">🌟 Easy</option>
              <option value="3" selected>📊 Medium</option>
              <option value="4">💪 Hard</option>
              <option value="5">🔥 Very Hard</option>
            </select>
            
            <select v-model="newTask.impact_score" class="impact-select">
              <option value="1">📉 Low Impact</option>
              <option value="2">📈 Medium-Low</option>
              <option value="3" selected>🎯 Medium</option>
              <option value="4">🚀 High Impact</option>
              <option value="5">💥 Critical</option>
            </select>
            
            <input v-model="newTask.assigned_to" type="number" placeholder="User ID" class="assignee-input" />
            <button type="submit" class="add-btn">➕ Add Task</button>
          </div>
          
          <!-- Dependency Selection -->
          <div class="form-row" v-if="tasks.length > 0">
            <div class="dependency-section">
              <label>🔗 Dependencies (this task blocks):</label>
              <select multiple v-model="newTask.dependency_map" class="dependency-select">
                <option v-for="task in tasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>
            
            <div class="dependency-section">
              <label>⏸️ Blocked by:</label>
              <select multiple v-model="newTask.blocked_by" class="dependency-select">
                <option v-for="task in tasks" :key="task.id" :value="task.id">
                  {{ task.title }}
                </option>
              </select>
            </div>
          </div>
        </form>

        <!-- Filter and Sort Controls -->
        <div class="control-section">
          <div class="filter-section">
            <label>Filter by Status:</label>
            <select v-model="statusFilter" @change="fetchTasks">
              <option value="">All Statuses</option>
              <option 
                v-for="status in customStatuses" 
                :key="status.id" 
                :value="status.id"
              >
                {{ status.name }}
              </option>
            </select>
          </div>
          
          <div class="sort-section">
            <label>Sort by:</label>
            <select v-model="sortBy" @change="fetchTasks">
              <option value="smart">🧠 Smart Priority</option>
              <option value="due_date">📅 Due Date</option>
              <option value="priority">🎯 Priority Level</option>
              <option value="created_at">🕒 Created Date</option>
            </select>
          </div>
        </div>

        <!-- Dependency Graph Visualization -->
        <div v-if="showDependencyGraph && dependencyGraph.length > 0" class="dependency-graph">
          <h3>🔗 Task Dependencies</h3>
          <div class="graph-container">
            <div v-for="dep in dependencyGraph" :key="dep.task_id" class="dependency-node">
              <div class="node-task">
                <strong>{{ dep.title }}</strong>
                <span class="priority-badge" :class="getPriorityClass(dep.priority)">
                  {{ dep.priority }} ({{ dep.priority_score }})
                </span>
              </div>
              <div v-if="dep.blocks.length" class="blocks-section">
                <small>🚫 Blocks: {{ dep.blocks.length }} task(s)</small>
              </div>
              <div v-if="dep.depends_on.length" class="depends-section">
                <small>⏸️ Blocked by: {{ dep.depends_on.length }} task(s)</small>
              </div>
            </div>
          </div>
        </div>

        <!-- 📝 Enhanced Task List -->
        <ul v-if="tasks.length" class="task-list">
          <li v-for="task in tasks" :key="task.id" :class="{ 'blocked-task': task.is_blocked }">
            <div class="task-header">
              <div class="task-title-section">
                <strong>{{ task.title }}</strong>
                <div class="task-badges">
                  <span 
                    class="status-badge" 
                    :style="{ backgroundColor: task.status?.color || '#6B7280' }"
                  >
                    {{ task.status?.name || 'No Status' }}
                  </span>
                  <span class="priority-badge" :class="getPriorityClass(task.priority)">
                    {{ task.priority }}
                  </span>
                  <span class="priority-score-badge">
                    🧠 {{ task.priority_score || 0 }}
                  </span>
                </div>
              </div>
              
              <div class="task-indicators">
                <span v-if="task.is_blocked" class="blocked-indicator" title="This task is blocked">
                  ⏸️
                </span>
                <span v-if="task.blocks_others" class="blocking-indicator" title="This task blocks others">
                  🚫
                </span>
              </div>
            </div>
            
            <small class="task-description">{{ task.description }}</small>
            
            <div class="task-meta">
              📅 Due: {{ formatDate(task.due_date) }} |
              🎯 Priority: {{ task.priority || 'Medium' }} ({{ task.priority_score || 0 }}) |
              💪 Effort: {{ getEffortLabel(task.effort_score) }} |
              🚀 Impact: {{ getImpactLabel(task.impact_score) }} |
              👤 Assigned to: {{ task.assignee_name || 'Unassigned' }}
            </div>
            
            <!-- Add task discussions -->
            <TaskDiscussions 
              :task-id="task.id"
              :project-id="parseInt(projectId)"
              :current-user-id="currentUser.id"
            />
            
            <!-- Add deadline warning component -->
            <TaskDeadlineWarning 
              v-if="task.due_date" 
              :task-id="task.id" 
              class="task-deadline-warning"
            />
            
            <div v-if="task.dependency_map?.length || task.blocked_by?.length" class="dependency-info">
              <div v-if="task.dependency_map?.length" class="depends-info">
                🔗 Blocks {{ task.dependency_map.length }} task(s)
              </div>
              <div v-if="task.blocked_by?.length" class="blocked-info">
                ⏸️ Blocked by {{ task.blocked_by.length }} task(s)
              </div>
            </div>
            
            <div class="task-actions">
              <button @click="startEdit(task)" class="edit-btn">✏️ Edit</button>
              <button @click="showPriorityInsights(task)" class="insights-btn">🧠 Insights</button>
              <button @click="deleteTask(task.id)" class="delete-btn">🗑️ Delete</button>
            </div>
          </li>
        </ul>

        <p v-else class="no-tasks">No tasks found.</p>

        <!-- ✏️ Enhanced Edit Form Modal -->
        <div v-if="editingTask" class="modal-overlay" @click="cancelEdit">
          <div class="modal edit-modal" @click.stop>
            <h3>✏️ Edit Task</h3>
            <form @submit.prevent="updateTask">
              <div class="form-group">
                <label>Title:</label>
                <input v-model="editingTask.title" required />
              </div>
              <div class="form-group">
                <label>Description:</label>
                <textarea v-model="editingTask.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>Due Date:</label>
                <input v-model="editingTask.due_date" type="date" />
              </div>
              <div class="form-group">
                <label>Status:</label>
                <select v-model="editingTask.status_id" required>
                  <option 
                    v-for="status in customStatuses" 
                    :key="status.id" 
                    :value="status.id"
                  >
                    {{ status.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Effort Level:</label>
                <select v-model="editingTask.effort_score">
                  <option value="1">⚡ Very Easy</option>
                  <option value="2">🌟 Easy</option>
                  <option value="3">📊 Medium</option>
                  <option value="4">💪 Hard</option>
                  <option value="5">🔥 Very Hard</option>
                </select>
              </div>
              <div class="form-group">
                <label>Impact Level:</label>
                <select v-model="editingTask.impact_score">
                  <option value="1">📉 Low Impact</option>
                  <option value="2">📈 Medium-Low</option>
                  <option value="3">🎯 Medium</option>
                  <option value="4">🚀 High Impact</option>
                  <option value="5">💥 Critical</option>
                </select>
              </div>
              <div class="form-group">
                <label>Assigned to (User ID):</label>
                <input v-model="editingTask.assigned_to" type="number" />
              </div>
              <div class="form-group">
                <label>Dependencies (this task blocks):</label>
                <select multiple v-model="editingTask.dependency_map">
                  <option v-for="task in tasks.filter(t => t.id !== editingTask.id)" 
                          :key="task.id" :value="task.id">
                    {{ task.title }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Blocked by:</label>
                <select multiple v-model="editingTask.blocked_by">
                  <option v-for="task in tasks.filter(t => t.id !== editingTask.id)" 
                          :key="task.id" :value="task.id">
                    {{ task.title }}
                  </option>
                </select>
              </div>
              <div class="modal-actions">
                <button type="submit" class="save-btn">✅ Save</button>
                <button type="button" @click="cancelEdit" class="cancel-btn">❌ Cancel</button>
              </div>
            </form>
          </div>
        </div>

        <!-- Priority Insights Modal -->
        <div v-if="showingInsights" class="modal-overlay" @click="closeInsights">
          <div class="modal insights-modal" @click.stop>
            <h3>🧠 Priority Insights: {{ insightsData?.title }}</h3>
            <div v-if="insightsData" class="insights-content">
              <div class="score-breakdown">
                <h4>Score Breakdown:</h4>
                <div class="score-item">
                  <span class="score-label">🕒 Urgency:</span>
                  <span class="score-value">{{ insightsData.scores.urgency.value }}/10</span>
                  <span class="score-weighted">(weighted: {{ insightsData.scores.urgency.weighted.toFixed(2) }})</span>
                </div>
                <div class="score-item">
                  <span class="score-label">💪 Effort:</span>
                  <span class="score-value">{{ insightsData.scores.effort.value }}/10</span>
                  <span class="score-weighted">(weighted: {{ insightsData.scores.effort.weighted.toFixed(2) }})</span>
                </div>
                <div class="score-item">
                  <span class="score-label">🔗 Dependencies:</span>
                  <span class="score-value">{{ insightsData.scores.dependency.value }}/10</span>
                  <span class="score-weighted">(weighted: {{ insightsData.scores.dependency.weighted.toFixed(2) }})</span>
                </div>
                <div class="score-item">
                  <span class="score-label">🚀 Impact:</span>
                  <span class="score-value">{{ insightsData.scores.impact.value }}/10</span>
                  <span class="score-weighted">(weighted: {{ insightsData.scores.impact.weighted.toFixed(2) }})</span>
                </div>
                <div class="total-score">
                  <strong>Total Priority Score: {{ insightsData.total_score }}/10</strong>
                </div>
              </div>
              
              <div class="dependency-summary">
                <p><strong>🚫 Blocking:</strong> {{ insightsData.blocking_tasks }} task(s)</p>
                <p><strong>⏸️ Blocked by:</strong> {{ insightsData.blocked_by_tasks }} task(s)</p>
              </div>
            </div>
            <div class="modal-actions">
              <button @click="closeInsights" class="cancel-btn">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import axios from '../axios'
  import TaskDeadlineWarning from '../components/TaskDeadlineWarning.vue'
  import TaskDiscussions from '../components/TaskDiscussions.vue'
  import NaturalTaskInput from '../components/NaturalTaskInput.vue'
  import { useAuthStore } from '../store/auth'
  
  const route = useRoute()
  const authStore = useAuthStore()
  const currentUser = computed(() => authStore.user)
  const projectId = route.params.id
  
  const tasks = ref([])
  const customStatuses = ref([])
  const statusFilter = ref('')
  const sortBy = ref('smart')
  const showDependencyGraph = ref(false)
  const dependencyGraph = ref([])
  const showingInsights = ref(false)
  const insightsData = ref(null)
  
  const newTask = ref({
    title: '',
    description: '',
    due_date: '',
    status_id: '',
    assigned_to: null,
    effort_score: 3,
    impact_score: 3,
    dependency_map: [],
    blocked_by: []
  })
  
  const editingTask = ref(null)
  const recalculating = ref(false)
  
  // Load custom statuses for this project
  const fetchCustomStatuses = async () => {
    try {
      const res = await axios.get(`/custom-status/project/${projectId}`)
      customStatuses.value = res.data
      
      // Set default status for new task
      const defaultStatus = customStatuses.value.find(s => s.is_default)
      if (defaultStatus) {
        newTask.value.status_id = defaultStatus.id
      }
    } catch (err) {
      console.error('Failed to load custom statuses', err)
    }
  }
  
  // Load tasks
  const fetchTasks = async () => {
    try {
      let url = `/tasks/project/${projectId}`
      const params = new URLSearchParams()
      
      if (statusFilter.value) {
        params.append('status_id', statusFilter.value)
      }
      if (sortBy.value) {
        params.append('sort_by', sortBy.value)
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      const res = await axios.get(url)
      tasks.value = res.data
    } catch (err) {
      console.error('Failed to load tasks', err)
    }
  }
  
  // Create default statuses
  const createDefaultStatuses = async () => {
    try {
      await axios.post(`/custom-status/create-defaults/${projectId}`)
      await fetchCustomStatuses()
      alert('Default statuses created successfully!')
    } catch (err) {
      console.error('Failed to create default statuses', err)
      alert('Failed to create default statuses')
    }
  }
  
  // Create task
  const createTask = async () => {
    if (!newTask.value.status_id) {
      alert('Please select a status')
      return
    }
  
    try {
      await axios.post('/tasks/', {
        ...newTask.value,
        project_id: projectId
      })
      
      // Reset form
      const defaultStatus = customStatuses.value.find(s => s.is_default)
      newTask.value = {
        title: '',
        description: '',
        due_date: '',
        status_id: defaultStatus ? defaultStatus.id : '',
        assigned_to: null,
        effort_score: 3,
        impact_score: 3,
        dependency_map: [],
        blocked_by: []
      }
      
      fetchTasks()
      alert('Task created successfully!')
    } catch (err) {
      console.error('Failed to create task', err)
      alert(err.response?.data?.error || 'Failed to create task')
    }
  }
  
  // Start editing
  const startEdit = (task) => {
    editingTask.value = {
      ...task,
      status_id: task.status?.id || '',
      due_date: task.due_date || '',
      effort_score: task.effort_score || 3,
      impact_score: task.impact_score || 3,
      dependency_map: task.dependency_map?.map(id => id) || [],
      blocked_by: task.blocked_by?.map(id => id) || []
    }
  }
  
  // Update task
  const updateTask = async () => {
    try {
      await axios.put(`/tasks/${editingTask.value.id}`, {
        title: editingTask.value.title,
        description: editingTask.value.description,
        due_date: editingTask.value.due_date,
        status_id: editingTask.value.status_id,
        assigned_to: editingTask.value.assigned_to,
        effort_score: editingTask.value.effort_score,
        impact_score: editingTask.value.impact_score,
        dependency_map: editingTask.value.dependency_map,
        blocked_by: editingTask.value.blocked_by
      })
      
      editingTask.value = null
      fetchTasks()
      alert('Task updated successfully!')
    } catch (err) {
      console.error('Update failed', err)
      alert(err.response?.data?.error || 'Update failed')
    }
  }
  
  // Cancel editing
  const cancelEdit = () => {
    editingTask.value = null
  }
  
  // Delete task
  const deleteTask = async (id) => {
    if (!confirm('Delete this task?')) return
    
    try {
      await axios.delete(`/tasks/${id}`)
      fetchTasks()
      alert('Task deleted successfully!')
    } catch (err) {
      console.error('Delete failed', err)
      alert('Delete failed')
    }
  }
  
  // Format date
  const formatDate = (date) => {
    if (!date) return 'No due date'
    return new Date(date).toLocaleDateString()
  }
  
  // Smart Prioritization Functions
  const recalculatePriorities = async () => {
    recalculating.value = true
    try {
      await axios.post(`/tasks/priority/recalculate/${projectId}`)
      await fetchTasks()
      alert('Priorities recalculated successfully!')
    } catch (err) {
      console.error('Failed to recalculate priorities', err)
      alert('Failed to recalculate priorities')
    } finally {
      recalculating.value = false
    }
  }
  
  const fetchDependencyGraph = async () => {
    try {
      const res = await axios.get(`/tasks/dependencies/${projectId}`)
      dependencyGraph.value = res.data.dependency_graph
    } catch (err) {
      console.error('Failed to load dependency graph', err)
    }
  }
  
  const showPriorityInsights = async (task) => {
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
  
  // Helper functions
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
  
  const getEffortLabel = (effort) => {
    const labels = {
      1: '⚡ Very Easy',
      2: '🌟 Easy',
      3: '📊 Medium',
      4: '💪 Hard',
      5: '🔥 Very Hard'
    }
    return labels[effort] || '📊 Medium'
  }
  
  const getImpactLabel = (impact) => {
    const labels = {
      1: '📉 Low',
      2: '📈 Medium-Low',
      3: '🎯 Medium',
      4: '🚀 High',
      5: '💥 Critical'
    }
    return labels[impact] || '🎯 Medium'
  }
  
  const handleAiTaskCreated = () => {
    // Refresh tasks when AI creates a task
    fetchTasks()
  }
  
  const handleFillManualForm = (parsedTask) => {
    // Fill the manual form with AI-parsed data
    if (parsedTask) {
      newTask.value.title = parsedTask.title || ''
      newTask.value.description = parsedTask.description || ''
      newTask.value.due_date = parsedTask.due_date || ''
      newTask.value.assigned_to = parsedTask.assigned_to || null
      newTask.value.effort_score = parsedTask.effort_score || 3
      newTask.value.impact_score = parsedTask.impact_score || 3
      newTask.value.status_id = parsedTask.status_id || (customStatuses.value.find(s => s.is_default)?.id || '')
      
      // Scroll to manual form
      const taskForm = document.querySelector('.task-form')
      if (taskForm) {
        taskForm.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }
  
  onMounted(async () => {
    await fetchCustomStatuses()
    await fetchTasks()
    await fetchDependencyGraph()
  })
  </script>
  
  <style scoped>
  .project-tasks {
    padding: 2rem;
    font-family: Arial, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  /* Header Section */
  .header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .priority-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }
  
  .recalculate-btn, .dependency-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }
  
  .recalculate-btn:hover, .dependency-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  .recalculate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  .status-management-link {
    margin-bottom: 1rem;
  }
  
  .manage-status-btn {
    background: #8b5cf6;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .manage-status-btn:hover {
    background: #7c3aed;
  }
  
  .no-statuses-warning {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
  }
  
  .create-defaults-btn {
    background: #10b981;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 1rem;
  }
  
  .create-defaults-btn:hover {
    background: #059669;
  }
  
  /* Enhanced Task Form */
  .task-form {
    margin-bottom: 2rem;
    padding: 2rem;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }
  
  .form-row {
    display: grid;
    gap: 1rem;
    margin-bottom: 1rem;
    align-items: end;
  }
  
  .form-row:first-child {
    grid-template-columns: 2fr 2fr 1fr;
  }
  
  .form-row:nth-child(2) {
    grid-template-columns: 1.5fr 1fr 1fr 1fr auto;
  }
  
  .form-row:last-child {
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
  
  .dependency-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .dependency-section label {
    font-weight: 600;
    color: #475569;
    font-size: 0.875rem;
  }
  
  .dependency-select {
    min-height: 80px;
    resize: vertical;
  }
  
  .add-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
  }
  
  .add-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3) !important;
  }
  
  /* Control Section */
  .control-section {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }
  
  .filter-section, .sort-section {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    min-width: 200px;
  }
  
  .filter-section label, .sort-section label {
    font-weight: 600;
    color: #475569;
    white-space: nowrap;
  }
  
  .filter-section select, .sort-section select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
    min-width: 120px;
    transition: border-color 0.2s;
  }
  
  .filter-section select:focus, .sort-section select:focus {
    border-color: #6366f1;
    outline: none;
  }
  
  input, select, textarea, button {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #d1d5db;
    font-size: 0.875rem;
  }
  
  button {
    background-color: #3b82f6;
    color: white;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  button:hover {
    background-color: #2563eb;
  }
  
  .task-list {
    list-style: none;
    padding: 0;
    display: grid;
    gap: 1rem;
  }
  
  .task-list li {
    padding: 1.5rem;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s;
  }
  
  .task-list li:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
  }
  
  .blocked-task {
    border-left: 4px solid #f59e0b !important;
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
  }
  
  .task-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1rem;
    gap: 1rem;
  }
  
  .task-title-section {
    flex: 1;
  }
  
  .task-header strong {
    color: #1f2937;
    font-size: 1.1rem;
    display: block;
    margin-bottom: 0.5rem;
  }
  
  .task-badges {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .status-badge, .priority-badge, .priority-score-badge {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: bold;
    border-radius: 12px;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .priority-badge.priority-urgent {
    background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
    animation: pulse 2s infinite;
  }
  
  .priority-badge.priority-high {
    background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
  }
  
  .priority-badge.priority-medium {
    background: linear-gradient(135deg, #d97706 0%, #a16207 100%);
  }
  
  .priority-badge.priority-low {
    background: linear-gradient(135deg, #65a30d 0%, #4d7c0f 100%);
  }
  
  .priority-score-badge {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
  
  .task-indicators {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }
  
  .blocked-indicator, .blocking-indicator {
    font-size: 1.2rem;
    cursor: help;
  }
  
  .dependency-info {
    background: #f1f5f9;
    padding: 0.75rem;
    border-radius: 6px;
    margin: 0.75rem 0;
    font-size: 0.875rem;
    border-left: 3px solid #6366f1;
  }
  
  .depends-info, .blocked-info {
    color: #475569;
    margin: 0.25rem 0;
  }
  
  .badge {
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: bold;
    border-radius: 12px;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .task-description {
    display: block;
    color: #6b7280;
    margin-bottom: 0.75rem;
    line-height: 1.4;
  }
  
  .task-meta {
    color: #9ca3af;
    font-size: 0.875rem;
    margin-bottom: 1rem;
  }
  
  .task-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
  
  .edit-btn, .delete-btn, .insights-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    border-radius: 6px;
    transition: all 0.2s ease;
  }
  
  .insights-btn {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
  }
  
  .insights-btn:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
    transform: translateY(-1px);
  }
  
  .edit-btn {
    background: #f59e0b;
  }
  
  .edit-btn:hover {
    background: #d97706;
  }
  
  .delete-btn {
    background: #ef4444;
  }
  
  .delete-btn:hover {
    background: #dc2626;
  }
  
  .no-tasks {
    text-align: center;
    color: #6b7280;
    font-style: italic;
    padding: 2rem;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  /* Dependency Graph */
  .dependency-graph {
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #0ea5e9;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(14, 165, 233, 0.1);
  }
  
  .dependency-graph h3 {
    color: #0369a1;
    margin-bottom: 1.5rem;
  }
  
  .graph-container {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .dependency-node {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
  
  .node-task {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  
  .node-task strong {
    color: #1e293b;
  }
  
  .blocks-section, .depends-section {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0.25rem 0;
  }
  
  /* Modal Enhancements */
  .modal {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  }
  
  .edit-modal {
    max-width: 700px;
  }
  
  .insights-modal {
    max-width: 500px;
  }
  
  /* Priority Insights */
  .insights-content {
    margin: 1rem 0;
  }
  
  .score-breakdown h4 {
    color: #1e293b;
    margin-bottom: 1rem;
  }
  
  .score-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    margin: 0.5rem 0;
    background: #f8fafc;
    border-radius: 6px;
    border-left: 3px solid #6366f1;
  }
  
  .score-label {
    font-weight: 600;
    color: #475569;
  }
  
  .score-value {
    font-weight: bold;
    color: #1e293b;
  }
  
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
    border-radius: 6px;
    margin-top: 1rem;
  }
  
  .dependency-summary p {
    margin: 0.5rem 0;
    color: #475569;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
  }
  
  .form-group input,
  .form-group select,
  .form-group textarea {
    width: 100%;
  }
  
  .modal-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }
  
  .save-btn {
    background: #10b981;
    flex: 1;
  }
  
  .save-btn:hover {
    background: #059669;
  }
  
  .cancel-btn {
    background: #6b7280;
    flex: 1;
  }
  
  .cancel-btn:hover {
    background: #4b5563;
  }
  
  @media (max-width: 768px) {
    .header-section {
      flex-direction: column;
      align-items: stretch;
    }
    
    .priority-controls {
      justify-content: center;
    }
    
    .form-row {
      grid-template-columns: 1fr !important;
      gap: 0.75rem;
    }
    
    .control-section {
      flex-direction: column;
      gap: 1rem;
    }
    
    .filter-section, .sort-section {
      min-width: auto;
    }
    
    .task-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
    
    .task-badges {
      justify-content: flex-start;
    }
    
    .task-actions {
      justify-content: flex-start;
    }
    
    .graph-container {
      grid-template-columns: 1fr;
    }
    
    .score-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }
  }
  </style>
  