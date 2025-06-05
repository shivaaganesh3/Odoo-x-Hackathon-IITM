<template>
  <AppLayout>
    <div class="project-detail-page">
      <!-- Project Header -->
      <div v-if="project" class="project-header">
        <div class="header-content">
          <h1 class="project-title">{{ project.name }}</h1>
          <div class="project-meta">
            <span class="owner-info">
              👤 Owner: {{ project.owner?.name || 'Unknown' }}
            </span>
            <span class="created-date">
              📅 Created: {{ formatDate(project.created_at) }}
            </span>
            <span class="team-count">
              👥 {{ project.team_members?.length || 0 }} team members
            </span>
          </div>
        </div>
        <div v-if="project.is_owner" class="admin-actions">
          <router-link :to="`/custom-status`" class="manage-status-btn">
            🎨 Manage Statuses
          </router-link>
        </div>
      </div>

      <!-- Project Description -->
      <div v-if="project?.description" class="project-description card">
        <h3>📋 Description</h3>
        <p>{{ project.description }}</p>
      </div>

      <!-- Team Members Section -->
      <div v-if="project" class="team-members-section card">
        <h3>👥 Team Members</h3>
        <div class="team-grid">
          <div v-for="member in project.team_members" :key="member.id" class="team-member">
            <div class="member-avatar">{{ member.name?.[0] || '?' }}</div>
            <div class="member-info">
              <div class="member-name">{{ member.name }}</div>
              <div class="member-email">{{ member.email }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks Section -->
      <div class="tasks-section card">
        <div class="section-header">
          <h3>📝 Tasks</h3>
          <button 
            v-if="canManageTasks" 
            @click="showAddTaskModal = true" 
            class="add-task-btn"
          >
            ➕ Add Task
          </button>
        </div>

        <!-- Status Management Warning -->
        <div v-if="customStatuses.length === 0" class="no-statuses-warning">
          <p>⚠️ No custom statuses found for this project.</p>
          <button 
            v-if="project?.is_owner" 
            @click="createDefaultStatuses" 
            class="create-defaults-btn"
          >
            🎯 Create Default Statuses
          </button>
        </div>

        <!-- Task Filters -->
        <div v-if="customStatuses.length > 0" class="task-filters">
          <div class="filter-group">
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
          <div class="filter-group">
            <label>Filter by Assignee:</label>
            <select v-model="assigneeFilter" @change="fetchTasks">
              <option value="">All Assignees</option>
              <option value="unassigned">Unassigned</option>
              <option 
                v-for="member in project?.team_members" 
                :key="member.id" 
                :value="member.id"
              >
                {{ member.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Task List -->
        <div v-if="tasks.length > 0" class="task-list">
          <div v-for="task in tasks" :key="task.id" class="task-card">
            <div class="task-header">
              <h4 class="task-title">{{ task.title }}</h4>
              <div class="task-actions">
                <button 
                  v-if="canManageTasks" 
                  @click="startEdit(task)" 
                  class="edit-btn"
                >
                  ✏️
                </button>
                <button 
                  v-if="canManageTasks" 
                  @click="deleteTask(task.id)" 
                  class="delete-btn"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            <div class="task-meta">
              <span 
                class="status-badge" 
                :style="{ backgroundColor: task.status?.color || '#6B7280' }"
              >
                {{ task.status?.name || 'No Status' }}
              </span>
              <span class="priority-badge" :class="`priority-${task.priority?.toLowerCase()}`">
                🎯 {{ task.priority || 'Medium' }}
              </span>
            </div>

            <p v-if="task.description" class="task-description">{{ task.description }}</p>

            <div class="task-details">
              <div class="detail-item">
                📅 Due: {{ formatDate(task.due_date) || 'No due date' }}
              </div>
              <div class="detail-item">
                👤 Assigned: {{ task.assignee_name || 'Unassigned' }}
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="customStatuses.length > 0" class="no-tasks">
          <p>No tasks found.</p>
        </div>
      </div>

      <!-- Add Task Modal -->
      <div v-if="showAddTaskModal" class="modal-overlay" @click="closeAddTaskModal">
        <div class="modal" @click.stop>
          <h3>➕ Add New Task</h3>
          <form @submit.prevent="createTask">
            <div class="form-group">
              <label>Title *</label>
              <input v-model="newTask.title" required placeholder="Enter task title" />
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="newTask.description" 
                rows="3" 
                placeholder="Enter task description"
              ></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Status *</label>
                <select v-model="newTask.status_id" required>
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
              
              <div class="form-group">
                <label>Due Date</label>
                <input v-model="newTask.due_date" type="date" />
              </div>
            </div>
            
            <div class="form-group">
              <label>Assign to Team Member</label>
              <select v-model="newTask.assigned_to">
                <option value="">Leave Unassigned</option>
                <option 
                  v-for="member in project?.team_members" 
                  :key="member.id" 
                  :value="member.id"
                >
                  {{ member.name }} ({{ member.email }})
                </option>
              </select>
            </div>
            
            <div class="modal-actions">
              <button type="submit" class="save-btn">✅ Create Task</button>
              <button type="button" @click="closeAddTaskModal" class="cancel-btn">❌ Cancel</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Edit Task Modal -->
      <div v-if="editingTask" class="modal-overlay" @click="cancelEdit">
        <div class="modal" @click.stop>
          <h3>✏️ Edit Task</h3>
          <form @submit.prevent="updateTask">
            <div class="form-group">
              <label>Title *</label>
              <input v-model="editingTask.title" required />
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editingTask.description" rows="3"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Status *</label>
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
                <label>Due Date</label>
                <input v-model="editingTask.due_date" type="date" />
              </div>
            </div>
            
            <div class="form-group">
              <label>Assign to Team Member</label>
              <select v-model="editingTask.assigned_to">
                <option value="">Leave Unassigned</option>
                <option 
                  v-for="member in project?.team_members" 
                  :key="member.id" 
                  :value="member.id"
                >
                  {{ member.name }} ({{ member.email }})
                </option>
              </select>
            </div>
            
            <div class="modal-actions">
              <button type="submit" class="save-btn">✅ Save Changes</button>
              <button type="button" @click="cancelEdit" class="cancel-btn">❌ Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import { useAuthStore } from '../store/auth'
import axios from '../axios'

export default {
  name: 'ProjectDetailPage',
  components: {
    AppLayout,
  },
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()
    const projectId = route.params.id
    
    const project = ref(null)
    const tasks = ref([])
    const customStatuses = ref([])
    const statusFilter = ref('')
    const assigneeFilter = ref('')
    const showAddTaskModal = ref(false)
    const editingTask = ref(null)
    const loading = ref(true)
    const error = ref('')
    
    const newTask = ref({
      title: '',
      description: '',
      due_date: '',
      status_id: '',
      assigned_to: ''
    })

    const canManageTasks = computed(() => {
      return project.value && project.value.team_members?.some(
        member => member.id === authStore.user?.id
      )
    })

    const formatDate = (dateString) => {
      if (!dateString) return null
      return new Date(dateString).toLocaleDateString()
    }

    const fetchProjectDetails = async () => {
      try {
        const response = await axios.get(`/projects/${projectId}`)
        project.value = response.data
      } catch (err) {
        console.error('Failed to fetch project details:', err)
        error.value = 'Failed to load project details'
      }
    }

    const fetchCustomStatuses = async () => {
      try {
        const response = await axios.get(`/custom-status/project/${projectId}`)
        customStatuses.value = response.data
        
        // Set default status for new task
        const defaultStatus = customStatuses.value.find(s => s.is_default)
        if (defaultStatus) {
          newTask.value.status_id = defaultStatus.id
        }
      } catch (err) {
        console.error('Failed to load custom statuses:', err)
      }
    }

    const fetchTasks = async () => {
      try {
        let url = `/tasks/project/${projectId}`
        const params = new URLSearchParams()
        
        if (statusFilter.value) {
          params.append('status_id', statusFilter.value)
        }
        if (assigneeFilter.value) {
          if (assigneeFilter.value === 'unassigned') {
            params.append('assigned_to', '0')
          } else {
            params.append('assigned_to', assigneeFilter.value)
          }
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`
        }
        
        const response = await axios.get(url)
        tasks.value = response.data
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const createDefaultStatuses = async () => {
      try {
        await axios.post(`/custom-status/create-defaults/${projectId}`)
        await fetchCustomStatuses()
        alert('Default statuses created successfully!')
      } catch (err) {
        console.error('Failed to create default statuses:', err)
        alert('Failed to create default statuses')
      }
    }

    const createTask = async () => {
      if (!newTask.value.status_id) {
        alert('Please select a status')
        return
      }

      try {
        await axios.post('/tasks/', {
          ...newTask.value,
          project_id: parseInt(projectId)
        })
        
        // Reset form
        newTask.value = {
          title: '',
          description: '',
          due_date: '',
          status_id: customStatuses.value.find(s => s.is_default)?.id || '',
          assigned_to: ''
        }
        
        showAddTaskModal.value = false
        await fetchTasks()
        alert('Task created successfully!')
      } catch (err) {
        console.error('Failed to create task:', err)
        alert(err.response?.data?.error || 'Failed to create task')
      }
    }

    const startEdit = (task) => {
      editingTask.value = {
        ...task,
        status_id: task.status?.id || ''
      }
    }

    const updateTask = async () => {
      try {
        await axios.put(`/tasks/${editingTask.value.id}`, editingTask.value)
        editingTask.value = null
        await fetchTasks()
        alert('Task updated successfully!')
      } catch (err) {
        console.error('Failed to update task:', err)
        alert(err.response?.data?.error || 'Failed to update task')
      }
    }

    const deleteTask = async (taskId) => {
      if (!confirm('Are you sure you want to delete this task?')) return

      try {
        await axios.delete(`/tasks/${taskId}`)
        await fetchTasks()
        alert('Task deleted successfully!')
      } catch (err) {
        console.error('Failed to delete task:', err)
        alert('Failed to delete task')
      }
    }

    const closeAddTaskModal = () => {
      showAddTaskModal.value = false
      newTask.value = {
        title: '',
        description: '',
        due_date: '',
        status_id: customStatuses.value.find(s => s.is_default)?.id || '',
        assigned_to: ''
      }
    }

    const cancelEdit = () => {
      editingTask.value = null
    }

    onMounted(async () => {
      loading.value = true
      try {
        // Ensure user is loaded
        if (!authStore.user) {
          try {
            await authStore.fetchUser()
          } catch (err) {
            console.log('User not authenticated')
          }
        }
        
        await Promise.all([
          fetchProjectDetails(),
          fetchCustomStatuses(),
          fetchTasks()
        ])
      } finally {
        loading.value = false
      }
    })

    return {
      project,
      tasks,
      customStatuses,
      statusFilter,
      assigneeFilter,
      showAddTaskModal,
      editingTask,
      loading,
      error,
      newTask,
      canManageTasks,
      formatDate,
      fetchTasks,
      createDefaultStatuses,
      createTask,
      startEdit,
      updateTask,
      deleteTask,
      closeAddTaskModal,
      cancelEdit
    }
  }
}
</script>

<style scoped>
.project-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  space-y: 24px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.project-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.project-meta {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  color: #6b7280;
  font-size: 0.9rem;
}

.admin-actions {
  display: flex;
  gap: 12px;
}

.manage-status-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: transform 0.2s;
}

.manage-status-btn:hover {
  transform: translateY(-2px);
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.project-description h3 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 1.1rem;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  text-transform: uppercase;
}

.member-name {
  font-weight: 500;
  color: #1f2937;
}

.member-email {
  font-size: 0.85rem;
  color: #6b7280;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #374151;
  font-size: 1.25rem;
}

.add-task-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.add-task-btn:hover {
  background: #059669;
}

.no-statuses-warning {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.create-defaults-btn {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 8px;
}

.task-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
}

.task-list {
  display: grid;
  gap: 16px;
}

.task-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.task-title {
  margin: 0;
  color: #1f2937;
  font-size: 1.1rem;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: #e5e7eb;
}

.delete-btn:hover {
  background: #fee2e2;
}

.task-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.status-badge {
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.priority-urgent {
  background: #fee2e2;
  color: #dc2626;
}

.priority-high {
  background: #fed7aa;
  color: #ea580c;
}

.priority-medium {
  background: #fef3c7;
  color: #d97706;
}

.priority-low {
  background: #dcfce7;
  color: #16a34a;
}

.task-description {
  color: #6b7280;
  margin: 12px 0;
  line-height: 1.5;
}

.task-details {
  display: flex;
  gap: 20px;
  font-size: 0.875rem;
  color: #6b7280;
  flex-wrap: wrap;
}

.no-tasks {
  text-align: center;
  color: #6b7280;
  padding: 40px 20px;
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

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin: 0 0 20px 0;
  color: #1f2937;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.save-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.save-btn:hover {
  background: #059669;
}

.cancel-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn:hover {
  background: #4b5563;
}

@media (max-width: 768px) {
  .project-header {
    flex-direction: column;
    gap: 16px;
  }

  .project-meta {
    flex-direction: column;
    gap: 8px;
  }

  .task-filters {
    flex-direction: column;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal {
    width: 95%;
    margin: 20px;
  }
}
</style> 