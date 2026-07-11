import { reactive } from "vue"

export const authStore = reactive({
  token: localStorage.getItem("token") || null,
  userRole: localStorage.getItem("userRole") || null,
  username: localStorage.getItem("username") || null,
  
  get isAuthenticated() {
    return !!this.token
  },
  
  login(token, role, username) {
    this.token = token
    this.userRole = role
    this.username = username
    localStorage.setItem("token", token)
    localStorage.setItem("userRole", role)
    localStorage.setItem("username", username)
  },
  
  logout() {
    this.token = null
    this.userRole = null
    this.username = null
    localStorage.removeItem("token")
    localStorage.removeItem("userRole")
    localStorage.removeItem("username")
  }
  
})
