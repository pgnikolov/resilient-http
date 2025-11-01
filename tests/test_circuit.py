import pytest
from resilient_http.circuit_breaker import CircuitBreaker
from resilient_http.exceptions import CircuitBreakerOpenError
from resilient_http.httpx_async import ResilientAsyncClient


@pytest.mark.asyncio
async def test_circuit_breaker_blocks():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=999)
    client = ResilientAsyncClient(circuit_breaker=breaker)

    breaker.record_failure("https://test")

    with pytest.raises(CircuitBreakerOpenError):
        await client.get("https://test")
