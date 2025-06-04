<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="email" placeholder="Email" type="email" required />
      <input v-model="password" placeholder="Password" type="password" required />
      <button type="submit">Login</button>
    </form>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from '../axios'

const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()
const auth = useAuthStore()

const login = async () => {
  error.value = ''
  try {
    const res = await axios.post('/auth/login', {
      email: email.value,
      password: password.value
    })
    auth.user = res.data.user
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed'
  }
}
</script>

  