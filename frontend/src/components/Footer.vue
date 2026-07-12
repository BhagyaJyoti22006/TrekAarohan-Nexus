<template>
  <footer class="site-footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <p>&copy; 2026 TrekAarohan-Nexus. All rights reserved.</p>
      <div class="footer-links">
        <router-link to="/footer">Contact Us</router-link>
        <span style="margin: 0 1.0rem; color: rgba(255,255,255,0.5);">|</span>
        <router-link to="/footer">Terms & Conditions</router-link>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: "Footer"
}
</script>
