# ArXiv 论文采集适配器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个轻量级 ArXiv 论文采集适配器，统一单篇/批量/订阅采集接口，支持去重、版本管理、元数据标准化，并提供 Web 界面展示。

**Architecture:** 核心库封装 arxiv.py 和 feedparser，提供统一的 ArxivAdapter 类。存储层抽象支持 SQLite 和无存储模式。Web 层使用 FastAPI 提供 REST API，Vue 3 前端展示数据。

**Tech Stack:** Python 3.10+, arxiv.py, feedparser, FastAPI, SQLite, Vue 3, Vite, uv

---

## Task 1: 初始化 Python 项目

**Files:**
- Create: `pyproject.toml`
- Create: `src/paper_arxiv_adapter/__init__.py`

**Step 1: 初始化 uv 项目**

Run: `uv init --name paper-arxiv-adapter`
Expected: 创建 pyproject.toml

**Step 2: 添加核心依赖**

Run: `uv add arxiv feedparser`
Expected: 更新 pyproject.toml 和 uv.lock

**Step 3: 创建包目录结构**

Run: `mkdir -p src/paper_arxiv_adapter`
Expected: 创建源码目录

**Step 4: 创建 __init__.py**

```python
__version__ = "0.1.0"
```

**Step 5: Commit**

```bash
git add pyproject.toml uv.lock src/paper_arxiv_adapter/__init__.py
git commit -m "chore: init project with uv"
```

---

## Task 2: 实现数据模型

**Files:**
- Create: `src/paper_arxiv_adapter/models.py`
- Create: `tests/test_models.py`

**Step 1: 写失败的测试**

```python
from paper_arxiv_adapter.models import Paper

def test_paper_creation():
    paper = Paper(
        arxiv_id="2301.07041",
        version="v2",
        title="Test Paper",
        authors=["Author One", "Author Two"],
        abstract="This is a test abstract.",
        categories=["cs.AI", "cs.LG"],
        published="2023-01-17T00:00:00Z",
        updated="2023-01-20T00:00:00Z",
        pdf_url="https://arxiv.org/pdf/2301.07041v2",
        source_url="https://arxiv.org/abs/2301.07041v2",
    )
    assert paper.arxiv_id == "2301.07041"
    assert paper.version == "v2"
    assert paper.unique_key == "2301.07041v2"
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL - Paper not defined

**Step 3: 实现数据模型**

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Paper:
    arxiv_id: str
    version: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    published: datetime | str
    updated: datetime | str
    pdf_url: str
    source_url: str
    keywords: list[str] | None = None
    summary: str | None = None
    embedding: list[float] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def unique_key(self) -> str:
        return f"{self.arxiv_id}{self.version}"
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/paper_arxiv_adapter/models.py tests/test_models.py
git commit -m "feat: add Paper data model"
```

---

## Task 3: 实现存储抽象层

**Files:**
- Create: `src/paper_arxiv_adapter/storage.py`
- Create: `tests/test_storage.py`

**Step 1: 写失败的测试**

```python
import tempfile
import os
from paper_arxiv_adapter.storage import SQLiteBackend
from paper_arxiv_adapter.models import Paper
from datetime import datetime

def test_sqlite_backend_save_and_get():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        backend = SQLiteBackend(db_path)
        
        paper = Paper(
            arxiv_id="2301.07041",
            version="v2",
            title="Test Paper",
            authors=["Author One"],
            abstract="Abstract text",
            categories=["cs.AI"],
            published=datetime(2023, 1, 17),
            updated=datetime(2023, 1, 20),
            pdf_url="https://arxiv.org/pdf/2301.07041v2",
            source_url="https://arxiv.org/abs/2301.07041v2",
        )
        
        backend.save(paper)
        retrieved = backend.get("2301.07041v2")
        
        assert retrieved is not None
        assert retrieved.arxiv_id == "2301.07041"
        assert retrieved.version == "v2"

def test_sqlite_backend_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        backend = SQLiteBackend(db_path)
        
        paper1 = Paper(
            arxiv_id="2301.07041",
            version="v1",
            title="Paper 1",
            authors=["Author"],
            abstract="Abstract",
            categories=["cs.AI"],
            published=datetime(2023, 1, 17),
            updated=datetime(2023, 1, 17),
            pdf_url="https://arxiv.org/pdf/2301.07041v1",
            source_url="https://arxiv.org/abs/2301.07041v1",
        )
        paper2 = Paper(
            arxiv_id="2301.07042",
            version="v1",
            title="Paper 2",
            authors=["Author"],
            abstract="Abstract",
            categories=["cs.AI"],
            published=datetime(2023, 1, 18),
            updated=datetime(2023, 1, 18),
            pdf_url="https://arxiv.org/pdf/2301.07042v1",
            source_url="https://arxiv.org/abs/2301.07042v1",
        )
        
        backend.save(paper1)
        backend.save(paper2)
        
        papers = backend.list()
        assert len(papers) == 2
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_storage.py -v`
Expected: FAIL - SQLiteBackend not defined

