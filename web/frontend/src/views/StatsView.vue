<template>
  <div class="stats-view">
    <div class="page-header">
      <h1>数据统计</h1>
      <p class="page-desc">查看数据库中的论文统计信息</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载统计数据...</span>
    </div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total_papers }}</span>
            <span class="stat-label">论文总数</span>
          </div>
        </div>

        <div class="stat-card cta">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.db_size_mb }} MB</span>
            <span class="stat-label">存储空间</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ categoryCount }}</span>
            <span class="stat-label">分类数量</span>
          </div>
        </div>
      </div>

      <div class="section-card">
        <h2>分类分布</h2>
        <div v-if="categoryCount === 0" class="empty-state">
          <p>暂无分类数据</p>
        </div>
        <div v-else class="category-list">
          <div 
            v-for="[category, count] in sortedCategories" 
            :key="category" 
            class="category-item"
          >
            <div class="category-info">
              <span class="category-name">{{ category }}</span>
              <span class="category-count">{{ count }} 篇</span>
            </div>
            <div class="category-bar">
              <div 
                class="category-bar-fill" 
                :style="{ width: getBarWidth(count) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { paperApi, type Stats } from '../api'

const stats = ref<Stats>({
  total_papers: 0,
  db_size_bytes: 0,
  db_size_mb: 0,
  categories: {},
})

const loading = ref(true)

const categoryCount = computed(() => Object.keys(stats.value.categories).length)

const sortedCategories = computed(() => {
  return Object.entries(stats.value.categories)
    .sort((a, b) => b[1] - a[1])
})

const maxCategoryCount = computed(() => {
  return Math.max(...Object.values(stats.value.categories), 1)
})

function getBarWidth(count: number): number {
  return (count / maxCategoryCount.value) * 100
}

onMounted(async () => {
  try {
    const { data } = await paperApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stats-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.page-desc {
  color: var(--text-muted);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
  color: var(--text-muted);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.stat-card.primary {
  border-left: 4px solid var(--primary);
}

.stat-card.primary .stat-icon {
  color: var(--primary);
  background: rgba(30, 64, 175, 0.1);
}

.stat-card.cta {
  border-left: 4px solid var(--cta);
}

.stat-card.cta .stat-icon {
  color: var(--cta);
  background: rgba(245, 158, 11, 0.1);
}

.stat-card.success {
  border-left: 4px solid var(--success);
}

.stat-card.success .stat-icon {
  color: var(--success);
  background: rgba(34, 197, 94, 0.1);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: var(--radius);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 1.5rem;
  height: 1.5rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text);
  font-family: 'Fira Code', monospace;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.section-card {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

.section-card h2 {
  font-size: 1.125rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 500;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
}

.category-count {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.category-bar {
  height: 0.5rem;
  background: var(--border-light);
  border-radius: 9999px;
  overflow: hidden;
}

.category-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
  border-radius: 9999px;
  transition: width 0.3s ease;
}

@media (max-width: 640px) {
  .stats-view {
    padding: 1.5rem 1rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
