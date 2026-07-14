<template>
  <div style="max-width: 1200px; margin: 0 auto; padding: 2rem 1rem;">
    <h2 style="text-align: center; margin-bottom: 2rem; font-size: 2.5rem; color: var(--text-color);">Explore All Treks</h2>
    
    <!-- Search and Filter Form -->
    <div style="display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; margin-bottom: 3rem; background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
      <div style="flex: 1; min-width: 250px;">
        <input type="text" v-model="searchQuery" class="form-control" placeholder="Search by trek name or location..." style="height: 100%;">
      </div>
      <div style="width: 150px;">
        <input type="number" v-model="filterMaxPrice" class="form-control" placeholder="Max Price (₹)" style="height: 100%;" min="0" step="1">
      </div>
      <div style="width: 130px;">
        <input type="number" v-model="filterDuration" class="form-control" placeholder="Max Duration" style="height: 100%;" min="1" step="1">
      </div>
      <div style="width: 200px;">
        <select v-model="filterDifficulty" class="form-control" style="height: 100%;">
          <option value="">All Difficulties</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>
      <button @click="clearFilters" class="btn btn-secondary" style="display: flex; align-items: center; justify-content: center;">Clear</button>
    </div>
    <div v-if="loading" style="text-align: center; padding: 4rem; color: var(--secondary-color);">
      Loading treks...
    </div>
    
    <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2.5rem;">
      <div v-for="trek in filteredTreks" :key="trek.id" class="card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); transition: transform 0.2s;">
        <div :style="{
          height: '200px',
          backgroundImage: `url(${getCoverImageUrl(trek.cover_image)})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }"></div>
        
        <div style="padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.25rem;">
            <h3 style="margin: 0; font-size: 1.35rem;">{{ trek.name }}</h3>
            <strong style="color: var(--primary-color); font-size: 1.15rem;">₹{{ parseFloat(trek.price).toFixed(0) }}</strong>
          </div>
          
          <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.25rem 0;">📍 {{ trek.location }}</p>
          <div style="display: flex; justify-content: space-between; align-items: center; margin: 0.25rem 0 0.75rem 0;">
            <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0;">📅 {{ formatDate(trek.start_date) }} &nbsp;|&nbsp; ⏱️ {{ trek.duration }} Days</p>
            <span class="badge badge-active" style="padding: 0.15rem 0.5rem; font-size: 0.8rem;">{{ capitalize(trek.difficulty) }}</span>
          </div>
          
          <p v-if="trek.description" style="color: var(--secondary-color); font-size: 0.9rem; margin: 0.5rem 0 1.5rem 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;">{{ trek.description }}</p>
          <p v-else style="color: #9ca3af; font-style: italic; font-size: 0.9rem; margin: 0.5rem 0 1.5rem 0; line-height: 1.5;">No description provided.</p>
          
          <div style="margin-top: auto;">
            <router-link :to="'/trek/' + trek.id" class="btn btn-primary" style="display: block; width: 100%; box-sizing: border-box;">View Details</router-link>
          </div>
        </div>
      </div>
      
      <div v-if="filteredTreks.length === 0" style="grid-column: 1 / -1; text-align: center; padding: 4rem; background: #f9fafb; border-radius: 12px; color: var(--secondary-color);">
        <h3 style="margin-top: 0;">No Treks Found</h3>
        <p>Try adjusting your search criteria or clearing filters.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch, SERVER_URL } from "../utils/api"

export default {
  name: "PublicTreks",
  data() {
    return {
      treks: [],
      loading: true,
      searchQuery: "",
      filterMaxPrice: "",
      filterDifficulty: "",
      filterDuration: "",
      SERVER_URL
    }
  },
  computed: {
    filteredTreks() {
      return this.treks.filter(trek => {
        const searchLower = this.searchQuery.toLowerCase()
        const matchSearch = trek.name.toLowerCase().includes(searchLower) || trek.location.toLowerCase().includes(searchLower)
        const matchMaxPrice = this.filterMaxPrice === "" || parseFloat(trek.price) <= parseFloat(this.filterMaxPrice)
        const matchDifficulty = this.filterDifficulty === "" || trek.difficulty === this.filterDifficulty
        const matchDuration = this.filterDuration === "" || trek.duration <= parseInt(this.filterDuration)
        return matchSearch && matchMaxPrice && matchDifficulty && matchDuration
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
        const data = await apiFetch("/treks", { method: "GET" })
        this.treks = data
      } catch (err) {
        console.error("Failed to load treks:", err)
      } finally {
        this.loading = false
      }
    },
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
    },
    clearFilters() {
      this.searchQuery = ""
      this.filterMaxPrice = ""
      this.filterDifficulty = ""
      this.filterDuration = ""
    }
  }
}
</script>
