<template>
  <div class="min-h-screen bg-gray-100">
    <NavBar />
    <main class="container mx-auto py-6 px-4">
      <router-view />
    </main>
  </div>
</template>
<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar,
  },
}
</script>
