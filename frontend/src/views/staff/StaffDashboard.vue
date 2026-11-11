<template>
  <div>
    <h2>Welcome back, {{ profile.name }}</h2>
    
    <div v-if="!loading && profile.is_blacklisted" style="background-color: #fef2f2; color: #991b1b; padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; margin-bottom: 2rem; border: 1px solid #fecaca; text-align: center;">
      <h3 style="margin-top: 0; color: #7f1d1d;">⚠️ Account Suspended</h3>
      <p style="margin-bottom: 0;">Your staff account has been suspended. You cannot be assigned to new treks. If you believe this is an error, please contact an administrator.</p>
    </div>
    
    <div v-if="!loading && (!profile.emergency_phone || !profile.emergency_relation)" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 6px; margin-top: 1.5rem; margin-bottom: 2rem; border-left: 4px solid #ef4444; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <strong>Action Required:</strong> Please complete your emergency contact information.
      </div>
      <router-link to="/staff/profile" class="btn btn-danger" style="padding: 0.4rem 1rem;">Update Profile</router-link>
    </div>
    
    <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading dashboard...
    </div>
    
    <div v-else-if="stats">
      <!-- Quick Stats -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem; margin-bottom: 3rem;">
        <div class="card" style="text-align: center; border-top: 4px solid var(--accent-color);">
          <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Total Assigned Treks</h3>
          <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--accent-color);">{{ stats.total_treks }}</p>
        </div>
        <div class="card" style="text-align: center; border-top: 4px solid var(--primary-color);">
          <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Active Participants</h3>
          <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--primary-color);">{{ stats.active_participants }}</p>
        </div>
        <div class="card" style="text-align: center; border-top: 4px solid var(--secondary-color);">
          <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Unique Trekkers</h3>
          <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--secondary-color);">{{ stats.unique_trekkers }}</p>
        </div>
      </div>
      
      <!-- Ongoing Treks Section -->
      <div style="margin-bottom: 3rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1.5rem;">
          <h2 style="margin: 0; font-size: 1.5rem;">Ongoing Treks</h2>
          <router-link to="/staff/treks" style="color: var(--primary-color); text-decoration: none; font-weight: 500;">View All Assigned Treks &rarr;</router-link>
        </div>
        
        <div v-if="stats.ongoing_treks && stats.ongoing_treks.length > 0" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem;">
          <div v-for="t in stats.ongoing_treks" :key="t.id" class="card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); transition: transform 0.2s;">
            <div :style="{ height: '180px', backgroundImage: `url(${getCoverImageUrl(t.cover_image)})`, backgroundSize: 'cover', backgroundPosition: 'center' }"></div>
            
            <div style="padding: 1.25rem; display: flex; flex-direction: column; flex-grow: 1;">
              <h3 style="margin: 0 0 0.5rem 0; font-size: 1.25rem;">{{ t.name }}</h3>
              
              <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0;">📍 {{ t.location }}</p>
              <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 1.5rem 0;">📅 {{ formatDate(t.start_date) }} to {{ formatDate(t.end_date) }}</p>
              
              <div style="margin-top: auto; text-align: center;">
                <router-link :to="`/staff/treks/${t.id}`" class="btn btn-primary" style="width: 100%; display: block; box-sizing: border-box;">Manage Trek</router-link>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="card" style="text-align: center; padding: 3rem; color: var(--secondary-color);">
          <p style="margin: 0;">You currently have no ongoing treks.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch, SERVER_URL } from "../../utils/api"

export default {
  name: "StaffDashboard",
  data() {
    return {
      profile: {},
      stats: null,
      loading: true
    }
  },
  async mounted() {
    try {
      this.profile = await apiFetch("/staff/profile")
      this.stats = await apiFetch("/staff/dashboard")
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    },
    getCoverImageUrl(path) {
      if (path) {
        return `${SERVER_URL}${path}`
      }
      return `${SERVER_URL}/static/images/trek.jpg`
    }
  }
}
</script>
