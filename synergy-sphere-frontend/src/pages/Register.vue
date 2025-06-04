<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="name" placeholder="Name" required />
      <input v-model="email" placeholder="Email" type="email" required />
      <input v-model="password" placeholder="Password" type="password" required />
      <button type="submit">Register</button>
    </form>
    <p v-if="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const register = async () => {
  error.value = ''
  try {
    await axios.post('/auth/register', {
      name: name.value,
      email: email.value,
      password: password.value
    })
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed'
  }
}
</script>
