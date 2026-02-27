<template>
  <div class="pagination">
    <button 
      class="page-btn" 
      :disabled="currentPage === 1"
      @click="goToPage(currentPage - 1)"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M15 18l-6-6 6-6"/>
      </svg>
    </button>

    <div class="page-numbers">
      <button
        v-for="page in displayedPages"
        :key="page"
        class="page-num"
        :class="{ active: page === currentPage, ellipsis: page === '...' }"
        :disabled="page === '...'"
        @click="page !== '...' && goToPage(page as number)"
      >
        {{ page }}
      </button>
    </div>

    <button 
      class="page-btn" 
      :disabled="currentPage === totalPages"
      @click="goToPage(currentPage + 1)"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 18l6-6-6-6"/>
      </svg>
    </button>

    <span class="page-info">
      共 {{ total }} 条
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  total: number
  pageSize: number
  currentPage: number
}>()

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void
}>()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

const displayedPages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const current = props.currentPage

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total)
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total)
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total)
    }
  }

  return pages
})

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
    emit('update:currentPage', page)
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0;
}

.page-btn {
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.page-btn:hover:not(:disabled) {
  background: var(--surface-hover);
  border-color: var(--primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-btn svg {
  width: 1rem;
  height: 1rem;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-num {
  min-width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0 0.5rem;
}

.page-num:hover:not(:disabled):not(.ellipsis) {
  background: var(--surface-hover);
  border-color: var(--primary);
}

.page-num.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.page-num.ellipsis {
  border: none;
  background: transparent;
  cursor: default;
}

.page-info {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

@media (max-width: 640px) {
  .page-info {
    display: none;
  }

  .page-num {
    min-width: 2rem;
    height: 2rem;
    font-size: 0.8125rem;
  }

  .page-btn {
    width: 2rem;
    height: 2rem;
  }
}
</style>
