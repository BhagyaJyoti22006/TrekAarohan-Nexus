<template>
  <div>
    <div class="card" style="max-width: 600px; margin: 0 auto;">
      <div style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
        <h3 style="margin: 0; color: var(--primary-color);">Register New Staff</h3>
      </div>
      
      <div v-if="error" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b;">
        {{ error }}
      </div>
      <div v-if="success" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #dcfce7; color: #166534;">
        {{ success }}
      </div>
      
      <form @submit.prevent="handleCreateStaff" v-if="!success">
        <div class="form-group">
          <label class="form-label">Username</label>
          <input type="text" v-model="form.username" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input type="text" v-model="form.name" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Email Address</label>
          <input type="email" v-model="form.email" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label class="form-label">Phone Number</label>
          <input type="number" v-model="form.phone" class="form-control" required>
        </div>
        
        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label class="form-label">Experience (Optional)</label>
          <textarea v-model="form.experience" class="form-control" rows="3" placeholder="List any relevant trekking experience..." style="resize: vertical;"></textarea>
        </div>
        
        <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
          <router-link to="/admin/staffs" class="btn btn-secondary">Cancel</router-link>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? "Registering..." : "Register New Staff" }}
          </button>
        </div>
      </form>
      
      <div v-else style="display: flex; justify-content: flex-end; margin-top: 2rem;">
        <router-link to="/admin/staffs" class="btn btn-secondary">Back to staffs</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminFormStaff",
  data() {
    return {
      form: {
        username: "",
        name: "",
        email: "",
        phone: "",
        experience: ""
      },
      error: null,
      success: null,
      loading: false
    }
  },
  methods: {
    // Backend handles the actual Celery task for welcome emails
    async handleCreateStaff() {
      this.error = null
      this.success = null
      this.loading = true
      const payload = {
        ...this.form
      }
      try {
        const data = await apiFetch("/admin/staffs", {
          method: "POST",
          body: JSON.stringify(payload)
        })
        this.success = "Staff account created successfully! The credentials have been securely emailed to them."
        this.form = { username: "", name: "", email: "", phone: "", experience: "" }
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
        document.querySelector('.card').scrollIntoView({ behavior: 'smooth' })
      }
    }
  }
}
</script>
