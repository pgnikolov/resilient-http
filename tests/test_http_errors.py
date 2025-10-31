from resilient_http.session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy


def test_no_retry_on_400(monkeypatch):
    class FakeResp:
        status_code = 400

    class FakeSession:
        def request(self, *a, **k):
            return FakeResp()

    s = ResilientRequestsSession(
        retry_policy=RetryPolicy(max_attempts=3), session=FakeSession()
    )

    resp = s.get("http://example.com")
    assert resp.status_code == 400
