<template>
  <div class="home-view">
    <header class="hero">
      <h1>ArXiv Paper Adapter</h1>
      <p class="hero-desc">搜索、发现、管理学术论文</p>
    </header>

    <section class="search-section">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input 
          v-model="searchQuery" 
          placeholder="搜索论文标题、作者或关键词..."
          @keyup.enter="search"
          class="search-input"
        />
        <button @click="search" class="search-btn" :disabled="loading">
          搜索
        </button>
      </div>

      <div class="search-options">
        <div class="option-group">
          <label>排序方式</label>
          <select v-model="sortBy">
            <option value="relevance">相关性</option>
            <option value="submittedDate">发布日期</option>
            <option value="lastUpdatedDate">更新日期</option>
          </select>
        </div>
        <div class="option-group">
          <label>每页显示</label>
          <select v-model="pageSize">
            <option :value="10">10 条</option>
            <option :value="20">20 条</option>
            <option :value="50">50 条</option>
          </select>
        </div>
      </div>

      <div class="quick-tags">
        <span class="tag-label">热门搜索：</span>
        <button 
          v-for="tag in popularTags" 
          :key="tag" 
          @click="quickSearch(tag)"
          class="quick-tag"
        >
          {{ tag }}
        </button>
      </div>
    </section>

    <section v-if="loading" class="loading-section">
      <div class="spinner"></div>
      <span>搜索中...</span>
    </section>

    <template v-else-if="searchResults.length > 0">
      <section class="results-header">
        <div class="results-info">
          <h2>搜索结果</h2>
          <span class="results-count">共 {{ searchResults.length }} 篇论文</span>
        </div>
        <div class="selection-actions">
          <label class="select-all">
            <input 
              type="checkbox" 
              :checked="allSelected"
              @change="toggleSelectAll"
            />
            <span>全选</span>
          </label>
          <button 
            v-if="selectedPapers.length > 0"
            class="btn-cta"
            @click="saveSelected"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              <polyline points="17 21 17 13 7 13 7 21"/>
              <polyline points="7 3 7 8 15 8"/>
            </svg>
            保存选中 ({{ selectedPapers.length }})
          </button>
        </div>
      </section>

      <div class="results-list">
        <div 
          v-for="paper in searchResults" 
          :key="paper.unique_key"
          class="result-item"
          :class="{ selected: isSelected(paper.unique_key) }"
        >
          <div class="result-checkbox">
            <input 
              type="checkbox"
              :checked="isSelected(paper.unique_key)"
              @change="toggleSelect(paper)"
            />
          </div>
          <div class="result-content" @click="openPreview(paper)">
            <div class="result-header">
              <span class="arxiv-id">{{ paper.arxiv_id }}{{ paper.version }}</span>
              <span class="result-date">{{ formatDate(paper.published) }}</span>
            </div>
            <h3 class="result-title">{{ paper.title }}</h3>
            <p class="result-authors">{{ paper.authors.slice(0, 3).join(', ') }}{{ paper.authors.length > 3 ? ` 等 ${paper.authors.length} 位` : '' }}</p>
            <p class="result-abstract">{{ truncate(paper.abstract, 200) }}</p>
            <div class="result-categories">
              <span v-for="cat in paper.categories.slice(0, 3)" :key="cat" class="category-tag">
                {{ cat }}
              </span>
            </div>
          </div>
          <div class="result-actions">
            <button class="preview-btn" @click.stop="openPreview(paper)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </template>

    <section v-else-if="searched" class="empty-section">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
      </svg>
      <p>未找到相关论文</p>
      <p class="empty-hint">尝试使用不同的关键词搜索</p>
    </section>

    <PaperPreview
      :visible="showPreview"
      :paper="previewPaper"
      :saved="isSaved(previewPaper?.unique_key)"
      @close="showPreview = false"
      @save="savePaper(previewPaper)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { paperApi, type Paper } from '../api'
import PaperPreview from '../components/PaperPreview.vue'

const searchQuery = ref('')
const sortBy = ref('relevance')
const pageSize = ref(10)
const loading = ref(false)
const searched = ref(false)

const searchResults = ref<Paper[]>([])
const selectedKeys = ref<Set<string>>(new Set())
const savedKeys = ref<Set<string>>(new Set())

const showPreview = ref(false)
const previewPaper = ref<Paper | null>(null)

const popularTags = ['machine learning', 'deep learning', 'NLP', 'computer vision', 'transformer', 'GPT']

const allSelected = computed(() => {
  return searchResults.value.length > 0 && 
         searchResults.value.every(p => selectedKeys.value.has(p.unique_key))
})