**Step 3: 实现存储抽象**

```python
import sqlite3
import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import Protocol

from .models import Paper


class StorageBackend(Protocol):
    def save(self, paper: Paper) -> None: ...
    def get(self, unique_key: str) -> Paper | None: ...
    def list(self, limit: int = 100, offset: int = 0) -> list[Paper]: ...
    def delete(self, unique_key: str) -> bool: ...
    def exists(self, unique_key: str) -> bool: ...
    def get_versions(self, arxiv_id: str) -> list[Paper]: ...


class SQLiteBackend:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    unique_key TEXT PRIMARY KEY,
                    arxiv_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    abstract TEXT,
                    categories TEXT NOT NULL,
                    published TEXT,
                    updated TEXT,
                    pdf_url TEXT,
                    source_url TEXT,
                    keywords TEXT,
                    summary TEXT,
                    embedding TEXT,
                    extra TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_arxiv_id ON papers(arxiv_id)
            """)

    def save(self, paper: Paper) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO papers 
                (unique_key, arxiv_id, version, title, authors, abstract, 
                 categories, published, updated, pdf_url, source_url, 
                 keywords, summary, embedding, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                paper.unique_key,
                paper.arxiv_id,
                paper.version,
                paper.title,
                json.dumps(paper.authors),
                paper.abstract,
                json.dumps(paper.categories),
                self._serialize_datetime(paper.published),
                self._serialize_datetime(paper.updated),
                paper.pdf_url,
                paper.source_url,
                json.dumps(paper.keywords) if paper.keywords else None,
                paper.summary,
                json.dumps(paper.embedding) if paper.embedding else None,
                json.dumps(paper.extra) if paper.extra else None,
            ))

    def get(self, unique_key: str) -> Paper | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM papers WHERE unique_key = ?", (unique_key,)
            ).fetchone()
            if row:
                return self._row_to_paper(row)
            return None

    def list(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM papers ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
            return [self._row_to_paper(row) for row in rows]

    def delete(self, unique_key: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM papers WHERE unique_key = ?", (unique_key,)
            )
            return cursor.rowcount > 0

    def exists(self, unique_key: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM papers WHERE unique_key = ?", (unique_key,)
            ).fetchone()
            return row is not None

    def get_versions(self, arxiv_id: str) -> list[Paper]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM papers WHERE arxiv_id = ? ORDER BY version",
                (arxiv_id,),
            ).fetchall()
            return [self._row_to_paper(row) for row in rows]

    def _serialize_datetime(self, dt: datetime | str | None) -> str | None:
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt
        return dt.isoformat()

    def _row_to_paper(self, row: sqlite3.Row) -> Paper:
        return Paper(
            arxiv_id=row["arxiv_id"],
            version=row["version"],
            title=row["title"],
            authors=json.loads(row["authors"]),
            abstract=row["abstract"] or "",
            categories=json.loads(row["categories"]),
            published=row["published"],
            updated=row["updated"],
            pdf_url=row["pdf_url"] or "",
            source_url=row["source_url"] or "",
            keywords=json.loads(row["keywords"]) if row["keywords"] else None,
            summary=row["summary"],
            embedding=json.loads(row["embedding"]) if row["embedding"] else None,
            extra=json.loads(row["extra"]) if row["extra"] else {},
        )


class MemoryBackend:
    def __init__(self):
        self._papers: dict[str, Paper] = {}

    def save(self, paper: Paper) -> None:
        self._papers[paper.unique_key] = paper

    def get(self, unique_key: str) -> Paper | None:
        return self._papers.get(unique_key)

    def list(self, limit: int = 100, offset: int = 0) -> list[Paper]:
        papers = list(self._papers.values())
        return papers[offset : offset + limit]

    def delete(self, unique_key: str) -> bool:
        if unique_key in self._papers:
            del self._papers[unique_key]
            return True
        return False

    def exists(self, unique_key: str) -> bool:
        return unique_key in self._papers

    def get_versions(self, arxiv_id: str) -> list[Paper]:
        return [p for p in self._papers.values() if p.arxiv_id == arxiv_id]
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_storage.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/paper_arxiv_adapter/storage.py tests/test_storage.py
git commit -m "feat: add storage abstraction layer"
```

