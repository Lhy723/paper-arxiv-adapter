from __future__ import annotations

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
