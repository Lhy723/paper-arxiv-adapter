from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from paper_arxiv_adapter import ArxivAdapter, SQLiteBackend
from paper_arxiv_adapter.models import Paper


BASE_DIR = Path(__file__).resolve().parent

adapter: ArxivAdapter | None = None


class PaperData(BaseModel):
    arxiv_id: str
    version: str = "v1"
    title: str
    authors: List[str]
    abstract: str = ""
    categories: List[str]
    published: str | None = None
    updated: str | None = None
    pdf_url: str = ""
    source_url: str = ""


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
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>ArXiv Paper Adapter - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body { margin: 0; padding: 0; }</style>
</head>
<body>
    <redoc spec-url='/openapi.json'></redoc>
    <script src="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js"></script>
</body>
</html>
""")


@app.get("/api/stats")
async def get_stats():
    if not adapter or not adapter.storage:
        return {"total_papers": 0, "db_size_bytes": 0, "db_size_mb": 0, "categories": {}}
    return adapter.storage.get_stats()


@app.get("/api/papers")
async def list_papers(
    limit: int = 20, 
    offset: int = 0,
    sort_by: str = Query("created_at", pattern="^(created_at|title|published|updated|arxiv_id)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    if not adapter or not adapter.storage:
        return {"papers": [], "total": 0, "limit": limit, "offset": offset}
    
    total = adapter.storage.count()
    papers = adapter.storage.list(limit=limit, offset=offset, sort_by=sort_by, order=order)
    
    return {
        "papers": [paper_to_dict(p) for p in papers],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/papers/{unique_key}")
async def get_paper(unique_key: str):
    if not adapter or not adapter.storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    paper = adapter.storage.get(unique_key)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper_to_dict(paper)


@app.delete("/api/papers/{unique_key}")
async def delete_paper(unique_key: str):
    if not adapter or not adapter.storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    if not adapter.storage.exists(unique_key):
        raise HTTPException(status_code=404, detail="Paper not found")
    
    success = adapter.storage.delete(unique_key)
    if success:
        return {"message": "Paper deleted successfully"}
    raise HTTPException(status_code=500, detail="Failed to delete paper")


@app.get("/api/papers/{arxiv_id}/versions")
async def get_versions(arxiv_id: str):
    if not adapter:
        return {"versions": []}
    versions = adapter.get_versions(arxiv_id)
    return {"versions": [paper_to_dict(v) for v in versions]}


@app.post("/api/search")
async def search_papers(query: str, max_results: int = 10):
    if not adapter:
        return {"papers": []}
    papers = adapter.search(query, max_results=max_results)
    return {"papers": [paper_to_dict(p) for p in papers]}


@app.post("/api/papers/batch-save")
async def batch_save_papers(papers: List[PaperData]):
    if not adapter or not adapter.storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    saved_count = 0
    for paper_data in papers:
        paper = Paper(
            arxiv_id=paper_data.arxiv_id,
            version=paper_data.version,
            title=paper_data.title,
            authors=paper_data.authors,
            abstract=paper_data.abstract,
            categories=paper_data.categories,
            published=paper_data.published or "",
            updated=paper_data.updated or "",
            pdf_url=paper_data.pdf_url,
            source_url=paper_data.source_url,
        )
        adapter.storage.save(paper)
        saved_count += 1
    
    return {"message": f"Saved {saved_count} papers", "count": saved_count}


@app.post("/api/subscribe")
async def create_subscription(category: str):
    if not adapter:
        return {"papers": []}
    papers = adapter.subscribe(category=category, on_new=lambda p: None)
    return {"papers": [paper_to_dict(p) for p in papers], "count": len(papers)}


def paper_to_dict(paper: Paper) -> dict:
    return {
        "arxiv_id": paper.arxiv_id,
        "version": paper.version,
        "unique_key": paper.unique_key,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "categories": paper.categories,
        "published": str(paper.published) if paper.published else None,
        "updated": str(paper.updated) if paper.updated else None,
        "pdf_url": paper.pdf_url,
        "source_url": paper.source_url,
        "keywords": paper.keywords,
        "summary": paper.summary,
    }


app.mount("/assets", StaticFiles(directory=BASE_DIR / "static" / "assets"), name="assets")


@app.get("/")
async def serve_frontend():
    return FileResponse(BASE_DIR / "static" / "index.html")