---

## Task 4: 实现 ArXiv 合规请求规则

**Files:**
- Create: `src/paper_arxiv_adapter/compliance.py`
- Create: `tests/test_compliance.py`

**Step 1: 写失败的测试**

```python
import time
from paper_arxiv_adapter.compliance import RateLimiter

def test_rate_limiter_enforces_delay():
    limiter = RateLimiter(min_interval=0.5)
    
    start = time.time()
    limiter.wait_if_needed()
    limiter.wait_if_needed()
    elapsed = time.time() - start
    
    assert elapsed >= 0.5
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_compliance.py -v`
Expected: FAIL - RateLimiter not defined

**Step 3: 实现合规请求规则**

```python
import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    min_interval: float = 3.0
    _last_request: float = 0.0

    def wait_if_needed(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_request = time.time()


DEFAULT_USER_AGENT = "paper-arxiv-adapter/0.1.0 (https://github.com/user/paper-arxiv-adapter)"


def get_compliant_headers(user_agent: str = DEFAULT_USER_AGENT) -> dict[str, str]:
    return {"User-Agent": user_agent}
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_compliance.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/paper_arxiv_adapter/compliance.py tests/test_compliance.py
git commit -m "feat: add ArXiv compliance rules"
```

---

## Task 5: 实现核心适配器

**Files:**
- Create: `src/paper_arxiv_adapter/adapter.py`
- Create: `tests/test_adapter.py`

**Step 1: 写失败的测试**

```python
from paper_arxiv_adapter.adapter import ArxivAdapter
from paper_arxiv_adapter.storage import MemoryBackend

def test_adapter_fetch_by_id():
    adapter = ArxivAdapter(storage=MemoryBackend())
    paper = adapter.fetch("2301.07041")
    
    assert paper is not None
    assert paper.arxiv_id == "2301.07041"
    assert paper.title != ""

def test_adapter_search():
    adapter = ArxivAdapter(storage=MemoryBackend())
    papers = adapter.search("machine learning", max_results=5)
    
    assert len(papers) <= 5
    if papers:
        assert papers[0].title != ""
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_adapter.py -v`
Expected: FAIL - ArxivAdapter not defined

**Step 3: 实现核心适配器**

