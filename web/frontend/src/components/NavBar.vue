<template>
  <nav class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="navbar-brand">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <span class="brand-text">ArXiv Adapter</span>
      </router-link>
      
      <div class="navbar-links">
        <router-link 
          v-for="link in navLinks" 
          :key="link.path" 
          :to="link.path"
          class="nav-link"
          :class="{ active: isActive(link.path) }"
        >
          <component :is="link.icon" class="nav-icon" />
          <span>{{ link.name }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const SearchIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor', 
  'stroke-width': '2' 
}, [
  h('circle', { cx: '11', cy: '11', r: '8' }),
  h('path', { d: 'M21 21l-4.35-4.35' })
])

const DatabaseIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor', 
  'stroke-width': '2' 
}, [
  h('ellipse', { cx: '12', cy: '5', rx: '9', ry: '3' }),
  h('path', { d: 'M21 12c0 1.66-4 3-9 3s-9-1.34-9-3' }),
  h('path', { d: 'M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5' })
])

const ChartIcon = () => h('svg', { 
  viewBox: '0 0 24 24', 
  fill: 'none', 
  stroke: 'currentColor', 
  'stroke-width': '2' 
}, [
  h('path', { d: 'M18 20V10' }),
  h('path', { d: 'M12 20V4' }),
  h('path', { d: 'M6 20v-6' })
])

const navLinks = [
  { name: '搜索', path: '/', icon: SearchIcon },
  { name: '数据库', path: '/papers', icon: DatabaseIcon },
  { name: '统计', path: '/stats', icon: ChartIcon },
]

const isActive = computed(() => (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
})
</script>

<style scoped>
.navbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}

.navbar-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 4rem;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: var(--text);
}

.brand-icon {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--primary);
}

.brand-text {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 700;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.9375rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-link:hover {
  background: rgba(30, 64, 175, 0.08);
  color: var(--primary);
}

.nav-link.active {
  background: var(--primary);
  color: white;
}

.nav-icon {
  width: 1.25rem;
  height: 1.25rem;
}

@media (max-width: 640px) {
  .navbar-container {
    padding: 0 1rem;
  }

  .brand-text {
    display: none;
  }

  .nav-link span {
    display: none;
  }

  .nav-link {
    padding: 0.5rem;
  }

  .nav-icon {
    width: 1.5rem;
    height: 1.5rem;
  }
}
</style>
