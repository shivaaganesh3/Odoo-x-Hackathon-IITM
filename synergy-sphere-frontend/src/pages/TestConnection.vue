<template>
  <div class="test-connection">
    <h2>🔧 Connection Test</h2>
    
    <div class="test-section">
      <h3>Backend Connection Test</h3>
      <button @click="testBackend" :disabled="testing">
        {{ testing ? 'Testing...' : '🧪 Test Backend' }}
      </button>
      <div v-if="backendResult" class="result" :class="backendResult.success ? 'success' : 'error'">
        {{ backendResult.message }}
      </div>
    </div>

    <div class="test-section">
      <h3>Authentication Test</h3>
      <div class="auth-form">
        <input v-model="testEmail" placeholder="Email (try: abc@gmail.com)" />
        <input v-model="testPassword" type="password" placeholder="Password (try: test123)" />
        <button @click="testLogin" :disabled="testing">
          {{ testing ? 'Testing...' : '🔐 Test Login' }}
        </button>
      </div>
      <div v-if="authResult" class="result" :class="authResult.success ? 'success' : 'error'">
        {{ authResult.message }}
      </div>
    </div>

    <div class="test-section">
      <h3>Projects API Test</h3>
      <button @click="testProjects" :disabled="testing || !isLoggedIn">
        {{ testing ? 'Testing...' : '📋 Test Projects API' }}
      </button>
      <div v-if="projectsResult" class="result" :class="projectsResult.success ? 'success' : 'error'">
        {{ projectsResult.message }}
      </div>
    </div>

    <div class="test-section">
      <h3>Custom Status API Test</h3>
      <button @click="testCustomStatus" :disabled="testing || !isLoggedIn">
        {{ testing ? 'Testing...' : '🎨 Test Custom Status API' }}
      </button>
      <div v-if="statusResult" class="result" :class="statusResult.success ? 'success' : 'error'">
        {{ statusResult.message }}
      </div>
    </div>

    <div v-if="isLoggedIn" class="user-info">
      <h3>✅ Logged in as: {{ currentUser?.name || 'Unknown' }}</h3>
      <button @click="logout" class="logout-btn">🚪 Logout</button>
    </div>

    <div class="navigation">
      <router-link to="/projects/create" class="nav-btn">
        📝 Go to Create Project
      </router-link>
      <router-link to="/custom-status" class="nav-btn">
        🎨 Go to Custom Status Manager
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '../axios'

const testing = ref(false)
const backendResult = ref(null)
const authResult = ref(null)
const projectsResult = ref(null)
const statusResult = ref(null)
const isLoggedIn = ref(false)
const currentUser = ref(null)

const testEmail = ref('abc@gmail.com')
const testPassword = ref('test123')

const testBackend = async () => {
  testing.value = true
  try {
    const response = await axios.get('/auth/debug/users')
    backendResult.value = {
      success: true,
      message: `✅ Backend connected! Found ${response.data.total_users} users.`
    }
  } catch (error) {
    backendResult.value = {
      success: false,
      message: `❌ Backend connection failed: ${error.message}`
    }
  } finally {
    testing.value = false
  }
}

const testLogin = async () => {
  if (!testEmail.value || !testPassword.value) {
    authResult.value = {
      success: false,
      message: '❌ Please enter email and password'
    }
    return
  }

  testing.value = true
  try {
    const response = await axios.post('/auth/login', {
      email: testEmail.value,
      password: testPassword.value
    })
    
    authResult.value = {
      success: true,
      message: `✅ Login successful! Welcome ${response.data.user.name}`
    }
    isLoggedIn.value = true
    currentUser.value = response.data.user
  } catch (error) {
    authResult.value = {
      success: false,
      message: `❌ Login failed: ${error.response?.data?.error || error.message}`
    }
  } finally {
    testing.value = false
  }
}

const testProjects = async () => {
  testing.value = true
  try {
    const response = await axios.get('/projects/')
    projectsResult.value = {
      success: true,
      message: `✅ Projects API working! Found ${response.data.length} projects.`
    }
  } catch (error) {
    projectsResult.value = {
      success: false,
      message: `❌ Projects API failed: ${error.response?.data?.error || error.message}`
    }
  } finally {
    testing.value = false
  }
}

const testCustomStatus = async () => {
  testing.value = true
  try {
    const response = await axios.get('/custom-status/project/1')
    statusResult.value = {
      success: true,
      message: `✅ Custom Status API working! Found ${response.data.length} statuses.`
    }
  } catch (error) {
    statusResult.value = {
      success: false,
      message: `❌ Custom Status API failed: ${error.response?.data?.error || error.message}`
    }
  } finally {
    testing.value = false
  }
}

const logout = async () => {
  try {
    await axios.post('/auth/logout')
    isLoggedIn.value = false
    currentUser.value = null
    authResult.value = { success: true, message: '✅ Logged out successfully' }
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>

<style scoped>
.test-connection {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

.test-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
}

.test-section h3 {
  margin-top: 0;
  color: #374151;
}

.auth-form {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.auth-form input {
  flex: 1;
  min-width: 200px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
}

button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

button:hover:not(:disabled) {
  background: #2563eb;
}

button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.result {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 4px;
  font-weight: 500;
}

.result.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #10b981;
}

.result.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.user-info {
  background: #f0f9ff;
  border: 1px solid #0ea5e9;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  margin-bottom: 2rem;
}

.user-info h3 {
  margin: 0 0 1rem 0;
  color: #0c4a6e;
}

.logout-btn {
  background: #ef4444;
}

.logout-btn:hover {
  background: #dc2626;
}

.navigation {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.nav-btn {
  background: #10b981;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.nav-btn:hover {
  background: #059669;
}

@media (max-width: 768px) {
  .auth-form {
    flex-direction: column;
  }
  
  .navigation {
    flex-direction: column;
  }
}
</style> 