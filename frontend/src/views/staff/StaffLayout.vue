<template>
  <div style="display: flex; height: calc(100vh - 60px); flex-grow: 1;">
    
    <div class="sidebar">
      <div class="sidebar-links">
        <router-link to="/staff" :class="{ active: $route.path === '/staff' }">My Dashboard</router-link>
        <router-link to="/staff/treks" :class="{ active: $route.path.startsWith('/staff/treks') }">My Treks</router-link>
        <router-link to="/staff/participants" :class="{ active: $route.path.startsWith('/staff/participants') }">All Participants</router-link>
        <router-link to="/staff/profile" :class="{ active: $route.path.startsWith('/staff/profile') }">Profile Settings</router-link>
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
  name: "StaffLayout",
  methods: {
    logout() {
      authStore.logout()
      this.$router.push("/login")
    }
  }
}
</script>
