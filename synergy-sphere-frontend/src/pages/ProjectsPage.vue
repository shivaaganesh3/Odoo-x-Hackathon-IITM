<template>
  <AppLayout>
    <!-- Header section -->
    <div class="mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Projects</h1>
          <p class="mt-2 text-gray-600">Manage and track all your projects in one place</p>
        </div>
        <div class="mt-4 sm:mt-0">
          <router-link to="/projects/create" class="btn-primary">
            <PlusIcon class="h-4 w-4 mr-2" />
            New Project
          </router-link>
        </div>
      </div>
    </div>

    <!-- Filters and search -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search projects..."
              class="input-field pl-10"
            />
          </div>
        </div>
        <div class="flex gap-4">
          <select v-model="selectedPriority" class="input-field">
            <option value="">All Priorities</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <select v-model="selectedStatus" class="input-field">
            <option value="">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="COMPLETED">Completed</option>
            <option value="ON_HOLD">On Hold</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Projects grid -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="card p-6 animate-pulse">
        <div class="w-full h-32 bg-gray-200 rounded-lg mb-4"></div>
        <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div class="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="flex justify-between items-center">
          <div class="h-6 bg-gray-200 rounded w-16"></div>
          <div class="h-8 w-8 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    </div>

    <div v-else-if="filteredProjects.length === 0" class="text-center py-16">
      <FolderIcon class="mx-auto h-24 w-24 text-gray-400" />
      <h3 class="mt-4 text-lg font-medium text-gray-900">No projects found</h3>
      <p class="mt-2 text-gray-500">
        {{ searchQuery || selectedPriority || selectedStatus ? 'Try adjusting your filters' : 'Get started by creating your first project' }}
      </p>
      <div class="mt-6">
        <router-link to="/projects/create" class="btn-primary">
          <PlusIcon class="h-4 w-4 mr-2" />
          Create Project
        </router-link>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in filteredProjects"
        :key="project.id"
        class="card overflow-hidden hover:shadow-lg transition-shadow duration-200 cursor-pointer group"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <!-- Project image -->
        <div class="aspect-w-16 aspect-h-9 bg-gradient-to-br from-primary-500 to-primary-700">
          <img
            v-if="project.image"
            :src="project.image"
            :alt="project.name"
            class="w-full h-32 object-cover"
          />
          <div v-else class="w-full h-32 bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
            <FolderIcon class="h-12 w-12 text-white" />
          </div>
        </div>

        <!-- Project content -->
        <div class="p-6">
          <div class="flex items-start justify-between mb-2">
            <h3 class="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors duration-200">
              {{ project.name }}
            </h3>
            <span :class="getPriorityBadgeClass(project.priority)" class="badge ml-2">
              {{ project.priority }}
            </span>
          </div>
          
          <p class="text-gray-600 text-sm mb-4 line-clamp-2">
            {{ project.description }}
          </p>

          <!-- Project stats -->
          <div class="flex items-center justify-between text-sm text-gray-500 mb-4">
            <div class="flex items-center space-x-4">
              <div class="flex items-center">
                <CheckCircleIcon class="h-4 w-4 mr-1" />
                <span>{{ project.completed_tasks || 0 }}/{{ project.total_tasks || 0 }}</span>
              </div>
              <div class="flex items-center">
                <CalendarIcon class="h-4 w-4 mr-1" />
                <span>{{ formatDate(project.deadline) }}</span>
              </div>
            </div>
          </div>

          <!-- Progress bar -->
          <div class="mb-4">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{{ getProgressPercentage(project) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                :class="getProgressBarClass(project)"
                class="h-2 rounded-full transition-all duration-300"
                :style="{ width: `${getProgressPercentage(project)}%` }"
              ></div>
            </div>
          </div>

          <!-- Team avatars and actions -->
          <div class="flex items-center justify-between">
            <div class="flex -space-x-2">
              <div
                v-for="(member, index) in project.team_members?.slice(0, 3)"
                :key="member.id"
                class="w-8 h-8 rounded-full border-2 border-white overflow-hidden"
                :style="{ zIndex: 10 - index }"
              >
                <img
                  :src="member.avatar || `https://ui-avatars.com/api/?name=${member.name}&background=3b82f6&color=fff`"
                  :alt="member.name"
                  class="w-full h-full object-cover"
                />
              </div>
              <div
                v-if="project.team_members?.length > 3"
                class="w-8 h-8 rounded-full border-2 border-white bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600"
              >
                +{{ project.team_members.length - 3 }}
              </div>
            </div>
            
            <div class="flex items-center space-x-2">
              <button
                @click.stop="toggleFavorite(project)"
                class="p-2 text-gray-400 hover:text-yellow-500 transition-colors duration-200"
              >
                <StarIcon :class="project.is_favorite ? 'text-yellow-500 fill-current' : ''" class="h-4 w-4" />
              </button>
              <EllipsisVerticalIcon class="h-4 w-4 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Load more button -->
    <div v-if="hasMore && !isLoading" class="mt-8 text-center">
      <button @click="loadMore" class="btn-secondary">
        Load More Projects
      </button>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import {
  FolderIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  CalendarIcon,
  StarIcon,
  EllipsisVerticalIcon,
} from '@heroicons/vue/24/outline'
import axios from '../axios'

export default {
  name: 'ProjectsPage',
  components: {
    AppLayout,
    FolderIcon,
    PlusIcon,
    MagnifyingGlassIcon,
    CheckCircleIcon,
    CalendarIcon,
    StarIcon,
    EllipsisVerticalIcon,
  },
  setup() {
    const projects = ref([])
    const isLoading = ref(true)
    const hasMore = ref(false)
    const searchQuery = ref('')
    const selectedPriority = ref('')
    const selectedStatus = ref('')

    const filteredProjects = computed(() => {
      let filtered = projects.value

      if (searchQuery.value) {
        filtered = filtered.filter(project =>
          project.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          project.description.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }

      if (selectedPriority.value) {
        filtered = filtered.filter(project => project.priority === selectedPriority.value)
      }

      if (selectedStatus.value) {
        filtered = filtered.filter(project => project.status === selectedStatus.value)
      }

      return filtered
    })

    const fetchProjects = async () => {
      try {
        isLoading.value = true
        // TODO: Replace with actual API call
        // Simulate API call
        setTimeout(() => {
          projects.value = [
            {
              id: 1,
              name: 'Website Redesign',
              description: 'Complete redesign of the company website with modern UI/UX principles and responsive design',
              priority: 'HIGH',
              status: 'ACTIVE',
              deadline: '2024-02-15',
              completed_tasks: 8,
              total_tasks: 12,
              team_members: [
                { id: 1, name: 'John Doe', avatar: null },
                { id: 2, name: 'Jane Smith', avatar: null },
                { id: 3, name: 'Mike Johnson', avatar: null }
              ],
              is_favorite: true,
              image: null
            },
            {
              id: 2,
              name: 'Mobile App Development',
              description: 'Building our first mobile application for iOS and Android platforms',
              priority: 'MEDIUM',
              status: 'ACTIVE',
              deadline: '2024-03-20',
              completed_tasks: 3,
              total_tasks: 15,
              team_members: [
                { id: 4, name: 'Sarah Wilson', avatar: null },
                { id: 5, name: 'Tom Brown', avatar: null }
              ],
              is_favorite: false,
              image: null
            },
            {
              id: 3,
              name: 'Database Migration',
              description: 'Migrating from legacy database to modern cloud solution',
              priority: 'LOW',
              status: 'COMPLETED',
              deadline: '2024-01-10',
              completed_tasks: 5,
              total_tasks: 5,
              team_members: [
                { id: 6, name: 'David Lee', avatar: null }
              ],
              is_favorite: false,
              image: null
            }
          ]
          isLoading.value = false
        }, 1000)
      } catch (error) {
        console.error('Error fetching projects:', error)
        isLoading.value = false
      }
    }

    const getPriorityBadgeClass = (priority) => {
      const classes = {
        HIGH: 'badge-danger',
        MEDIUM: 'badge-warning',
        LOW: 'badge-success'
      }
      return classes[priority] || 'badge-secondary'
    }

    const getProgressPercentage = (project) => {
      if (!project.total_tasks || project.total_tasks === 0) return 0
      return Math.round((project.completed_tasks / project.total_tasks) * 100)
    }

    const getProgressBarClass = (project) => {
      const percentage = getProgressPercentage(project)
      if (percentage >= 80) return 'bg-green-500'
      if (percentage >= 50) return 'bg-yellow-500'
      return 'bg-primary-500'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'No deadline'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
    }

    const toggleFavorite = async (project) => {
      try {
        project.is_favorite = !project.is_favorite
        // TODO: API call to update favorite status
      } catch (error) {
        console.error('Error toggling favorite:', error)
        project.is_favorite = !project.is_favorite // Revert on error
      }
    }

    const loadMore = () => {
      // TODO: Implement pagination
      console.log('Loading more projects...')
    }

    onMounted(() => {
      fetchProjects()
    })

    return {
      projects,
      filteredProjects,
      isLoading,
      hasMore,
      searchQuery,
      selectedPriority,
      selectedStatus,
      getPriorityBadgeClass,
      getProgressPercentage,
      getProgressBarClass,
      formatDate,
      toggleFavorite,
      loadMore,
    }
  }
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 