<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 flex items-center justify-center">
          <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
            <span class="text-white font-bold text-xl">S</span>
          </div>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Join <span class="font-medium text-primary-600">Synergy Sphere</span> today
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSignup">
        <!-- Error Message -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">{{ error }}</h3>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="rounded-md bg-green-50 p-4">
          <div class="flex">
            <div class="ml-3">
              <h3 class="text-sm font-medium text-green-800">{{ success }}</h3>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <div>
            <label for="name" class="label">Full Name</label>
            <input
              id="name"
              name="name"
              type="text"
              required
              v-model="form.name"
              class="input-field"
              placeholder="Enter your full name"
            />
          </div>
          <div>
            <label for="email" class="label">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              v-model="form.email"
              class="input-field"
              placeholder="Enter your email"
            />
          </div>
          <div>
            <label for="password" class="label">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              v-model="form.password"
              class="input-field"
              placeholder="Create a password"
            />
          </div>
        </div>

        <div>
          <button type="submit" :disabled="isLoading" class="btn-primary w-full">
            {{ isLoading ? 'Creating account...' : 'Sign up' }}
          </button>
        </div>

        <div class="text-center">
          <span class="text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">
              Sign in here
            </router-link>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../axios'

export default {
  name: 'SignupPage',
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const error = ref('')
    const success = ref('')
    
    const form = ref({
      name: '',
      email: '',
      password: ''
    })

    const handleSignup = async () => {
      if (!form.value.name.trim() || !form.value.email.trim() || !form.value.password.trim()) {
        error.value = 'All fields are required'
        return
      }

      isLoading.value = true
      error.value = ''
      success.value = ''

      try {
        const response = await axios.post('/auth/register', {
          name: form.value.name.trim(),
          email: form.value.email.trim(),
          password: form.value.password
        })

        if (response.status === 201) {
          success.value = 'Registration successful! Redirecting to login...'
          
          // Reset form
          form.value = {
            name: '',
            email: '',
            password: ''
          }

          // Redirect to login after success
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        }
      } catch (err) {
        console.error('Registration error:', err)
        error.value = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      isLoading,
      error,
      success,
      handleSignup,
    }
  }
}
</script> 