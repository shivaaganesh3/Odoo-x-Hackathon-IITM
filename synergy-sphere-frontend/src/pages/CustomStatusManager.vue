<template>
  <div class="custom-status-manager">
    <div class="header">
      <h2>🎨 Manage Custom Statuses</h2>
      <p>Create and customize status categories for your projects</p>
    </div>

    <!-- Project Selection -->
    <div class="project-selector">
      <label for="project">Select Project:</label>
      <select id="project" v-model="selectedProjectId" @change="fetchStatuses">
        <option value="">-- Select a Project --</option>
        <option v-for="project in projects" :key="project.id" :value="project.id">
          {{ project.name }}
        </option>
      </select>
    </div>

    <div v-if="selectedProjectId">
      <!-- Add New Status Form -->
      <div class="add-status-form">
        <h3>➕ Add New Status</h3>
        <form @submit.prevent="createStatus" class="status-form">
          <div class="form-row">
            <input 
              v-model="newStatus.name" 
              placeholder="Status name (e.g., 'Review', 'Testing')" 
              required 
            />
            <input 
              v-model="newStatus.description" 
              placeholder="Description (optional)" 
            />
            <input 
              v-model="newStatus.color" 
              type="color" 
              title="Choose color"
            />
            <input 
              v-model.number="newStatus.position" 
              type="number" 
              placeholder="Position" 
              min="1"
            />
            <label class="checkbox-label">
              <input 
                v-model="newStatus.is_default" 
                type="checkbox"
              />
              Default for new tasks
            </label>
            <button type="submit" :disabled="!newStatus.name.trim()">
              ➕ Add Status
            </button>
          </div>
        </form>
      </div>

      <!-- Existing Statuses -->
      <div class="statuses-list">
        <h3>📋 Current Statuses</h3>
        
        <div v-if="statuses.length === 0" class="no-statuses">
          <p>No custom statuses found for this project.</p>
          <button @click="createDefaultStatuses" class="create-defaults-btn">
            🎯 Create Default Statuses (To-Do, In Progress, Done)
          </button>
        </div>

        <div v-else class="status-cards">
          <div 
            v-for="status in statuses" 
            :key="status.id" 
            class="status-card"
            :style="{ borderLeft: `5px solid ${status.color}` }"
          >
            <div class="status-header">
              <div class="status-info">
                <h4>{{ status.name }}</h4>
                <span class="task-count">{{ status.task_count }} tasks</span>
                <span v-if="status.is_default" class="default-badge">DEFAULT</span>
              </div>
              <div class="status-actions">
                <button @click="editStatus(status)" class="edit-btn">✏️ Edit</button>
                <button 
                  @click="deleteStatus(status.id)" 
                  class="delete-btn"
                  :disabled="status.task_count > 0"
                  :title="status.task_count > 0 ? 'Cannot delete: status has tasks' : 'Delete status'"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
            <p v-if="status.description" class="status-description">
              {{ status.description }}
            </p>
            <div class="status-meta">
              <span>Position: {{ status.position }}</span>
              <span class="color-preview" :style="{ backgroundColor: status.color }"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="editingStatus" class="modal-overlay" @click="cancelEdit">
        <div class="modal" @click.stop>
          <h3>✏️ Edit Status</h3>
          <form @submit.prevent="updateStatus">
            <div class="form-group">
              <label>Status Name:</label>
              <input v-model="editingStatus.name" required />
            </div>
            <div class="form-group">
              <label>Description:</label>
              <input v-model="editingStatus.description" />
            </div>
            <div class="form-group">
              <label>Color:</label>
              <input v-model="editingStatus.color" type="color" />
            </div>
            <div class="form-group">
              <label>Position:</label>
              <input v-model.number="editingStatus.position" type="number" min="1" />
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="editingStatus.is_default" type="checkbox" />
                Set as default for new tasks
              </label>
            </div>
            <div class="modal-actions">
              <button type="submit" class="save-btn">✅ Save Changes</button>
              <button type="button" @click="cancelEdit" class="cancel-btn">❌ Cancel</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const projects = ref([])
