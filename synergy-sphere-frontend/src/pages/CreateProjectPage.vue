<template>
  <AppLayout>
    <div class="max-w-2xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Create New Project</h1>
        <p class="mt-2 text-gray-600">Start a new project and organize your team's work</p>
      </div>

      <div class="card p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Project Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
              Project Name *
            </label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="input-field"
              placeholder="Enter project name"
            />
          </div>

          <!-- Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="4"
              class="input-field"
              placeholder="Describe your project goals and requirements"
            ></textarea>
          </div>

          <!-- Priority -->
          <div>
            <label for="priority" class="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <select id="priority" v-model="form.priority" class="input-field">
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          <!-- Deadline -->
          <div>
            <label for="deadline" class="block text-sm font-medium text-gray-700 mb-2">
              Deadline
            </label>
            <input
              id="deadline"
              v-model="form.deadline"
              type="date"
              class="input-field"
            />
          </div>

          <!-- Tags -->
          <div>
            <label for="tags" class="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <input
              id="tags"
              v-model="form.tags"
              type="text"
              class="input-field"
              placeholder="Enter tags separated by commas (e.g., web, frontend, api)"
            />
            <p class="mt-1 text-sm text-gray-500">
              Use tags to categorize and organize your projects
            </p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex">
              <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Error</h3>
                <p class="mt-1 text-sm text-red-700">{{ error }}</p>
              </div>
            </div>
          </div>

          <!-- Success Message -->
          <div v-if="success" class="bg-green-50 border border-green-200 rounded-md p-4">
            <div class="flex">
              <CheckCircleIcon class="h-5 w-5 text-green-400" />
              <div class="ml-3">
                <h3 class="text-sm font-medium text-green-800">Success</h3>
                <p class="mt-1 text-sm text-green-700">{{ success }}</p>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="flex gap-4 pt-6">
            <button
              type="submit"
              :disabled="isLoading"
              class="btn-primary flex-1"
            >
              <span v-if="isLoading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating...
              </span>
              <span v-else>Create Project</span>
            </button>
            <router-link to="/dashboard" class="btn-secondary flex-1 text-center">
              Cancel
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../components/AppLayout.vue'
import axios from '../axios'
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/vue/24/outline'

export default {
  name: 'CreateProjectPage',
  components: {
    AppLayout,
    ExclamationTriangleIcon,
    CheckCircleIcon,
  },
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const error = ref('')
    const success = ref('')

    const form = ref({
      name: '',
      description: '',
      priority: 'MEDIUM',
      deadline: '',
      tags: ''
    })

    const handleSubmit = async () => {
      if (!form.value.name.trim()) {
        error.value = 'Project name is required'
        return
      }

      isLoading.value = true
      error.value = ''
      success.value = ''

      try {
        const projectData = {
          name: form.value.name.trim(),
          description: form.value.description.trim(),
          priority: form.value.priority,
          deadline: form.value.deadline || null,
          tags: form.value.tags.trim()
        }

        const response = await axios.post('/projects', projectData)

        if (response.status === 201) {
          success.value = 'Project created successfully!'
          
          // Reset form
          form.value = {
            name: '',
            description: '',
            priority: 'MEDIUM',
            deadline: '',
            tags: ''
          }

          // Redirect to projects page after a short delay
          setTimeout(() => {
            router.push('/projects')
          }, 1500)
        }
      } catch (err) {
        console.error('Error creating project:', err)
        error.value = err.response?.data?.error || 'Failed to create project. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      isLoading,
      error,
      success,
      handleSubmit,
    }
  }
}
</script> 