function isSelected(key: string) {
  return selectedKeys.value.has(key)
}

function isSaved(key?: string) {
  return key ? savedKeys.value.has(key) : false
}

function toggleSelect(paper: Paper) {
  if (selectedKeys.value.has(paper.unique_key)) {
    selectedKeys.value.delete(paper.unique_key)
  } else {
    selectedKeys.value.add(paper.unique_key)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedKeys.value.clear()
  } else {
    searchResults.value.forEach(p => selectedKeys.value.add(p.unique_key))
  }
}

const selectedPapers = computed(() => {
  return searchResults.value.filter(p => selectedKeys.value.has(p.unique_key))
})

async function search() {
  if (!searchQuery.value.trim()) return
  
  loading.value = true
  searched.value = false
  selectedKeys.value.clear()
  
  try {
    const { data } = await paperApi.search(searchQuery.value, pageSize.value)
    searchResults.value = data.papers.map(p => ({
      ...p,
      unique_key: `${p.arxiv_id}${p.version}`
    }))
    searched.value = true
  } catch (error) {
    console.error('Search failed:', error)
  } finally {
    loading.value = false
  }
}

function quickSearch(tag: string) {
  searchQuery.value = tag
  search()
}

function openPreview(paper: Paper) {
  previewPaper.value = paper
  showPreview.value = true
}

async function savePaper(paper: Paper | null) {
  if (!paper) return
  
  try {
    await paperApi.batchSave([paper])
    savedKeys.value.add(paper.unique_key)
    selectedKeys.value.delete(paper.unique_key)
  } catch (error) {
    console.error('Failed to save paper:', error)
  }
}

async function saveSelected() {
  if (selectedPapers.value.length === 0) return
  
  try {
    await paperApi.batchSave(selectedPapers.value)
    selectedPapers.value.forEach(p => {
      savedKeys.value.add(p.unique_key)
    })
    selectedKeys.value.clear()
  } catch (error) {
    console.error('Failed to save papers:', error)
  }
}

function truncate(text: string, length: number): string {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.home-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.hero {
  text-align: center;
  margin-bottom: 2rem;
}

.hero h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-desc {
  color: var(--text-muted);
  font-size: 1.125rem;
}

.search-section {
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: var(--surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  padding: 0.5rem;
  gap: 0.5rem;
  border: 2px solid var(--border);
  transition: border-color 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--primary);
}

.search-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: var(--text-muted);
  margin-left: 1rem;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.75rem;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  box-shadow: none;
}

.search-btn {
  background: var(--primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-lg);
  font-weight: 600;
}

.search-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.search-options {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  justify-content: center;
}

.option-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-group label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.option-group select {
  padding: 0.375rem 2rem 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.quick-tags {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.tag-label {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.quick-tag {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--primary);
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-tag:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.loading-section,
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  gap: 1rem;
  color: var(--text-muted);
  text-align: center;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  opacity: 0.5;
}

.empty-hint {
  font-size: 0.875rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.results-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-info h2 {
  font-size: 1.25rem;
}

.results-count {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.selection-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
  cursor: pointer;
}

.select-all input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-item {
  display: flex;
  gap: 1rem;
  background: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  padding: 1rem;
  transition: all 0.2s ease;
}

.result-item:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow);
}

.result-item.selected {
  border-color: var(--primary);
  background: rgba(30, 64, 175, 0.02);
}

.result-checkbox {
  padding-top: 0.25rem;
}

.result-checkbox input {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.result-content {
  flex: 1;
  cursor: pointer;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.arxiv-id {
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--primary);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: var(--radius-sm);
}

.result-date {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.result-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.result-authors {
  font-size: 0.8125rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.result-abstract {
  font-size: 0.875rem;
  color: var(--text);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.result-categories {
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

.result-actions {
  display: flex;
  align-items: flex-start;
}

.preview-btn {
  width: 2rem;
  height: 2rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--radius);
  cursor: pointer;
}

.preview-btn:hover {
  background: var(--surface-hover);
  color: var(--primary);
  border-color: var(--primary);
}

.preview-btn svg {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .home-view {
    padding: 1.5rem 1rem;
  }

  .hero h1 {
    font-size: 1.5rem;
  }

  .search-box {
    flex-direction: column;
    padding: 1rem;
  }

  .search-icon {
    display: none;
  }

  .search-input {
    width: 100%;
    text-align: center;
  }

  .search-btn {
    width: 100%;
  }

  .search-options {
    flex-direction: column;
    align-items: stretch;
  }

  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .selection-actions {
    justify-content: space-between;
  }
}
</style>
