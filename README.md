# Resilient HTTP

**Production‑grade resilience layer for Python HTTP clients**

Smart retries, jitter backoff, and a circuit breaker with half‑open probes. Works with both **requests** and **httpx (async)**.

[![CI](https://img.shields.io/github/actions/workflow/status/pgnikolov/resilient-http/ci.yml?label=CI)](https://github.com/pgnikolov/resilient-http/actions)
![Python](https://img.shields.io/badge/python-3.9--3.13-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/resilient-http?color=blue)](https://pypi.org/project/resilient-http/)

---

## 🚀 Install

```bash
pip install resilient-http
```

Development:

```bash
pip install -e .[dev]
```

---

## 🍰 Quickstart (Requests)

```python
from resilient_http.session import ResilientRequestsSession
from resilient_http.retry_policy import RetryPolicy

session = ResilientRequestsSession(retry_policy=RetryPolicy(max_attempts=4))
resp = session.get("https://httpbin.org/status/503")
print(resp.status_code)
```

✅ Retries on 503 / 502 / 504 / 429
✅ Exponential backoff + jitter
✅ Stops retrying on 400/401/403/404

---

## ⚡ Quickstart (HTTPX Async)

```python
import httpx
from resilient_http.httpx_async import ResilientAsyncClient
from resilient_http.retry_policy import RetryPolicy

async def main():
    client = ResilientAsyncClient(retry_policy=RetryPolicy(max_attempts=3))
    response = await client.get("https://httpbin.org/status/503")
    print(response.status_code)

import asyncio; asyncio.run(main())
```

---

## ✅ Features

| Capability         | Description                          |
| ------------------ | ------------------------------------ |
| Smart retries      | Status + exception aware             |
| Backoff strategies | Full jitter / exponential            |
| Circuit breaker    | closed → open → half‑open            |
| Idempotency‑aware  | Retries only safe methods by default |
| Sync + Async       | requests + httpx support             |
| Pluggable          | Custom retry logic/backoff hooks     |

---

## 🧠 Why this exists

Production APIs fail. Networks glitch. SaaS rate‑limits you.

This project makes failures boring using proven patterns:

* AWS retry strategy (full jitter)
* Google SRE (equal jitter)
* Netflix Hystrix circuit breaker

---

## 🧱 Design

* No monkey‑patching
* Zero global state
* Strict typing (`mypy` clean)
* Deterministic backoff math
* Works with chaos testing / latency injection

---

## 🧪 Development

```bash
pytest -q
ruff check .
black .
mypy .
```

---

## 📜 License

MIT © 2025 Plamen Nikolov
