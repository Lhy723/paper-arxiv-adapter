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
