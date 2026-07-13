<template>
  <div style="display: flex; height: calc(100vh - 60px); flex-grow: 1;">
    
    <div class="sidebar">
      <div class="sidebar-links">
        <router-link to="/trekker" :class="{ active: $route.path === '/trekker' }">My Dashboard</router-link>
        <router-link to="/trekker/bookings" :class="{ active: $route.path.startsWith('/trekker/bookings') }">My Bookings</router-link>
        <router-link to="/trekker/history" :class="{ active: $route.path.startsWith('/trekker/history') }">Trek History</router-link>
        <router-link to="/trekker/profile" :class="{ active: $route.path.startsWith('/trekker/profile') }">Profile Settings</router-link>
      </div>
      
      <div class="sidebar-bottom">
        <a href="#" @click.prevent="logout">Log out</a>
      </div>
    </div>
    
    <div style="flex-grow: 1; background: white; padding: 2.5rem; overflow-y: auto;">
      <router-view></router-view>
    </div>
  
  </div>
</template>

<script>
import { authStore } from "../../store"

export default {
  name: "TrekkerLayout",
  methods: {
    logout() {
      authStore.logout()
      this.$router.push("/login")
    }
  }
}
</script>
