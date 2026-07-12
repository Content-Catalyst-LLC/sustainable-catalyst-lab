from __future__ import annotations

import hmac
import os
import threading
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request, status


class FixedWindowRateLimiter:
    def __init__(self) -> None:
        self.limit = max(5, min(600, int(os.getenv("SC_LAB_RATE_LIMIT_PER_MINUTE", "60"))))
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - 60.0
        with self._lock:
            events = self._events[key]
            while events and events[0] < cutoff:
                events.popleft()
            if len(events) >= self.limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Compute rate limit exceeded.")
            events.append(now)


limiter = FixedWindowRateLimiter()


def require_api_key(x_sc_lab_key: str | None = Header(default=None)) -> None:
    expected = os.getenv("SC_LAB_COMPUTE_API_KEY", "").strip()
    if not expected:
        return
    if not x_sc_lab_key or not hmac.compare_digest(x_sc_lab_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid compute API key.")


def rate_limit(request: Request) -> None:
    host = request.client.host if request.client else "unknown"
    limiter.check(host)
