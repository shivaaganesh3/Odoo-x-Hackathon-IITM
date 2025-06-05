<template>
  <AppLayout>
    <!-- Welcome section -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">
        Welcome back, {{ userName }}! 👋
      </h1>
      <p class="mt-2 text-gray-600">
        Here's what's happening with your projects today.
      </p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div
        v-for="stat in stats"
        :key="stat.name"
        class="card p-6 hover:shadow-md transition-shadow duration-200"
      >
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div :class="[stat.iconBg, 'p-3 rounded-lg']">
              <component :is="stat.icon" class="h-6 w-6 text-white" />
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">{{ stat.name }}</p>
            <p class="text-2xl font-semibold text-gray-900">{{ stat.value }}</p>
            <div class="flex items-center mt-1">
              <span :class="[stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600', 'text-sm font-medium']">
                {{ stat.change }}
              </span>
              <span class="text-gray-500 text-sm ml-1">from last week</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main content grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Recent Projects -->
      <div class="lg:col-span-2">
        <div class="card">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium text-gray-900">Recent Projects</h2>
              <router-link 
                to="/projects" 
                class="text-sm text-primary-600 hover:text-primary-500 font-medium"
              >
                View all
              </router-link>
            </div>
          </div>
          <div class="p-6">
            <div v-if="isLoadingProjects" class="space-y-4">
              <div v-for="i in 3" :key="i" class="animate-pulse">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
                  <div class="flex-1">
                    <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div class="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="space-y-4">
              <div
                v-for="project in recentProjects"
                :key="project.id"
                class="flex items-center space-x-4 p-4 rounded-lg hover:bg-gray-50 transition-colors duration-200 cursor-pointer"
                @click="$router.push(`/projects/${project.id}`)"
              >
                <div class="flex-shrink-0">
                  <div v-if="project.image" class="w-12 h-12 rounded-lg overflow-hidden">
                    <img :src="project.image" :alt="project.name" class="w-full h-full object-cover" />
                  </div>
                  <div v-else class="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                    <FolderIcon class="h-6 w-6 text-white" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-medium text-gray-900 truncate">{{ project.name }}</h3>
                  <p class="text-sm text-gray-500 truncate">{{ project.description }}</p>
                  <div class="flex items-center mt-2">
                    <span :class="getPriorityBadgeClass(project.priority)" class="badge">
                      {{ project.priority }}
                    </span>
                    <span class="ml-2 text-xs text-gray-500">
                      {{ formatDate(project.created_at) }}
                    </span>
                  </div>
                </div>
                <div class="flex-shrink-0">
                  <div class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
                    <ChevronRightIcon class="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!isLoadingProjects && recentProjects.length === 0" class="text-center py-8">
              <FolderIcon class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">No projects yet</h3>
              <p class="mt-1 text-sm text-gray-500">Get started by creating your first project.</p>
              <div class="mt-6">
                <router-link to="/projects/create" class="btn-primary">
                  <PlusIcon class="h-4 w-4 mr-2" />
                  Create Project
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right sidebar -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="card">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Quick Actions</h2>
          </div>
          <div class="p-6 space-y-3">
            <router-link
              to="/projects/create"
              class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 group"
            >
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200">
                  <PlusIcon class="h-4 w-4 text-primary-600" />
                </div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">New Project</p>
                <p class="text-xs text-gray-500">Create a new project</p>
              </div>
            </router-link>
            <router-link
              to="/team"
              class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 group"
            >
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200">
                  <UserGroupIcon class="h-4 w-4 text-green-600" />
                </div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">Invite Team</p>
                <p class="text-xs text-gray-500">Add collaborators</p>
              </div>
            </router-link>
            <router-link
              to="/settings"
              class="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 group"
            >
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200">
                  <Cog6ToothIcon class="h-4 w-4 text-purple-600" />
                </div>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">Settings</p>
                <p class="text-xs text-gray-500">Manage preferences</p>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="card">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Recent Activity</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div
                v-for="activity in recentActivity"
                :key="activity.id"
                class="flex items-start space-x-3"
              >
                <div class="flex-shrink-0">
                  <div :class="[activity.iconBg, 'w-8 h-8 rounded-full flex items-center justify-center']">
                    <component :is="activity.icon" class="h-4 w-4 text-white" />
                  </div>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-900">{{ activity.message }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ formatDate(activity.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import {
  FolderIcon,
  UserGroupIcon,
  CalendarIcon,
  CheckCircleIcon,
  PlusIcon,
  ChevronRightIcon,
  Cog6ToothIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'
