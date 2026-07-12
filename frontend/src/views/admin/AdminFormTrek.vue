<template>
  <div>
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div style="margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem;">
        <h3 style="margin: 0; color: var(--primary-color);">{{ isEditMode && form.name ? 'Edit Trek: ' + form.name : 'Add New Trek' }}</h3>
      </div>
      
      <div v-if="error" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b;">
        {{ error }}
      </div>
      <div v-if="success" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #dcfce7; color: #166534;">
        {{ success }}
      </div>
      
      <form @submit.prevent="handleSubmit" v-if="!success">
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
              <small v-if="isEditMode && form.cover_image" style="color: var(--secondary-color); margin-top: 0.5rem; display: block;">Current: {{ form.cover_image.split('/').pop() }}</small>
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
              <input type="number" v-model="form.slots_available" class="form-control" :min="isEditMode ? 0 : 1" required>
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
                <option value="" disabled>Select an approved staff</option>
                <option v-for="s in staffOptions" :key="s.id" :value="s.id">
                  {{ s.name }} ({{ s.username }}) {{ s.is_blacklisted ? '[BLACKLISTED]' : '' }}
                </option>
              </select>
              <small style="color: var(--secondary-color); margin-top: 0.5rem; display: block;">Only approved staffs or the assigned staff shown.</small>
            </div>
            <div v-if="isEditMode" class="form-group" style="flex: 1; margin-bottom: 0;">
              <label class="form-label">Status</label>
              <select v-model="form.status" class="form-control" required>
                <option value="open">Open</option>
                <option value="full">Full</option>
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <small style="color: var(--secondary-color); margin-top: 0.5rem; display: block;">May auto-update.</small>
            </div>
          </div>
        </fieldset>
        
        <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
          <router-link to="/admin/treks" class="btn btn-secondary">Cancel</router-link>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ isEditMode ? (loading ? 'Saving...' : 'Save Changes') : (loading ? 'Adding...' : 'Add Trek') }}
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
      isEditMode: false,
      form: {
        name: "",
        location: "",
        description: "",
        start_date: "",
        end_date: "",
        difficulty: "",
        slots_available: 1,
        price: 0.0,
        assigned_staff_id: "",
        status: "open",
        cover_image: ""
      },
      cover_image_file: null,
      staffOptions: [],
      error: null,
      success: null,
      loading: false
    }
  },
  async mounted() {
    const trekId = this.$route.params.id
    if (trekId) {
      this.isEditMode = true
      await this.fetchTrek(trekId)
    }
    await this.fetchStaffs()
  },
  methods: {
    async fetchTrek(id) {
      try {
        const data = await apiFetch(`/admin/treks/${id}`, { method: "GET" })
        this.form = {
          name: data.name,
          location: data.location,
          description: data.description,
          start_date: data.start_date,
          end_date: data.end_date,
          difficulty: data.difficulty,
          slots_available: data.slots_available,
          price: data.price,
          assigned_staff_id: data.assigned_staff_id,
          status: data.status,
          cover_image: data.cover_image
        }
      } catch (err) {
        this.error = "Failed to load trek details."
      }
    },
    async fetchStaffs() {
      try {
        const data = await apiFetch("/admin/staffs", { method: "GET" })
        // Show active staffs, OR the currently assigned staff even if blacklisted
        this.staffOptions = data.filter(s => !s.is_blacklisted || (this.isEditMode && s.id === this.form.assigned_staff_id))
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
    async handleSubmit() {
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
        const endpoint = this.isEditMode ? `/admin/treks/${this.$route.params.id}` : "/admin/treks"
        const method = this.isEditMode ? "PUT" : "POST"
        const data = await apiFetch(endpoint, {
          method: method,
          body: formData
        })
        this.success = this.isEditMode ? "Trek updated successfully!" : "Trek added successfully!"
        if (!this.isEditMode) {
          this.form = {
            name: "", location: "", description: "", start_date: "", end_date: "",
            difficulty: "", slots_available: 1, price: 0.0, assigned_staff_id: "", status: "open", cover_image: ""
          }
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