```python
import re
from typing import Callable
from dataclasses import dataclass, field

import arxiv
import feedparser

from .models import Paper
from .storage import StorageBackend, MemoryBackend
from .compliance import RateLimiter, DEFAULT_USER_AGENT


@dataclass
class ArxivAdapter:
    storage: StorageBackend | None = None
    rate_limiter: RateLimiter = field(default_factory=RateLimiter)
    user_agent: str = DEFAULT_USER_AGENT

    def fetch(self, arxiv_id: str) -> Paper | None:
        self.rate_limiter.wait_if_needed()
        
        clean_id, version = self._parse_id_with_version(arxiv_id)
        
        client = arxiv.Client()
        client.headers = {"User-Agent": self.user_agent}
        
        search = arxiv.Search(id_list=[clean_id])
        results = list(client.results(search))
        
        if not results:
            return None
        
        result = results[0]
        paper = self._result_to_paper(result, version)
        
        if self.storage:
            self.storage.save(paper)
        
        return paper

    def search(
        self,
        query: str,
        max_results: int = 10,
        categories: list[str] | None = None,
    ) -> list[Paper]:
        self.rate_limiter.wait_if_needed()
        
        client = arxiv.Client()
        client.headers = {"User-Agent": self.user_agent}
        
        search_query = query
        if categories:
            cat_query = " OR ".join(f"cat:{cat}" for cat in categories)
            search_query = f"({query}) AND ({cat_query})"
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        
        results = list(client.results(search))
        papers = [self._result_to_paper(r) for r in results]
        
        if self.storage:
            for paper in papers:
                self.storage.save(paper)
        
        return papers

    def subscribe(
        self,
        category: str,
        on_new: Callable[[Paper], None],
        max_results: int = 100,
    ) -> list[Paper]:
        self.rate_limiter.wait_if_needed()
        
        feed_url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        
        feed = feedparser.parse(feed_url)
        
        new_papers = []
        for entry in feed.entries:
            paper = self._entry_to_paper(entry)
            
            if self.storage and self.storage.exists(paper.unique_key):
                continue
            
            if self.storage:
                self.storage.save(paper)
            
            new_papers.append(paper)
            on_new(paper)
        
        return new_papers

    def get_versions(self, arxiv_id: str) -> list[Paper]:
        if self.storage:
            return self.storage.get_versions(arxiv_id)
        return []

    def _parse_id_with_version(self, arxiv_id: str) -> tuple[str, str]:
        match = re.match(r"^(.+?)(v\d+)?$", arxiv_id)
        if match:
            clean_id = match.group(1)
            version = match.group(2) or "v1"
            return clean_id, version
        return arxiv_id, "v1"

    def _result_to_paper(
        self, result: arxiv.Result, version: str = "v1"
    ) -> Paper:
        arxiv_id = result.entry_id.split("/")[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        
        return Paper(
            arxiv_id=arxiv_id,
            version=version,
            title=result.title,
            authors=[a.name for a in result.authors],
            abstract=result.summary,
            categories=[c for c in result.categories],
            published=result.published,
            updated=result.updated,
            pdf_url=result.pdf_url,
            source_url=result.entry_id,
        )

    def _entry_to_paper(self, entry) -> Paper:
        arxiv_url = entry.get("id", "")
        arxiv_id = arxiv_url.split("/")[-1]
        
        version = "v1"
        match = re.search(r"v(\d+)$", arxiv_id)
        if match:
            version = f"v{match.group(1)}"
            arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        
        return Paper(
            arxiv_id=arxiv_id,
            version=version,
            title=entry.get("title", ""),
            authors=[a.get("name", "") for a in entry.get("authors", [])],
            abstract=entry.get("summary", ""),
            categories=[tag.get("term", "") for tag in entry.get("tags", [])],
            published=entry.get("published"),
            updated=entry.get("updated"),
            pdf_url=f"https://arxiv.org/pdf/{arxiv_id}{version}",
            source_url=arxiv_url,
        )
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_adapter.py -v`
Expected: PASS (注意：此测试会真实调用 ArXiv API)

**Step 5: Commit**

```bash
git add src/paper_arxiv_adapter/adapter.py tests/test_adapter.py
git commit -m "feat: add core ArxivAdapter"
```

---

## Task 6: 更新包导出

**Files:**
- Modify: `src/paper_arxiv_adapter/__init__.py`

**Step 1: 更新 __init__.py**

```python
from .adapter import ArxivAdapter
from .models import Paper
from .storage import SQLiteBackend, MemoryBackend
from .compliance import RateLimiter, DEFAULT_USER_AGENT

__all__ = [
    "ArxivAdapter",
    "Paper",
    "SQLiteBackend",
    "MemoryBackend",
    "RateLimiter",
    "DEFAULT_USER_AGENT",
]
__version__ = "0.1.0"
```

**Step 2: 验证导入**

Run: `uv run python -c "from paper_arxiv_adapter import ArxivAdapter; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add src/paper_arxiv_adapter/__init__.py
git commit -m "feat: export public API"
```

---

## Task 7: 初始化 Web 后端

**Files:**
- Create: `web/backend/pyproject.toml`
- Create: `web/backend/main.py`

