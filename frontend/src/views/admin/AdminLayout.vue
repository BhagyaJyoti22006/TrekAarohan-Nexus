<template>
  <div style="display: flex; height: calc(100vh - 60px); flex-grow: 1;">
    
    <div class="sidebar">
      <div class="sidebar-links">
        <router-link to="/admin" :class="{ active: $route.path === '/admin' }">TAC Overview</router-link>
        <router-link to="/admin/treks" :class="{ active: $route.path.startsWith('/admin/treks') }">Manage Treks</router-link>
        <router-link to="/admin/staffs" :class="{ active: $route.path.startsWith('/admin/staffs') }">Manage Staffs</router-link>
        <router-link to="/admin/trekkers" :class="{ active: $route.path.startsWith('/admin/trekkers') }">Manage Trekkers</router-link>
        <router-link to="/admin/bookings" :class="{ active: $route.path.startsWith('/admin/bookings') }">Manage Bookings</router-link>
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
  name: "AdminLayout",
  methods: {
    logout() {
      authStore.logout()
      this.$router.push("/login")
    }
  }
}
</script>
