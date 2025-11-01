import pytest
import httpx
from resilient_http.httpx_async import ResilientAsyncClient
from resilient_http.circuit_breaker import CircuitBreaker
from resilient_http.retry_policy_async import AsyncRetryPolicy
from resilient_http.exceptions import CircuitBreakerOpenError


@pytest.mark.asyncio
async def test_retry_and_success():
    # Mock server response
    async def handler(request):
        if not hasattr(test_retry_and_success, "called"):
            test_retry_and_success.called = True
            return httpx.Response(503)  # fail first time
        return httpx.Response(200, text="OK")

    transport = httpx.MockTransport(handler)
    client = ResilientAsyncClient(
        client=httpx.AsyncClient(transport=transport), retry_policy=AsyncRetryPolicy()
    )

    response = await client.get("http://test")
    assert response.status_code == 200
    assert response.text == "OK"


@pytest.mark.asyncio
async def test_circuit_breaker_blocks():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=999)
    client = ResilientAsyncClient(circuit_breaker=breaker)

    # Simulate failure
    breaker.record_failure("http://test")

    with pytest.raises(CircuitBreakerOpenError):
        await client.get("http://test")
