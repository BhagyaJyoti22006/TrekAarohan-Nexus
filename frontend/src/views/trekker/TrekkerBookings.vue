<template>
  <div>
    <div v-if="successMessage" style="background-color: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #bbf7d0;">
      {{ successMessage }}
    </div>
    
    <h2>My Bookings</h2>
    
    <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading your bookings...
    </div>
    
    <div v-else-if="bookings.length > 0">
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 2.5rem; margin-top: 2rem;">
        <div v-for="booking in bookings" :key="booking.id" class="card" style="padding: 0; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); transition: transform 0.2s;">
          <div 
            :style="{
              height: '200px', 
              backgroundImage: `url(${getCoverImageUrl(booking.trek.cover_image)})`, 
              backgroundSize: 'cover', 
              backgroundPosition: 'center'
            }">
          </div>
          
          <div style="padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.25rem;">
              <h3 style="margin: 0; font-size: 1.35rem;">{{ booking.trek.name }}</h3>
              <span class="badge badge-active" style="padding: 0.25rem 0.75rem; background-color: #dcfce7; color: #166534; font-size: 0.9rem;">Confirmed</span>
            </div>
            
            <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0;">📍 {{ booking.trek.location }}</p>
            <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0;">📅 {{ formatDate(booking.trek.start_date) }} to {{ formatDate(booking.trek.end_date) }}</p>
            <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 0.5rem 0; font-weight: 500;">⏳ {{ capitalize(booking.trek.difficulty) }} difficulty trek for {{ booking.trek.duration }} days</p>
            <p style="color: var(--secondary-color); font-size: 0.95rem; margin: 0 0 1.5rem 0; line-height: 1.5;"><strong>Booked On:</strong> {{ formatDate(booking.booking_date) }}</p>
            
            <div style="margin-top: auto; display: flex; gap: 1rem;">
              <router-link :to="`/trek/${booking.trek.id}`" class="btn btn-primary" style="flex: 1; text-align: center; box-sizing: border-box;">View Details</router-link>
              <button @click="cancelBooking(booking)" class="btn" style="background-color: transparent; color: #ef4444; border: 1px solid #ef4444; cursor: pointer; text-align: center; box-sizing: border-box;">Cancel Booking</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="card" style="margin-top: 2rem; text-align: center; padding: 3rem;">
      <h3 style="margin-top: 0; color: var(--text-color);">No Active Bookings</h3>
      <p style="color: var(--secondary-color); margin-bottom: 0;">You don't have any upcoming treks planned yet.</p>
    </div>
  </div>
</template>

<script>
import { apiFetch, SERVER_URL } from "../../utils/api"

export default {
  name: "TrekkerBookings",
  data() {
    return {
      bookings: [],
      loading: true,
      successMessage: ""
    }
  },
  async mounted() {
    // Check for success message from redirection
    if (this.$route.query.message) {
      this.successMessage = this.$route.query.message
      // Clean up the URL to remove the query parameter
      this.$router.replace({ path: '/trekker/bookings' })
    }
    await this.fetchBookings()
  },
  methods: {
    async fetchBookings() {
      this.loading = true
      try {
        const data = await apiFetch("/trekker/bookings", { method: "GET" })
        this.bookings = data
      } catch (err) {
        console.error("Failed to load bookings:", err)
      } finally {
        this.loading = false
      }
    },
    async cancelBooking(booking) {
      if (confirm(`Are you sure you want to cancel your booking for ${booking.trek.name}? This action cannot be undone.`)) {
        try {
          const res = await apiFetch(`/trekker/bookings/${booking.id}/cancel`, { method: "POST" })
          this.successMessage = res.message || `Successfully cancelled booking for ${booking.trek.name}.`
          await this.fetchBookings()
        } catch (err) {
          alert(err.message || "Failed to cancel booking.")
        }
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
    }
  }
}
</script>
