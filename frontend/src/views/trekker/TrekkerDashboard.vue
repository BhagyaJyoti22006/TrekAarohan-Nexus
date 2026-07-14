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
    
    <!-- Quick Stats -->
    <div v-if="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem; margin-bottom: 3rem;">
        <div class="card" style="text-align: center; border-top: 4px solid var(--accent-color);">
            <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Upcoming Treks</h3>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--accent-color);">{{ stats.upcoming_count }}</p>
        </div>
        <div class="card" style="text-align: center; border-top: 4px solid var(--primary-color);">
            <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Completed Treks</h3>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--primary-color);">{{ stats.completed_count }}</p>
        </div>
        <div class="card" style="text-align: center; border-top: 4px solid var(--text-color);">
            <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Total Bookings</h3>
            <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--text-color);">{{ stats.total_count }}</p>
        </div>
    </div>
    
    <!-- Available Treks -->
    <div style="margin-bottom: 3rem;" v-if="availableTreks">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
            <h2 style="margin: 0; font-size: 1.5rem;">Available Treks</h2>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end;">
                <input type="text" v-model="searchQuery" placeholder="Search treks or locations..." class="form-control" style="width: 200px; margin-bottom: 0;">
                <select v-model="difficultyFilter" class="form-control" style="width: 130px; margin-bottom: 0;">
                    <option value="">All Difficulties</option>
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                </select>
                <input type="number" v-model="maxPriceFilter" placeholder="Max ₹" class="form-control" style="width: 100px; margin-bottom: 0;" min="0">
                <input type="number" v-model="maxDurationFilter" placeholder="Max Days" class="form-control" style="width: 100px; margin-bottom: 0;" min="1">
                <button @click="searchQuery = ''; difficultyFilter = ''; maxPriceFilter = ''; maxDurationFilter = ''" class="btn btn-secondary">Clear</button>
            </div>
        </div>
        
        <div v-if="availableTreks.length === 0" class="card" style="text-align: center; padding: 3rem; color: var(--secondary-color);">
            <p style="margin: 0;">No open treks available at the moment. Check back later!</p>
        </div>
        <div v-else-if="filteredTreks.length > 0" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2.5rem;">
            <div v-for="t in filteredTreks" :key="t.id" class="card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); transition: transform 0.2s;">
                <div :style="{ height: '200px', backgroundImage: `url(${getCoverImageUrl(t.cover_image)})`, backgroundSize: 'cover', backgroundPosition: 'center' }"></div>
                
                <div style="padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.25rem;">
                        <h3 style="margin: 0; font-size: 1.35rem;">{{ t.name }}</h3>
                        <span style="font-weight: bold; font-size: 1.2rem; color: var(--primary-color);">₹{{ t.price.toFixed(2) }}</span>
                    </div>
                    
                    <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0;">📍 {{ t.location }}</p>
                    <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0;">📅 {{ formatDate(t.start_date) }} to {{ formatDate(t.end_date) }}</p>
                    <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 1.5rem 0; font-weight: 500;">⏳ {{ capitalize(t.difficulty) }} difficulty trek for {{ t.duration }} days</p>
                    
                    <div style="margin-top: auto; text-align: center;">
                        <router-link :to="`/trek/${t.id}`" class="btn btn-primary" style="width: 100%; display: block; box-sizing: border-box;">View Details</router-link>
                    </div>
                </div>
            </div>
        </div>
        <div v-else class="card" style="text-align: center; padding: 3rem; color: var(--secondary-color);">
            <p style="margin: 0;">No available treks match your search criteria.</p>
        </div>
    </div>
  </div>
</template>

<script>
import { authStore } from "../../store"
import { apiFetch, SERVER_URL } from "../../utils/api"

export default {
  name: "TrekkerDashboard",
  data() {
    return {
      authStore,
      profile: {},
      stats: null,
      availableTreks: null,
      loading: true,
      searchQuery: "",
      difficultyFilter: "",
      maxPriceFilter: "",
      maxDurationFilter: ""
    }
  },
  computed: {
    filteredTreks() {
      if (!this.availableTreks) return []
      let filtered = this.availableTreks
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(t => 
          t.name.toLowerCase().includes(query) || 
          t.location.toLowerCase().includes(query)
        )
      }
      if (this.difficultyFilter) {
        filtered = filtered.filter(t => t.difficulty === this.difficultyFilter)
      }
      if (this.maxPriceFilter) {
        filtered = filtered.filter(t => t.price <= parseFloat(this.maxPriceFilter))
      }
      if (this.maxDurationFilter) {
        filtered = filtered.filter(t => t.duration <= parseInt(this.maxDurationFilter))
      }
      return filtered
    }
  },
  async mounted() {
    try {
      this.profile = await apiFetch("/trekker/profile")
      this.stats = await apiFetch("/trekker/dashboard")
      this.availableTreks = await apiFetch("/trekker/available_treks")
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
    capitalize(str) {
      if (!str) return ""
      return str.charAt(0).toUpperCase() + str.slice(1)
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
