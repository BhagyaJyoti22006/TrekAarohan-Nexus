import { createRouter, createWebHistory } from "vue-router"
import { authStore } from "../store"

import Home from "../views/Home.vue"
import PublicTreks from "../views/PublicTreks.vue"
import PublicAbout from "../views/PublicAbout.vue"
import PublicFooter from "../views/PublicFooter.vue"
import TrekDetail from "../views/TrekDetail.vue"
import Login from "../views/Login.vue"
import Register from "../views/Register.vue"
import NotFound from "../views/NotFound.vue"

import AdminLayout from "../views/admin/AdminLayout.vue"
import AdminDashboard from "../views/admin/AdminDashboard.vue"
import AdminTreks from "../views/admin/AdminTreks.vue"
import AdminFormTrek from "../views/admin/AdminFormTrek.vue"
import AdminStaffs from "../views/admin/AdminStaffs.vue"
import AdminFormStaff from "../views/admin/AdminFormStaff.vue"
import AdminTrekkers from "../views/admin/AdminTrekkers.vue"
import AdminBookings from "../views/admin/AdminBookings.vue"

import StaffLayout from "../views/staff/StaffLayout.vue"
import StaffDashboard from "../views/staff/StaffDashboard.vue"
import StaffTreks from "../views/staff/StaffTreks.vue"
import StaffTrekManage from "../views/staff/StaffTrekManage.vue"
import StaffParticipants from "../views/staff/StaffParticipants.vue"
import StaffProfile from "../views/staff/StaffProfile.vue"

import TrekkerLayout from "../views/trekker/TrekkerLayout.vue"
import TrekkerDashboard from "../views/trekker/TrekkerDashboard.vue"
import TrekkerBookings from "../views/trekker/TrekkerBookings.vue"
import TrekkerHistory from "../views/trekker/TrekkerHistory.vue"
import TrekkerProfile from "../views/trekker/TrekkerProfile.vue"

const routes = [
  { path: "/", component: Home },
  { path: "/treks", component: PublicTreks },
  { path: "/about", component: PublicAbout },
  { path: "/footer", component: PublicFooter },
  { path: "/trek/:id", component: TrekDetail },
  { path: "/login", component: Login, meta: { requiresGuest: true } },
  { path: "/register", component: Register, meta: { requiresGuest: true } },
  { 
    path: "/admin", 
    component: AdminLayout, 
    meta: { requiresAuth: true, role: "admin" },
    children: [
      { path: "", component: AdminDashboard },
      { path: "treks", component: AdminTreks },
      { path: "treks/new", component: AdminFormTrek },
      { path: "treks/:id/edit", component: AdminFormTrek },
      { path: "staffs", component: AdminStaffs },
      { path: "staffs/new", component: AdminFormStaff },
      { path: "trekkers", component: AdminTrekkers },
      { path: "bookings", component: AdminBookings }
    ]
  },
  { 
    path: "/staff", 
    component: StaffLayout, 
    meta: { requiresAuth: true, role: "staff" },
    children: [
      { path: "", component: StaffDashboard },
      { path: "treks", component: StaffTreks },
      { path: "treks/:id", component: StaffTrekManage },
      { path: "participants", component: StaffParticipants },
      { path: "profile", component: StaffProfile }
    ]
  },
  { 
    path: "/trekker", 
    component: TrekkerLayout, 
    meta: { requiresAuth: true, role: "trekker" },
    children: [
      { path: "", component: TrekkerDashboard },
      { path: "bookings", component: TrekkerBookings },
      { path: "history", component: TrekkerHistory },
      { path: "profile", component: TrekkerProfile }
    ]
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NotFound
  }
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
