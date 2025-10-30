from dataclasses import dataclass
from typing import Iterable, Set, Callable, Optional

import requests


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    retry_on_status: Set[int] = None
    retry_on_exceptions: Iterable[type] = (requests.Timeout, requests.ConnectionError)
    retry_on_methods: Set[str] = None  # default: only idempotent if None
    backoff: Optional[Callable[[int], float]] = None
    give_up_on_status: Set[int] = None  # permanent errors

    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = {429, 500, 502, 503, 504}
        if self.retry_on_methods is None:
            self.retry_on_methods = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}
        if self.give_up_on_status is None:
            self.give_up_on_status = {400, 401, 403, 404}

        if self.backoff is None:
            from .backoff import full_jitter, exponential_backoff
            self.backoff = full_jitter(exponential_backoff())

    def should_retry(self, method: str, attempt: int, *, status: Optional[int] = None, exc: Optional[BaseException] = None) -> bool:
        if attempt >= self.max_attempts - 1:
            return False

        if method.upper() not in self.retry_on_methods:
            return False

        if exc is not None:
            return any(isinstance(exc, t) for t in self.retry_on_exceptions)

        if status is not None:
            if status in self.give_up_on_status:
                return False
            return status in self.retry_on_status

        return False

    def next_delay(self, attempt: int) -> float:
        return float(self.backoff(attempt))
