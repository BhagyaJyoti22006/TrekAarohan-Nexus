import { createRouter, createWebHistory } from "vue-router"
import { authStore } from "../store"

import Login from "../views/Login.vue"
import Register from "../views/Register.vue"

import AdminLayout from "../views/admin/AdminLayout.vue"
import AdminDashboard from "../views/admin/AdminDashboard.vue"
import AdminTreks from "../views/admin/AdminTreks.vue"
import AdminStaffs from "../views/admin/AdminStaffs.vue"
import AdminTrekkers from "../views/admin/AdminTrekkers.vue"
import AdminBookings from "../views/admin/AdminBookings.vue"

import StaffDashboard from "../views/StaffDashboard.vue"
import TrekkerDashboard from "../views/TrekkerDashboard.vue"

const routes = [
  { path: "/login", component: Login, meta: { requiresGuest: true } },
  { path: "/register", component: Register, meta: { requiresGuest: true } },
  { 
    path: "/admin", 
    component: AdminLayout, 
    meta: { requiresAuth: true, role: "admin" },
    children: [
      { path: "", component: AdminDashboard },
      { path: "treks", component: AdminTreks },
      { path: "staffs", component: AdminStaffs },
      { path: "trekkers", component: AdminTrekkers },
      { path: "bookings", component: AdminBookings }
    ]
  },
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
