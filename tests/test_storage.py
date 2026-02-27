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
