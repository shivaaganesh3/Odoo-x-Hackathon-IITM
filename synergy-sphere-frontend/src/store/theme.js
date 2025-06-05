import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // State
  const isDarkMode = ref(false)
  
  // Initialize theme from localStorage or system preference
  const initializeTheme = () => {
    const savedTheme = localStorage.getItem('synergy-sphere-theme')
    
    if (savedTheme) {
      isDarkMode.value = savedTheme === 'dark'
    } else {
      // Check system preference
      isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    
    applyTheme()
  }
  
  // Apply theme to document
  const applyTheme = () => {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
  
  // Toggle theme
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
  }
  
  // Watch for changes and persist to localStorage
  watch(isDarkMode, (newValue) => {
    localStorage.setItem('synergy-sphere-theme', newValue ? 'dark' : 'light')
    applyTheme()
  }, { immediate: false })
  
  // Listen for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    const savedTheme = localStorage.getItem('synergy-sphere-theme')
    // Only update if no manual preference is saved
    if (!savedTheme) {
      isDarkMode.value = e.matches
    }
  })
  
  return {
    isDarkMode,
    initializeTheme,
    toggleTheme,
    applyTheme
  }
}) 