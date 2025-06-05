<template>
  <AppLayout>
    <div>
      <h1 class="text-3xl font-bold text-gray-900 mb-8">Project Details</h1>
      <div class="card p-6">
        <p class="text-gray-600">Project detail page coming soon...</p>
        <p class="text-sm text-gray-500 mt-2">Project ID: {{ $route.params.id }}</p>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '../components/AppLayout.vue'

export default {
  name: 'ProjectDetailPage',
  components: {
    AppLayout,
  }
}
</script> 