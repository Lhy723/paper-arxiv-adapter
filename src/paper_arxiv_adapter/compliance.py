from __future__ import annotations

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
