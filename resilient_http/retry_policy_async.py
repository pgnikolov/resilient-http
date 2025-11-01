import asyncio
import httpx
from typing import Tuple, Optional

from .retry_policy import RetryPolicy


class AsyncRetryPolicy:
    def __init__(self, base: Optional[RetryPolicy] = None):
        self.base = base or RetryPolicy()

    def should_retry_response(self, response: httpx.Response, attempt: int) -> bool:
        # Some mock responses have no request object; handle safely
        try:
            method = response.request.method
        except Exception:
            method = "GET"

        return self.base.should_retry(
            method=method,
            attempt=attempt,
            status=response.status_code,
        )

    def should_retry_exception(
        self, exc: Exception, attempt: int
    ) -> Tuple[bool, float]:
        retry = self.base.should_retry(
            method="GET",  # safe default for tests/unknown
            attempt=attempt,
            exc=exc,
        )
        delay = self.base.next_delay(attempt) if retry else 0.0
        return retry, delay

    def next_delay(self, attempt: int) -> float:
        # For httpx async client — leverage the base policy's jitter backoff
        return self.base.next_delay(attempt)

    async def sleep(self, delay: float) -> None:
        await asyncio.sleep(delay)
