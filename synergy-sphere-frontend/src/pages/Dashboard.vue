<template>
  <div class="dashboard">
    <nav class="navbar">
      <h2>SynergySphere</h2>
      <div class="links">
        <router-link to="/my-tasks">🗂 My Tasks</router-link>
        <router-link to="/projects">📁 Projects</router-link>
        <button @click="logout">🚪 Logout</button>
      </div>
    </nav>

    <main class="content">
      <h1>Welcome, {{ auth.user?.name || 'User' }} 👋</h1>
      <p>This is your dashboard. Use the navigation above to manage your work.</p>

      <!-- Optional summary section -->
      <div class="summary">
        <div class="card">
          <h3>Total Projects</h3>
          <p>{{ totalProjects ?? '-' }}</p>
        </div>
        <div class="card">
          <h3>My Tasks</h3>
          <p>{{ totalTasks ?? '-' }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from '../axios'

const auth = useAuthStore()
const router = useRouter()

const totalProjects = ref(null)
const totalTasks = ref(null)

onMounted(async () => {
  try {
    await auth.fetchUser()

    // Optional: Fetch totals
    const taskRes = await axios.get('/tasks/my')
    totalTasks.value = taskRes.data.length

    const projRes = await axios.get('/projects')
    totalProjects.value = projRes.data.length
  } catch (err) {
    console.error(err)
    router.push('/login')
  }
})

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  font-family: Arial, sans-serif;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #3b82f6;
  padding: 1rem;
  color: white;
}

.navbar h2 {
  margin: 0;
}

.links {
  display: flex;
  gap: 1rem;
}

.links a,
.links button {
  background: none;
  border: none;
  color: white;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
}

.content {
  padding: 2rem;
}

.summary {
  display: flex;
  gap: 2rem;
  margin-top: 2rem;
}

.card {
  background: #f0f4ff;
  padding: 1rem 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
</style>
