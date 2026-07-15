<template>
  <div>
    <h2>Welcome back, {{ dashboard.admin_name || authStore.username }}</h2>
    
    <!-- Quick Stats -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem; margin-bottom: 3rem;" v-if="!loadingStats">
      <div class="card" style="text-align: center; border-top: 4px solid var(--primary-color);">
        <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Total Treks</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--primary-color);">{{ dashboard.total_treks }}</p>
      </div>
      <div class="card" style="text-align: center; border-top: 4px solid var(--accent-color);">
        <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Active Bookings</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--accent-color);">{{ dashboard.active_bookings }}</p>
      </div>
      <div class="card" style="text-align: center; border-top: 4px solid var(--secondary-color);">
        <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Total Trekkers</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--secondary-color);">{{ dashboard.total_trekkers }}</p>
      </div>
      <div class="card" style="text-align: center; border-top: 4px solid var(--danger-color);">
        <h3 style="color: var(--secondary-color); font-size: 1rem; margin-top: 0;">Registered Staffs</h3>
        <p style="font-size: 2.5rem; font-weight: bold; margin: 0; color: var(--danger-color);">{{ dashboard.total_staffs }}</p>
      </div>
    </div>
    <div v-else style="text-align: center; margin: 3rem 0; color: var(--secondary-color);">
      Loading dashboard...
    </div>
    
    <!-- Master Table -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3rem; margin-bottom: 1rem;">
      <h3 style="margin: 0; color: var(--primary-color);">Complete User Database</h3>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <input type="text" v-model="filters.q" placeholder="Search ID, Name, Username..." class="form-control" style="width: 250px;">
        <select v-model="filters.role" class="form-control" style="width: 150px;">
          <option value="">All Roles</option>
          <option value="0">Trekker</option>
          <option value="1">Staff</option>
          <option value="2">Admin</option>
        </select>
        <select v-model="filters.status" class="form-control" style="width: 150px;">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="blacklisted">Blacklisted</option>
        </select>
        <button type="button" @click="clearFilters" class="btn btn-secondary" :disabled="loadingUsers">Clear</button>
      </div>
    </div>
    
    <div class="data-table-wrapper" v-if="!loadingUsers">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Role</th>
            <th>Username</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Emergency Info</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filteredUsers" :key="u.id">
            <td>#{{ u.id }}</td>
            <td>
              <span v-if="u.role === 2" class="badge badge-special">Admin</span>
              <span v-else-if="u.role === 1" class="badge badge-ongoing">Staff</span>
              <span v-else class="badge badge-completed">Trekker</span>
            </td>
            <td>{{ u.username }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone || "N/A" }}</td>
            <td>
              <span v-if="!u.emergency_phone && !u.emergency_relation" style="color: var(--secondary-color);">N/A</span>
              <div v-else>
                Phone: {{ u.emergency_phone || "N/A" }}<br>
                Relation: {{ u.emergency_relation || "N/A" }}
              </div>
            </td>
            <td>
              <span v-if="u.is_blacklisted" class="badge badge-blacklisted">Blacklisted</span>
              <span v-else class="badge badge-active">Active</span>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="8" style="text-align: center; color: var(--secondary-color);">No users found.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else style="text-align: center; margin: 3rem 0; color: var(--secondary-color);">
      Loading users...
    </div>
  </div>
</template>

<script>
import { authStore } from "../../store"
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminDashboard",
  data() {
    return {
      authStore,
      dashboard: {
        total_treks: 0,
        active_bookings: 0,
        total_trekkers: 0,
        total_staffs: 0,
        users: []
      },
      filters: {
        q: "",
        role: "",
        status: ""
      },
      loadingStats: true,
      loadingUsers: true
    }
  },
  computed: {
    filteredUsers() {
      return this.dashboard.users.filter(u => {
        const query = this.filters.q.toLowerCase()
        const matchQ = !query || 
                       u.id.toString() === query || 
                       u.name.toLowerCase().includes(query) || 
                       u.username.toLowerCase().includes(query)
        const matchRole = this.filters.role === "" || u.role.toString() === this.filters.role
        let matchStatus = true
        if (this.filters.status === "active") matchStatus = !u.is_blacklisted
        if (this.filters.status === "blacklisted") matchStatus = u.is_blacklisted
        return matchQ && matchRole && matchStatus
      })
    }
  },
  async mounted() {
    await this.fetchDashboard()
    this.loadingStats = false
  },
  methods: {
    async fetchDashboard() {
      this.loadingUsers = true
      try {
        const data = await apiFetch(`/admin/dashboard`)
        this.dashboard = data
      } catch (err) {
        console.error("Failed to load dashboard:", err)
      } finally {
        this.loadingUsers = false
      }
    },
    clearFilters() {
      this.filters = { q: "", role: "", status: "" }
    }
  }
}
</script>
