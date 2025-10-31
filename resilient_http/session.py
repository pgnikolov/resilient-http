import time
from typing import Optional

import requests

from .retry_policy import RetryPolicy
from .circuit_breaker import CircuitBreaker
from .exceptions import CircuitOpenError


class ResilientRequestsSession:
    """
    HTTP client wrapper providing:
    - Smart retry (status/exception aware)
    - Idempotency-safe retry behavior
    - Exponential backoff w/ jitter
    - Circuit breaker pattern
    """

    def __init__(
        self,
        *,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        session: Optional[requests.Session] = None,
    ):
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit = circuit_breaker or CircuitBreaker()
        self.session = session or requests.Session()

    def request(self, method: str, url: str, **kwargs):
        key = self._circuit_key(method, url)

        # Circuit breaker gate
        if not self.circuit.allow_call(key):
            raise CircuitOpenError(key)

        attempt = 0

        while True:
            try:
                resp = self.session.request(method, url, **kwargs)

                # Success
                if resp.status_code < 400:
                    self.circuit.record_success(key)
                    return resp

                # Check retry by HTTP status
                if not self.retry_policy.should_retry(
                    method, attempt, status=resp.status_code
                ):
                    # Permanent or exhausted → failure
                    if 400 <= resp.status_code < 600:
                        self.circuit.record_failure(key)
                    return resp

                # Retry path
                self._sleep_retry(attempt)
                attempt += 1
                continue

            except Exception as e:
                # Check retry by exception
                if not self.retry_policy.should_retry(method, attempt, exc=e):
                    self.circuit.record_failure(key)
                    raise

                self._sleep_retry(attempt)
                attempt += 1

    # Convenience helpers
    def get(self, url, **kw):
        return self.request("GET", url, **kw)

    def post(self, url, **kw):
        return self.request("POST", url, **kw)

    def put(self, url, **kw):
        return self.request("PUT", url, **kw)

    def delete(self, url, **kw):
        return self.request("DELETE", url, **kw)

    # Helpers
    def _circuit_key(self, method: str, url: str) -> str:
        return f"{method.upper()} {url}"

    def _sleep_retry(self, attempt: int):
        delay = self.retry_policy.next_delay(attempt)
        time.sleep(delay)
