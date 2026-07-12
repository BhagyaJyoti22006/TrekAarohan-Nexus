<template>
  <div>
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
        <h3 style="margin: 0; color: var(--primary-color);">Add New Trek</h3>
      </div>
      
      <div v-if="error" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b;">
        {{ error }}
      </div>
      <div v-if="success" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #dcfce7; color: #166534;">
        {{ success }}
      </div>
      
      <form @submit.prevent="handleCreateTrek" v-if="!success">
        <fieldset style="border: none; padding: 0; margin: 0;">
          <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <div class="form-group" style="flex: 2; margin-bottom: 0;">
              <label class="form-label">Trek Name</label>
              <input type="text" v-model="form.name" class="form-control" required>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Location</label>
              <input type="text" v-model="form.location" class="form-control" required>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea v-model="form.description" class="form-control" rows="4" style="resize: vertical;"></textarea>
          </div>
          
          <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Start Date</label>
              <input type="date" v-model="form.start_date" class="form-control" required>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">End Date</label>
              <input type="date" v-model="form.end_date" class="form-control" required>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Cover Image</label>
              <input type="file" @change="handleFileUpload" class="form-control" accept="image/*">
            </div>
          </div>
          
          <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Difficulty</label>
              <select v-model="form.difficulty" class="form-control" required>
                <option value="" disabled>Select Difficulty</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Slots Available</label>
              <input type="number" v-model="form.slots_available" class="form-control" min="1" required>
            </div>
            <div class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Price (₹)</label>
              <input type="number" v-model="form.price" class="form-control" min="0" step="0.01" required>
            </div>
          </div>
          
          <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem;">
            <div class="form-group" style="flex: 2; margin-bottom: 0;">
              <label class="form-label">Assign Staff Member</label>
              <select v-model="form.assigned_staff_id" class="form-control" required>
                <option value="" disabled>Select the trek staff</option>
                <option v-for="s in staffOptions" :key="s.id" :value="s.id">
                  {{ s.name }} ({{ s.username }})
                </option>
              </select>
              <small style="color: var(--secondary-color); margin-top: 0.5rem; display: block;">Only active staffs are shown.</small>
            </div>
          </div>
        </fieldset>
        
        <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
          <router-link to="/admin/treks" class="btn btn-secondary">Cancel</router-link>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? "Adding..." : "Add Trek" }}
          </button>
        </div>
      </form>
      
      <div v-else style="display: flex; justify-content: flex-end; margin-top: 2rem;">
        <router-link to="/admin/treks" class="btn btn-secondary">Back to treks</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminFormTrek",
  data() {
    return {
      form: {
        name: "",
        location: "",
        description: "",
        start_date: "",
        end_date: "",
        difficulty: "",
        slots_available: 1,
        price: 0.0,
        assigned_staff_id: ""
      },
      cover_image_file: null,
      staffOptions: [],
      error: null,
      success: null,
      loading: false
    }
  },
  async mounted() {
    await this.fetchStaffs()
  },
  methods: {
    async fetchStaffs() {
      try {
        const data = await apiFetch("/admin/staffs", { method: "GET" })
        this.staffOptions = data.filter(s => !s.is_blacklisted)
      } catch (err) {
        console.error("Failed to load staffs:", err.message)
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.cover_image_file = file
      } else {
        this.cover_image_file = null
      }
    },
    async handleCreateTrek() {
      this.error = null
      this.success = null
      // Frontend date validation
      if (this.form.start_date && this.form.end_date) {
        if (new Date(this.form.start_date) > new Date(this.form.end_date)) {
          this.error = "Start date must be before or equal to end date."
          document.querySelector('.card').scrollIntoView({ behavior: 'smooth' })
          return
        }
      }
	  // Submit form
      this.loading = true
      try {
        const formData = new FormData()
        Object.keys(this.form).forEach(key => {
          formData.append(key, this.form[key])
        })
        if (this.cover_image_file) {
          formData.append("cover_image", this.cover_image_file)
        }
        const data = await apiFetch("/admin/treks", {
          method: "POST",
          body: formData
        })
        this.success = "Trek added successfully!"
        // Reset form
        this.form = {
          name: "", location: "", description: "", start_date: "", end_date: "",
          difficulty: "", slots_available: 1, price: 0.0, assigned_staff_id: ""
        }
        this.cover_image_file = null
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
