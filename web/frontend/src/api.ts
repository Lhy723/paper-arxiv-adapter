import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface Paper {
  arxiv_id: string
  version: string
  unique_key: string
  title: string
  authors: string[]
  abstract: string
  categories: string[]
  published: string | null
  updated: string | null
  pdf_url: string
  source_url: string
  keywords?: string[]
  summary?: string
}

export interface Stats {
  total_papers: number
  db_size_bytes: number
  db_size_mb: number
  categories: Record<string, number>
}

export interface PapersResponse {
  papers: Paper[]
  total: number
  limit: number
  offset: number
}

export const paperApi = {
  list: (limit = 20, offset = 0, sortBy = 'created_at', order = 'desc') =>
    api.get<PapersResponse>('/papers', { 
      params: { limit, offset, sort_by: sortBy, order } 
    }),
  
  get: (uniqueKey: string) =>
    api.get<Paper>(`/papers/${uniqueKey}`),
  
  delete: (uniqueKey: string) =>
    api.delete(`/papers/${uniqueKey}`),
  
  batchSave: (papers: Paper[]) =>
    api.post<{ message: string; count: number }>('/papers/batch-save', papers),
  
  search: (query: string, maxResults = 10) =>
    api.post<{ papers: Paper[] }>('/search', null, { params: { query, max_results: maxResults } }),
  
  subscribe: (category: string) =>
    api.post<{ papers: Paper[]; count: number }>('/subscribe', null, { params: { category } }),
  
  getStats: () =>
    api.get<Stats>('/stats'),
}