**Step 1: 创建后端目录**

Run: `mkdir -p web/backend`

**Step 2: 创建后端 pyproject.toml**

```toml
[project]
name = "paper-arxiv-adapter-web"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "paper-arxiv-adapter",
]

[tool.uv.sources]
paper-arxiv-adapter = { path = "../..", editable = true }
```

**Step 3: 安装后端依赖**

Run: `cd web/backend && uv sync`
Expected: 创建虚拟环境并安装依赖

**Step 4: 创建 FastAPI 应用**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from paper_arxiv_adapter import ArxivAdapter, SQLiteBackend


adapter: ArxivAdapter | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global adapter
    adapter = ArxivAdapter(storage=SQLiteBackend("papers.db"))
    yield
    adapter = None


app = FastAPI(
    title="ArXiv Paper Adapter",
    description="ArXiv 论文采集适配器 API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/api/papers")
async def list_papers(limit: int = 20, offset: int = 0):
    if not adapter or not adapter.storage:
        return {"papers": [], "total": 0}
    papers = adapter.storage.list(limit=limit, offset=offset)
    return {
        "papers": [p.__dict__ for p in papers],
        "total": len(papers),
    }


@app.get("/api/papers/{arxiv_id}")
async def get_paper(arxiv_id: str):
    if not adapter:
        return {"error": "Adapter not initialized"}
    paper = adapter.fetch(arxiv_id)
    if not paper:
        return {"error": "Paper not found"}
    return paper.__dict__


@app.get("/api/papers/{arxiv_id}/versions")
async def get_versions(arxiv_id: str):
    if not adapter:
        return {"versions": []}
    versions = adapter.get_versions(arxiv_id)
    return {"versions": [v.__dict__ for v in versions]}


@app.post("/api/search")
async def search_papers(query: str, max_results: int = 10):
    if not adapter:
        return {"papers": []}
    papers = adapter.search(query, max_results=max_results)
    return {"papers": [p.__dict__ for p in papers]}


@app.post("/api/subscribe")
async def create_subscription(category: str):
    if not adapter:
        return {"papers": []}
    papers = adapter.subscribe(category=category, on_new=lambda p: None)
    return {"papers": [p.__dict__ for p in papers], "count": len(papers)}


app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")


@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")
```

**Step 5: Commit**

```bash
git add web/backend/
git commit -m "feat: add FastAPI backend"
```

---

## Task 8: 初始化 Vue 前端

**Files:**
- Create: `web/frontend/` (Vue 项目)

**Step 1: 创建 Vue 项目**

Run: `cd web && npm create vite@latest frontend -- --template vue-ts`
Expected: 创建 Vue + TypeScript 项目

**Step 2: 安装依赖**

Run: `cd web/frontend && npm install && npm install axios`

**Step 3: 创建 API 服务**

创建 `web/frontend/src/api.ts`:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export interface Paper {
  arxiv_id: string
  version: string
  title: string
  authors: string[]
  abstract: string
  categories: string[]
  published: string
  updated: string
  pdf_url: string
  source_url: string
  keywords?: string[]
  summary?: string
}

export const paperApi = {
  list: (limit = 20, offset = 0) =>
    api.get<{ papers: Paper[]; total: number }>('/papers', { params: { limit, offset } }),
  
  get: (arxivId: string) =>
    api.get<Paper>(`/papers/${arxivId}`),
  
  search: (query: string, maxResults = 10) =>
    api.post<{ papers: Paper[] }>('/search', null, { params: { query, max_results: maxResults } }),
  
  subscribe: (category: string) =>
    api.post<{ papers: Paper[]; count: number }>('/subscribe', null, { params: { category } }),
}
```

**Step 4: 创建论文列表组件**

创建 `web/frontend/src/components/PaperList.vue`:

