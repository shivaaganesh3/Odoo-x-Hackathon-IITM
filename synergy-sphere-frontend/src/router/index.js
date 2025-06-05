import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import SignupPage from '../pages/SignupPage.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import ProjectsPage from '../pages/ProjectsPage.vue'
import ProjectDetailPage from '../pages/ProjectDetailPage.vue'
import CreateProjectPage from '../pages/CreateProjectPage.vue'
import TeamPage from '../pages/TeamPage.vue'
import CalendarPage from '../pages/CalendarPage.vue'
import SettingsPage from '../pages/SettingsPage.vue'
import CustomStatusManager from '../pages/CustomStatusManager.vue'
import TestConnection from '../pages/TestConnection.vue'
import SmartDashboard from '../pages/SmartDashboard.vue'

const routes = [
  { 
    path: '/', 
    redirect: '/dashboard',
    meta: { requiresAuth: true }
  },
  { 
    path: '/login', 
    name: 'Login',
    component: LoginPage,
    meta: { guest: true }
  },
  { 
    path: '/signup', 
    name: 'Signup',
    component: SignupPage,
    meta: { guest: true }
  },
  { 
    path: '/dashboard', 
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/smart-dashboard', 
    name: 'SmartDashboard',
    component: SmartDashboard,
    meta: { requiresAuth: true }
  },
  { 
    path: '/projects', 
    name: 'Projects',
    component: ProjectsPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/projects/create', 
    name: 'CreateProject',
    component: CreateProjectPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/projects/:id', 
    name: 'ProjectDetail',
    component: ProjectDetailPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/custom-status', 
    name: 'CustomStatus',
    component: CustomStatusManager,
    meta: { requiresAuth: true }
  },
  { 
    path: '/test-connection', 
    name: 'TestConnection',
    component: TestConnection,
    meta: { requiresAuth: false }
  },
  { 
    path: '/team', 
    name: 'Team',
    component: TeamPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/calendar', 
    name: 'Calendar',
    component: CalendarPage,
    meta: { requiresAuth: true }
  },
  { 
    path: '/settings', 
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('user') // Check for stored user data
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
