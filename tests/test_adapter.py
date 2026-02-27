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
