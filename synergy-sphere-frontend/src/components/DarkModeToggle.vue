<template>
  <button
    @click="toggleTheme"
    :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
    class="relative inline-flex items-center justify-center w-10 h-10 p-2 text-gray-400 dark:text-gray-300 hover:text-gray-500 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
  >
    <!-- Sun icon for light mode -->
    <transition
      enter-active-class="transition-all duration-300 ease-in-out"
      enter-from-class="opacity-0 rotate-90 scale-50"
      enter-to-class="opacity-100 rotate-0 scale-100"
      leave-active-class="transition-all duration-300 ease-in-out"
      leave-from-class="opacity-100 rotate-0 scale-100"
      leave-to-class="opacity-0 -rotate-90 scale-50"
    >
      <SunIcon
        v-if="!isDarkMode"
        key="sun"
        class="absolute w-5 h-5"
      />
    </transition>
    
    <!-- Moon icon for dark mode -->
    <transition
      enter-active-class="transition-all duration-300 ease-in-out"
      enter-from-class="opacity-0 -rotate-90 scale-50"
      enter-to-class="opacity-100 rotate-0 scale-100"
      leave-active-class="transition-all duration-300 ease-in-out"
      leave-from-class="opacity-100 rotate-0 scale-100"
      leave-to-class="opacity-0 rotate-90 scale-50"
    >
      <MoonIcon
        v-if="isDarkMode"
        key="moon"
        class="absolute w-5 h-5"
      />
    </transition>
  </button>
</template>

<script>
import { computed } from 'vue'
import { useThemeStore } from '../store/theme'
import { SunIcon, MoonIcon } from '@heroicons/vue/24/outline'

export default {
  name: 'DarkModeToggle',
  components: {
    SunIcon,
    MoonIcon,
  },
  setup() {
    const themeStore = useThemeStore()
    
    const isDarkMode = computed(() => themeStore.isDarkMode)
    
    const toggleTheme = () => {
      themeStore.toggleTheme()
    }
    
    return {
      isDarkMode,
      toggleTheme,
    }
  },
}
</script>

<style scoped>
/* Additional styles for smooth transitions */
button {
  overflow: hidden;
}

/* Ensure icons are properly positioned */
.absolute {
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style> 