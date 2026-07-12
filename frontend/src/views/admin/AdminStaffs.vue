<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Manage Staffs</h2>
      <router-link to="/admin/staffs/new" class="btn btn-accent">Register New Staff</router-link>
    </div>
    
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Username</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Experience</th>
            <th>Total Treks</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="staff in staffs" :key="staff.id">
            <td>{{ staff.name }}</td>
            <td>{{ staff.username }}</td>
            <td>{{ staff.email }}</td>
            <td>{{ staff.phone }}</td>
            <td>{{ staff.experience || "" }}</td>
            <td style="text-align: center;"><strong>{{ staff.total_treks }}</strong></td>
            <td>
              <span v-if="staff.is_blacklisted" class="badge badge-blacklisted">Blacklisted</span>
              <span v-else class="badge badge-active">Active</span>
            </td>
            <td>
              <button @click="toggleBlacklist(staff)" :class="['btn', staff.is_blacklisted ? 'btn-secondary' : 'btn-danger']" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                {{ staff.is_blacklisted ? "Un-blacklist" : "Blacklist" }}
              </button>
            </td>
          </tr>
          <tr v-if="staffs.length === 0 && !loading">
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
              No staffs found. Click "Register New Staff" to register one.
            </td>
          </tr>
          <tr v-if="loading">
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
              Loading...
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "../../utils/api"

export default {
  name: "AdminStaffs",
  data() {
    return {
      staffs: [],
      loading: true
    }
  },
  async mounted() {
    await this.fetchStaffs()
  },
  methods: {
    async fetchStaffs() {
      this.loading = true
      try {
        const data = await apiFetch("/admin/staffs", { method: "GET" })
        this.staffs = data
      } catch (err) {
        console.error(err.message)
      } finally {
        this.loading = false
      }
    },
    async toggleBlacklist(staff) {
      if (!confirm(`Are you sure you want to ${staff.is_blacklisted ? 'unblacklist' : 'blacklist'} ${staff.name}?`)) return
      try {
        await apiFetch(`/admin/staffs/${staff.id}/blacklist`, { method: "PUT" })
        await this.fetchStaffs()
      } catch (err) {
        alert(err.message)
      }
    }
  }
}
</script>
