import { authStore } from "../store"

export const SERVER_URL = "http://127.0.0.1:5000"
export const BASE_URL = `${SERVER_URL}/api`

export async function apiFetch(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers
  }
  
  if (options.body instanceof FormData) {
    delete headers["Content-Type"]
  }
  
  if (authStore.isAuthenticated) {
    headers["Authorization"] = `Bearer ${authStore.token}`
  }
  
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  })
  
  if (response.status === 401 && endpoint !== "/auth/login") {
    authStore.logout()
    window.location.href = "/login"
    throw new Error("Session expired. Please log in again.")
  }
  
  const data = await response.json()
  
  if (!response.ok) {
    throw new Error(data.error || "An error occurred")
  }
  
  return data
}
