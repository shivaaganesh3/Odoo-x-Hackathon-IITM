import { defineStore } from 'pinia'
import axios from '../axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null
  }),
  actions: {
    async login(email, password) {
      const res = await axios.post('/auth/login', { email, password })
      this.user = res.data.user
    },
    async register(name, email, password) {
      await axios.post('/auth/register', { name, email, password })
    },
    async fetchUser() {
      const res = await axios.get('/auth/whoami')
      this.user = res.data
    },
    logout() {
      this.user = null
      localStorage.removeItem('user')
    }
  }
})
