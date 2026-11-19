"""In-memory sliding-window limiter (anonymous AI requests, login/registration attempts).

Signed-in users are limited by counting their stored messages in PostgreSQL, so
their limits survive restarts. This in-process limiter is fine for a single API
instance; with several instances move it to Redis.
"""

import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def hit(self, key: str) -> int | None:
        """Register a request. Returns None if allowed, else seconds to wait."""
        now = time.monotonic()
        hits = self._hits[key]
        while hits and hits[0] <= now - self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return int(hits[0] + self.window - now) + 1
        hits.append(now)
        return None

    def reset(self) -> None:
        self._hits.clear()
