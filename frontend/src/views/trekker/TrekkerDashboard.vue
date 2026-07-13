<template>
  <div>
    <h2>Welcome back, {{ profile.name }}</h2>
    
    <div v-if="!loading && profile.is_blacklisted" style="background-color: #fef2f2; color: #991b1b; padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; margin-bottom: 2rem; border: 1px solid #fecaca; text-align: center;">
        <h3 style="margin-top: 0; color: #7f1d1d;">⚠️ Account Suspended</h3>
        <p style="margin-bottom: 0;">Your account has been blacklisted. You can view your past and current bookings, but you cannot book new treks. If you believe this is an error, please contact an administrator.</p>
    </div>
    
    <div v-if="!loading && (!profile.emergency_phone || !profile.emergency_relation)" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 6px; margin-top: 1.5rem; margin-bottom: 2rem; border-left: 4px solid #ef4444; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong>Action Required:</strong> Please complete your emergency contact information before your next trek.
        </div>
        <router-link to="/trekker/profile" class="btn btn-primary" style="padding: 0.4rem 1rem; background-color: #991b1b; color: white; border: none;">Update Profile</router-link>
    </div>
    
    <p v-if="loading">Loading dashboard...</p>
    <p v-else>Placeholder for Dashboard quick stats and available treks.</p>
  </div>
</template>

<script>
import { authStore } from "../../store"
import { apiFetch } from "../../utils/api"

export default {
  name: "TrekkerDashboard",
  data() {
    return {
      authStore,
      profile: {},
      loading: true
    }
  },
  async mounted() {
    try {
      this.profile = await apiFetch("/trekker/profile")
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  }
}
</script>
