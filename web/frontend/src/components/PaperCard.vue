<template>
  <article class="paper-card">
    <div class="paper-header">
      <div class="paper-meta">
        <span class="arxiv-id">{{ paper.arxiv_id }}{{ paper.version }}</span>
        <span class="divider">·</span>
        <span class="paper-date">{{ formatDate(paper.published) }}</span>
      </div>
      <h3 class="paper-title">{{ paper.title }}</h3>
    </div>

    <div class="paper-authors">
      <svg class="author-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
      <span>{{ authorsDisplay }}</span>
    </div>

    <p class="paper-abstract">{{ abstractDisplay }}</p>

    <div class="paper-categories">
      <span 
        v-for="category in displayCategories" 
        :key="category" 
        class="category-tag"
      >
        {{ category }}
      </span>
      <span v-if="paper.categories.length > 3" class="more-categories">
        +{{ paper.categories.length - 3 }}
      </span>
    </div>

    <div class="paper-actions">
      <a 
        :href="paper.pdf_url" 
        target="_blank" 
        rel="noopener noreferrer"
        class="action-btn primary"
      >
        <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="12" y1="18" x2="12" y2="12"/>
          <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <span>PDF</span>
      </a>
      <a 
        :href="paper.source_url" 
        target="_blank" 
        rel="noopener noreferrer"
        class="action-btn secondary"
      >
        <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
        <span>arXiv</span>
      </a>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Paper } from '../api'

const props = defineProps<{ paper: Paper }>()

const authorsDisplay = computed(() => {
  const authors = props.paper.authors
  if (authors.length <= 3) {
    return authors.join(', ')
  }
  return `${authors.slice(0, 3).join(', ')} 等 ${authors.length} 位作者`
})

const abstractDisplay = computed(() => {
  const abstract = props.paper.abstract || ''
  if (abstract.length <= 300) {
    return abstract
  }
  return abstract.slice(0, 300) + '...'
})

const displayCategories = computed(() => {
  return props.paper.categories.slice(0, 3)
})

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.paper-card {
  background: var(--surface);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}

.paper-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.paper-header {
  margin-bottom: 0.75rem;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.arxiv-id {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  letter-spacing: 0.025em;
}

.divider {
  color: var(--text-muted);
  opacity: 0.5;
}

.paper-date {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.paper-title {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.4;
  margin: 0;
}

.paper-authors {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.author-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.paper-abstract {
  color: var(--text);
  font-size: 0.9375rem;
  line-height: 1.7;
  margin-bottom: 1rem;
}

.paper-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.category-tag {
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(8, 145, 178, 0.1);
  color: var(--primary);
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
  border: 1px solid rgba(8, 145, 178, 0.2);
}

.more-categories {
  font-size: 0.75rem;
  color: var(--text-muted);
  padding: 0.25rem 0.5rem;
}

.paper-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.action-btn.primary {
  background: var(--primary);
  color: white;
}

.action-btn.primary:hover {
  background: var(--primary-hover);
  color: white;
}

.action-btn.secondary {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--border);
}

.action-btn.secondary:hover {
  background: rgba(8, 145, 178, 0.05);
  border-color: var(--primary);
  color: var(--primary);
}

.action-icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 640px) {
  .paper-card {
    padding: 1rem;
  }

  .paper-title {
    font-size: 1.125rem;
  }

  .paper-actions {
    flex-direction: column;
  }

  .action-btn {
    justify-content: center;
  }
}
</style>
