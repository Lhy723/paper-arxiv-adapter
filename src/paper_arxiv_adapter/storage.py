from __future__ import annotations

import sqlite3
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from .models import Paper


class StorageBackend(Protocol):
    def save(self, paper: Paper) -> None: ...
    def get(self, unique_key: str) -> Paper | None: ...
    def list(self, limit: int = 100, offset: int = 0, sort_by: str = "created_at", order: str = "desc") -> list[Paper]: ...
    def delete(self, unique_key: str) -> bool: ...
    def exists(self, unique_key: str) -> bool: ...
    def get_versions(self, arxiv_id: str) -> list[Paper]: ...
    def count(self) -> int: ...
    def get_stats(self) -> dict: ...
    def get_category_stats(self) -> dict[str, int]: ...


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

    def list(self, limit: int = 100, offset: int = 0, sort_by: str = "created_at", order: str = "desc") -> list[Paper]:
        valid_sort_fields = {"created_at", "title", "published", "updated", "arxiv_id"}
        valid_orders = {"asc", "desc"}
        
        sort_field = sort_by if sort_by in valid_sort_fields else "created_at"
        order_dir = order.upper() if order in valid_orders else "DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = f"SELECT * FROM papers ORDER BY {sort_field} {order_dir} LIMIT ? OFFSET ?"
            rows = conn.execute(query, (limit, offset)).fetchall()
            return [self._row_to_paper(row) for row in rows]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM papers").fetchone()
            return row[0] if row else 0

    def get_stats(self) -> dict:
        import os
        db_size = 0
        if os.path.exists(self.db_path):
            db_size = os.path.getsize(self.db_path)
        
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            categories_row = conn.execute("SELECT categories FROM papers").fetchall()
            
            category_counts: dict[str, int] = {}
            for (cats_json,) in categories_row:
                if cats_json:
                    cats = json.loads(cats_json)
                    for cat in cats:
                        category_counts[cat] = category_counts.get(cat, 0) + 1
            
            return {
                "total_papers": total,
                "db_size_bytes": db_size,
                "db_size_mb": round(db_size / (1024 * 1024), 2),
                "categories": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            }

    def get_category_stats(self) -> dict[str, int]:
        with sqlite3.connect(self.db_path) as conn:
            categories_row = conn.execute("SELECT categories FROM papers").fetchall()
            
            category_counts: dict[str, int] = {}
            for (cats_json,) in categories_row:
                if cats_json:
                    cats = json.loads(cats_json)
                    for cat in cats:
                        category_counts[cat] = category_counts.get(cat, 0) + 1
            
            return category_counts

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

    def list(self, limit: int = 100, offset: int = 0, sort_by: str = "created_at", order: str = "desc") -> list[Paper]:
        papers = list(self._papers.values())
        reverse = order == "desc"
        
        if sort_by == "title":
            papers.sort(key=lambda p: p.title, reverse=reverse)
        elif sort_by == "arxiv_id":
            papers.sort(key=lambda p: p.arxiv_id, reverse=reverse)
        else:
            papers.sort(key=lambda p: p.arxiv_id, reverse=reverse)
        
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

    def count(self) -> int:
        return len(self._papers)

    def get_stats(self) -> dict:
        category_counts: dict[str, int] = {}
        for paper in self._papers.values():
            for cat in paper.categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_papers": len(self._papers),
            "db_size_bytes": 0,
            "db_size_mb": 0,
            "categories": dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }

    def get_category_stats(self) -> dict[str, int]:
        category_counts: dict[str, int] = {}
        for paper in self._papers.values():
            for cat in paper.categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        return category_counts
