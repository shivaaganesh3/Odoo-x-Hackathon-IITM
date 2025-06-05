<template>
  <AppLayout>
    <div>
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Teams</h1>
      
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="teams.length === 0" class="card p-8 text-center">
        <div class="text-gray-400 text-6xl mb-4">👥</div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">No Teams Found</h3>
        <p class="text-gray-600 mb-4">You're not part of any project teams yet.</p>
        <router-link to="/projects/create" class="btn-primary">
          Create Your First Project
        </router-link>
      </div>

      <!-- Teams Grid -->
      <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div 
          v-for="team in teams" 
          :key="team.team_id" 
          class="card p-6 hover:shadow-lg transition-shadow duration-300"
        >
          <!-- Team Header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex-1">
              <h3 class="text-xl font-semibold text-gray-900 mb-1">
                {{ team.team_name }}
              </h3>
              <div class="flex items-center space-x-2 text-sm text-gray-500">
                <span v-if="team.is_owner" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8z" clip-rule="evenodd"></path>
                  </svg>
                  Owner
                </span>
                <span v-else class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  <svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  Member
                </span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-blue-600">{{ team.member_count }}</div>
              <div class="text-xs text-gray-500">
                {{ team.member_count === 1 ? 'member' : 'members' }}
              </div>
            </div>
          </div>

          <!-- Team Description -->
          <p v-if="team.description" class="text-gray-600 text-sm mb-4 line-clamp-2">
            {{ team.description }}
          </p>

          <!-- Team Members Preview -->
          <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-gray-700">Members</h4>
              <button 
                v-if="team.is_owner"
                @click="openAddMemberModal(team)"
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                + Add Member
              </button>
            </div>
            
            <!-- Members List -->
            <div v-if="team.members.length > 0" class="space-y-2 max-h-32 overflow-y-auto">
              <div 
                v-for="member in team.members" 
                :key="member.id"
                class="flex items-center justify-between py-1"
              >
                <div class="flex items-center space-x-2">
                  <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-xs font-medium text-blue-600">
                      {{ getInitials(member.name || member.email) }}
                    </span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ member.name || 'No name' }}
                    </div>
                    <div class="text-xs text-gray-500">{{ member.email }}</div>
                  </div>
                </div>
                <button 
                  v-if="team.is_owner && member.id !== currentUserId"
                  @click="removeMember(team.team_id, member.id, member.name || member.email)"
                  class="text-red-600 hover:text-red-800 text-xs"
                  title="Remove member"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div v-else class="text-sm text-gray-500 italic">
              No members yet
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-between items-center pt-4 border-t border-gray-200">
            <router-link 
              :to="`/projects/${team.team_id}`"
              class="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View Project →
            </router-link>
            <div class="text-xs text-gray-400">
              Created {{ formatDate(team.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Add Member Modal -->
      <div v-if="showAddMemberModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
          <div class="mt-3 text-center">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
              Add Member to {{ selectedTeam?.team_name }}
            </h3>
            
            <form @submit.prevent="addMember" class="space-y-4">
              <div>
                <label for="memberEmail" class="block text-sm font-medium text-gray-700 text-left mb-1">
                  Member Email
                </label>
                <input
                  id="memberEmail"
                  v-model="newMemberEmail"
                  type="email"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter member's email address"
                />
              </div>
              
              <div class="flex space-x-3">
                <button
                  type="button"
                  @click="closeAddMemberModal"
                  class="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  :disabled="addingMember"
                  class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-200 disabled:opacity-50"
                >
                  {{ addingMember ? 'Adding...' : 'Add Member' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" class="fixed bottom-4 right-4 z-50">
        <div :class="[
          'px-6 py-3 rounded-lg shadow-lg text-white',
          messageType === 'success' ? 'bg-green-500' : 'bg-red-500'
        ]">
          {{ message }}
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '../components/AppLayout.vue'
import axios from '../axios'

export default {
  name: 'TeamPage',
  components: {
    AppLayout,
  },
  data() {
    return {
      teams: [],
      loading: true,
      showAddMemberModal: false,
      selectedTeam: null,
      newMemberEmail: '',
      addingMember: false,
      message: '',
      messageType: 'success',
      currentUserId: null
    }
  },
  async mounted() {
    await this.loadTeams()
    this.loadCurrentUser()
  },
  methods: {
    async loadCurrentUser() {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        this.currentUserId = user.id
      } catch (error) {
        console.error('Error loading current user:', error)
      }
    },
    
    async loadTeams() {
      try {
        this.loading = true
        const response = await axios.get('/team/')
        this.teams = response.data
      } catch (error) {
        console.error('Error loading teams:', error)
        this.showMessage('Error loading teams', 'error')
      } finally {
        this.loading = false
      }
    },

    openAddMemberModal(team) {
      this.selectedTeam = team
      this.newMemberEmail = ''
      this.showAddMemberModal = true
    },

    closeAddMemberModal() {
      this.showAddMemberModal = false
      this.selectedTeam = null
      this.newMemberEmail = ''
      this.addingMember = false
    },

    async addMember() {
      if (!this.newMemberEmail.trim()) return

      try {
        this.addingMember = true
        const response = await axios.post('/team/add-by-email', {
          project_id: this.selectedTeam.team_id,
          user_email: this.newMemberEmail.trim()
        })

        this.showMessage(response.data.message, 'success')
        this.closeAddMemberModal()
        await this.loadTeams() // Refresh teams to show new member
      } catch (error) {
        console.error('Error adding member:', error)
        const errorMessage = error.response?.data?.error || 'Error adding member'
        this.showMessage(errorMessage, 'error')
      } finally {
        this.addingMember = false
      }
    },

    async removeMember(teamId, userId, userName) {
      if (!confirm(`Are you sure you want to remove ${userName} from this team?`)) {
        return
      }

      try {
        await axios.post('/team/remove', {
          project_id: teamId,
          user_id: userId
        })

        this.showMessage('Member removed successfully', 'success')
        await this.loadTeams() // Refresh teams
      } catch (error) {
        console.error('Error removing member:', error)
        const errorMessage = error.response?.data?.error || 'Error removing member'
        this.showMessage(errorMessage, 'error')
      }
    },

    getInitials(name) {
      if (!name) return '?'
      const names = name.split(' ')
      if (names.length >= 2) {
        return (names[0][0] + names[1][0]).toUpperCase()
      }
      return name.substring(0, 2).toUpperCase()
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      })
    },

    showMessage(text, type = 'success') {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 4000)
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

.card {
  @apply bg-white rounded-lg shadow-md border border-gray-200;
}

.btn-primary {
  @apply bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition duration-200;
}
</style> 