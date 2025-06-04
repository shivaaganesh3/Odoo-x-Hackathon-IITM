<template>
  <div class="projects">
    <h2>📁 My Projects</h2>

    <!-- 🔧 New Project Form -->
    <form @submit.prevent="createProject" class="project-form">
      <input v-model="newProject" placeholder="Enter project name" required />
      <input v-model="projectDescription" placeholder="Optional description" />
      <button type="submit">➕ Create Project</button>
    </form>

    <!-- 📃 Project List -->
    <ul v-if="projects.length > 0" class="project-list">
      <li v-for="project in projects" :key="project.id">
        <div class="project-info">
          <div v-if="editingProject === project.id">
            <input v-model="editName" placeholder="Edit name" />
            <input v-model="editDescription" placeholder="Edit description" />
            <button @click="saveProject">💾 Save</button>
            <button @click="cancelEdit">❌ Cancel</button>
          </div>
          <div v-else>
            <router-link :to="`/project/${project.id}/tasks`">
              <strong>{{ project.name }}</strong>
            </router-link>
            <small v-if="project.description" class="desc">{{ project.description }}</small>
          </div>
        </div>
        <div class="actions">
          <button @click="editProject(project)">✏️</button>
          <button @click="deleteProject(project.id)">🗑️</button>
        </div>
      </li>
    </ul>

    <p v-else>No projects created yet.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../axios'
import { useRouter } from 'vue-router'

const projects = ref([])
const newProject = ref('')
const projectDescription = ref('')
const editingProject = ref(null)
const editName = ref('')
const editDescription = ref('')
const router = useRouter()

// 🔁 Fetch projects for current user
const fetchProjects = async () => {
  try {
    const res = await axios.get('/projects')
    projects.value = res.data
  } catch (err) {
    console.error(err)
    if (err.response?.status === 401) {
      router.push('/login')
    }
  }
}

// ➕ Create new project
const createProject = async () => {
  try {
    await axios.post('/projects/', {
      name: newProject.value,
      description: projectDescription.value
    })
    newProject.value = ''
    projectDescription.value = ''
    fetchProjects()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create project')
  }
}

// ✏️ Start editing a project
const editProject = (project) => {
  editingProject.value = project.id
  editName.value = project.name
  editDescription.value = project.description || ''
}

// 💾 Save changes
const saveProject = async () => {
  try {
    await axios.put(`/projects/${editingProject.value}`, {
      name: editName.value,
      description: editDescription.value
    })
    editingProject.value = null
    fetchProjects()
  } catch (err) {
    alert('Failed to update project')
  }
}

// ❌ Cancel editing
const cancelEdit = () => {
  editingProject.value = null
}

// 🗑️ Delete project
const deleteProject = async (id) => {
  if (!confirm('Are you sure you want to delete this project?')) return
  try {
    await axios.delete(`/projects/${id}`)
    fetchProjects()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete project')
  }
}

onMounted(fetchProjects)
</script>

<style scoped>
.projects {
  padding: 2rem;
  font-family: Arial, sans-serif;
}

.project-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  max-width: 500px;
}

input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #3b82f6;
  color: white;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.25rem;
}

.project-list {
  list-style: none;
  padding: 0;
  max-width: 600px;
}

.project-list li {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem;
  background: #f3f4f6;
  margin-bottom: 0.5rem;
  border-radius: 4px;
}

.project-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.desc {
  color: #555;
  font-size: 0.9rem;
}
</style>
