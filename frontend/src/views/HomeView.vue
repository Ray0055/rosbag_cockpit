<template>
  <div>
    <div class="bg-white shadow-md rounded-lg p-6 mb-6">
      <h1 class="text-3xl font-bold mb-4">RosBag Visualizer Dashboard</h1>
      <p class="mb-4">
        Welcome to the RosBag Visualizer. This application allows you to upload, manage, and
        visualize ROS bag files.
      </p>
      <div class="flex space-x-4">
        <router-link
          to="/database"
          class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Browse Database
        </router-link>
        <router-link
          to="/upload"
          class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          Upload RosBag
        </router-link>
      </div>
    </div>

    <Dashboard />
  </div>
</template>

<script>
import Dashboard from '../components/Dashboard.vue'

export default {
  name: 'HomeView',
  components: {
    Dashboard,
  },
}
</script>
