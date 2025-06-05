import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from '../axios'

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)
  const loading = ref(false)
  const error = ref(null)
  
  // Computed
  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.is_read)
  )
  
  const deadlineWarnings = computed(() => 
    notifications.value.filter(n => n.type === 'deadline_warning')
  )
  
  const criticalNotifications = computed(() => 
    notifications.value.filter(n => n.priority === 'critical')
  )

  // Actions
  async function fetchNotifications(options = {}) {
    try {
      // Build query parameters from options
      const params = new URLSearchParams()
      
      if (options.limit) params.append('limit', options.limit)
      if (options.offset) params.append('offset', options.offset)
      if (options.unread_only) params.append('unread_only', 'true')
      if (options.type) params.append('type', options.type)
      if (options.priority) params.append('priority', options.priority)
      if (options.project_id) params.append('project_id', options.project_id)
      
      const queryString = params.toString()
      const url = queryString ? `/notifications?${queryString}` : '/notifications'
      
      const response = await axios.get(url)
      
      // Handle the API response format which wraps notifications in a data object
      if (response.data.notifications) {
        notifications.value = response.data.notifications
      } else {
        notifications.value = response.data
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }
  
  // Mark notification as read
  async function markAsRead(notificationId) {
    try {
      await axios.put(`/notifications/${notificationId}/read`)
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }
  
  // Get deadline insights for a task
  async function getTaskDeadlineInsights(taskId) {
    try {
      const response = await axios.get(`/notifications/task-insights/${taskId}`)
      return response.data
    } catch (error) {
      console.error('Failed to get task deadline insights:', error)
      return null
    }
  }
  
  // Clear all notifications
  async function clearAll() {
    try {
      await axios.delete('/notifications')
      notifications.value = []
    } catch (error) {
      console.error('Failed to clear notifications:', error)
    }
  }

  async function markAllAsRead(type = null) {
    try {
      const params = type ? `?type=${type}` : ''
      const response = await axios.put(`/notifications/read-all${params}`)
      
      // Update local state
      notifications.value.forEach(notification => {
        if (!type || notification.type === type) {
          notification.is_read = true
        }
      })
      
      if (!type) {
        unreadCount.value = 0
      } else {
        unreadCount.value = notifications.value.filter(n => !n.is_read).length
      }
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to mark notifications as read'
      console.error('Mark all as read error:', err)
      return false
    }
  }

  async function deleteNotification(notificationId) {
    try {
      await axios.delete(`/notifications/${notificationId}`)
      
      // Update local state
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const notification = notifications.value[index]
        if (!notification.is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
        notifications.value.splice(index, 1)
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to delete notification'
      console.error('Delete notification error:', err)
      return false
    }
  }

  async function runDeadlineAnalysis() {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/notifications/deadline-analysis')
      
      // Refresh notifications after analysis
      await fetchNotifications()
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to run deadline analysis'
      console.error('Deadline analysis error:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  async function getTaskInsights(taskId) {
    try {
      const response = await axios.get(`/notifications/task-insights/${taskId}`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to get task insights'
      console.error('Task insights error:', err)
      return null
    }
  }

  async function getNotificationStats() {
    try {
      const response = await axios.get('/notifications/stats')
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to get notification stats'
      console.error('Notification stats error:', err)
      return null
    }
  }

  function addNotification(notification) {
    // Add new notification to the beginning of the array
    notifications.value.unshift(notification)
    if (!notification.is_read) {
      unreadCount.value += 1
    }
  }

  function clearError() {
    error.value = null
  }

  function reset() {
    notifications.value = []
    unreadCount.value = 0
    loading.value = false
    error.value = null
  }

  return {
    // State
    notifications,
    unreadCount,
    loading,
    error,
    
    // Computed
    unreadNotifications,
    deadlineWarnings,
    criticalNotifications,
    
    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    runDeadlineAnalysis,
    getTaskInsights,
    getNotificationStats,
    addNotification,
    clearError,
    reset,
    getTaskDeadlineInsights,
    clearAll
  }
}) 