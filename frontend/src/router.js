import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import DatabaseView from './views/DatabaseView.vue'
// import UploadView from './views/UploadView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/database',
    name: 'database',
    component: DatabaseView,
  },
  //   {
  //     path: '/upload',
  //     name: 'upload',
  //     component: UploadView
  //   }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
