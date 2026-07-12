<template>
  <div class="top-navbar">
    <router-link to="/" style="text-decoration: none;">
      <h2 style="margin:0; color: white;">TrekAarohan-Nexus</h2>
    </router-link>
    <div class="nav-links" style="display: flex; align-items: center;">
      <router-link to="/">Home</router-link>
      <router-link to="/treks">Browse Treks</router-link>
      <router-link to="/about">About Us</router-link>
      
      <template v-if="authStore.isAuthenticated">
        <template v-if="authStore.userRole === 'admin'">
          <router-link to="/admin" class="btn btn-outline" style="margin-left: 2rem; padding: 0.4rem 1rem;">Dashboard</router-link>
        </template>
        <template v-else-if="authStore.userRole === 'staff'">
          <router-link to="/staff" class="btn btn-outline" style="margin-left: 2rem; padding: 0.4rem 1rem;">Dashboard</router-link>
        </template>
        <template v-else>
          <router-link to="/trekker" class="btn btn-outline" style="margin-left: 2rem; padding: 0.4rem 1rem;">Dashboard</router-link>
        </template>
      </template>
      <template v-else>
        <router-link to="/login" class="btn btn-outline" style="margin-left: 2rem; padding: 0.4rem 1rem;">Login</router-link>
        <router-link to="/register" class="btn btn-accent" style="margin-left: 1rem; padding: 0.5rem 1rem;">Register</router-link>
      </template>
    </div>
  </div>
</template>

<script>
import { authStore } from "../store"

export default {
  name: "Navbar",
  data() {
    return {
      authStore
    }
  }
}
</script>
