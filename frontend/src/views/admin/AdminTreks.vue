<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Manage Treks</h2>
      <router-link to="/admin/treks/new" class="btn btn-accent">+ Add New Trek</router-link>
    </div>
    
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>Dates</th>
            <th>Duration</th>
            <th>Difficulty</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trek in treks" :key="trek.id">
            <td><strong>#{{ trek.id }}</strong></td>
            <td><strong>{{ trek.name }}</strong></td>
            <td>{{ trek.location }}</td>
            <td>
              {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}
            </td>
            <td>
              <span style="color: var(--secondary-color);">{{ trek.duration }} Days</span>
            </td>
            <td>
              <span style="text-transform: capitalize;">{{ trek.difficulty }}</span>
            </td>
            <td>
              <span class="badge" :class="'badge-' + trek.status">{{ capitalize(trek.status) }}</span>
            </td>
            <td>
              <!-- Edit/View based on status -->
              <router-link :to="'/admin/treks/' + trek.id + '/edit'" class="btn" :class="['completed', 'cancelled'].includes(trek.status) ? 'btn-secondary' : 'btn-primary'" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-right: 0.5rem;">
                {{ ['completed', 'cancelled'].includes(trek.status) ? 'View' : 'Edit' }}
              </router-link>
              <router-link :to="'/trek/' + trek.id" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Show</router-link>
            </td>
          </tr>
          <tr v-if="treks.length === 0 && !loading">
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
              No treks found. Click "+ Add New Trek" to create one.
            </td>
          </tr>
          <tr v-if="loading">
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
              Loading...
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminTreks",
  data() {
    return {
      treks: [],
      loading: true
    }
  },
  async mounted() {
    await this.fetchTreks()
  },
  methods: {
    async fetchTreks() {
      this.loading = true
      try {
        const data = await apiFetch("/admin/treks", { method: "GET" })
        this.treks = data
      } catch (err) {
        console.error("Failed to load treks:", err.message)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    },
    capitalize(str) {
      if (!str) return ""
      return str.charAt(0).toUpperCase() + str.slice(1)
    }
  }
}
</script>
