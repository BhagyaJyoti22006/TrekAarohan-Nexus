<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <h2>Manage Trekkers</h2>
    </div>
    
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Username</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Emergency Info</th>
            <th>Total Treks</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trekker in trekkers" :key="trekker.id">
            <td>{{ trekker.name }}</td>
            <td>{{ trekker.username }}</td>
            <td>{{ trekker.email }}</td>
            <td>{{ trekker.phone }}</td>
            <td>
              <small>Phone: {{ trekker.emergency_phone || "N/A" }}<br>Relation: {{ trekker.emergency_relation || "N/A" }}</small>
            </td>
            <td style="text-align: center;"><strong>{{ trekker.total_bookings }}</strong></td>
            <td>
              <span v-if="trekker.is_blacklisted" class="badge badge-blacklisted">Blacklisted</span>
              <span v-else class="badge badge-active">Active</span>
            </td>
            <td>
              <button @click="toggleBlacklist(trekker)" :class="['btn', trekker.is_blacklisted ? 'btn-secondary' : 'btn-danger']" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                {{ trekker.is_blacklisted ? "Un-blacklist" : "Blacklist" }}
              </button>
            </td>
          </tr>
          <tr v-if="trekkers.length === 0 && !loading">
            <td colspan="8" style="text-align: center; padding: 2rem; color: var(--secondary-color);">
              No trekkers registered yet.
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
  name: "AdminTrekkers",
  data() {
    return {
      trekkers: [],
      loading: true
    }
  },
  async mounted() {
    await this.fetchTrekkers()
  },
  methods: {
    async fetchTrekkers() {
      this.loading = true
      try {
        const data = await apiFetch("/admin/trekkers", { method: "GET" })
        this.trekkers = data
      } catch (err) {
        console.error(err.message)
      } finally {
        this.loading = false
      }
    },
    async toggleBlacklist(trekker) {
      if (!confirm(`Are you sure you want to ${trekker.is_blacklisted ? 'unblacklist' : 'blacklist'} ${trekker.username}?`)) return
      try {
        await apiFetch(`/admin/trekkers/${trekker.id}/blacklist`, { method: "PUT" })
        await this.fetchTrekkers()
      } catch (err) {
        alert(err.message)
      }
    }
  }
}
</script>
