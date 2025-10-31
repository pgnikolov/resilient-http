from resilient_http.circuit_breaker import CircuitBreaker
import time


def test_circuit_opens_and_closes():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2)
    key = "GET http://x"

    # first failure
    cb.record_failure(key)
    assert cb.state(key) == "closed"

    # second failure triggers open
    cb.record_failure(key)
    assert cb.state(key) == "open"

    # wait for half-open
    time.sleep(0.25)
    assert cb.state(key) == "half-open"

    # on success closes
    cb.record_success(key)
    assert cb.state(key) == "closed"
