<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
    <!-- Mobile menu overlay -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-40 lg:hidden">
      <div class="fixed inset-0 bg-gray-600 bg-opacity-75" @click="sidebarOpen = false"></div>
      <nav class="fixed top-0 left-0 bottom-0 flex flex-col w-5/6 max-w-sm py-6 px-6 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto transition-colors duration-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">S</span>
              </div>
            </div>
            <h1 class="ml-3 text-xl font-bold text-gradient dark:text-white">Synergy Sphere</h1>
          </div>
          <button @click="sidebarOpen = false" class="p-2 rounded-md text-gray-400 dark:text-gray-300 hover:text-gray-500 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
        <nav class="mt-8 flex-1">
          <div class="space-y-1">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.href"
              :class="[
                $route.path === item.href
                  ? 'bg-primary-50 dark:bg-primary-900/50 border-primary-500 text-primary-700 dark:text-primary-300'
                  : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white',
                'group flex items-center px-3 py-2 text-sm font-medium border-l-4 transition-colors duration-200'
              ]"
            >
              <component
                :is="item.icon"
                :class="[
                  $route.path === item.href ? 'text-primary-500 dark:text-primary-400' : 'text-gray-400 dark:text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300',
                  'mr-3 h-5 w-5 transition-colors duration-200'
                ]"
              />
              {{ item.name }}
            </router-link>
          </div>
        </nav>
      </nav>
    </div>

    <!-- Desktop sidebar -->
    <div class="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div class="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <div class="flex items-center flex-shrink-0 px-4">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">S</span>
            </div>
          </div>
          <h1 class="ml-3 text-xl font-bold text-gradient dark:text-white">Synergy Sphere</h1>
        </div>
        <nav class="mt-8 flex-1 px-2 space-y-1">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              $route.path === item.href
                ? 'bg-primary-50 dark:bg-primary-900/50 border-primary-500 text-primary-700 dark:text-primary-300'
                : 'border-transparent text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white',
              'group flex items-center px-3 py-2 text-sm font-medium border-l-4 rounded-r-lg transition-colors duration-200'
            ]"
          >
            <component
              :is="item.icon"
                          :class="[
              $route.path === item.href ? 'text-primary-500 dark:text-primary-400' : 'text-gray-400 dark:text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300',
              'mr-3 h-5 w-5 transition-colors duration-200'
            ]"
            />
            {{ item.name }}
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Main content -->
    <div class="lg:pl-64 flex flex-col flex-1">
      <!-- Top header -->
      <div class="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <button
          @click="sidebarOpen = true"
          class="px-4 border-r border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 lg:hidden transition-colors duration-200"
        >
          <Bars3Icon class="h-6 w-6" />
        </button>
        <div class="flex-1 px-4 flex justify-between items-center">
          <h1 class="text-2xl font-semibold text-gray-900 dark:text-white transition-colors duration-200">{{ pageTitle }}</h1>
          <div class="ml-4 flex items-center md:ml-6">
            <!-- Dark Mode Toggle -->
            <DarkModeToggle class="mr-3" />
            <!-- Notification Bell -->
            <NotificationBell class="mr-4" />
            <!-- Profile dropdown -->
            <div class="ml-3 relative">
              <div>
                <button
                  @click="profileOpen = !profileOpen"
                  class="max-w-xs bg-white dark:bg-gray-800 flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 dark:ring-offset-gray-800 focus:ring-primary-500 transition-colors duration-200"
                >
                  <img
                    class="h-8 w-8 rounded-full"
                    :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=3b82f6&color=fff`"
                    :alt="`${userName} avatar`"
                  />
                </button>
              </div>
              <div
                v-if="profileOpen"
                @click.away="profileOpen = false"
                class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-800 ring-1 ring-black dark:ring-gray-600 ring-opacity-5 dark:ring-opacity-25 focus:outline-none transition-colors duration-200"
              >
                <a href="#" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">Your Profile</a>
                <a href="#" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">Settings</a>
                <a href="#" @click="logout" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">Sign out</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Page content -->
      <main class="flex-1">
        <div class="py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <slot />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from '../axios'
import {
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  FolderIcon,
  UserGroupIcon,
  CalendarIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline'
import NotificationBell from './NotificationBell.vue'
import DarkModeToggle from './DarkModeToggle.vue'

export default {
  name: 'AppLayout',
  components: {
    Bars3Icon,
    XMarkIcon,
    NotificationBell,
    DarkModeToggle,
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    const sidebarOpen = ref(false)
    const profileOpen = ref(false)

    // Get user data for avatar
    const userName = ref('User')
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        userName.value = userData.name || 'User'
      } catch (error) {
        console.error('Error parsing stored user data:', error)
      }
    }

    const navigation = [
      { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
      { name: 'Projects', href: '/projects', icon: FolderIcon },
      { name: 'Team', href: '/team', icon: UserGroupIcon },
      { name: 'Calendar', href: '/calendar', icon: CalendarIcon },
      { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
    ]

    const pageTitle = computed(() => {
      const currentNav = navigation.find(item => item.href === route.path)
      return currentNav ? currentNav.name : 'Synergy Sphere'
    })

    const logout = async () => {
      try {
        // Call backend logout endpoint
        await axios.post('/auth/logout')
      } catch (error) {
        console.error('Error during logout:', error)
        // Continue with logout even if backend call fails
      } finally {
        // Clear auth state and localStorage
        authStore.logout()
        // Close profile dropdown
        profileOpen.value = false
        // Redirect to login page
        router.push('/login')
      }
    }

    return {
      sidebarOpen,
      profileOpen,
      navigation,
      pageTitle,
      userName,
      logout,
      HomeIcon,
      FolderIcon,
      UserGroupIcon,
      CalendarIcon,
      Cog6ToothIcon,
    }
  }
}
</script> 