const selectedProjectId = ref('')
const statuses = ref([])
const editingStatus = ref(null)

const newStatus = ref({
  name: '',
  description: '',
  color: '#6B7280',
  position: 1,
  is_default: false
})

// Fetch user's projects
const fetchProjects = async () => {
  try {
    const res = await axios.get('/projects/')
    projects.value = res.data
  } catch (err) {
    console.error('Error fetching projects:', err)
    if (err.response?.status === 401) {
      router.push('/login')
    }
  }
}

// Fetch statuses for selected project
const fetchStatuses = async () => {
  if (!selectedProjectId.value) {
    statuses.value = []
    return
  }

  try {
    const res = await axios.get(`/custom-status/project/${selectedProjectId.value}`)
    statuses.value = res.data
  } catch (err) {
    console.error('Error fetching statuses:', err)
  }
}

// Create new status
const createStatus = async () => {
  try {
    await axios.post('/custom-status/', {
      ...newStatus.value,
      project_id: selectedProjectId.value
    })
    
    // Reset form
    newStatus.value = {
      name: '',
      description: '',
      color: '#6B7280',
      position: statuses.value.length + 1,
      is_default: false
    }
    
    // Refresh statuses
    await fetchStatuses()
    
    alert('Status created successfully!')
  } catch (err) {
    console.error('Error creating status:', err)
    alert(err.response?.data?.error || 'Failed to create status')
  }
}

// Create default statuses
const createDefaultStatuses = async () => {
  try {
    await axios.post(`/custom-status/create-defaults/${selectedProjectId.value}`)
    await fetchStatuses()
    alert('Default statuses created successfully!')
  } catch (err) {
    console.error('Error creating default statuses:', err)
    alert(err.response?.data?.error || 'Failed to create default statuses')
  }
}

// Edit status
const editStatus = (status) => {
  editingStatus.value = { ...status }
}

// Update status
const updateStatus = async () => {
  try {
    await axios.put(`/custom-status/${editingStatus.value.id}`, editingStatus.value)
    editingStatus.value = null
    await fetchStatuses()
    alert('Status updated successfully!')
  } catch (err) {
    console.error('Error updating status:', err)
    alert(err.response?.data?.error || 'Failed to update status')
  }
}

// Cancel edit
const cancelEdit = () => {
  editingStatus.value = null
}

// Delete status
const deleteStatus = async (statusId) => {
  if (!confirm('Are you sure you want to delete this status?')) return

  try {
    await axios.delete(`/custom-status/${statusId}`)
    await fetchStatuses()
    alert('Status deleted successfully!')
  } catch (err) {
    console.error('Error deleting status:', err)
    alert(err.response?.data?.error || 'Failed to delete status')
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.custom-status-manager {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h2 {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.header p {
  color: #6b7280;
}

.project-selector {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.project-selector select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.add-status-form {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.form-row input[type="text"], 
.form-row input[type="number"] {
  flex: 1;
  min-width: 150px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
}

.form-row input[type="color"] {
  width: 50px;
  height: 40px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.form-row button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.form-row button:hover {
  background: #2563eb;
}

.form-row button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.statuses-list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.no-statuses {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
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

.status-cards {
  display: grid;
  gap: 1rem;
  margin-top: 1rem;
}

.status-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 1rem;
  position: relative;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.status-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1f2937;
}

.task-count {
  background: #e5e7eb;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.default-badge {
  background: #fbbf24;
  color: #92400e;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
}

.status-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .delete-btn {
  background: none;
  border: 1px solid #d1d5db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.edit-btn:hover {
  background: #f3f4f6;
}

.delete-btn:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #fca5a5;
}

.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-description {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0.5rem 0;
}

.status-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #d1d5db;
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
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.save-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
}

.save-btn:hover {
  background: #059669;
}

.cancel-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  flex: 1;
}

.cancel-btn:hover {
  background: #4b5563;
}
</style> 