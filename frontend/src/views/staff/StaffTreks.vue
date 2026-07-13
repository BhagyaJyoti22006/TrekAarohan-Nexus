<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>My Treks</h2>
    </div>
    
    <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading treks...
    </div>
    
    <div v-else-if="errorMessage" style="text-align: center; padding: 2rem; color: #dc2626;">
      {{ errorMessage }}
    </div>
    
    <div v-else-if="treks.length > 0" class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Trek Name</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Slots Available</th>
            <th>Participants</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trek in treks" :key="trek.id">
            <td><strong>{{ trek.name }}</strong></td>
            <td>{{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}</td>
            <td>
              <span :class="['badge', `badge-${trek.status}`]">{{ capitalize(trek.status) }}</span>
            </td>
            <td>{{ trek.slots_available }}</td>
            <td>{{ trek.active_participants }}</td>
            <td>
              <router-link 
                v-if="['completed', 'cancelled'].includes(trek.status)" 
                :to="`/staff/treks/${trek.id}`" 
                class="btn btn-secondary" 
                style="padding: 0.25rem 0.5rem; font-size: 0.8rem; text-decoration: none;"
              >
                View
              </router-link>
              <router-link 
                v-else
                :to="`/staff/treks/${trek.id}`" 
                class="btn btn-primary" 
                style="padding: 0.25rem 0.5rem; font-size: 0.8rem; text-decoration: none;"
              >
                Manage
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Trek Name</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Slots Available</th>
            <th>Participants</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colspan="6" style="text-align: center; color: var(--secondary-color);">You have no assigned treks.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "StaffTreks",
  data() {
    return {
      treks: [],
      loading: true,
      errorMessage: ""
    }
  },
  async mounted() {
    await this.fetchTreks()
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
    async fetchTreks() {
      this.loading = true
      try {
        const data = await apiFetch("/staff/treks")
        this.treks = data
      } catch (e) {
        this.errorMessage = e.message || "Failed to load treks"
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
