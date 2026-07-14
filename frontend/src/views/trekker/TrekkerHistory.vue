<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h2 style="margin: 0;">Trek History</h2>
      <button v-if="bookings.length > 0" @click="exportHistory" class="btn btn-accent" :disabled="exporting">
        {{ exporting ? "Exporting..." : "Export Booking History" }}
      </button>
    </div>
    
    <div v-if="successMessage" style="background-color: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #bbf7d0;">
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #fecaca;">
      {{ errorMessage }}
    </div>
    
    <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading historical bookings...
    </div>
    
    <div v-else-if="bookings.length > 0" class="card" style="margin-top: 2rem; padding: 0;">
      <div class="data-table-wrapper" style="box-shadow: none;">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Trek Name</th>
              <th>Location</th>
              <th>Trek Dates</th>
              <th>Status</th>
              <th>Details</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in bookings" :key="booking.id">
              <td>#{{ booking.id }}</td>
              <td>
                <strong>{{ booking.trek.name }}</strong>
              </td>
              <td>{{ booking.trek.location }}</td>
              <td>
                {{ formatDate(booking.trek.start_date) }} to <br> 
                {{ formatDate(booking.trek.end_date) }}
              </td>
              <td>
                <span v-if="booking.status === 'completed'" class="badge badge-approved">Completed</span>
                <span v-else class="badge badge-blacklisted">Cancelled</span>
              </td>
              <td>
                <span v-if="booking.status === 'completed'" style="color: var(--secondary-color); font-size: 0.9rem;">
                  Booked: {{ formatDate(booking.booking_date) }}
                </span>
                <span v-else>
                  <span style="color: var(--secondary-color); font-size: 0.9rem;">Booked: {{ formatDate(booking.booking_date) }}</span><br>
                  <span style="color: var(--danger-color); font-size: 0.9rem;">Cancelled: {{ booking.cancelled_date ? formatDate(booking.cancelled_date) : formatDate(booking.booking_date) }}</span>
                </span>
              </td>
              <td>
                <router-link :to="`/trek/${booking.trek.id}`" class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">View Trek</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div v-else class="card" style="margin-top: 2rem; text-align: center; padding: 3rem;">
      <h3 style="margin-top: 0; color: var(--text-color);">No Historical Bookings</h3>
      <p style="color: var(--secondary-color); margin-bottom: 0;">You don't have any completed or cancelled treks yet.</p>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "TrekkerHistory",
  data() {
    return {
      bookings: [],
      loading: true,
      exporting: false,
      successMessage: "",
      errorMessage: ""
    }
  },
  async mounted() {
    await this.fetchHistory()
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    },
    async fetchHistory() {
      this.loading = true
      try {
        const data = await apiFetch("/trekker/history")
        this.bookings = data
      } catch (e) {
        this.errorMessage = e.message || "Failed to load history."
      } finally {
        this.loading = false
      }
    },
    async exportHistory() {
      this.exporting = true
      this.successMessage = ""
      this.errorMessage = ""
      try {
        const res = await apiFetch("/trekker/export_history", { method: "POST" })
        this.successMessage = res.message || "Export initiated."
      } catch (e) {
        this.errorMessage = e.message || "Failed to start export."
      } finally {
        this.exporting = false
      }
    }
  }
}
</script>
