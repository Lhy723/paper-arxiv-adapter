<template>
  <div class="paper-detail-view">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>加载论文详情...</span>
    </div>

    <template v-else-if="paper">
      <div class="detail-header">
        <button class="back-btn" @click="goBack">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>返回</span>
        </button>
      </div>

      <article class="paper-detail">
        <header class="paper-header">
          <div class="paper-meta">
            <span class="arxiv-badge">{{ paper.arxiv_id }}{{ paper.version }}</span>
            <span class="meta-item">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              {{ formatDate(paper.published) }}
            </span>
          </div>
          <h1 class="paper-title">{{ paper.title }}</h1>
        </header>

        <section class="paper-section">
          <h2>作者</h2>
          <div class="authors-list">
            <span v-for="author in paper.authors" :key="author" class="author-tag">
              {{ author }}
            </span>
          </div>
        </section>

        <section class="paper-section">
          <h2>分类</h2>
          <div class="categories-list">
            <span v-for="cat in paper.categories" :key="cat" class="category-tag">
              {{ cat }}
            </span>
          </div>
        </section>

        <section class="paper-section">
          <h2>摘要</h2>
          <p class="abstract-text">{{ paper.abstract }}</p>
        </section>

        <section class="paper-section metadata">
          <h2>元数据</h2>
          <div class="metadata-grid">
            <div class="meta-row">
              <span class="meta-label">arXiv ID</span>
              <span class="meta-value">{{ paper.arxiv_id }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">版本</span>
              <span class="meta-value">{{ paper.version }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">发布日期</span>
              <span class="meta-value">{{ formatDate(paper.published) || '-' }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">更新日期</span>
              <span class="meta-value">{{ formatDate(paper.updated) || '-' }}</span>
            </div>
          </div>
        </section>

        <section class="paper-actions">
          <a 
            :href="paper.pdf_url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="action-btn primary"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            下载 PDF
          </a>
          <a 
            :href="paper.source_url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="action-btn secondary"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            访问 arXiv
          </a>
          <button class="action-btn danger" @click="confirmDelete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
            删除
          </button>
        </section>
      </article>
    </template>

    <div v-else class="error-state">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      <p>论文未找到</p>
      <button class="btn-primary" @click="goBack">返回列表</button>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal" @click.stop>
        <h3>确认删除</h3>
        <p>确定要删除这篇论文吗？此操作无法撤销。</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="showDeleteModal = false">取消</button>
          <button class="btn-danger" @click="deletePaper">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { paperApi, type Paper } from '../api'

const route = useRoute()
const router = useRouter()

const paper = ref<Paper | null>(null)
const loading = ref(true)
const showDeleteModal = ref(false)

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  } catch {
    return dateStr
  }
}

function goBack() {
  router.push('/papers')
}

function confirmDelete() {
  showDeleteModal.value = true
}

async function deletePaper() {
  if (!paper.value) return
  
  try {
    await paperApi.delete(paper.value.unique_key)
    router.push('/papers')
  } catch (error) {
    console.error('Failed to delete paper:', error)
  }
}

onMounted(async () => {
  const uniqueKey = route.params.id as string
  
  try {
    const { data } = await paperApi.get(uniqueKey)
    paper.value = data
  } catch (error) {
    console.error('Failed to load paper:', error)
    paper.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.paper-detail-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
  color: var(--text-muted);
  text-align: center;
}

.error-icon {
  width: 4rem;
  height: 4rem;
  color: var(--danger);
}

.detail-header {
  margin-bottom: 1.5rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 0.5rem 0;
  cursor: pointer;
  font-weight: 500;
}

.back-btn:hover {
  color: var(--primary);
}

.back-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.paper-detail {
  background: var(--surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.paper-header {
  padding: 2rem;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(135deg, rgba(30, 64, 175, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.arxiv-badge {
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
  font-weight: 700;
  background: var(--primary);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

.meta-item svg {
  width: 1rem;
  height: 1rem;
}

.paper-title {
  font-size: 1.5rem;
  line-height: 1.4;
  margin: 0;
}

.paper-section {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border);
}

.paper-section:last-of-type {
  border-bottom: none;
}

.paper-section h2 {
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

.authors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.author-tag {
  background: var(--surface-hover);
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  color: var(--text);
}

.categories-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category-tag {
  background: rgba(30, 64, 175, 0.1);
  color: var(--primary);
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius);
  font-size: 0.8125rem;
  font-weight: 500;
}

.abstract-text {
  font-size: 0.9375rem;
  line-height: 1.8;
  color: var(--text);
  margin: 0;
  white-space: pre-wrap;
}

.metadata-grid {
  display: grid;
  gap: 0.75rem;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-light);
}

.meta-row:last-child {
  border-bottom: none;
}

.meta-label {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.meta-value {
  font-weight: 500;
  font-family: 'Fira Code', monospace;
  font-size: 0.875rem;
}

.paper-actions {
  padding: 1.5rem 2rem;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  background: var(--surface-hover);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: var(--radius);
  font-weight: 600;
  font-size: 0.9375rem;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.action-btn.primary {
  background: var(--primary);
  color: white;
  border: none;
}

.action-btn.primary:hover {
  background: var(--primary-hover);
}

.action-btn.secondary {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}

.action-btn.secondary:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.action-btn.danger {
  background: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}

.action-btn.danger:hover {
  background: var(--danger);
  color: white;
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
  .paper-detail-view {
    padding: 1.5rem 1rem;
  }

  .paper-header {
    padding: 1.5rem;
  }

  .paper-section {
    padding: 1.25rem 1.5rem;
  }

  .paper-title {
    font-size: 1.25rem;
  }

  .paper-actions {
    padding: 1.25rem 1.5rem;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
