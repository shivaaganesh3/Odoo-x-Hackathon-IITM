import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' // ✅ Use external router file

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Initialize auth store and fetch user if logged in
;(async () => {
  const { useAuthStore } = await import('./store/auth')
  const authStore = useAuthStore()
  try {
    await authStore.fetchUser()
  } catch (error) {
    // User not logged in or session expired - this is expected
    console.log('No active session found')
  }
  
  app.mount('#app')
})()
