<template>
  <div style="padding: 2rem;">
    <h1>Trekker Dashboard</h1>
    <p>Welcome back, {{ authStore.username }}!</p>
  </div>
</template>

<script>
import { authStore } from "../store"

export default {
  name: "TrekkerDashboard",
  data() {
    return {
      authStore
    }
  }
}
</script>
