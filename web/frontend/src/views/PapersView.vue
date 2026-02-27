<template>
  <div class="papers-view">
    <div class="page-header">
      <div class="header-content">
        <h1>论文数据库</h1>
        <p class="page-desc">管理本地存储的论文数据</p>
      </div>
      <div class="header-actions">
        <span class="paper-count">{{ total }} 篇论文</span>
      </div>
    </div>

    <div class="controls-bar">
      <div class="search-filter">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input 
          v-model="searchQuery" 
          placeholder="搜索标题或作者..."
          class="search-input"
        />
      </div>
      <div class="sort-controls">
        <select v-model="sortBy" class="sort-select">
          <option value="created_at">添加时间</option>
          <option value="title">标题</option>
          <option value="published">发布日期</option>
          <option value="arxiv_id">arXiv ID</option>
        </select>
        <button 
          class="order-btn" 
          :class="{ asc: order === 'asc' }"
          @click="toggleOrder"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 4h13M3 8h9M3 12h5"/>
            <path d="M17 8l4 4-4 4"/>
          </svg>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载论文列表...</span>
    </div>

    <div v-else-if="filteredPapers.length === 0" class="empty-state">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <p>{{ searchQuery ? '未找到匹配的论文' : '数据库为空' }}</p>
      <p class="empty-hint">前往搜索页面添加论文</p>
    </div>

    <template v-else>
      <div class="table-container">
        <table class="papers-table">
          <thead>
            <tr>
              <th>arXiv ID</th>
              <th>标题</th>
              <th>作者</th>
              <th>分类</th>
              <th>添加时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="paper in paginatedPapers" 
              :key="paper.unique_key"
              @click="goToDetail(paper.unique_key)"
              class="paper-row"
            >
              <td>
                <span class="arxiv-id">{{ paper.arxiv_id }}{{ paper.version }}</span>
              </td>
              <td>
                <span class="paper-title">{{ truncate(paper.title, 50) }}</span>
              </td>
              <td>
                <span class="paper-authors">{{ truncate(paper.authors.join(', '), 30) }}</span>
              </td>
              <td>
                <div class="category-tags">
                  <span 
                    v-for="cat in paper.categories.slice(0, 2)" 
                    :key="cat" 
                    class="category-tag"
                  >
                    {{ cat }}
                  </span>
                  <span v-if="paper.categories.length > 2" class="more-tag">
                    +{{ paper.categories.length - 2 }}
                  </span>
                </div>
              </td>
              <td>
                <span class="date">{{ formatDate(paper.published) }}</span>
              </td>
              <td>
                <div class="actions" @click.stop>
                  <button class="action-btn" @click="goToDetail(paper.unique_key)" title="查看详情">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  </button>
                  <button class="action-btn danger" @click="confirmDelete(paper)" title="删除">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        :total="filteredPapers.length"
        :page-size="pageSize"
        v-model:current-page="currentPage"
      />
    </template>

    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>确定要删除论文 <strong>{{ paperToDelete?.title }}</strong> 吗？</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn-danger" @click="deletePaper">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { paperApi, type Paper } from '../api'
import Pagination from '../components/Pagination.vue'

const router = useRouter()

const papers = ref<Paper[]>([])
const loading = ref(true)
const searchQuery = ref('')
const sortBy = ref('created_at')
const order = ref<'asc' | 'desc'>('desc')
const currentPage = ref(1)
const pageSize = 15
const total = ref(0)

const showDeleteModal = ref(false)
const paperToDelete = ref<Paper | null>(null)

const filteredPapers = computed(() => {
  if (!searchQuery.value) return papers.value
  
  const query = searchQuery.value.toLowerCase()
  return papers.value.filter(p => 
    p.title.toLowerCase().includes(query) ||
    p.authors.some(a => a.toLowerCase().includes(query))
  )
})

const paginatedPapers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredPapers.value.slice(start, start + pageSize)
})

function toggleOrder() {
  order.value = order.value === 'asc' ? 'desc' : 'asc'
}

function truncate(text: string, length: number): string {
  return text.length > length ? text.slice(0, length) + '...' : text
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function goToDetail(uniqueKey: string) {
  router.push(`/papers/${uniqueKey}`)
}

function confirmDelete(paper: Paper) {
  paperToDelete.value = paper
  showDeleteModal.value = true
}

async function deletePaper() {
  if (!paperToDelete.value) return
  
  try {
    await paperApi.delete(paperToDelete.value.unique_key)
    papers.value = papers.value.filter(p => p.unique_key !== paperToDelete.value!.unique_key)
    total.value--
    showDeleteModal.value = false
    paperToDelete.value = null
  } catch (error) {
    console.error('Failed to delete paper:', error)
  }
}

async function loadPapers() {
  loading.value = true
  try {
    const { data } = await paperApi.list(1000, 0, sortBy.value, order.value)
    papers.value = data.papers
    total.value = data.total
  } catch (error) {
    console.error('Failed to load papers:', error)
  } finally {
    loading.value = false
  }
}

watch([sortBy, order], () => {
  loadPapers()
})

onMounted(loadPapers)
</script>

<style scoped>
.papers-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.75rem;
  margin-bottom: 0.25rem;
}

.page-desc {
  color: var(--text-muted);
  font-size: 0.9375rem;
}

.paper-count {
  background: var(--primary);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.controls-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-filter {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.125rem;
  height: 1.125rem;
  color: var(--text-muted);
}

.search-input {
  width: 100%;
  padding-left: 2.5rem;
}

.sort-controls {
  display: flex;
  gap: 0.5rem;
}

.sort-select {
  min-width: 120px;
}

.order-btn {
  width: 2.5rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-muted);
}

.order-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.order-btn.asc svg {
  transform: scaleX(-1);
}

.order-btn svg {
  width: 1.125rem;
  height: 1.125rem;
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

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-hint {
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 1rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--surface);
}

.papers-table {
  width: 100%;
  border-collapse: collapse;
}

.papers-table th {
  white-space: nowrap;
}

.paper-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.paper-row:hover {
  background: var(--surface-hover);
}

.arxiv-id {
  font-family: 'Fira Code', monospace;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--primary);
}

.paper-title {
  font-weight: 500;
}

.paper-authors {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.category-tag {
  font-size: 0.6875rem;
  padding: 0.125rem 0.375rem;
  background: rgba(30, 64, 175, 0.1);
  color: var(--primary);
  border-radius: 0.25rem;
  font-weight: 500;
}

.more-tag {
  font-size: 0.6875rem;
  color: var(--text-muted);
}

.date {
  font-size: 0.8125rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 2rem;
  height: 2rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--radius-sm);
}

.action-btn:hover {
  background: var(--surface-hover);
  color: var(--primary);
  border-color: var(--primary);
}

.action-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  border-color: var(--danger);
}

.action-btn svg {
  width: 1rem;
  height: 1rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: var(--shadow-lg);
}

.modal h3 {
  margin-bottom: 0.75rem;
}

.modal p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .papers-view {
    padding: 1.5rem 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
  }

  .controls-bar {
    flex-direction: column;
  }

  .search-filter {
    min-width: 100%;
  }
}
</style>
