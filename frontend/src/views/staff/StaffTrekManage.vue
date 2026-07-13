<template>
  <div v-if="loading" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
    Loading trek details...
  </div>
  <div v-else-if="errorMessage" style="text-align: center; padding: 2rem; color: #dc2626;">
    {{ errorMessage }}
  </div>
  <div v-else-if="trek">
    <router-link to="/staff/treks" style="color: var(--secondary-color); text-decoration: none; display: inline-block; margin-bottom: 1rem;">&larr; Back to My Treks</router-link>
    
    <div v-if="successMessage" style="background-color: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #bbf7d0;">
      {{ successMessage }}
    </div>
    
    <div v-if="actionErrorMessage" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #fecaca;">
      {{ actionErrorMessage }}
    </div>
    
    <div class="card" style="padding: 0; overflow: hidden; margin-bottom: 2rem;">
      <div 
        :style="{ height: '300px', backgroundImage: `url(${getCoverImageUrl(trek.cover_image)})`, backgroundSize: 'cover', backgroundPosition: 'center' }"
      ></div>
      
      <div style="padding: 2.5rem;">
        <!-- Header & Price -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <h1 style="margin: 0; color: var(--text-color); font-size: 2.5rem;">{{ trek.name }}</h1>
          <h2 style="margin: 0; font-size: 2rem;">₹{{ parseFloat(trek.price).toFixed(2) }}</h2>
        </div>
        
        <!-- Badges -->
        <div style="display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap;">
          <span class="badge badge-active" style="font-size: 1rem; padding: 0.5rem 1rem; background-color: var(--primary-color); color: white;">{{ capitalize(trek.difficulty) }} Difficulty</span>
          <span class="badge badge-open" style="font-size: 1rem; padding: 0.5rem 1rem;">📍 {{ trek.location }}</span>
          
          <span v-if="['completed', 'cancelled'].includes(trek.status)" class="badge" style="font-size: 1rem; padding: 0.5rem 1rem; background-color: var(--secondary-color); color: white; border: 1px solid var(--secondary-color);">Concluded</span>
          <span v-else class="badge badge-open" style="font-size: 1rem; padding: 0.5rem 1rem;">🧑‍🤝‍🧑 {{ trek.slots_available }} Slots Left</span>
          
          <span :class="['badge', `badge-${trek.status}`]" style="font-size: 1rem; padding: 0.5rem 1rem; margin-left: auto;">{{ capitalize(trek.status) }}</span>
        </div>
        
        <!-- Dates Row -->
        <div style="display: flex; gap: 4rem; margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border-color);">
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Start Date</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ formatFullDate(trek.start_date) }}</p>
          </div>
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">End Date</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ formatFullDate(trek.end_date) }}</p>
          </div>
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Duration</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ trek.duration }} Days</p>
          </div>
          <div>
            <strong style="color: var(--secondary-color); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Total Participants</strong>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 500;">{{ totalParticipants }}</p>
          </div>
        </div>
        
        <!-- Description & Management Grid -->
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 3rem;">
          <div>
            <h3 style="margin-top: 0; font-size: 1.5rem;">About This Trek</h3>
            <div v-if="trek.description" style="line-height: 1.8; color: var(--text-color); font-size: 1.05rem; white-space: pre-wrap;">{{ trek.description }}</div>
            <div v-else style="line-height: 1.8; color: #9ca3af; font-style: italic; font-size: 1.05rem;">No description provided.</div>
          </div>
          
          <div>
            <div class="card" style="padding: 1.5rem; background-color: #f8fafc; border: 1px solid #e2e8f0; box-shadow: none;">
              <h3 style="margin-top: 0; font-size: 1.2rem; margin-bottom: 1.5rem; color: var(--primary-color);">Management Tools</h3>
              <form @submit.prevent="saveTrek">
                <fieldset :disabled="['completed', 'cancelled'].includes(trek.status)" style="border: none; padding: 0; margin: 0;">
                  <div class="form-group">
                    <label for="slots_available" class="form-label">Slots Available</label>
                    <input type="number" id="slots_available" v-model="form.slots_available" class="form-control" min="0" required>
                  </div>
                  
                  <div class="form-group">
                    <label for="status" class="form-label">Trek Status</label>
                    <select id="status" v-model="form.status" class="form-control">
                      <option value="open">Open</option>
                      <option value="full">Full</option>
                      <option value="ongoing">Ongoing</option>
                      <option value="completed">Completed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                </fieldset>
                
                <button 
                  v-if="!['completed', 'cancelled'].includes(trek.status)" 
                  type="submit" 
                  class="btn btn-accent" 
                  style="width: 100%; margin-top: 1rem; padding: 0.75rem;"
                  :disabled="saving"
                >
                  {{ saving ? "Saving..." : "Save Changes" }}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Participant Roster -->
    <div class="card">
      <h3 style="margin-top: 0; margin-bottom: 1.5rem; color: var(--text-color); border-bottom: 1px solid #e2e8f0; padding-bottom: 0.5rem;">Participant Roster</h3>
      
      <div v-if="trek.bookings && trek.bookings.length > 0" class="data-table-wrapper">
        <table class="data-table">
          <thead>
            <tr>
              <th>Booking ID</th>
              <th>Trekker</th>
              <th>Contact</th>
              <th>Emergency</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in trek.bookings" :key="booking.id">
              <td>#{{ booking.id }}</td>
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
      <p v-else style="color: var(--secondary-color); text-align: center; padding: 2rem 0;">No active participants found for this trek.</p>
    </div>
  </div>
