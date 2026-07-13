<template>
  <div>
    <div v-if="successMessage" style="background-color: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #bbf7d0;">
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #fecaca;">
      {{ errorMessage }}
    </div>
    
    <h2>All Bookings</h2>
    
    <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading bookings...
    </div>
    
    <div v-else-if="bookings.length > 0" class="data-table-wrapper" style="margin-top: 2rem;">
      <table class="data-table">
        <thead>
          <tr>
            <th>Booking ID</th>
            <th>Trek</th>
            <th>Trekker</th>
            <th>Contact</th>
            <th>Emergency</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in bookings" :key="booking.id">
            <td>#{{ booking.id }}</td>
            <td>
              <strong>{{ booking.trek.name }}</strong><br>
              <span style="color: var(--secondary-color);">{{ formatDate(booking.trek.start_date) }}</span>
            </td>
            <td>
              <strong>{{ booking.user.name }}</strong><br>
              <span style="font-size: 0.85rem; color: var(--secondary-color);">{{ booking.user.username }}</span>
            </td>
            <td>
              {{ booking.user.email }}<br>
              {{ booking.user.phone || "N/A" }}
            </td>
            <td>
              {{ booking.user.emergency_relation || "N/A" }}<br>
              {{ booking.user.emergency_phone || "N/A" }}
            </td>
            <td>
              <span v-if="booking.status === 'booked'" class="badge badge-active">Active</span>
              <span v-else-if="booking.status === 'cancelled'" class="badge badge-blacklisted">Cancelled</span>
              <span v-else-if="booking.status === 'completed'" class="badge badge-active">Completed</span>
            </td>
            <td>
              <button 
                v-if="booking.status === 'booked'"
                @click="cancelBooking(booking.id)"
                class="btn btn-danger" 
                style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" 
                :disabled="cancellingId === booking.id"
              >
                {{ cancellingId === booking.id ? "Cancelling..." : "Cancel" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <p v-else style="color: var(--secondary-color); text-align: center; padding: 2rem 0;">
      No bookings found in the system.
    </p>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminBookings",
  data() {
    return {
      bookings: [],
      loading: true,
      successMessage: "",
      errorMessage: "",
      cancellingId: null
    }
  },
  async mounted() {
    await this.fetchBookings()
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    },
    async fetchBookings() {
      this.loading = true
      try {
        const data = await apiFetch("/admin/bookings")
        this.bookings = data
      } catch (e) {
        this.errorMessage = e.message || "Failed to load bookings"
      } finally {
        this.loading = false
      }
    },
    async cancelBooking(bookingId) {
      if (!confirm('Are you sure you want to cancel this booking? This will reopen a slot.')) {
        return
      }
      this.successMessage = ""
      this.errorMessage = ""
      this.cancellingId = bookingId
      try {
        const res = await apiFetch(`/admin/cancel_booking/${bookingId}`, {
          method: "POST"
        })
        this.successMessage = res.message || "Booking cancelled successfully."
        await this.fetchBookings()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (e) {
        this.errorMessage = e.message || "Failed to cancel booking"
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } finally {
        this.cancellingId = null
      }
    }
  }
}
</script>