```vue
<template>
  <div class="paper-list">
    <div v-for="paper in papers" :key="paper.arxiv_id + paper.version" class="paper-card">
      <h3>{{ paper.title }}</h3>
      <p class="authors">{{ paper.authors.join(', ') }}</p>
      <p class="abstract">{{ paper.abstract.slice(0, 200) }}...</p>
      <div class="meta">
        <span class="arxiv-id">{{ paper.arxiv_id }}{{ paper.version }}</span>
        <span class="categories">{{ paper.categories.join(', ') }}</span>
      </div>
      <div class="actions">
        <a :href="paper.pdf_url" target="_blank">PDF</a>
        <a :href="paper.source_url" target="_blank">arXiv</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Paper } from '../api'

defineProps<{ papers: Paper[] }>()
</script>

<style scoped>
.paper-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
.paper-card h3 {
  margin: 0 0 8px;
}
.authors {
  color: #666;
  font-size: 14px;
}
.abstract {
  color: #333;
  font-size: 14px;
  line-height: 1.5;
}
.meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
}
.arxiv-id {
  font-family: monospace;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
}
.actions {
  margin-top: 8px;
  display: flex;
  gap: 12px;
}
.actions a {
  color: #0066cc;
  text-decoration: none;
}
</style>
```

**Step 5: 更新 App.vue**

```vue
<template>
  <div class="app">
    <header>
      <h1>ArXiv Paper Adapter</h1>
      <div class="search">
        <input v-model="searchQuery" placeholder="搜索论文..." @keyup.enter="search" />
        <button @click="search">搜索</button>
      </div>
    </header>
    <main>
      <PaperList :papers="papers" />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PaperList from './components/PaperList.vue'
import { paperApi, type Paper } from './api'

const papers = ref<Paper[]>([])
const searchQuery = ref('')

onMounted(async () => {
  const { data } = await paperApi.list()
  papers.value = data.papers
})

async function search() {
  if (!searchQuery.value.trim()) return
  const { data } = await paperApi.search(searchQuery.value)
  papers.value = data.papers
}
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
header {
  margin-bottom: 24px;
}
header h1 {
  margin-bottom: 16px;
}
.search {
  display: flex;
  gap: 8px;
}
.search input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.search button {
  padding: 8px 16px;
  background: #0066cc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
```

**Step 6: Commit**

```bash
git add web/frontend/
git commit -m "feat: add Vue frontend"
```

---

## Task 9: 配置前端构建和后端集成

**Files:**
- Modify: `web/frontend/vite.config.ts`
- Modify: `web/backend/main.py`

**Step 1: 配置 Vite 构建输出到后端静态目录**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**Step 2: 构建前端**

Run: `cd web/frontend && npm run build`
Expected: 构建输出到 web/backend/static

**Step 3: Commit**

```bash
git add web/frontend/vite.config.ts web/backend/static/
git commit -m "feat: configure frontend build and backend integration"
```

---

## Task 10: 添加项目文档

**Files:**
- Create: `README.md`

**Step 1: 创建 README.md**

```markdown
# ArXiv Paper Adapter

轻量封装 arxiv.py/feedparser，统一「单篇 / 批量 / 订阅」采集接口。

## 功能特性

- 统一采集接口：单篇、批量搜索、RSS 订阅
- 论文去重：基于 arxiv_id + version
- 版本管理：保留所有版本历史
- 元数据标准化：适配 AI 处理场景
- ArXiv 合规请求：内置请求间隔控制
- 可选存储：SQLite 或无存储模式

## 安装

```bash
uv sync
```

## 核心库使用

```python
from paper_arxiv_adapter import ArxivAdapter, SQLiteBackend

adapter = ArxivAdapter(storage=SQLiteBackend("papers.db"))

# 单篇采集
paper = adapter.fetch("2301.07041v2")

# 批量搜索
papers = adapter.search("machine learning", max_results=10)

# RSS 订阅
adapter.subscribe(category="cs.AI", on_new=lambda p: print(p.title))
```

## 运行 Web 应用

```bash
# 构建前端
cd web/frontend && npm run build

# 启动后端
cd web/backend && uv run uvicorn main:app --reload
```

访问 http://localhost:8000

## 开源协议

MIT License
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## 完成检查

- [ ] 核心库可以正常导入
- [ ] 单篇采集功能正常
- [ ] 批量搜索功能正常
- [ ] RSS 订阅功能正常
- [ ] SQLite 存储功能正常
- [ ] Web API 可以访问
- [ ] 前端页面可以显示论文列表
