import { createRouter, createWebHistory } from "vue-router"
import { authStore } from "../store"

import Login from "../views/Login.vue"
import Register from "../views/Register.vue"
import AdminDashboard from "../views/AdminDashboard.vue"
import StaffDashboard from "../views/StaffDashboard.vue"
import TrekkerDashboard from "../views/TrekkerDashboard.vue"

const routes = [
  { path: "/login", component: Login, meta: { requiresGuest: true } },
  { path: "/register", component: Register, meta: { requiresGuest: true } },
  { path: "/admin", component: AdminDashboard, meta: { requiresAuth: true, role: "admin" } },
  { path: "/staff", component: StaffDashboard, meta: { requiresAuth: true, role: "staff" } },
  { path: "/trekker", component: TrekkerDashboard, meta: { requiresAuth: true, role: "trekker" } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.userRole
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login")
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next(`/${userRole}`)
  } else if (to.meta.requiresAuth && to.meta.role !== userRole) {
    next(`/${userRole}`)
  } else {
    next()
  }
})

export default router
