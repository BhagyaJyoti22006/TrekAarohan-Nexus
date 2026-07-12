<template>
  <div style="display: flex; height: calc(100vh - 60px); flex-grow: 1;">
    
    <div class="sidebar">
      <div class="sidebar-links">
        <router-link to="/admin" exact-active-class="active">TAC Overview</router-link>
        <router-link to="/admin/treks" active-class="active">Manage Treks</router-link>
        <router-link to="/admin/staffs" active-class="active">Manage Staffs</router-link>
        <router-link to="/admin/trekkers" active-class="active">Manage Trekkers</router-link>
        <router-link to="/admin/bookings" active-class="active">Manage Bookings</router-link>
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
