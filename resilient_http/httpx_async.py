from __future__ import annotations

import httpx
import asyncio
from typing import Optional, Callable, Any
from .retry_policy_async import AsyncRetryPolicy
from .retry_policy import RetryPolicy
from .circuit_breaker import CircuitBreaker
from .exceptions import CircuitBreakerOpenError


class ResilientAsyncClient:
    def __init__(
        self,
        retry_policy: Optional[object] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        client: Optional[httpx.AsyncClient] = None,
        on_retry: Optional[Callable[[int, Exception], Any]] = None,
    ):
        #  convert sync RetryPolicy to async one automatically
        if isinstance(retry_policy, RetryPolicy):
            retry_policy = AsyncRetryPolicy(retry_policy)

        #  If None, use default async retry policy
        self.retry_policy = retry_policy or AsyncRetryPolicy()

        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.client = client or httpx.AsyncClient()
        self.on_retry = on_retry

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        key = url

        if not self.circuit_breaker.allow_call(key):
            raise CircuitBreakerOpenError(f"Circuit open for {key}")

        attempts = 0

        while True:
            try:
                # Wrap request in try so exception is caught for retry
                response = await self.client.request(method, url, **kwargs)

                # Retry on retryable response
                if self.retry_policy.should_retry_response(response, attempts):
                    if self.on_retry:
                        self.on_retry(attempts, response)
                    wait = self.retry_policy.next_delay(attempts)
                    attempts += 1
                    await asyncio.sleep(wait)
                    continue

                # Success
                self.circuit_breaker.record_success(key)
                return response

            except Exception as exc:
                # Check if we should retry exception
                should_retry, delay = self.retry_policy.should_retry_exception(
                    exc, attempts
                )

                if not should_retry:
                    self.circuit_breaker.record_failure(key)
                    raise

                attempts += 1

                if self.on_retry:
                    self.on_retry(attempts, exc)

                await self.retry_policy.sleep(delay)
                continue

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def close(self):
        await self.client.aclose()
