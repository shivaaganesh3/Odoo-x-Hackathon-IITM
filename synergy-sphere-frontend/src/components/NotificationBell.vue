<template>
  <div class="relative">
    <!-- Notification Bell Button -->
    <button
      @click="toggleDropdown"
      class="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
      :class="{ 'text-red-600 hover:text-red-700': unreadCount > 0 }"
    >
      <!-- Bell Icon -->
      <svg 
        class="w-6 h-6" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          stroke-linecap="round" 
          stroke-linejoin="round" 
          stroke-width="2" 
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      
      <!-- Unread Badge -->
      <span 
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-semibold"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Dropdown Panel -->
    <div
      v-if="showDropdown"
      class="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
      @click.stop
    >
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 class="font-semibold text-gray-900">Notifications</h3>
        <div class="flex items-center space-x-2">
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Mark all read
          </button>
          <button
            @click="runAnalysis"
            :disabled="loading"
            class="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loading ? 'Analyzing...' : 'Run Analysis' }}
          </button>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="max-h-96 overflow-y-auto">
        <div v-if="loading && notifications.length === 0" class="p-4 text-center text-gray-500">
          Loading notifications...
        </div>
        
        <div v-else-if="notifications.length === 0" class="p-4 text-center text-gray-500">
          No notifications yet
        </div>
        
        <div v-else>
          <div
            v-for="notification in displayedNotifications"
            :key="notification.id"
            class="border-b border-gray-100 last:border-b-0"
          >
            <div
              class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
              :class="{ 'bg-blue-50': !notification.is_read }"
              @click="handleNotificationClick(notification)"
            >
              <!-- Notification Header -->
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center space-x-2">
                  <!-- Priority Icon -->
                  <span
                    :class="getPriorityIconClass(notification.priority)"
                    class="text-sm"
                  >
                    {{ getPriorityIcon(notification.priority) }}
                  </span>
                  
                  <!-- Title -->
                  <h4 
                    class="font-medium text-sm"
                    :class="notification.is_read ? 'text-gray-700' : 'text-gray-900'"
                  >
                    {{ notification.title }}
                  </h4>
                </div>
                
                <!-- Actions -->
                <div class="flex items-center space-x-1">
                  <button
                    v-if="!notification.is_read"
                    @click.stop="markAsRead(notification.id)"
                    class="text-xs text-blue-600 hover:text-blue-700"
                  >
                    Mark read
                  </button>
                  <button
                    @click.stop="deleteNotification(notification.id)"
                    class="text-xs text-red-600 hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <!-- Message Preview -->
              <p 
                class="text-sm text-gray-600 mb-2 line-clamp-2"
                v-html="formatNotificationMessage(notification.message)"
              ></p>

              <!-- Footer -->
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>{{ formatTime(notification.created_at) }}</span>
                <div class="flex items-center space-x-2">
                  <span v-if="notification.project_name" class="bg-gray-100 px-2 py-1 rounded">
                    {{ notification.project_name }}
                  </span>
                  <span v-if="notification.task_title" class="bg-blue-100 px-2 py-1 rounded">
                    {{ notification.task_title }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-3 border-t border-gray-200 bg-gray-50">
        <router-link
          to="/notifications"
          class="text-sm text-blue-600 hover:text-blue-700 font-medium"
          @click="closeDropdown"
        >
          View all notifications →
        </router-link>
      </div>
    </div>

    <!-- Backdrop -->
    <div
      v-if="showDropdown"
      class="fixed inset-0 z-40"
      @click="closeDropdown"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationsStore } from '../store/notifications'
import { useRouter } from 'vue-router'

const notificationsStore = useNotificationsStore()
const router = useRouter()

// State
const showDropdown = ref(false)

// Computed
const notifications = computed(() => notificationsStore.notifications)
const unreadCount = computed(() => notificationsStore.unreadCount)
const loading = computed(() => notificationsStore.loading)

const displayedNotifications = computed(() => 
  notifications.value.slice(0, 5)
)

// Methods
function toggleDropdown() {
  showDropdown.value = !showDropdown.value
  
  if (showDropdown.value && notifications.value.length === 0) {
    fetchNotifications()
  }
}

function closeDropdown() {
  showDropdown.value = false
}

async function fetchNotifications() {
  await notificationsStore.fetchNotifications({ limit: 10 })
}

async function markAsRead(notificationId) {
  await notificationsStore.markAsRead(notificationId)
}

async function markAllAsRead() {
  await notificationsStore.markAllAsRead()
}

async function deleteNotification(notificationId) {
  await notificationsStore.deleteNotification(notificationId)
}

async function runAnalysis() {
  const result = await notificationsStore.runDeadlineAnalysis()
  if (result) {
    console.log('Analysis completed:', result.summary)
  }
}

function handleNotificationClick(notification) {
  if (!notification.is_read) {
    markAsRead(notification.id)
  }
  
  if (notification.task_id && notification.project_id) {
    router.push(`/projects/${notification.project_id}/tasks`)
  } else if (notification.project_id) {
    router.push(`/projects/${notification.project_id}`)
  }
  
  closeDropdown()
}

function getPriorityIcon(priority) {
  const icons = {
    critical: '🚨',
    high: '⚠️',
    medium: '⚡',
    low: '📢'
  }
  return icons[priority] || '📢'
}

function getPriorityIconClass(priority) {
  const classes = {
    critical: 'text-red-600',
    high: 'text-orange-500',
    medium: 'text-yellow-500',
    low: 'text-blue-500'
  }
  return classes[priority] || 'text-gray-500'
}

function formatNotificationMessage(message) {
  return message
    .replace(/\n/g, '<br>')
    .replace(/📊/g, '<strong>📊</strong>')
    .replace(/📅/g, '<strong>📅</strong>')
    .replace(/🎯/g, '<strong>🎯</strong>')
    .replace(/(\d+%)/g, '<strong>$1</strong>')
}

function formatTime(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

let refreshInterval = null

onMounted(() => {
  fetchNotifications()
  refreshInterval = setInterval(fetchNotifications, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 