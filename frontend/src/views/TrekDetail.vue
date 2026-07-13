<template>
  <div v-if="trek" style="max-width: 900px; margin: 0 auto; padding-bottom: 4rem;">
    <router-link to="/treks" style="color: var(--secondary-color); text-decoration: none; display: inline-block; margin-bottom: 1rem; margin-top: 2rem;">&larr; Back to Treks</router-link>
    
    <div class="card" style="padding: 0; overflow: hidden;">
      <div 
        :style="{
          height: '450px',
          backgroundImage: `url(${getCoverImageUrl(trek.cover_image)})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }"
      ></div>
      
      <div style="padding: 2.5rem;">
        <!-- Header & Price -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <h1 style="margin: 0; color: var(--text-color); font-size: 2.5rem;">{{ trek.name }}</h1>
          <h2 style="margin: 0; font-size: 2rem;">₹{{ parseFloat(trek.price).toFixed(2) }}</h2>
        </div>
        
        <!-- Badges -->
        <div style="display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;">
          <span class="badge" style="font-size: 1rem; padding: 0.5rem 1rem; background-color: var(--primary-color); color: white;">{{ capitalize(trek.difficulty) }} Difficulty</span>
          <span class="badge badge-open" style="font-size: 1rem; padding: 0.5rem 1rem;">📍 {{ trek.location }}</span>
          <span class="badge badge-open" style="font-size: 1rem; padding: 0.5rem 1rem;">🧑‍🤝‍🧑 {{ trek.slots_available }} Slots Left</span>
          <span class="badge" :class="'badge-' + trek.status" style="font-size: 1rem; padding: 0.5rem 1rem; margin-left: auto;">{{ capitalize(trek.status) }}</span>
        </div>
        
        <!-- Dates Row -->
        <div style="display: flex; gap: 4rem; margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border-color);">
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Start Date</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ formatDate(trek.start_date) }}</p>
          </div>
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">End Date</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ formatDate(trek.end_date) }}</p>
          </div>
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Duration</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ trek.duration }} Days</p>
          </div>
        </div>
        
        <!-- Description & Staff Grid -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 3rem;">
          <div>
            <h3 style="margin-top: 0; font-size: 1.5rem;">About This Trek</h3>
            <div v-if="trek.description" style="line-height: 1.8; color: var(--text-color); font-size: 1.05rem; white-space: pre-wrap;">{{ trek.description }}</div>
            <div v-else style="line-height: 1.8; color: #9ca3af; font-style: italic; font-size: 1.05rem;">No description provided.</div>
          </div>
          
          <div>
            <h3 style="margin-top: 0; font-size: 1.5rem;">Your Guide</h3>
            <h4 style="margin: 0 0 0.5rem 0; font-size: 1.2rem; color: var(--primary-color);">{{ trek.staff_name }}</h4>
            <p style="margin: 0 0 1rem 0; font-weight: bold; color: var(--text-color);">{{ trek.staff_completed_treks }} Past Treks Completed</p>
            <p style="margin: 0; color: var(--secondary-color); font-size: 0.95rem; line-height: 1.6;">
              {{ trek.staff_experience || 'An experienced guide ready to lead you on this adventure.' }}
            </p>
          </div>
        </div>
        
        <!-- Call to Action -->
        <div style="margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border-color); text-align: center;">
          <router-link v-if="!isAuthenticated" to="/login" class="btn btn-primary" style="padding: 1rem 4rem; font-size: 1.2rem;">Log in to Book</router-link>
          <div v-else-if="userRole !== 'trekker'" class="badge" style="padding: 1rem 4rem; font-size: 1.2rem; background-color: var(--secondary-color); color: white;">
            Only Trekkers can book
          </div>
          <div v-else-if="trek.booking_status === 'completed'" class="badge badge-special" style="padding: 1rem 4rem; font-size: 1.2rem;">
            🏆 Trek Completed
          </div>
          <div v-else-if="trek.booking_status" class="badge" style="padding: 1rem 4rem; font-size: 1.2rem; background-color: var(--secondary-color); color: white;">
            BOOKED
          </div>
          <div v-else-if="trek.status === 'full'" class="badge" style="padding: 1rem 4rem; font-size: 1.2rem; background-color: #ef4444; color: white;">
            Sold Out
          </div>
          <div v-else-if="trek.status !== 'open'" class="badge" style="padding: 1rem 4rem; font-size: 1.2rem; background-color: var(--primary-color); color: white;">
            Booking Closed ({{ capitalize(trek.status) }})
          </div>
          
          <button v-else @click="bookTrek" class="btn btn-accent" style="padding: 1rem 4rem; font-size: 1.2rem; border-radius: 8px;">
            Book This Trek
          </button>
        </div>
        
      </div>
    </div>
  </div>
  <div v-else-if="loading" style="text-align: center; padding: 4rem; color: var(--secondary-color);">
    Loading trek details...
  </div>
  <div v-else style="text-align: center; padding: 4rem; color: #991b1b;">
    {{ error || 'Trek not found.' }}
  </div>
</template>

<script>
import { apiFetch, SERVER_URL } from "../utils/api"
import { authStore } from "../store"

export default {
  name: "TrekDetail",
  data() {
    return {
      trek: null,
      loading: true,
      error: null
    }
  },
  computed: {
    isAuthenticated() {
      return authStore.isAuthenticated
    },
    userRole() {
      return authStore.userRole
    }
  },
  async mounted() {
    await this.fetchTrek()
  },
  methods: {
    async fetchTrek() {
      this.loading = true
      try {
        const id = this.$route.params.id
        const data = await apiFetch(`/treks/${id}`, { method: "GET" })
        this.trek = data
      } catch (err) {
        this.error = "Failed to load trek details."
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
    },
    capitalize(str) {
      if (!str) return ""
      return str.charAt(0).toUpperCase() + str.slice(1)
    },
    getCoverImageUrl(path) {
      if (path) {
        return `${SERVER_URL}${path}`
      }
      return `${SERVER_URL}/static/images/trek.jpg` // Default image from backend
    },
    async bookTrek() {
      try {
        await apiFetch(`/trekker/treks/${this.trek.id}/book`, { method: "POST" })
        alert("Booking successful! Get ready for your adventure.")
        await this.fetchTrek() // Refresh data
      } catch (err) {
        alert(err.message || "Failed to book the trek.")
      }
    }
  }
}
</script>
