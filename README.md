# resilient-http

**Resilience layer for Python HTTP clients**: smart retries (idempotency-aware), jitter backoff, and a circuit breaker with half-open probes.

Designed for production workloads where flaky upstreams, throttling (429) and transient 5xx failures are reality.

[![CI](https://img.shields.io/github/actions/workflow/status/pgnikolov/resilient-http/ci.yml?label=CI)](https://github.com/pgnikolov/resilient-http/actions)
![Python](https://img.shields.io/badge/python-3.9--3.13-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/resilient-http?color=blue)](https://pypi.org/project/resilient-http/)
[![Typing](https://img.shields.io/badge/typing-mypy%20strict-blue.svg)](#)

---

## Install

```bash
pip install resilient-http
````

Development install:

```bash
pip install -e .[dev]
```

---

## Quickstart

```python
from resilient_http.session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy

session = ResilientRequestsSession(
    retry_policy=RetryPolicy(max_attempts=4)
)

resp = session.get("https://httpbin.org/status/503")

print("HTTP:", resp.status_code)
```

Expected behavior:

* retry on 503 (and timeouts, 502/504, 429)
* exponential backoff + jitter
* stops retrying on permanent errors (400/401/403/404)

---

## Features

✅ Smart retry (status/exception aware)

✅ Exponential backoff (full jitter / equal jitter)

✅ Circuit breaker (closed → open → half-open trial)

✅ Idempotent-method policy by default

✅ Drop-in wrapper for `requests.Session`


Planned

* HTTPX wrapper (`sync` + `async`)
* Prometheus metrics hooks
* Persistent circuit state
* Policy plugins

---

## Why?

Naive sleeps and dumb retry loops don’t survive production load.

This library implements practices from:

* AWS retry strategy (full jitter)
* Google SRE (equal jitter)
* Netflix Hystrix-style circuit breaking

Make upstream failures boring. 🧊

---

## Design Principles

* Sensible defaults, override when needed
* Zero global state
* Pure python, no patching `requests`
* Type-safe (`mypy` clean)
* Works under real latency & chaos scenarios

---

## Development

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -e .[dev]

pytest -q
black resilient_http tests
flake8 resilient_http tests
mypy resilient_http
```

---

## License

MIT © 2025 Plamen Nikolov
