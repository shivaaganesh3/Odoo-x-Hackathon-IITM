<template>
  <AppLayout>
    <div class="bg-white rounded-lg shadow">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-semibold text-gray-900">Notifications</h2>
            <p class="text-sm text-gray-600 mt-1">
              Manage your deadline warnings and project updates
            </p>
          </div>
          <div class="flex items-center space-x-3">
            <!-- Quick Actions -->
            <button
              @click="runDeadlineAnalysis"
              :disabled="loading"
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>{{ loading ? 'Analyzing...' : 'Run Analysis' }}</span>
            </button>

            <button
              v-if="unreadCount > 0"
              @click="markAllAsRead"
              class="text-blue-600 hover:text-blue-700 font-medium px-4 py-2 border border-blue-600 rounded-lg hover:bg-blue-50"
            >
              Mark All Read ({{ unreadCount }})
            </button>
          </div>
        </div>

        <!-- Stats -->
        <div v-if="stats" class="mt-4 grid grid-cols-4 gap-4">
          <div class="bg-gray-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-gray-900">{{ stats.total_notifications }}</div>
            <div class="text-sm text-gray-600">Total</div>
          </div>
          <div class="bg-red-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-red-600">{{ stats.unread_notifications }}</div>
            <div class="text-sm text-gray-600">Unread</div>
          </div>
          <div class="bg-orange-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-orange-600">{{ stats.by_priority?.critical || 0 }}</div>
            <div class="text-sm text-gray-600">Critical</div>
          </div>
          <div class="bg-blue-50 rounded-lg p-3">
            <div class="text-2xl font-bold text-blue-600">{{ stats.by_type?.deadline_warning || 0 }}</div>
            <div class="text-sm text-gray-600">Deadline Warnings</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center space-x-4">
          <!-- Type Filter -->
          <div>
            <label class="text-sm font-medium text-gray-700">Type</label>
            <select
              v-model="filters.type"
              @change="applyFilters"
              class="mt-1 block w-40 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">All Types</option>
              <option value="deadline_warning">Deadline Warnings</option>
              <option value="task_overdue">Overdue Tasks</option>
              <option value="general">General</option>
            </select>
          </div>

          <!-- Priority Filter -->
          <div>
            <label class="text-sm font-medium text-gray-700">Priority</label>
            <select
              v-model="filters.priority"
              @change="applyFilters"
              class="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <!-- Read Status Filter -->
          <div>
            <label class="text-sm font-medium text-gray-700">Status</label>
            <select
              v-model="filters.unread_only"
              @change="applyFilters"
              class="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option :value="false">All</option>
              <option :value="true">Unread Only</option>
            </select>
          </div>

          <!-- Clear Filters -->
          <button
            v-if="hasActiveFilters"
            @click="clearFilters"
            class="mt-6 text-sm text-gray-600 hover:text-gray-800"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="divide-y divide-gray-200">
        <div v-if="loading && notifications.length === 0" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-500">Loading notifications...</p>
        </div>

        <div v-else-if="notifications.length === 0" class="p-8 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">No notifications</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ hasActiveFilters ? 'No notifications match your filters.' : 'You\'re all caught up!' }}
          </p>
        </div>

        <div v-else>
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="p-6 hover:bg-gray-50 transition-colors"
            :class="{ 'bg-blue-25': !notification.is_read }"
          >
            <!-- Notification Content -->
            <div class="flex items-start space-x-4">
              <!-- Priority Icon -->
              <div class="flex-shrink-0">
                <div
                  class="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                  :class="getPriorityBgClass(notification.priority)"
                >
                  {{ getPriorityIcon(notification.priority) }}
                </div>
              </div>

              <!-- Main Content -->
              <div class="flex-1 min-w-0">
                <!-- Header -->
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <h3 
                      class="text-lg font-medium"
                      :class="notification.is_read ? 'text-gray-700' : 'text-gray-900'"
                    >
                      {{ notification.title }}
                    </h3>
                    <div class="flex items-center space-x-4 mt-1">
                      <span 
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize"
                        :class="getPriorityClass(notification.priority)"
                      >
                        {{ notification.priority }} Priority
                      </span>
                      <span class="text-sm text-gray-500">
                        {{ formatTime(notification.created_at) }}
                      </span>
                      <span v-if="!notification.is_read" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        New
                      </span>
                    </div>
                  </div>

                  <!-- Actions -->
                  <div class="flex items-center space-x-2">
                    <button
                      v-if="notification.task_id"
                      @click="viewTaskInsights(notification.task_id)"
                      class="text-sm text-blue-600 hover:text-blue-700"
                    >
                      View Insights
                    </button>
                    <button
                      v-if="!notification.is_read"
                      @click="markAsRead(notification.id)"
                      class="text-sm text-blue-600 hover:text-blue-700"
                    >
                      Mark Read
                    </button>
                    <button
                      @click="deleteNotification(notification.id)"
                      class="text-sm text-red-600 hover:text-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                <!-- Message -->
                <div class="mt-3">
                  <p 
                    class="text-gray-700 whitespace-pre-line"
                    v-html="formatNotificationMessage(notification.message)"
                  ></p>
                </div>

                <!-- Context Info -->
                <div v-if="notification.project_name || notification.task_title" class="mt-3 flex items-center space-x-4">
                  <span v-if="notification.project_name" class="inline-flex items-center text-sm text-gray-600">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    Project: {{ notification.project_name }}
                  </span>
                  <span v-if="notification.task_title" class="inline-flex items-center text-sm text-gray-600">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    Task: {{ notification.task_title }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="p-6 border-t border-gray-200 text-center">
        <button
          @click="loadMore"
          :disabled="loading"
          class="text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Load More' }}
        </button>
      </div>
    </div>

    <!-- Task Insights Modal -->
    <div v-if="showInsights" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeInsights"></div>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <TaskInsightsModal
            v-if="selectedTaskInsights"
            :insights="selectedTaskInsights"
            @close="closeInsights"
          />
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '@/store/notifications'
import AppLayout from '@/components/AppLayout.vue'
import TaskInsightsModal from '@/components/TaskInsightsModal.vue'

const notificationsStore = useNotificationsStore()

// State
const filters = ref({
  type: '',
  priority: '',
  unread_only: false
})

const stats = ref(null)
const showInsights = ref(false)
const selectedTaskInsights = ref(null)
const currentOffset = ref(0)
const limit = 20

// Computed
const notifications = computed(() => notificationsStore.notifications)
const unreadCount = computed(() => notificationsStore.unreadCount)
const loading = computed(() => notificationsStore.loading)
const hasMore = ref(false)

const hasActiveFilters = computed(() => {
  return filters.value.type || filters.value.priority || filters.value.unread_only
})

// Methods
async function fetchNotifications(reset = true) {
  if (reset) {
    currentOffset.value = 0
  }

  const result = await notificationsStore.fetchNotifications({
    ...filters.value,
    limit,
    offset: currentOffset.value
  })

  if (result) {
    hasMore.value = result.has_more
  }
}

async function applyFilters() {
  await fetchNotifications(true)
}

async function clearFilters() {
  filters.value = {
    type: '',
    priority: '',
    unread_only: false
  }
  await fetchNotifications(true)
}

async function loadMore() {
  currentOffset.value += limit
  await fetchNotifications(false)
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

async function runDeadlineAnalysis() {
  const result = await notificationsStore.runDeadlineAnalysis()
  if (result) {
    await loadStats()
  }
}

async function loadStats() {
  stats.value = await notificationsStore.getNotificationStats()
}

async function viewTaskInsights(taskId) {
  selectedTaskInsights.value = await notificationsStore.getTaskInsights(taskId)
  if (selectedTaskInsights.value) {
    showInsights.value = true
  }
}

function closeInsights() {
  showInsights.value = false
  selectedTaskInsights.value = null
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

function getPriorityClass(priority) {
  const classes = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

function getPriorityBgClass(priority) {
  const classes = {
    critical: 'bg-red-100 text-red-600',
    high: 'bg-orange-100 text-orange-600',
    medium: 'bg-yellow-100 text-yellow-600',
    low: 'bg-blue-100 text-blue-600'
  }
  return classes[priority] || 'bg-gray-100 text-gray-600'
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
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffHours < 1) return 'Just now'
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

// Initialize
onMounted(async () => {
  await fetchNotifications()
  await loadStats()
})
</script> 