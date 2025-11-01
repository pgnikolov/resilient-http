import pytest
import httpx
from resilient_http.httpx_async import ResilientAsyncClient
from resilient_http.retry_policy import RetryPolicy
from resilient_http.circuit_breaker import CircuitBreaker
from resilient_http.exceptions import CircuitBreakerOpenError


@pytest.mark.asyncio
async def test_async_retry_success(monkeypatch):
    call_count = {"n": 0}

    async def mock_request(method, url, **kwargs):
        call_count["n"] += 1
        if call_count["n"] < 3:
            raise httpx.ConnectError("boom", request=None)
        return httpx.Response(200)

    client = ResilientAsyncClient(
        retry_policy=RetryPolicy(max_attempts=5)
    )

    monkeypatch.setattr(client.client, "request", mock_request)

    response = await client.get("https://example.com")
    assert response.status_code == 200
    assert call_count["n"] == 3


@pytest.mark.asyncio
async def test_circuit_breaker_blocks(monkeypatch):
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=999)
    client = ResilientAsyncClient(circuit_breaker=breaker)

    # Fail once to open the circuit
    breaker.record_failure("https://test")

    with pytest.raises(CircuitBreakerOpenError):
        await client.get("https://test")

