import pytest
from resilient_http.session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy


def test_retry_on_503(monkeypatch):
    # Fake response object
    class FakeResp:
        def __init__(self, status):
            self.status_code = status

    call_count = {"n": 0}

    class FakeSession:
        def request(self, *a, **k):
            call_count["n"] += 1
            return FakeResp(503)

    s = ResilientRequestsSession(
        retry_policy=RetryPolicy(max_attempts=3),
        session=FakeSession()
    )

    resp = s.get("http://example.com")

    # Should retry 3 times then return response
    assert resp.status_code == 503
    assert call_count["n"] == 3