</template>

<script>
import { apiFetch, SERVER_URL } from "../../utils/api"

export default {
  name: "StaffTrekManage",
  data() {
    return {
      trek: null,
      loading: true,
      errorMessage: "",
      actionErrorMessage: "",
      successMessage: "",
      saving: false,
      cancellingId: null,
      form: {
        slots_available: 0,
        status: "open"
      }
    }
  },
  computed: {
    totalParticipants() {
      if (!this.trek || !this.trek.bookings) return 0;
      return this.trek.bookings.filter(b => ['booked', 'completed'].includes(b.status)).length;
    }
  },
  async mounted() {
    await this.fetchTrek()
  },
  methods: {
    getCoverImageUrl(path) {
      if (path) {
        return `${SERVER_URL}/static/uploads/${path}`
      }
      return `${SERVER_URL}/static/images/trek.jpg`
    },
    formatFullDate(dateString) {
      if (!dateString) return ""
      const d = new Date(dateString)
      return d.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })
    },
    capitalize(str) {
      if (!str) return ""
      return str.charAt(0).toUpperCase() + str.slice(1)
    },
    async fetchTrek() {
      this.loading = true
      try {
        const id = this.$route.params.id
        const data = await apiFetch(`/staff/treks/${id}`)
        this.trek = data
        this.form.slots_available = data.slots_available
        this.form.status = data.status
      } catch (e) {
        this.errorMessage = e.message || "Failed to load trek details"
      } finally {
        this.loading = false
      }
    },
    async saveTrek() {
      this.saving = true
      this.actionErrorMessage = ""
      this.successMessage = ""
      try {
        const id = this.trek.id
        const res = await apiFetch(`/staff/treks/${id}`, {
          method: "POST",
          body: JSON.stringify(this.form)
        })
        this.successMessage = res.message || "Trek updated successfully."
        await this.fetchTrek()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (e) {
        this.actionErrorMessage = e.message || "Failed to update trek"
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } finally {
        this.saving = false
      }
    },
    async cancelBooking(bookingId) {
      if (!confirm('Are you sure you want to cancel this booking? This will reopen a slot.')) {
        return
      }
      this.actionErrorMessage = ""
      this.successMessage = ""
      this.cancellingId = bookingId
      try {
        const res = await apiFetch(`/staff/cancel_booking/${bookingId}`, {
          method: "POST"
        })
        this.successMessage = res.message || "Booking cancelled successfully."
        await this.fetchTrek()
      } catch (e) {
        this.actionErrorMessage = e.message || "Failed to cancel booking"
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } finally {
        this.cancellingId = null
      }
    }
  }
}
</script>
