<template>
  <AppLayout>
    <!-- Header section -->
    <div class="mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Calendar</h1>
          <p class="mt-2 text-gray-600">Manage your project deadlines and schedule</p>
        </div>
        <div class="mt-4 sm:mt-0 flex gap-3">
          <button @click="showCreateEventModal = true" class="btn-primary">
            <PlusIcon class="h-4 w-4 mr-2" />
            Add Event
          </button>
        </div>
      </div>
    </div>

    <!-- Calendar controls -->
    <div class="mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <!-- View selector -->
        <div class="flex rounded-lg border border-gray-200 p-1 bg-gray-50">
          <button
            v-for="view in views"
            :key="view.value"
            @click="currentView = view.value"
            :class="[
              'px-3 py-1 text-sm font-medium rounded-md transition-colors duration-200',
              currentView === view.value
                ? 'bg-white text-primary-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            ]"
          >
            {{ view.label }}
          </button>
        </div>

        <!-- Month/Year navigation -->
        <div class="flex items-center gap-4 mt-4 sm:mt-0">
          <div class="flex items-center gap-2">
            <button
              @click="navigateMonth(-1)"
              class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <ChevronLeftIcon class="h-5 w-5" />
            </button>
            <h2 class="text-lg font-semibold text-gray-900 min-w-[180px] text-center">
              {{ formatMonthYear(currentDate) }}
            </h2>
            <button
              @click="navigateMonth(1)"
              class="p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <ChevronRightIcon class="h-5 w-5" />
            </button>
          </div>
          <button
            @click="goToToday"
            class="btn-secondary text-sm"
          >
            Today
          </button>
        </div>
      </div>
    </div>

    <!-- Calendar content -->
    <div class="card overflow-hidden">
      <!-- Month view -->
      <div v-if="currentView === 'month'" class="calendar-grid">
        <!-- Day headers -->
        <div class="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
          <div
            v-for="day in dayHeaders"
            :key="day"
            class="p-3 text-center text-sm font-medium text-gray-500"
          >
            {{ day }}
          </div>
        </div>

        <!-- Calendar days -->
        <div class="grid grid-cols-7 divide-x divide-y divide-gray-200">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            :class="[
              'min-h-[120px] p-2 relative group transition-colors duration-200',
              day.isCurrentMonth ? 'bg-white' : 'bg-gray-50',
              day.isToday ? 'bg-blue-50' : '',
              'hover:bg-gray-50'
            ]"
          >
            <!-- Day number -->
            <div
              :class="[
                'text-sm font-medium mb-1',
                day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400',
                day.isToday ? 'text-primary-600' : ''
              ]"
            >
              {{ day.date.getDate() }}
            </div>

            <!-- Events for this day -->
            <div class="space-y-1">
              <div
                v-for="event in getEventsForDay(day.date)"
                :key="event.id"
                :class="[
                  'text-xs px-2 py-1 rounded truncate cursor-pointer',
                  getEventStyleClass(event.type),
                  'hover:opacity-80 transition-opacity duration-200'
                ]"
                @click="openEventDetail(event)"
                :title="event.title"
              >
                {{ event.title }}
              </div>
            </div>

            <!-- Add event button (shows on hover) -->
            <button
              @click="addEventForDay(day.date)"
              class="absolute top-1 right-1 w-5 h-5 text-gray-400 hover:text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
            >
              <PlusIcon class="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Week view -->
      <div v-else-if="currentView === 'week'" class="week-view">
        <div class="flex">
          <!-- Time column -->
          <div class="w-16 border-r border-gray-200">
            <div class="h-12 border-b border-gray-200"></div>
            <div
              v-for="hour in hours"
              :key="hour"
              class="h-16 border-b border-gray-200 text-xs text-gray-500 p-2"
            >
              {{ formatHour(hour) }}
            </div>
          </div>

          <!-- Days columns -->
          <div class="flex-1 grid grid-cols-7">
            <div
              v-for="day in weekDays"
              :key="day.toISOString()"
              class="border-r border-gray-200 last:border-r-0"
            >
              <!-- Day header -->
              <div class="h-12 border-b border-gray-200 p-2 text-center">
                <div class="text-xs text-gray-500">{{ formatDayOfWeek(day) }}</div>
                <div
                  :class="[
                    'text-sm font-medium',
                    isToday(day) ? 'text-primary-600' : 'text-gray-900'
                  ]"
                >
                  {{ day.getDate() }}
                </div>
              </div>

              <!-- Hour slots -->
              <div class="relative">
                <div
                  v-for="hour in hours"
                  :key="hour"
                  class="h-16 border-b border-gray-200"
                ></div>

                <!-- Events overlay -->
                <div class="absolute inset-0 pointer-events-none">
                  <div
                    v-for="event in getEventsForDay(day)"
                    :key="event.id"
                    class="absolute left-1 right-1 p-1 pointer-events-auto"
                    :style="getEventPosition(event)"
                  >
                    <div
                      :class="[
                        'text-xs px-2 py-1 rounded cursor-pointer truncate',
                        getEventStyleClass(event.type)
                      ]"
                      @click="openEventDetail(event)"
                    >
                      {{ event.title }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Day view -->
      <div v-else-if="currentView === 'day'" class="day-view">
        <div class="flex">
          <!-- Time column -->
          <div class="w-20 border-r border-gray-200">
            <div
              v-for="hour in hours"
              :key="hour"
              class="h-16 border-b border-gray-200 text-sm text-gray-500 p-3"
            >
              {{ formatHour(hour) }}
            </div>
          </div>

          <!-- Day column -->
          <div class="flex-1 relative">
            <div
              v-for="hour in hours"
              :key="hour"
              class="h-16 border-b border-gray-200"
            ></div>

            <!-- Events overlay -->
            <div class="absolute inset-0">
              <div
                v-for="event in getEventsForDay(currentDate)"
                :key="event.id"
                class="absolute left-2 right-2 p-1"
                :style="getEventPosition(event)"
              >
                <div
                  :class="[
                    'text-sm px-3 py-2 rounded cursor-pointer',
                    getEventStyleClass(event.type)
                  ]"
                  @click="openEventDetail(event)"
                >
                  <div class="font-medium">{{ event.title }}</div>
                  <div class="text-xs opacity-75">{{ event.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Events Legend -->
    <div class="mt-6 card p-4">
      <h3 class="text-sm font-medium text-gray-900 mb-3">Event Types</h3>
      <div class="flex flex-wrap gap-4">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-red-500 rounded"></div>
          <span class="text-sm text-gray-600">Project Deadlines</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-blue-500 rounded"></div>
          <span class="text-sm text-gray-600">Tasks</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-green-500 rounded"></div>
          <span class="text-sm text-gray-600">Meetings</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-purple-500 rounded"></div>
          <span class="text-sm text-gray-600">Events</span>
        </div>
      </div>
    </div>

    <!-- Create Event Modal -->
    <div
      v-if="showCreateEventModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click="closeCreateEventModal"
    >
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
          @click.stop
        >
          <form @submit.prevent="createEvent">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Create New Event
                  </h3>
                  
                  <div class="space-y-4">
                    <div>
                      <label class="label">Event Title</label>
                      <input
                        v-model="eventForm.title"
                        type="text"
                        required
                        class="input-field"
                        placeholder="Enter event title"
                      />
                    </div>

                    <div>
                      <label class="label">Description</label>
                      <textarea
                        v-model="eventForm.description"
                        class="input-field"
                        rows="3"
                        placeholder="Event description (optional)"
                      ></textarea>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <label class="label">Date</label>
                        <input
                          v-model="eventForm.date"
                          type="date"
                          required
                          class="input-field"
                        />
                      </div>
                      <div>
                        <label class="label">Time</label>
                        <input
                          v-model="eventForm.time"
                          type="time"
                          class="input-field"
                        />
                      </div>
                    </div>

                    <div>
                      <label class="label">Event Type</label>
                      <select v-model="eventForm.type" class="input-field">
                        <option value="event">Event</option>
                        <option value="meeting">Meeting</option>
                        <option value="task">Task</option>
                        <option value="deadline">Deadline</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button type="submit" class="btn-primary sm:ml-3">
                Create Event
              </button>
              <button
                type="button"
                @click="closeCreateEventModal"
                class="btn-secondary mt-3 sm:mt-0"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Event Detail Modal -->
    <div
      v-if="selectedEvent"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click="closeEventDetail"
    >
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity">
          <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div
          class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
          @click.stop
        >
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
            <div class="flex justify-between items-start mb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ selectedEvent.title }}
              </h3>
              <button
                @click="closeEventDetail"
                class="text-gray-400 hover:text-gray-500"
              >
                <XMarkIcon class="h-5 w-5" />
              </button>
            </div>
            
            <div class="space-y-3">
              <div v-if="selectedEvent.description" class="text-gray-600">
                {{ selectedEvent.description }}
              </div>
              
              <div class="flex items-center gap-2">
                <CalendarIcon class="h-4 w-4 text-gray-400" />
                <span class="text-sm text-gray-600">
                  {{ formatEventDate(selectedEvent.date) }}
                </span>
              </div>
              
              <div v-if="selectedEvent.time" class="flex items-center gap-2">
                <ClockIcon class="h-4 w-4 text-gray-400" />
                <span class="text-sm text-gray-600">{{ selectedEvent.time }}</span>
              </div>
              
              <div class="flex items-center gap-2">
                <span :class="['inline-flex px-2 py-1 text-xs rounded-full', getEventStyleClass(selectedEvent.type)]">
                  {{ selectedEvent.type.charAt(0).toUpperCase() + selectedEvent.type.slice(1) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../components/AppLayout.vue'
import {
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarIcon,
  ClockIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import axios from '../axios'

export default {
  name: 'CalendarPage',
  components: {
    AppLayout,
    PlusIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    CalendarIcon,
    ClockIcon,
    XMarkIcon,
  },
  setup() {
    const currentDate = ref(new Date())
    const currentView = ref('month')
    const events = ref([])
    const showCreateEventModal = ref(false)
    const selectedEvent = ref(null)

    const views = [
      { label: 'Month', value: 'month' },
      { label: 'Week', value: 'week' },
      { label: 'Day', value: 'day' }
    ]

    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    const hours = Array.from({ length: 24 }, (_, i) => i)

    const eventForm = ref({
      title: '',
      description: '',
      date: '',
      time: '',
      type: 'event'
    })

    const calendarDays = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      const days = []
      const today = new Date()
      
      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate)
        date.setDate(date.getDate() + i)
        
        days.push({
          date,
          isCurrentMonth: date.getMonth() === month,
          isToday: date.toDateString() === today.toDateString()
        })
      }
      
      return days
    })

    const weekDays = computed(() => {
      const startOfWeek = new Date(currentDate.value)
      const day = startOfWeek.getDay()
      startOfWeek.setDate(startOfWeek.getDate() - day)
      
      const days = []
      for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek)
        date.setDate(date.getDate() + i)
        days.push(date)
      }
      return days
    })

    const fetchProjectsAndEvents = async () => {
      try {
        // Fetch projects to get deadlines
        const projectsResponse = await axios.get('/projects')
        const projects = projectsResponse.data

        // Convert project deadlines to calendar events
        const projectEvents = projects
          .filter(project => project.deadline)
          .map(project => ({
            id: `project-${project.id}`,
            title: `${project.name} Deadline`,
            description: project.description,
            date: project.deadline,
            type: 'deadline',
            projectId: project.id
          }))

        // Add project events to calendar
        events.value = [...projectEvents, ...events.value]
      } catch (error) {
        console.error('Error fetching projects:', error)
      }
    }

    const formatMonthYear = (date) => {
      return date.toLocaleDateString('en-US', { 
        month: 'long', 
        year: 'numeric' 
      })
    }

    const formatDayOfWeek = (date) => {
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    }

    const formatHour = (hour) => {
      const date = new Date()
      date.setHours(hour, 0, 0, 0)
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        hour12: true 
      })
    }

    const formatEventDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const isToday = (date) => {
      const today = new Date()
      return date.toDateString() === today.toDateString()
    }

    const navigateMonth = (direction) => {
      const newDate = new Date(currentDate.value)
      newDate.setMonth(newDate.getMonth() + direction)
      currentDate.value = newDate
    }

    const goToToday = () => {
      currentDate.value = new Date()
    }

    const getEventsForDay = (date) => {
      const dateString = date.toISOString().split('T')[0]
      return events.value.filter(event => {
        const eventDate = new Date(event.date).toISOString().split('T')[0]
        return eventDate === dateString
      })
    }

    const getEventStyleClass = (type) => {
      const styles = {
        deadline: 'bg-red-100 text-red-800 border border-red-200',
        task: 'bg-blue-100 text-blue-800 border border-blue-200',
        meeting: 'bg-green-100 text-green-800 border border-green-200',
        event: 'bg-purple-100 text-purple-800 border border-purple-200'
      }
      return styles[type] || styles.event
    }

    const getEventPosition = (event) => {
      const time = event.time || '09:00'
      const [hours, minutes] = time.split(':').map(Number)
      const top = (hours * 64) + (minutes * 64 / 60) // 64px per hour
      return {
        top: `${top}px`,
        height: '32px'
      }
    }

    const addEventForDay = (date) => {
      eventForm.value.date = date.toISOString().split('T')[0]
      showCreateEventModal.value = true
    }

    const createEvent = () => {
      const newEvent = {
        id: Date.now(),
        title: eventForm.value.title,
        description: eventForm.value.description,
        date: eventForm.value.date,
        time: eventForm.value.time,
        type: eventForm.value.type
      }

      events.value.push(newEvent)
      closeCreateEventModal()
    }

    const closeCreateEventModal = () => {
      showCreateEventModal.value = false
      eventForm.value = {
        title: '',
        description: '',
        date: '',
        time: '',
        type: 'event'
      }
    }

    const openEventDetail = (event) => {
      selectedEvent.value = event
    }

    const closeEventDetail = () => {
      selectedEvent.value = null
    }

    onMounted(() => {
      fetchProjectsAndEvents()
    })

    return {
      currentDate,
      currentView,
      events,
      showCreateEventModal,
      selectedEvent,
      views,
      dayHeaders,
      hours,
      eventForm,
      calendarDays,
      weekDays,
      formatMonthYear,
      formatDayOfWeek,
      formatHour,
      formatEventDate,
      isToday,
      navigateMonth,
      goToToday,
      getEventsForDay,
      getEventStyleClass,
      getEventPosition,
      addEventForDay,
      createEvent,
      closeCreateEventModal,
      openEventDetail,
      closeEventDetail,
    }
  }
}
</script>

<style scoped>
.calendar-grid {
  @apply bg-white;
}

.week-view, .day-view {
  @apply bg-white;
  max-height: 600px;
  overflow-y: auto;
}
</style> 