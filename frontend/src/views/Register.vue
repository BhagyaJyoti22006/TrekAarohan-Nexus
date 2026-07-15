<template>
  <div style="display: flex; justify-content: center; padding-top: 4rem; padding-bottom: 6rem;">
    <div class="card" style="width: 100%; max-width: 500px;">
      <h3 style="margin-top: 0; text-align: center; color: var(--primary-color);">Join TrekAarohan-Nexus</h3>
      
      <div v-if="error" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b;">
        {{ error }}
      </div>
      <div v-if="success" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #dcfce7; color: #166534;">
        {{ success }}
      </div>
      
      <form @submit.prevent="handleRegister" v-if="!success">
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
          <label class="form-label">Password</label>
          <input type="password" v-model="form.password" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-accent" style="width: 100%; padding: 1rem; font-size: 1rem;" :disabled="loading">
          {{ loading ? "Creating..." : "Create Account" }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 1.5rem; margin-bottom: 0;">Already have an account? <router-link to="/login" style="color: var(--primary-color); font-weight: 500;">Sign In</router-link></p>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../utils/api"

export default {
  name: "Register",
  data() {
    return {
      form: {
        username: "",
        name: "",
        email: "",
        phone: "",
        password: ""
      },
      error: null,
      success: null,
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      this.error = null
      this.success = null
      this.loading = true
      
      try {
        const data = await apiFetch("/auth/register", {
          method: "POST",
          body: JSON.stringify(this.form)
        })
        this.success = data.message + ". You can now sign in."
        this.form = { username: "", name: "", email: "", phone: "", password: "" }
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
