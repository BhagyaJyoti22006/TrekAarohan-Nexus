<template>
  <div style="display: flex; flex-direction: column; min-height: 100vh;">
    <Navbar />
    
    <div class="app-content" style="flex-grow: 1; background: white; padding: 0;">
      <!-- Router View will render the matched component here -->
      <router-view></router-view>
      
      <!-- Placeholder Home -->
      <div style="padding: 3rem; text-align: center;" v-if="$route.path === '/'">
        <h1>Welcome to TrekAarohan-Nexus</h1>
        <p>The Vue.js frontend is successfully running!</p>
      </div>
    </div>
    
    <Footer v-if="isPublicPage" />
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue"
import Footer from "./components/Footer.vue"

export default {
  name: "App",
  components: {
    Navbar,
    Footer
  },
  computed: {
    isPublicPage() {
      const p = this.$route.path
      return !p.startsWith("/admin") && !p.startsWith("/staff") && !p.startsWith("/trekker")
    }
  }
}
</script>
