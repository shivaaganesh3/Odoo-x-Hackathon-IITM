<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useThemeStore } from './store/theme'

export default {
  name: 'App',
  setup() {
    const themeStore = useThemeStore()
    
    // Initialize theme on app mount
    onMounted(() => {
      themeStore.initializeTheme()
    })
    
    return {}
  }
}
</script>

<style>
@import './style.css';
</style>
