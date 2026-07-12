<template>
  <div style="padding: 2rem;">
    <h1>Admin Dashboard</h1>
    <p>Welcome back, {{ authStore.username }}!</p>
  </div>
</template>

<script>
import { authStore } from "../../store"

export default {
  name: "AdminDashboard",
  data() {
    return {
      authStore
    }
  }
}
</script>
