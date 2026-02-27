<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible && paper" class="preview-overlay" @click="$emit('close')">
        <div class="preview-modal" @click.stop>
          <header class="preview-header">
            <span class="preview-badge">{{ paper.arxiv_id }}{{ paper.version }}</span>
            <button class="close-btn" @click="$emit('close')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </header>

          <div class="preview-content">
            <h2 class="preview-title">{{ paper.title }}</h2>

            <div class="preview-authors">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
              </svg>
              <span>{{ authorsDisplay }}</span>
            </div>

            <div class="preview-categories">
              <span 
                v-for="cat in paper.categories.slice(0, 4)" 
                :key="cat" 
                class="category-tag"
              >
                {{ cat }}
              </span>
            </div>

            <div class="preview-abstract">
              <h3>摘要</h3>
              <p>{{ abstractDisplay }}</p>
            </div>

            <div class="preview-meta">
              <div class="meta-item">
                <span class="meta-label">发布日期</span>
                <span class="meta-value">{{ formatDate(paper.published) }}</span>
              </div>
            </div>
          </div>

          <footer class="preview-actions">
            <button 
              v-if="!saved"
              class="btn-cta" 
              @click="$emit('save')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              保存到数据库
            </button>
            <span v-else class="saved-badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              已保存
            </span>
            <a 
              :href="paper.pdf_url" 
              target="_blank" 
              rel="noopener noreferrer"
              class="btn-secondary"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              PDF
            </a>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Paper } from '../api'

const props = defineProps<{
  visible: boolean
  paper: Paper | null
  saved?: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
}>()

const authorsDisplay = computed(() => {
  if (!props.paper) return ''
  const authors = props.paper.authors
  if (authors.length <= 3) return authors.join(', ')
  return `${authors.slice(0, 3).join(', ')} 等 ${authors.length} 位作者`
})

const abstractDisplay = computed(() => {
  if (!props.paper) return ''
  const abstract = props.paper.abstract || ''
  if (abstract.length <= 400) return abstract
  return abstract.slice(0, 400) + '...'
})

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.preview-modal {
  background: var(--surface);
  border-radius: var(--radius-xl);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--surface);
  z-index: 1;
}

.preview-badge {
  font-family: 'Fira Code', monospace;
  font-size: 0.8125rem;
  font-weight: 700;
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

.close-btn {
  width: 2rem;
  height: 2rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius);
}

.close-btn:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.close-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.preview-content {
  padding: 1.5rem;
}

.preview-title {
  font-size: 1.25rem;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.preview-authors {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.preview-authors svg {
  width: 1rem;
  height: 1rem;
}

.preview-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-bottom: 1.25rem;
}

.category-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background: rgba(30, 64, 175, 0.1);
  color: var(--primary);
  border-radius: 0.25rem;
  font-weight: 500;
}

.preview-abstract {
  margin-bottom: 1.25rem;
}

.preview-abstract h3 {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.preview-abstract p {
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--text);
}

.preview-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.meta-value {
  font-size: 0.875rem;
  font-weight: 500;
}

.preview-actions {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border);
  background: var(--surface-hover);
}

.preview-actions .btn-cta,
.preview-actions .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: var(--radius);
  font-weight: 600;
  font-size: 0.875rem;
  text-decoration: none;
  cursor: pointer;
}

.preview-actions .btn-cta {
  background: var(--cta);
  color: white;
  border: none;
}

.preview-actions .btn-cta:hover {
  background: var(--cta-hover);
}

.preview-actions .btn-secondary {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}

.preview-actions .btn-secondary:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.preview-actions svg {
  width: 1rem;
  height: 1rem;
}

.saved-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: rgba(34, 197, 94, 0.1);
  color: var(--success);
  border-radius: var(--radius);
  font-weight: 600;
  font-size: 0.875rem;
}

.saved-badge svg {
  width: 1rem;
  height: 1rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
