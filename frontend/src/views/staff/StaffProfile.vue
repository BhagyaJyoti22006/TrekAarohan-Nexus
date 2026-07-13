<template>
  <div>
    <h2>Profile Settings</h2>
    
    <div class="card" style="margin-top: 2rem;" v-if="!loading">
      <div v-if="successMessage" style="background-color: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #bbf7d0;">
        {{ successMessage }}
      </div>
      
      <div v-if="errorMessage" style="background-color: #fee2e2; color: #991b1b; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #fecaca;">
        {{ errorMessage }}
      </div>
      
      <h3 style="margin-top: 0;">Personal Information</h3>
      
      <form @submit.prevent="updateProfile" style="display: flex; flex-direction: column; gap: 1rem; margin-top: 1rem;">
        
        <div class="form-group">
          <label>Username (Non-editable)</label>
          <input type="text" class="form-control" :value="profile.username" readonly style="background-color: #f1f5f9; color: #64748b;">
        </div>
        
        <div class="form-group">
          <label for="email">Email Address <span style="color: #ef4444;">*</span></label>
          <input type="email" id="email" v-model="profile.email" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label for="name">Full Name <span style="color: #ef4444;">*</span></label>
          <input type="text" id="name" v-model="profile.name" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label for="phone">Phone Number <span style="color: #ef4444;">*</span></label>
          <input type="number" id="phone" v-model="profile.phone" class="form-control" required>
        </div>
        
        <div class="form-group">
          <label for="experience">Experience / Bio</label>
          <textarea id="experience" v-model="profile.experience" class="form-control" rows="4" style="resize: vertical;" placeholder="Briefly describe your guiding experience and qualifications"></textarea>
          <small style="color: var(--secondary-color); display: block; margin-top: 0.25rem;">This will be displayed to trekkers on the trek details page.</small>
        </div>
        
        <hr style="border: 0; border-top: 1px solid var(--border-color); margin: 0.5rem 0;">
        <h3 style="margin: 0; color: #ef4444;">Emergency Contact</h3>
        
        <div class="form-group">
          <label for="emergency_phone">Phone Number</label>
          <input type="number" id="emergency_phone" v-model="profile.emergency_phone" class="form-control">
          <small style="color: var(--secondary-color); display: block; margin-top: 0.25rem;">We will only call this number in case of an emergency.</small>
        </div>
        
        <div class="form-group">
          <label for="emergency_relation">Relationship to You</label>
          <input type="text" id="emergency_relation" v-model="profile.emergency_relation" class="form-control" placeholder="e.g., Spouse, Parent, Sibling">
        </div>
        
        <div style="margin-top: 0.5rem;">
          <button type="submit" class="btn btn-primary" :disabled="saving" style="padding: 0.75rem 2rem; font-size: 1.1rem;">
            {{ saving ? "Saving..." : "Save Changes" }}
          </button>
        </div>
      </form>
    </div>
    
    <div v-else style="text-align: center; padding: 2rem; color: var(--secondary-color);">
      Loading profile...
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "StaffProfile",
  data() {
    return {
      profile: {
        username: "",
        email: "",
        name: "",
        phone: "",
        experience: "",
        emergency_phone: "",
        emergency_relation: ""
      },
      loading: true,
      saving: false,
      successMessage: "",
      errorMessage: ""
    }
  },
  async mounted() {
    await this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      this.loading = true
      try {
        const data = await apiFetch("/staff/profile", { method: "GET" })
        this.profile = data
      } catch (err) {
        this.errorMessage = err.message || "Failed to load profile."
      } finally {
        this.loading = false
      }
    },
    async updateProfile() {
      this.saving = true
      this.successMessage = ""
      this.errorMessage = ""
      try {
        const res = await apiFetch("/staff/profile", {
          method: "PUT",
          body: JSON.stringify({
            email: this.profile.email,
            name: this.profile.name,
            phone: this.profile.phone,
            experience: this.profile.experience,
            emergency_phone: this.profile.emergency_phone,
            emergency_relation: this.profile.emergency_relation
          })
        })
        this.successMessage = res.message || "Profile updated successfully."
        document.querySelector('.card').scrollIntoView({ behavior: 'smooth' })
      } catch (err) {
        this.errorMessage = err.message || "Failed to update profile."
        document.querySelector('.card').scrollIntoView({ behavior: 'smooth' })
      } finally {
        this.saving = false
      }
    }
  }
}
</script>
