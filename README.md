# resilient-http

**Resilience layer for Python HTTP clients** (Requests/HTTPX): smart retries with jitter, idempotency-aware policies, and a circuit breaker with half-open probes.

[![CI](https://img.shields.io/github/actions/workflow/status/pgnikolov/resilient-http/ci.yml?label=CI)](https://github.com/pgnikolov/resilient-http/actions)
[![Python](https://img.shields.io/badge/python-3.9--3.13-blue.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Install

```bash
pip install resilient-http
# dev (from source)
pip install -e .[dev]
````

## Quickstart

```python
from resilient_http.session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy

s = ResilientRequestsSession(retry_policy=RetryPolicy(max_attempts=4))
resp = s.get("https://httpbin.org/status/503")
print(resp.status_code)
```

## Features

* Smart retry: exception/status-aware, idempotency by default
* Exponential backoff with jitter (full/equal jitter)
* Circuit breaker (closed → open → half-open)
* Requests wrapper (HTTPX support planned)
* Zero-config defaults; extensible policies

## Why

Stop naive retries. Make your HTTP calls resilient under load, rate limits (429), and transient failures (5xx, timeouts).

## Roadmap

* HTTPX wrapper (sync/async)
* Pluggable metrics (Prometheus)
* Persistent circuit state

## Development

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# or: source .venv/bin/activate  # Linux/macOS

pip install -e .[dev]
pytest -q
black resilient_http tests examples
flake8 resilient_http tests
mypy resilient_http
```

## License

MIT © 2025 Plamen Nikolov
