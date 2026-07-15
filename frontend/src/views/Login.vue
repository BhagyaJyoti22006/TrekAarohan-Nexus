<template>
  <div style="display: flex; justify-content: center; padding-top: 4rem; padding-bottom: 6rem;">
    <div class="card" style="width: 100%; max-width: 400px;">
      <h3 style="margin-top: 0; text-align: center; color: var(--primary-color);">Welcome Back</h3>
      
      <div v-if="error" style="padding: 0.75rem; margin-bottom: 1rem; border-radius: 6px; background-color: #fee2e2; color: #991b1b;">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Username</label>
          <input type="text" v-model="username" class="form-control" required>
        </div>
        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label class="form-label">Password</label>
          <input type="password" v-model="password" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-accent" style="width: 100%; padding: 1rem; font-size: 1rem;" :disabled="loading">
          {{ loading ? "Signing in..." : "Sign In" }}
        </button>
      </form>
      <p style="text-align: center; margin-top: 1.5rem; margin-bottom: 0;">Don't have an account? <router-link to="/register" style="color: var(--primary-color); font-weight: 500;">Register</router-link></p>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../utils/api"
import { authStore } from "../store"

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",
      error: null,
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      this.error = null
      this.loading = true
      try {
        const data = await apiFetch("/auth/login", {
          method: "POST",
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        })
        const roleMap = {0: "trekker", 1: "staff", 2: "admin"}
        const roleName = roleMap[data.user.role] || "trekker"
        authStore.login(data.access_token, roleName, data.user.username)
        // Redirect based on role
        if (roleName === "admin") this.$router.push("/admin")
        else if (roleName === "staff") this.$router.push("/staff")
        else this.$router.push("/trekker")
        
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
