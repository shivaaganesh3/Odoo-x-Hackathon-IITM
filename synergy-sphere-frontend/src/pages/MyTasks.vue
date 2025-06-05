<template>
  <div class="tasks">
    <h2>🗂 My Tasks</h2>

    <!-- 🔽 Filters -->
    <div class="filter">
      <label for="status">Status:</label>
      <select id="status" v-model="statusFilter">
        <option value="">All Statuses</option>
        <option 
          v-for="status in availableStatuses" 
          :key="status.id" 
          :value="status.id"
        >
          {{ status.name }}
        </option>
      </select>

      <label for="due">Due Date:</label>
      <input id="due" type="date" v-model="dueDateFilter" />

      <button @click="fetchTasks">🔍 Apply Filters</button>
    </div>

    <!-- Task Table -->
    <table v-if="tasks.length > 0">
      <thead>
        <tr>
          <th>Title</th>
          <th>Status</th>
          <th>Priority</th>
          <th>Due Date</th>
          <th>Project</th>
          <th>Deadline Warning</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td>
            <strong>{{ task.title }}</strong>
            <br>
            <small class="task-description">{{ task.description }}</small>
          </td>
          <td>
            <span 
              class="badge" 
              :style="{ backgroundColor: task.status?.color || '#6B7280' }"
            >
              {{ task.status?.name || 'No Status' }}
            </span>
          </td>
          <td>
            <span :class="getPriorityClass(task.priority)">
              {{ task.priority || 'Medium' }}
            </span>
          </td>
          <td>{{ formatDate(task.due_date) }}</td>
          <td>
            <span class="project-name">{{ task.project_name }}</span>
          </td>
          <td>
            <TaskDeadlineWarning 
              v-if="task.due_date" 
              :task-id="task.id" 
              class="task-deadline-warning"
            />
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="no-tasks">No tasks found for the selected filters.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { useRouter } from 'vue-router'
import TaskDeadlineWarning from '../components/TaskDeadlineWarning.vue'

const tasks = ref([])
const availableStatuses = ref([])
const statusFilter = ref('')
const dueDateFilter = ref('')
const router = useRouter()

// Fetch all unique statuses from user's tasks
const fetchAvailableStatuses = async () => {
  try {
    // Get all tasks first to extract unique statuses
    const res = await axios.get('/tasks/my')
    const allTasks = res.data
    
    // Extract unique statuses
    const statusMap = new Map()
    allTasks.forEach(task => {
      if (task.status && task.status.id) {
        statusMap.set(task.status.id, task.status)
      }
    })
    
    availableStatuses.value = Array.from(statusMap.values())
  } catch (err) {
    console.error('Error fetching available statuses:', err)
  }
}

const fetchTasks = async () => {
  try {
    let url = '/tasks/my'
    const params = new URLSearchParams()

    if (statusFilter.value) {
      params.append('status_id', statusFilter.value)
    }
    if (dueDateFilter.value) {
      params.append('due_date', dueDateFilter.value)
    }

    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const res = await axios.get(url)
    tasks.value = res.data
  } catch (err) {
    console.error(err)
    if (err.response?.status === 401) {
      router.push('/login')
    }
  }
}

onMounted(async () => {
  await fetchAvailableStatuses()
  await fetchTasks()
})

const formatDate = (date) => {
  if (!date) return 'No due date'
  return new Date(date).toLocaleDateString()
}

const getPriorityClass = (priority) => {
  switch (priority) {
    case 'Urgent':
      return 'priority urgent'
    case 'High':
      return 'priority high'
    case 'Medium':
      return 'priority medium'
    case 'Low':
      return 'priority low'
    default:
      return 'priority medium'
  }
}
</script>

<style scoped>
.tasks {
  padding: 2rem;
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

.filter {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter label {
  font-weight: 500;
  color: #374151;
}

.filter select,
.filter input {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.875rem;
}

.filter button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.filter button:hover {
  background: #2563eb;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

th, td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: top;
}

th {
  background-color: #f9fafb;
  font-weight: 600;
  color: #374151;
}

.task-description {
  color: #6b7280;
  font-style: italic;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  display: inline-block;
}

.priority {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority.urgent {
  background: #fee2e2;
  color: #dc2626;
}

.priority.high {
  background: #fef3c7;
  color: #d97706;
}

.priority.medium {
  background: #dbeafe;
  color: #2563eb;
}

.priority.low {
  background: #d1fae5;
  color: #059669;
}

.project-name {
  color: #6b7280;
  font-size: 0.875rem;
}

.no-tasks {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  table, thead, tbody, th, td, tr {
    display: block;
  }
  
  thead tr {
    position: absolute;
    top: -9999px;
    left: -9999px;
  }
  
  tr {
    border: 1px solid #e5e7eb;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    padding: 0.5rem;
  }
  
  td {
    border: none;
    border-bottom: 1px solid #e5e7eb;
    position: relative;
    padding-left: 30%;
  }
  
  td:before {
    content: attr(data-label);
    position: absolute;
    left: 6px;
    width: 25%;
    padding-right: 10px;
    white-space: nowrap;
    font-weight: bold;
  }
}
</style>
