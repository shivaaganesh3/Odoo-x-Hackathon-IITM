import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Dashboard from '../pages/Dashboard.vue'
import MyTasks from '../pages/MyTasks.vue'
import Projects from '../pages/Projects.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/dashboard', component: Dashboard },
  { path: '/my-tasks', component: MyTasks },
  { path: '/projects', component: Projects },
  {
    path: '/project/:id/tasks',
    component: () => import('../pages/ProjectTasks.vue') // ✅ lazy loaded
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
