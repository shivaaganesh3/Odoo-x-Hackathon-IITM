<template>
  <div class="tasks">
    <h2>🗂 My Tasks</h2>

    <!-- 🔽 Filters -->
    <div class="filter">
      <label for="status">Status:</label>
      <select id="status" v-model="statusFilter">
        <option value="">All</option>
        <option value="To-Do">To-Do</option>
        <option value="In Progress">In Progress</option>
        <option value="Done">Done</option>
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
          <th>Due Date</th>
          <th>Project ID</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td>{{ task.title }}</td>
          <td>
            <span :class="getStatusClass(task.status)">
              {{ task.status }}
            </span>
          </td>
          <td>{{ formatDate(task.due_date) }}</td>
          <td>{{ task.project_id }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else>No tasks found for this filter.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { useRouter } from 'vue-router'

const tasks = ref([])
const statusFilter = ref('')
const dueDateFilter = ref('')
const router = useRouter()

const fetchTasks = async () => {
  try {
    let url = '/tasks/my'
    const params = new URLSearchParams()

    if (statusFilter.value) {
      params.append('status', statusFilter.value)
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

onMounted(fetchTasks)

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

const getStatusClass = (status) => {
  switch (status) {
    case 'To-Do':
      return 'badge todo'
    case 'In Progress':
      return 'badge progress'
    case 'Done':
      return 'badge done'
    default:
      return 'badge'
  }
}
</script>

<style scoped>
.tasks {
  padding: 2rem;
  font-family: Arial, sans-serif;
}

.filter {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

th, td {
  padding: 0.75rem;
  border: 1px solid #ccc;
  text-align: left;
}

th {
  background-color: #f0f0f0;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
}

.todo {
  background-color: #facc15; /* yellow */
  color: #000;
}

.progress {
  background-color: #3b82f6; /* blue */
}

.done {
  background-color: #22c55e; /* green */
}
</style>
