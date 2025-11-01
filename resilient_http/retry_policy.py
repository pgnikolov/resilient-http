from dataclasses import dataclass, field
from typing import Iterable, Set, Callable, Optional, Type
from requests import Timeout, ConnectionError as RequestsConnectionError
from httpx import ConnectError as HttpxConnectError, ReadTimeout as HttpxTimeout


@dataclass
class RetryPolicy:
    max_attempts: int = 3

    retry_on_status: Optional[Set[int]] = field(default=None)
    retry_on_exceptions: Iterable[Type[BaseException]] = (
        Timeout,
        RequestsConnectionError,
        HttpxConnectError,
        HttpxTimeout,
    )
    retry_on_methods: Optional[Set[str]] = field(
        default=None
    )  # default: only idempotent if None
    backoff: Optional[Callable[[int], float]] = field(default=None)
    give_up_on_status: Optional[Set[int]] = field(default=None)

    def __post_init__(self):
        if self.retry_on_status is None:
            self.retry_on_status = {429, 500, 502, 503, 504}

        if self.retry_on_methods is None:
            self.retry_on_methods = {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}

        if self.give_up_on_status is None:
            self.give_up_on_status = {400, 401, 403, 404}

        if self.backoff is None:
            from .backoff import full_jitter, exponential_backoff

            exp = exponential_backoff()
            self.backoff = full_jitter(exp)

        # Let mypy know backoff is now definitely callable
        assert self.retry_on_status is not None
        assert self.retry_on_methods is not None
        assert self.give_up_on_status is not None
        assert self.backoff is not None

    def should_retry(
        self,
        method: str,
        attempt: int,
        *,
        status: Optional[int] = None,
        exc: Optional[BaseException] = None,
    ) -> bool:
        # mypy: guarantee non-None sets
        assert self.retry_on_methods is not None
        assert self.retry_on_status is not None
        assert self.give_up_on_status is not None

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
        assert self.backoff is not None
        return float(self.backoff(attempt))

    def should_retry_exception(self, exc: Exception, attempt: int):
        if attempt >= self.max_attempts:
            return False, 0.0

        # Retry on network issues (httpx, requests unified)
        retryable = any(
            isinstance(exc, t)
            for t in self.retry_on_exceptions
        )

        if not retryable:
            return False, 0.0

        delay = self.next_delay(attempt)
        return True, delay