import axios from '../axios'

export default {
  name: 'DashboardPage',
  components: {
    AppLayout,
    FolderIcon,
    UserGroupIcon,
    PlusIcon,
    ChevronRightIcon,
    Cog6ToothIcon,
  },
  setup() {
    const userName = ref('User') // Default fallback
    const isLoadingProjects = ref(true)
    const recentProjects = ref([])
    const recentActivity = ref([])

    // Get user name from localStorage
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        userName.value = userData.name || 'User'
      } catch (error) {
        console.error('Error parsing stored user data:', error)
      }
    }

    const stats = ref([
      {
        name: 'Total Projects',
        value: '0',
        change: '+0%',
        changeType: 'increase',
        icon: FolderIcon,
        iconBg: 'bg-primary-500'
      },
      {
        name: 'Active Tasks',
        value: '0',
        change: '+0%',
        changeType: 'increase',
        icon: CheckCircleIcon,
        iconBg: 'bg-green-500'
      },
      {
        name: 'Team Members',
        value: '0',
        change: '+0',
        changeType: 'increase',
        icon: UserGroupIcon,
        iconBg: 'bg-blue-500'
      },
      {
        name: 'Overdue',
        value: '0',
        change: '0',
        changeType: 'decrease',
        icon: ExclamationTriangleIcon,
        iconBg: 'bg-red-500'
      }
    ])

    const fetchDashboardData = async () => {
      try {
        // Fetch dashboard stats
        const statsResponse = await axios.get('/auth/dashboard-stats')
        const statsData = statsResponse.data

        // Update stats with real data
        stats.value[0].value = statsData.total_projects.toString()
        stats.value[1].value = statsData.active_tasks.toString()
        stats.value[2].value = statsData.team_members.toString()
        stats.value[3].value = statsData.overdue_tasks.toString()
        
        // Update change indicators for overdue tasks
        if (statsData.overdue_tasks > 0) {
          stats.value[3].change = `${statsData.overdue_tasks} overdue`
          stats.value[3].changeType = 'decrease'
        } else {
          stats.value[3].change = 'All up to date!'
          stats.value[3].changeType = 'increase'
        }

        // Fetch recent projects
        const projectsResponse = await axios.get('/auth/recent-projects')
        recentProjects.value = projectsResponse.data

        // Sample activity data (could be replaced with real endpoint later)
        recentActivity.value = [
          {
            id: 1,
            message: 'Project updated successfully',
            icon: CheckCircleIcon,
            iconBg: 'bg-green-500',
            created_at: new Date().toISOString()
          },
          {
            id: 2,
            message: 'New project was created',
            icon: FolderIcon,
            iconBg: 'bg-primary-500',
            created_at: new Date().toISOString()
          },
          {
            id: 3,
            message: 'Team member added',
            icon: UserGroupIcon,
            iconBg: 'bg-blue-500',
            created_at: new Date().toISOString()
          }
        ]

        isLoadingProjects.value = false
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        isLoadingProjects.value = false
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

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) return 'Yesterday'
      if (diffDays < 7) return `${diffDays} days ago`
      return date.toLocaleDateString()
    }

    onMounted(() => {
      fetchDashboardData()
    })

    return {
      userName,
      stats,
      isLoadingProjects,
      recentProjects,
      recentActivity,
      getPriorityBadgeClass,
      formatDate,
    }
  }
}
</script> 