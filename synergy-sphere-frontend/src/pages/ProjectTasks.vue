<template>
    <div class="project-tasks">
      <h2>📋 Tasks for Project ID: {{ projectId }}</h2>
  
      <!-- ➕ Add New Task -->
      <form @submit.prevent="createTask" class="task-form">
        <input v-model="newTask.title" placeholder="Task title" required />
        <input v-model="newTask.description" placeholder="Description" />
        <input v-model="newTask.due_date" type="date" />
        <select v-model="newTask.status">
          <option value="To-Do">To-Do</option>
          <option value="In Progress">In Progress</option>
          <option value="Done">Done</option>
        </select>
        <input v-model="newTask.assigned_to" type="number" placeholder="User ID" />
        <button type="submit">➕ Add</button>
      </form>
  
      <!-- 📝 Task List -->
      <ul v-if="tasks.length" class="task-list">
        <li v-for="task in tasks" :key="task.id" class="task-item">
          <div class="task-header">
            <strong>{{ task.title }}</strong>
            <span :class="getStatusClass(task.status)" class="badge">{{ task.status }}</span>
          </div>
          <div class="task-body">
            <small>{{ task.description }}</small><br />
            �� Due: {{ formatDate(task.due_date) }} |
            👤 Assigned to: {{ getUserName(task.assigned_to) }}<br />
  
            <div class="task-actions">
              <button @click="startEdit(task)">✏️ Edit</button>
              <button @click="deleteTask(task.id)">🗑️ Delete</button>
            </div>
          </div>
          
          <!-- Comments Section -->
          <TaskComments :taskId="task.id" />
        </li>
      </ul>
  
      <p v-else>No tasks yet.</p>
  
      <!-- ✏️ Edit Form (optional inline) -->
      <div v-if="editingTask" class="edit-box">
        <h3>✏️ Edit Task</h3>
        <form @submit.prevent="updateTask">
          <input v-model="editingTask.title" required />
          <input v-model="editingTask.description" />
          <input v-model="editingTask.due_date" type="date" />
          <select v-model="editingTask.status">
            <option value="To-Do">To-Do</option>
            <option value="In Progress">In Progress</option>
            <option value="Done">Done</option>
          </select>
          <input v-model="editingTask.assigned_to" type="number" />
          <button type="submit">✅ Save</button>
          <button @click="cancelEdit" type="button">❌ Cancel</button>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import axios from '../axios'
  import TaskComments from '../components/TaskComments.vue'
  
  const route = useRoute()
  const projectId = route.params.id
  
  const tasks = ref([])
  const newTask = ref({
    title: '',
    description: '',
    due_date: '',
    status: 'To-Do',
    assigned_to: null
  })
  const editingTask = ref(null)
  
  // 🔁 Load tasks
  const fetchTasks = async () => {
    try {
      const res = await axios.get(`/tasks/project/${projectId}`)
      tasks.value = res.data
    } catch (err) {
      console.error('Failed to load tasks', err)
    }
  }
  
  // ➕ Create task
  const createTask = async () => {
    try {
      await axios.post('/tasks/', {
        ...newTask.value,
        project_id: projectId
      })
      newTask.value = {
        title: '',
        description: '',
        due_date: '',
        status: 'To-Do',
        assigned_to: null
      }
      fetchTasks()
    } catch (err) {
      alert('Failed to create task')
    }
  }
  
  // ✏️ Start editing
  const startEdit = (task) => {
    editingTask.value = { ...task }
  }
  
  // ✅ Save update
  const updateTask = async () => {
    try {
      await axios.put(`/tasks/${editingTask.value.id}`, editingTask.value)
      editingTask.value = null
      fetchTasks()
    } catch (err) {
      alert('Update failed')
    }
  }
  
  // ❌ Cancel editing
  const cancelEdit = () => {
    editingTask.value = null
  }
  
  // 🗑️ Delete task
  const deleteTask = async (id) => {
    if (!confirm('Delete this task?')) return
    try {
      await axios.delete(`/tasks/${id}`)
      fetchTasks()
    } catch (err) {
      alert('Delete failed')
    }
  }
  
  // Format date
  const formatDate = (date) => date ? new Date(date).toLocaleDateString() : '-'
  
  // Badge styles
  const getStatusClass = (status) => {
    switch (status) {
      case 'To-Do': return 'todo'
      case 'In Progress': return 'progress'
      case 'Done': return 'done'
      default: return ''
    }
  }
  
  // Placeholder for user names
  const getUserName = (id) => {
    if (!id) return 'Unassigned'
    return `User #${id}` // Replace with real names if needed
  }
  
  onMounted(fetchTasks)
  </script>
  
  <style scoped>
  .project-tasks {
    padding: 2rem;
    font-family: Arial, sans-serif;
  }
  .task-form, .edit-box form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    max-width: 500px;
  }
  input, select, button {
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ccc;
  }
  button {
    background-color: #10b981;
    color: white;
    border: none;
    cursor: pointer;
  }
  .task-list {
    list-style: none;
    padding: 0;
    max-width: 800px;
  }
  .task-item {
    padding: 1rem;
    background: #f3f4f6;
    margin-bottom: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  .task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  .task-body {
    margin-bottom: 1rem;
  }
  .task-actions {
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
  }
  .badge {
    padding: 2px 6px;
    font-size: 0.8rem;
    font-weight: bold;
    border-radius: 3px;
    color: white;
  }
  .todo { background: #facc15; color: black; }
  .progress { background: #3b82f6; }
  .done { background: #22c55e; }
  </style>
  