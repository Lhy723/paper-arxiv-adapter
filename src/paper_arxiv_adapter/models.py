from __future__ import annotations

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
