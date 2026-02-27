import time
from paper_arxiv_adapter.compliance import RateLimiter


def test_rate_limiter_enforces_delay():
    limiter = RateLimiter(min_interval=0.5)
    
    start = time.time()
    limiter.wait_if_needed()
    limiter.wait_if_needed()
    elapsed = time.time() - start
    
    assert elapsed >= 0.5
