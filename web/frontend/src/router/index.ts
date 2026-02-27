import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/papers',
      name: 'papers',
      component: () => import('../views/PapersView.vue'),
    },
    {
      path: '/papers/:id',
      name: 'paper-detail',
      component: () => import('../views/PaperDetailView.vue'),
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('../views/StatsView.vue'),
    },
  ],
})

export default router
