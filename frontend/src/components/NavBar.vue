<template>
  <nav class="bg-blue-600 shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex justify-between">
        <div class="flex space-x-4">
          <!-- Logo -->
          <div>
            <router-link to="/" class="flex items-center py-5 px-2 text-white">
              <span class="font-bold text-xl">RosBag Visualizer</span>
            </router-link>
          </div>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-1">
            <router-link to="/" class="py-5 px-3 text-white hover:text-blue-200"
              >Home</router-link
            >
            <router-link
              to="/database"
              class="py-5 px-3 text-white hover:text-blue-200"
              >Database</router-link
            >
            <router-link
              to="/upload"
              class="py-5 px-3 text-white hover:text-blue-200"
              >Upload</router-link
            >
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <div class="md:hidden flex items-center">
          <button
            @click="toggleMobileMenu"
            class="mobile-menu-button p-2 text-white focus:outline-none"
          >
            <svg
              class="h-6 w-6"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div class="md:hidden" :class="{ hidden: !mobileMenuOpen }">
      <router-link
        to="/"
        class="block py-2 px-4 text-sm text-white hover:bg-blue-700"
        >Home</router-link
      >
      <router-link
        to="/database"
        class="block py-2 px-4 text-sm text-white hover:bg-blue-700"
        >Database</router-link
      >
      <router-link
        to="/upload"
        class="block py-2 px-4 text-sm text-white hover:bg-blue-700"
        >Upload</router-link
      >
    </div>
  </nav>
</template>

<script>
export default {
  name: "NavBar",
  data() {
    return {
      mobileMenuOpen: false,
    };
  },
  methods: {
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen;
    },
  },
};
</script>
