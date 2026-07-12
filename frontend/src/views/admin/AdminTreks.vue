<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Manage Treks</h2>
      <router-link to="/admin/treks/new" class="btn btn-accent">+ Add New Trek</router-link>
    </div>
    
    <!-- Search and Filters -->
    <div class="card" style="margin-bottom: 2rem; display: flex; gap: 1rem; align-items: flex-end; padding: 1.5rem; overflow-x: auto; white-space: nowrap;">
      <div style="flex-grow: 1; min-width: 200px;">
        <label class="form-label">Search</label>
        <input type="text" v-model="searchQuery" class="form-control" placeholder="Search by name or location...">
      </div>
      
      <div>
        <label class="form-label">Status</label>
        <select v-model="filterStatus" class="form-control" style="min-width: 130px;">
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="full">Full</option>
          <option value="ongoing">Ongoing</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
      
      <div>
        <label class="form-label">Difficulty</label>
        <select v-model="filterDifficulty" class="form-control" style="min-width: 130px;">
          <option value="">All Difficulties</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>
      
      <div>
        <label class="form-label">Duration</label>
        <input type="number" v-model="filterDuration" class="form-control" placeholder="Days" min="1" style="width: 80px;">
      </div>
      
      <div>
        <button class="btn btn-secondary" @click="clearFilters">Clear</button>
      </div>
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
          <tr v-for="trek in filteredTreks" :key="trek.id">
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
          <tr v-if="filteredTreks.length === 0 && !loading">
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
      loading: true,
      searchQuery: "",
      filterStatus: "",
      filterDifficulty: "",
      filterDuration: ""
    }
  },
  computed: {
    filteredTreks() {
      return this.treks.filter(trek => {
        const searchLower = this.searchQuery.toLowerCase()
        const matchSearch = trek.name.toLowerCase().includes(searchLower) || trek.location.toLowerCase().includes(searchLower)
        const matchStatus = this.filterStatus === "" || trek.status === this.filterStatus
        const matchDifficulty = this.filterDifficulty === "" || trek.difficulty === this.filterDifficulty
        const matchDuration = this.filterDuration === "" || trek.duration == this.filterDuration
        return matchSearch && matchStatus && matchDifficulty && matchDuration
      })
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
    clearFilters() {
      this.searchQuery = ""
      this.filterStatus = ""
      this.filterDifficulty = ""
      this.filterDuration = ""
    },
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    },
    capitalize(str) {
      if (!str) return ""
      return str.charAt(0).toUpperCase() + str.slice(1)
    }
  }
}
</script>
